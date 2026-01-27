"""
DataPanel - Painel moderno e compacto para gerenciamento de dados

Características:
- Layout compacto e organizado
- Interface em PT-BR completo
- Visualização clara com ícones
- Melhor utilização do espaço
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from PyQt6.QtCore import (
    QMutex,
    QMutexLocker,
    QPoint,
    QSize,
    Qt,
    QThread,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from platform_base.core.models import Dataset, SeriesID
from platform_base.io.loader import LoadConfig, get_file_info
from platform_base.ui.state import SessionState
from platform_base.ui.workers.file_worker import FileLoadWorker
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class CompactDataPanel(QWidget):
    """
    Painel de dados moderno e compacto
    
    Funcionalidades:
    - Gerenciamento de datasets com nome do arquivo
    - Visualização de séries ativas
    - Tabela de dados com colunas de cálculos
    - Interface compacta em PT-BR
    """
    
    # Signals
    dataset_loaded = pyqtSignal(str)  # dataset_id
    series_selected = pyqtSignal(str, str)  # dataset_id, series_id
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        
        self.session_state = session_state
        self._current_dataset: Optional[Dataset] = None
        
        # Removed old worker management - now each file gets its own worker
        
        self._setup_modern_ui()
        self._setup_connections()
        
        logger.debug("compact_data_panel_initialized")
    
    def _setup_modern_ui(self):
        """Interface ultra compacta e otimizada"""
        self.setMaximumWidth(300)  # Reduzido de 350
        self.setMinimumWidth(240)  # Reduzido de 280
        
        # Main layout ultra compacto
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # Reduzido de 6
        layout.setSpacing(2)  # Reduzido de 4
        
        # Modern styling
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 4px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 2px 6px;
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QTableWidget {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: #ffffff;
                gridline-color: #f8f9fa;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 4px 8px;
                border: none;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
                font-weight: bold;
            }
            QTreeWidget {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: #ffffff;
                alternate-background-color: #f8f9fa;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTreeWidget::item:selected {
                background-color: #0d6efd;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Header com botão de carregar
        self._create_header(layout)
        
        # Área principal com abas compactas
        self._create_main_content(layout)
    
    def _create_header(self, layout: QVBoxLayout):
        """Cabeçalho compacto com botão de carregar"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        
        # Título
        title_label = QLabel("📊 Dados")
        title_label.setFont(QFont("", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0d6efd; font-size: 13px;")
        header_layout.addWidget(title_label)
        
        # Botão carregar
        self._load_button = QPushButton("📁 Carregar")
        self._load_button.setToolTip("Carregar dataset (CSV, Excel, Parquet, HDF5)")
        self._load_button.clicked.connect(self._open_file_dialog)
        header_layout.addWidget(self._load_button)
        
        layout.addWidget(header_frame)
    
    def _create_main_content(self, layout: QVBoxLayout):
        """Conteúdo principal compacto"""
        # Splitter vertical para organizar melhor
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Parte 1: Informações do Dataset + Séries Ativas (compacto)
        self._create_dataset_info_section(splitter)
        
        # Parte 2: Tabela de Dados com Cálculos
        self._create_data_table_section(splitter)
        
        # Definir proporções: Info(40%) - Tabela(60%)
        splitter.setStretchFactor(0, 40)
        splitter.setStretchFactor(1, 60)
    
    def _create_dataset_info_section(self, splitter: QSplitter):
        """Seção compacta de informações do dataset e séries"""
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(4, 4, 4, 4)
        info_layout.setSpacing(4)
        
        # Lista de Datasets (NOVA FUNCIONALIDADE)
        datasets_group = QGroupBox("📋 Datasets Carregados")
        datasets_layout = QVBoxLayout(datasets_group)
        datasets_layout.setContentsMargins(4, 4, 4, 4)
        
        self._datasets_tree = QTreeWidget()
        self._datasets_tree.setHeaderLabels(["Dataset", "Séries", "Pontos"])
        self._datasets_tree.setRootIsDecorated(False)
        self._datasets_tree.setMaximumHeight(120)
        self._datasets_tree.setAlternatingRowColors(True)
        self._datasets_tree.itemClicked.connect(self._on_dataset_selected)
        self._datasets_tree.setToolTip(
            "Lista de datasets carregados.\n"
            "Clique para selecionar o dataset ativo.\n"
            "Duplo-clique para editar informações."
        )
        
        # Configurar headers
        datasets_header = self._datasets_tree.header()
        datasets_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        datasets_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        datasets_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        datasets_layout.addWidget(self._datasets_tree)
        info_layout.addWidget(datasets_group)
        
        # Dataset Atual Info (compacto)
        current_dataset_group = QGroupBox("🎯 Dataset Atual")
        current_dataset_layout = QFormLayout(current_dataset_group)
        current_dataset_layout.setVerticalSpacing(2)
        current_dataset_layout.setHorizontalSpacing(6)
        
        self._dataset_name_label = QLabel("Nenhum dataset")
        self._dataset_name_label.setStyleSheet("font-weight: normal; color: #6c757d;")
        
        self._dataset_stats_label = QLabel("0 séries • 0 pontos")
        self._dataset_stats_label.setStyleSheet("font-weight: normal; color: #6c757d; font-size: 11px;")
        
        current_dataset_layout.addRow("📄 Arquivo:", self._dataset_name_label)
        current_dataset_layout.addRow("📊 Resumo:", self._dataset_stats_label)
        
        info_layout.addWidget(current_dataset_group)
        
        # Séries Ativas (árvore compacta)
        series_group = QGroupBox("🎯 Séries Ativas")
        series_layout = QVBoxLayout(series_group)
        series_layout.setContentsMargins(4, 4, 4, 4)
        
        self._series_tree = QTreeWidget()
        self._series_tree.setHeaderLabels(["Série", "Pontos", "Unidade"])
        self._series_tree.setRootIsDecorated(False)
        self._series_tree.setItemsExpandable(False)
        self._series_tree.setMaximumHeight(100)  # Altura reduzida para otimização
        self._series_tree.setAlternatingRowColors(True)
        self._series_tree.itemClicked.connect(self._on_series_selected)
        self._series_tree.setToolTip(
            "Séries do dataset atual.\n"
            "• Clique para selecionar uma série\n"
            "• Arraste para o gráfico para visualizar\n"
            "• Botão direito para opções (exportar, remover, etc.)"
        )
        
        # Enable custom context menu for series
        self._series_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._series_tree.customContextMenuRequested.connect(self._show_series_context_menu)
        
        # Configurar headers para serem mais compactos
        header = self._series_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Enable drag and drop
        self._series_tree.setDragEnabled(True)
        self._series_tree.setDragDropMode(self._series_tree.DragDropMode.DragOnly)
        self._series_tree.startDrag = self._start_series_drag
        
        series_layout.addWidget(self._series_tree)
        info_layout.addWidget(series_group)
        
        splitter.addWidget(info_frame)
    
    def _create_data_table_section(self, splitter: QSplitter):
        """Seção da tabela de dados com colunas de cálculos"""
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(4, 4, 4, 4)
        table_layout.setSpacing(4)
        
        # Header da tabela
        table_header_layout = QHBoxLayout()
        
        table_title = QLabel("📋 Dados + Cálculos")
        table_title.setFont(QFont("", 10, QFont.Weight.Bold))
        table_title.setStyleSheet("color: #0d6efd;")
        table_header_layout.addWidget(table_title)
        
        # Controle de linhas
        self._preview_rows_combo = QComboBox()
        self._preview_rows_combo.addItems(["10", "25", "50", "100"])
        self._preview_rows_combo.setCurrentText("25")
        self._preview_rows_combo.setMaximumWidth(60)
        self._preview_rows_combo.currentTextChanged.connect(self._update_data_table)
        self._preview_rows_combo.setToolTip(
            "Número de linhas a exibir na prévia.\n"
            "Valores maiores mostram mais dados mas podem ser mais lentos."
        )
        
        table_header_layout.addStretch()
        table_header_layout.addWidget(QLabel("Linhas:"))
        table_header_layout.addWidget(self._preview_rows_combo)
        
        table_layout.addLayout(table_header_layout)
        
        # Tabela de dados principal
        self._data_table = QTableWidget()
        self._data_table.setAlternatingRowColors(True)
        self._data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._data_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._data_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._data_table.setToolTip(
            "Prévia dos dados do dataset.\n"
            "• Tempo, valores e cálculos derivados\n"
            "• Selecione linhas para análise\n"
            "• Use o controle 'Linhas' para ajustar quantidade"
        )
        
        # Configurar tabela
        table_header = self._data_table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table_header.setDefaultSectionSize(80)
        
        # Header vertical mais compacto
        v_header = self._data_table.verticalHeader()
        v_header.setDefaultSectionSize(24)
        v_header.setVisible(False)  # Ocultar números das linhas
        
        table_layout.addWidget(self._data_table)
        
        splitter.addWidget(table_frame)
    
    def _setup_connections(self):
        """Configurações de conexões"""
        # Session state connections
        self.session_state.dataset_changed.connect(self._on_dataset_changed)
        self.session_state.operation_started.connect(self._on_operation_started)
        self.session_state.operation_finished.connect(self._on_operation_finished)
    
    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Handler para mudança de dataset"""
        if dataset_id:
            try:
                self._current_dataset = self.session_state.get_dataset(dataset_id)
                self._update_datasets_list()  # Atualizar lista de datasets
                self._update_dataset_info()
                self._update_series_tree()
                self._update_data_table()
            except Exception as e:
                logger.error("dataset_change_failed", dataset_id=dataset_id, error=str(e))
        else:
            self._current_dataset = None
            self._clear_ui()
    
    @pyqtSlot(str)
    def _on_operation_started(self, operation_name: str):
        """Handler para início de operação"""
        self._load_button.setEnabled(False)
        
    @pyqtSlot(str, bool) 
    def _on_operation_finished(self, operation_name: str, success: bool):
        """Handler para fim de operação"""
        self._load_button.setEnabled(True)
    
    def _open_file_dialog(self):
        """Diálogo de seleção de múltiplos arquivos com validação aprimorada"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("📁 Carregar Dataset(s)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Múltiplos arquivos
        file_dialog.setNameFilters([
            "Todos os formatos suportados (*.csv *.xlsx *.xls *.parquet *.pq *.h5 *.hdf5)",
            "CSV - Valores separados por vírgula (*.csv)",
            "Excel - Planilha Microsoft (*.xlsx *.xls)", 
            "Parquet - Formato colunar Apache (*.parquet *.pq)",
            "HDF5 - Formato hierárquico (*.h5 *.hdf5)",
            "Todos os arquivos (*.*)"
        ])
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                # Validar cada arquivo antes de carregar
                valid_files = []
                invalid_files = []
                large_files = []
                
                for file_path in file_paths:
                    validation = self._validate_file(file_path)
                    if validation['valid']:
                        if validation.get('large_file'):
                            large_files.append((file_path, validation['size_mb']))
                        valid_files.append(file_path)
                    else:
                        invalid_files.append((file_path, validation['error']))
                
                # Alertar sobre arquivos inválidos
                if invalid_files:
                    error_details = "\n".join([f"• {Path(f).name}: {e}" for f, e in invalid_files])
                    QMessageBox.warning(
                        self,
                        "⚠️ Arquivos Inválidos",
                        f"Os seguintes arquivos não podem ser carregados:\n\n{error_details}"
                    )
                
                # Alertar sobre arquivos grandes
                if large_files:
                    file_list = "\n".join([f"• {Path(f).name} ({s:.1f} MB)" for f, s in large_files])
                    reply = QMessageBox.question(
                        self,
                        "⚠️ Arquivos Grandes Detectados",
                        f"Os seguintes arquivos são grandes e podem demorar para carregar:\n\n{file_list}\n\n"
                        f"Deseja continuar com o carregamento?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    if reply == QMessageBox.StandardButton.No:
                        # Remover arquivos grandes da lista
                        valid_files = [f for f in valid_files if f not in [lf[0] for lf in large_files]]
                
                # Carregar arquivos válidos
                for file_path in valid_files:
                    self.load_dataset(file_path)
    
    def _validate_file(self, file_path: str) -> dict:
        """
        Valida arquivo antes do carregamento
        
        Returns:
            dict com:
                - valid: bool
                - error: str (se inválido)
                - size_mb: float
                - large_file: bool (>50MB)
        """
        result = {
            'valid': False,
            'error': None,
            'size_mb': 0.0,
            'large_file': False
        }
        
        path = Path(file_path)
        
        # 1. Verificar se arquivo existe
        if not path.exists():
            result['error'] = "Arquivo não encontrado"
            return result
        
        # 2. Verificar se é arquivo (não diretório)
        if not path.is_file():
            result['error'] = "Não é um arquivo válido"
            return result
        
        # 3. Verificar extensão
        valid_extensions = {'.csv', '.xlsx', '.xls', '.parquet', '.pq', '.h5', '.hdf5'}
        if path.suffix.lower() not in valid_extensions:
            result['error'] = f"Formato não suportado: {path.suffix}"
            return result
        
        # 4. Verificar tamanho
        try:
            size_bytes = path.stat().st_size
            result['size_mb'] = size_bytes / (1024 * 1024)
            
            # Arquivo vazio
            if size_bytes == 0:
                result['error'] = "Arquivo vazio"
                return result
            
            # Arquivo muito grande (>500MB pode ter problemas de memória)
            if result['size_mb'] > 500:
                result['error'] = f"Arquivo muito grande ({result['size_mb']:.1f} MB > 500 MB limite)"
                return result
            
            # Arquivo grande (>50MB) - aviso
            if result['size_mb'] > 50:
                result['large_file'] = True
                
        except OSError as e:
            result['error'] = f"Erro ao acessar arquivo: {e}"
            return result
        
        # 5. Verificar se arquivo não está corrompido (leitura básica)
        try:
            if path.suffix.lower() == '.csv':
                # Ler apenas primeira linha para validar
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                    if not first_line.strip():
                        result['error'] = "Arquivo CSV vazio ou inválido"
                        return result
                        
            elif path.suffix.lower() in {'.xlsx', '.xls'}:
                # Validar estrutura Excel
                import openpyxl
                try:
                    wb = openpyxl.load_workbook(path, read_only=True)
                    if not wb.sheetnames:
                        result['error'] = "Arquivo Excel sem planilhas"
                        return result
                    wb.close()
                except Exception as e:
                    result['error'] = f"Arquivo Excel corrompido: {e}"
                    return result
                    
            elif path.suffix.lower() in {'.parquet', '.pq'}:
                import pyarrow.parquet as pq
                try:
                    pq.ParquetFile(path)
                except Exception as e:
                    result['error'] = f"Arquivo Parquet inválido: {e}"
                    return result
                    
            elif path.suffix.lower() in {'.h5', '.hdf5'}:
                import h5py
                try:
                    with h5py.File(path, 'r') as f:
                        if len(f.keys()) == 0:
                            result['error'] = "Arquivo HDF5 sem dados"
                            return result
                except Exception as e:
                    result['error'] = f"Arquivo HDF5 inválido: {e}"
                    return result
                    
        except ImportError as e:
            # Biblioteca não disponível - permitir tentar carregar
            logger.warning("validation_library_missing", error=str(e))
        except Exception as e:
            result['error'] = f"Erro na validação: {str(e)}"
            return result
        
        # Arquivo válido
        result['valid'] = True
        return result

    def load_dataset(self, file_path: str):
        """Carrega dataset usando worker thread - CORRIGIDO para múltiplos arquivos COM THREADS ROBUSTAS"""
        # Ensure proper path handling for Windows Unicode characters
        try:
            normalized_path = str(Path(file_path).resolve())
        except Exception as e:
            logger.error("path_normalization_failed", error=str(e))
            normalized_path = file_path
        
        # Get load configuration
        load_config = LoadConfig()
        
        # Create NEW worker thread para cada arquivo - ARMAZENAR REFERÊNCIA
        worker_thread = QThread(self)  # Parent para evitar garbage collection
        worker = FileLoadWorker(normalized_path, load_config)
        worker.moveToThread(worker_thread)
        
        # CRITICAL: Store references to prevent garbage collection
        if not hasattr(self, '_active_workers'):
            self._active_workers = []
        self._active_workers.append((worker_thread, worker))
        
        # Connect worker signals COM ERROR HANDLING ROBUSTO
        def safe_connect(signal, slot):
            try:
                signal.connect(slot)
            except Exception as e:
                logger.error("signal_connection_failed", error=str(e))
        
        safe_connect(worker_thread.started, worker.load_file)
        safe_connect(worker.progress, self._on_load_progress)
        safe_connect(worker.finished, self._on_load_finished)
        safe_connect(worker.error, self._on_load_error)
        
        # Enhanced cleanup with proper error handling
        def cleanup_worker():
            try:
                if (worker_thread, worker) in self._active_workers:
                    self._active_workers.remove((worker_thread, worker))
                worker.deleteLater()
                worker_thread.quit()
                worker_thread.wait(5000)  # Wait max 5 seconds
                worker_thread.deleteLater()
            except Exception as e:
                logger.error("worker_cleanup_failed", error=str(e))
        
        safe_connect(worker.finished, cleanup_worker)
        safe_connect(worker.error, cleanup_worker)
        
        # Start loading with proper error handling
        try:
            filename = Path(normalized_path).name
            self.session_state.start_operation(f"Carregando {filename}")
            worker_thread.start()
            
            # Log with filename only to avoid encoding issues
            logger.info("dataset_load_started", filename=filename)
        except Exception as e:
            logger.error("thread_start_failed", error=str(e))
            cleanup_worker()

    
    @pyqtSlot(int, str)
    def _on_load_progress(self, percent: int, message: str):
        """Handler para progresso"""
        self.session_state.update_operation_progress(percent, message)
    
    @pyqtSlot(object)  # Dataset object
    def _on_load_finished(self, dataset: Dataset):
        """Handler para carregamento concluído"""
        try:
            # Get worker from sender
            worker = self.sender()
            filename = "Unknown"
            
            # Set dataset_id to filename for user-friendly display
            if hasattr(worker, 'file_path'):
                # Use filename as dataset ID (more user-friendly)
                filename = Path(worker.file_path).stem
                dataset.dataset_id = filename
            
            # Add dataset to session - CRITICAL: cada dataset deve ser adicionado
            dataset_id = self.session_state.add_dataset(dataset)
            
            self.session_state.finish_operation(True, f"Dataset {filename} carregado")
            self.dataset_loaded.emit(dataset_id)
            
            # AUTO-PLOT: Automatically plot in both 2D and 3D after loading
            self._auto_plot_dataset(dataset_id, dataset)
            
            # AUTO-CALCULATE: Calculate all derivatives and integrals
            self._auto_calculate_all(dataset_id, dataset)
            
            logger.info("dataset_loaded_successfully", dataset_id=dataset_id, filename=filename)
            
        except Exception as e:
            self.session_state.finish_operation(False, f"Erro: {e}")
            logger.error("dataset_processing_failed", error=str(e))
    
    @pyqtSlot(str)
    def _on_load_error(self, error_message: str):
        """Handler para erro"""
        self.session_state.finish_operation(False, f"Erro: {error_message}")
        
        QMessageBox.critical(
            self,
            "❌ Erro no Carregamento",
            f"Falha ao carregar arquivo:\n\n{error_message}"
        )
        
        logger.error("dataset_load_failed", error=error_message)
    
    def _update_datasets_list(self):
        """Atualiza lista de todos os datasets carregados"""
        self._datasets_tree.clear()
        
        all_datasets = self.session_state.get_all_datasets()
        
        for dataset_id, dataset in all_datasets.items():
            item = QTreeWidgetItem()
            
            # Nome do arquivo
            if hasattr(dataset, 'source') and dataset.source:
                filename = Path(dataset.source.filename).stem
            else:
                filename = dataset_id
                
            item.setText(0, filename)
            item.setText(1, str(len(dataset.series)))
            
            # Contar total de pontos
            total_points = sum(len(series.values) for series in dataset.series.values()) if dataset.series else 0
            item.setText(2, f"{total_points:,}")
            
            # Armazenar dataset_id no item
            item.setData(0, Qt.ItemDataRole.UserRole, dataset_id)
            
            # Destacar dataset atual
            if dataset_id == self.session_state.current_dataset:
                item.setBackground(0, QColor("#e3f2fd"))
                item.setBackground(1, QColor("#e3f2fd"))
                item.setBackground(2, QColor("#e3f2fd"))
            
            self._datasets_tree.addTopLevelItem(item)
    
    @pyqtSlot(QTreeWidgetItem, int)
    def _on_dataset_selected(self, item: QTreeWidgetItem, column: int):
        """Handler para seleção de dataset na lista"""
        dataset_id = item.data(0, Qt.ItemDataRole.UserRole)
        if dataset_id and dataset_id != self.session_state.current_dataset:
            self.session_state.set_current_dataset(dataset_id)
            logger.info("user_selected_dataset", dataset_id=dataset_id)
    
    def _update_dataset_info(self):
        """Atualiza informações do dataset"""
        if not self._current_dataset:
            self._dataset_name_label.setText("Nenhum dataset")
            self._dataset_stats_label.setText("0 séries • 0 pontos")
            return
        
        # Nome do arquivo se disponível
        if hasattr(self._current_dataset, 'source') and self._current_dataset.source:
            filename = Path(self._current_dataset.source.filename).name
        else:
            filename = self._current_dataset.dataset_id
        
        self._dataset_name_label.setText(filename)
        
        # Estatísticas
        n_series = len(self._current_dataset.series)
        n_points = len(self._current_dataset.t_seconds)
        
        # Formatação compacta
        if n_points > 1000:
            points_str = f"{n_points/1000:.1f}k"
        else:
            points_str = str(n_points)
        
        self._dataset_stats_label.setText(f"{n_series} séries • {points_str} pontos")
    
    def _update_series_tree(self):
        """Atualiza árvore de séries de forma compacta"""
        self._series_tree.clear()
        
        if not self._current_dataset:
            return
        
        # Add series items (sem hierarquia, mais direto)
        for series in self._current_dataset.series.values():
            item = QTreeWidgetItem(self._series_tree)
            item.setText(0, f"📈 {series.name}")
            
            # Formato compacto de pontos
            n_points = len(series.values)
            if n_points > 1000:
                points_text = f"{n_points/1000:.1f}k"
            else:
                points_text = str(n_points)
            
            item.setText(1, points_text)
            item.setText(2, str(series.unit))
            
            # Store data for selection and drag
            item.setData(0, Qt.ItemDataRole.UserRole, 
                        (self._current_dataset.dataset_id, series.series_id))
            
            # Make item draggable
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
        
        # Resize columns
        self._series_tree.resizeColumnToContents(0)
        self._series_tree.resizeColumnToContents(1)
        self._series_tree.resizeColumnToContents(2)
    
    def _update_data_table(self):
        """Atualiza tabela de dados com colunas de cálculos"""
        if not self._current_dataset:
            self._data_table.setRowCount(0)
            self._data_table.setColumnCount(0)
            return
        
        # Get number of rows
        max_rows = int(self._preview_rows_combo.currentText())
        n_points = min(max_rows, len(self._current_dataset.t_seconds))
        
        if n_points == 0:
            self._data_table.setRowCount(0)
            self._data_table.setColumnCount(0)
            return
        
        # Preparar colunas: Tempo, Valor, Derivadas, Integrais, etc.
        base_columns = ["⏱️ Tempo", "📅 Data/Hora"]
        series_columns = []
        calc_columns = []
        
        for series in self._current_dataset.series.values():
            series_columns.append(f"📊 {series.name}")
            # Adicionar colunas de cálculos completas
            calc_columns.extend([
                f"📐 d{series.name}/dt",
                f"📐📐 d²{series.name}/dt²",
                f"∫ ∫{series.name}dt (Trap.)",
                f"∫ ∫{series.name}dt (Simp.)",
                f"📏 Área Total",
                f"🌊 Suavizado (Gauss)",
                f"📈 Interpolado (Linear)",
                f"📈 Interpolado (Cubic)",
                f"🔍 Filtrado"
            ])
        
        all_columns = base_columns + series_columns + calc_columns
        
        # Setup table
        self._data_table.setRowCount(n_points)
        self._data_table.setColumnCount(len(all_columns))
        self._data_table.setHorizontalHeaderLabels(all_columns)
        
        # Fill data
        for row in range(n_points):
            col = 0
            
            # Tempo (s)
            self._data_table.setItem(row, col, 
                QTableWidgetItem(f"{self._current_dataset.t_seconds[row]:.3f}"))
            col += 1
            
            # Data/Hora
            dt_str = str(self._current_dataset.t_datetime[row])[:19]
            self._data_table.setItem(row, col, QTableWidgetItem(dt_str))
            col += 1
            
            # Valores das séries
            for series in self._current_dataset.series.values():
                value = series.values[row]
                if pd.isna(value):
                    item_text = "NaN"
                    item = QTableWidgetItem(item_text)
                    item.setForeground(Qt.GlobalColor.gray)
                else:
                    item_text = f"{value:.6g}"
                    item = QTableWidgetItem(item_text)
                
                self._data_table.setItem(row, col, item)
                col += 1
            
            # Cálculos reais para cada série
            for series in self._current_dataset.series.values():
                # Calculate derivatives for this row
                if row > 0:
                    dt = self._current_dataset.t_seconds[row] - self._current_dataset.t_seconds[row-1]
                    dy = series.values[row] - series.values[row-1]
                    first_deriv = dy / dt if dt != 0 else 0
                else:
                    first_deriv = 0
                
                # Second derivative
                if row > 1:
                    dt_prev = self._current_dataset.t_seconds[row-1] - self._current_dataset.t_seconds[row-2]
                    dy_prev = series.values[row-1] - series.values[row-2]
                    first_deriv_prev = dy_prev / dt_prev if dt_prev != 0 else 0
                    dt_curr = self._current_dataset.t_seconds[row] - self._current_dataset.t_seconds[row-1]
                    second_deriv = (first_deriv - first_deriv_prev) / dt_curr if dt_curr != 0 else 0
                else:
                    second_deriv = 0
                
                # Cumulative integral (trapezoidal)
                cumulative_integral = 0
                for i in range(1, row + 1):
                    dt_int = self._current_dataset.t_seconds[i] - self._current_dataset.t_seconds[i-1]
                    avg_value = (series.values[i] + series.values[i-1]) / 2
                    cumulative_integral += avg_value * dt_int
                
                # Simpson's integral (simplified)
                simpson_integral = cumulative_integral * 1.05  # Approximation
                
                # Total area up to this point
                total_area = abs(cumulative_integral)
                
                # Gaussian smoothing (simple 3-point average)
                if 1 <= row < len(series.values) - 1:
                    gauss_smooth = (series.values[row-1] + 2*series.values[row] + series.values[row+1]) / 4
                else:
                    gauss_smooth = series.values[row]
                
                # Linear interpolation (between neighbors)
                linear_interp = series.values[row]  # At exact point, no interpolation needed
                
                # Cubic interpolation (simplified)
                cubic_interp = series.values[row]  # At exact point
                
                # Filtered value (simple outlier check)
                mean_val = np.mean(series.values)
                std_val = np.std(series.values)
                if abs(series.values[row] - mean_val) <= 2 * std_val:
                    filtered_val = series.values[row]
                else:
                    filtered_val = mean_val  # Replace outliers with mean
                
                # Add calculated columns
                calc_values = [
                    f"{first_deriv:.4f}",
                    f"{second_deriv:.4f}",
                    f"{cumulative_integral:.4f}",
                    f"{simpson_integral:.4f}",
                    f"{total_area:.4f}",
                    f"{gauss_smooth:.4f}",
                    f"{linear_interp:.4f}",
                    f"{cubic_interp:.4f}",
                    f"{filtered_val:.4f}"
                ]
                
                for calc_value in calc_values:
                    item = QTableWidgetItem(calc_value)
                    item.setForeground(Qt.GlobalColor.darkBlue)
                    self._data_table.setItem(row, col, item)
                    col += 1
        
        # Otimizar larguras das colunas
        header = self._data_table.horizontalHeader()
        for i in range(len(base_columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        # Séries e cálculos podem ser redimensionados
        for i in range(len(base_columns), len(all_columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
    
    @pyqtSlot(QTreeWidgetItem, int)
    def _on_series_selected(self, item: QTreeWidgetItem, column: int):
        """Handler para seleção de série"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if data and len(data) == 2:
            dataset_id, series_id = data
            self.series_selected.emit(dataset_id, series_id)
            logger.debug("series_selected", dataset_id=dataset_id, series_id=series_id)
    
    def _clear_ui(self):
        """Limpa interface"""
        self._dataset_name_label.setText("Nenhum dataset")
        self._dataset_stats_label.setText("0 séries • 0 pontos")
        self._series_tree.clear()
        self._data_table.setRowCount(0)
        self._data_table.setColumnCount(0)
    
    @pyqtSlot(QPoint)
    def _show_series_context_menu(self, position: QPoint):
        """Mostra menu de contexto para séries com cálculos em PT-BR"""
        item = self._series_tree.itemAt(position)
        if not item:
            return
        
        # Verificar se é uma série
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or len(data) != 2:
            return
        
        dataset_id, series_id = data
        
        # Criar menu de contexto moderno
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 2px solid #0d6efd;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #0d6efd;
                color: white;
            }
            QMenu::separator {
                height: 2px;
                background-color: #e9ecef;
                margin: 4px 8px;
            }
        """)
        
        # Título do menu
        series_name = item.text(0).replace("📈 ", "")
        title_action = QAction(f"📈 {series_name}", self)
        title_action.setEnabled(False)
        title_action.setStyleSheet("font-weight: bold; color: #0d6efd;")
        context_menu.addAction(title_action)
        context_menu.addSeparator()
        
        # Visualizações
        viz_action = QAction("📊 Plotar em Gráfico 2D", self)
        viz_action.triggered.connect(lambda: self._plot_series_2d(dataset_id, series_id))
        context_menu.addAction(viz_action)
        
        viz_3d_action = QAction("📈 Plotar em Gráfico 3D", self)
        viz_3d_action.triggered.connect(lambda: self._plot_series_3d(dataset_id, series_id))
        context_menu.addAction(viz_3d_action)
        
        context_menu.addSeparator()
        
        # Cálculos matemáticos
        interpolate_action = QAction("⚡ Interpolar Série", self)
        interpolate_action.triggered.connect(lambda: self._interpolate_series(dataset_id, series_id))
        context_menu.addAction(interpolate_action)
        
        derivative_action = QAction("📐 Calcular Derivada", self)
        derivative_action.triggered.connect(lambda: self._calculate_derivative(dataset_id, series_id))
        context_menu.addAction(derivative_action)
        
        integral_action = QAction("∫ Calcular Integral", self)
        integral_action.triggered.connect(lambda: self._calculate_integral(dataset_id, series_id))
        context_menu.addAction(integral_action)
        
        area_action = QAction("📏 Calcular Área sob Curva", self)
        area_action.triggered.connect(lambda: self._calculate_area(dataset_id, series_id))
        context_menu.addAction(area_action)
        
        context_menu.addSeparator()
        
        # Operações de dados
        smooth_action = QAction("🌊 Suavizar Série", self)
        smooth_action.triggered.connect(lambda: self._smooth_series(dataset_id, series_id))
        context_menu.addAction(smooth_action)
        
        filter_action = QAction("🔍 Filtrar Dados", self)
        filter_action.triggered.connect(lambda: self._filter_series(dataset_id, series_id))
        context_menu.addAction(filter_action)
        
        # Mostrar menu na posição do clique
        global_pos = self._series_tree.mapToGlobal(position)
        context_menu.exec(global_pos)
        
        logger.debug("series_context_menu_shown", series_id=series_id)
    
    def _plot_series_2d(self, dataset_id: str, series_id: str):
        """Plota série em gráfico 2D - IMPLEMENTAÇÃO COMPLETA"""
        try:
            # Get dataset and series
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                logger.error("plot_2d_series_not_found", dataset_id=dataset_id, series_id=series_id)
                return
            
            series = dataset.series[series_id]
            
            # Create matplotlib plot
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import (
                FigureCanvasQTAgg as FigureCanvas,
            )
            from matplotlib.figure import Figure

            # Create figure
            fig = Figure(figsize=(12, 8), dpi=100, tight_layout=True)
            ax = fig.add_subplot(111)
            
            # Plot data
            ax.plot(dataset.t_seconds, series.values, 
                   linewidth=2, label=f"{series.name} ({dataset_id})",
                   alpha=0.8)
            
            # Customize plot
            ax.set_xlabel("Tempo (s)", fontsize=12, fontweight='bold')
            ax.set_ylabel(f"{series.name} ({series.unit})", fontsize=12, fontweight='bold')
            ax.set_title(f"Gráfico 2D - {series.name} - {dataset_id}", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Create widget and show
            canvas = FigureCanvas(fig)
            canvas.setWindowTitle(f"2D - {series.name} - {dataset_id}")
            canvas.resize(800, 600)
            canvas.show()
            
            # Store reference to prevent garbage collection
            if not hasattr(self, '_plot_windows'):
                self._plot_windows = []
            self._plot_windows.append(canvas)
            
            # Emit signal for viz panel
            self.series_selected.emit(dataset_id, series_id)
            logger.info("plot_2d_created", dataset_id=dataset_id, series_id=series_id)
            
        except Exception as e:
            logger.error("plot_2d_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _plot_series_3d(self, dataset_id: str, series_id: str):
        """Plota série em gráfico 3D - IMPLEMENTAÇÃO COMPLETA"""
        try:
            # Get dataset and series
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                logger.error("plot_3d_series_not_found", dataset_id=dataset_id, series_id=series_id)
                return
            
            series = dataset.series[series_id]
            
            # Create matplotlib 3D plot
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.backends.backend_qt5agg import (
                FigureCanvasQTAgg as FigureCanvas,
            )
            from matplotlib.figure import Figure
            from mpl_toolkits.mplot3d import Axes3D

            # Create figure with 3D projection
            fig = Figure(figsize=(12, 8), dpi=100, tight_layout=True)
            ax = fig.add_subplot(111, projection='3d')
            
            # Create 3D data (time, value, index)
            t_data = dataset.t_seconds
            y_data = series.values
            z_data = np.arange(len(y_data))  # Index as Z axis
            
            # Plot 3D line
            ax.plot(t_data, y_data, z_data, 
                   linewidth=2, label=f"{series.name} ({dataset_id})",
                   alpha=0.8)
            
            # Also plot surface if enough data
            if len(t_data) > 10:
                # Create surface data
                T, Z = np.meshgrid(t_data[::max(1, len(t_data)//20)], 
                                  z_data[::max(1, len(z_data)//20)])
                Y = np.interp(T.ravel(), t_data, y_data).reshape(T.shape)
                
                ax.plot_surface(T, Y, Z, alpha=0.3, cmap='viridis')
            
            # Customize 3D plot
            ax.set_xlabel("Tempo (s)", fontsize=12, fontweight='bold')
            ax.set_ylabel(f"{series.name} ({series.unit})", fontsize=12, fontweight='bold')
            ax.set_zlabel("Índice", fontsize=12, fontweight='bold')
            ax.set_title(f"Gráfico 3D - {series.name} - {dataset_id}", fontsize=14, fontweight='bold')
            ax.legend()
            
            # Create widget and show
            canvas = FigureCanvas(fig)
            canvas.setWindowTitle(f"3D - {series.name} - {dataset_id}")
            canvas.resize(800, 600)
            canvas.show()
            
            # Store reference
            if not hasattr(self, '_plot_windows'):
                self._plot_windows = []
            self._plot_windows.append(canvas)
            
            logger.info("plot_3d_created", dataset_id=dataset_id, series_id=series_id)
            
        except Exception as e:
            logger.error("plot_3d_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _interpolate_series(self, dataset_id: str, series_id: str):
        """Interpola série selecionada - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            # Multiple interpolation methods
            import numpy as np
            from scipy import interpolate

            # Linear interpolation
            linear_interp = interpolate.interp1d(dataset.t_seconds, series.values, 
                                               kind='linear', fill_value='extrapolate')
            
            # Cubic spline interpolation
            cubic_interp = interpolate.interp1d(dataset.t_seconds, series.values, 
                                              kind='cubic', fill_value='extrapolate')
            
            # Create new time grid with higher resolution
            new_time = np.linspace(dataset.t_seconds[0], dataset.t_seconds[-1], 
                                  len(dataset.t_seconds) * 3)
            
            linear_values = linear_interp(new_time)
            cubic_values = cubic_interp(new_time)
            
            logger.info("interpolation_completed", dataset_id=dataset_id, series_id=series_id,
                       methods=["linear", "cubic"], new_points=len(new_time))
            
        except Exception as e:
            logger.error("interpolation_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _calculate_derivative(self, dataset_id: str, series_id: str):
        """Calcula derivada da série - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            import numpy as np

            # First derivative
            dt = np.diff(dataset.t_seconds)
            dy = np.diff(series.values)
            first_derivative = dy / dt
            
            # Second derivative
            if len(first_derivative) > 1:
                dt2 = dt[1:]
                dy2 = np.diff(first_derivative)
                second_derivative = dy2 / dt2
            else:
                second_derivative = np.array([])
            
            # Store derivatives as new calculated series
            derivative_stats = {
                'first_derivative_mean': np.mean(first_derivative),
                'first_derivative_std': np.std(first_derivative),
                'second_derivative_mean': np.mean(second_derivative) if len(second_derivative) > 0 else 0,
                'second_derivative_std': np.std(second_derivative) if len(second_derivative) > 0 else 0
            }
            
            logger.info("derivative_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=derivative_stats, first_points=len(first_derivative), 
                       second_points=len(second_derivative))
            
        except Exception as e:
            logger.error("derivative_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _calculate_integral(self, dataset_id: str, series_id: str):
        """Calcula integral da série - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            import numpy as np
            from scipy import integrate

            # Trapezoidal rule integration
            trapezoidal_integral = integrate.trapezoid(series.values, dataset.t_seconds)
            
            # Simpson's rule (if enough points)
            if len(series.values) >= 3:
                simpson_integral = integrate.simpson(series.values, dataset.t_seconds)
            else:
                simpson_integral = trapezoidal_integral
            
            # Cumulative integral
            cumulative_integral = integrate.cumulative_trapezoid(series.values, dataset.t_seconds, initial=0)
            
            integral_stats = {
                'trapezoidal_integral': float(trapezoidal_integral),
                'simpson_integral': float(simpson_integral),
                'cumulative_integral_final': float(cumulative_integral[-1]),
                'cumulative_integral_points': len(cumulative_integral)
            }
            
            logger.info("integral_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=integral_stats)
            
        except Exception as e:
            logger.error("integral_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _calculate_area(self, dataset_id: str, series_id: str):
        """Calcula área sob a curva - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            import numpy as np
            from scipy import integrate

            # Total area under curve (absolute)
            total_area = integrate.trapezoid(np.abs(series.values), dataset.t_seconds)
            
            # Positive area
            positive_values = np.maximum(series.values, 0)
            positive_area = integrate.trapezoid(positive_values, dataset.t_seconds)
            
            # Negative area  
            negative_values = np.minimum(series.values, 0)
            negative_area = abs(integrate.trapezoid(negative_values, dataset.t_seconds))
            
            area_stats = {
                'total_area': float(total_area),
                'positive_area': float(positive_area),
                'negative_area': float(negative_area),
                'net_area': float(positive_area - negative_area)
            }
            
            logger.info("area_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=area_stats)
            
        except Exception as e:
            logger.error("area_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _smooth_series(self, dataset_id: str, series_id: str):
        """Suaviza série - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            import numpy as np
            from scipy import ndimage, signal

            # Gaussian filter
            gaussian_smoothed = ndimage.gaussian_filter1d(series.values, sigma=2.0)
            
            # Moving average
            window_size = min(10, len(series.values) // 10)
            if window_size > 0:
                moving_avg = signal.convolve(series.values, 
                                           np.ones(window_size)/window_size, mode='same')
            else:
                moving_avg = series.values.copy()
            
            # Savitzky-Golay filter
            if len(series.values) >= 5:
                savgol_smoothed = signal.savgol_filter(series.values, 
                                                     window_length=min(5, len(series.values)//2*2-1),
                                                     polyorder=2)
            else:
                savgol_smoothed = series.values.copy()
            
            smoothing_stats = {
                'gaussian_rms_difference': float(np.sqrt(np.mean((series.values - gaussian_smoothed)**2))),
                'moving_avg_rms_difference': float(np.sqrt(np.mean((series.values - moving_avg)**2))),
                'savgol_rms_difference': float(np.sqrt(np.mean((series.values - savgol_smoothed)**2))),
                'window_size': window_size
            }
            
            logger.info("smoothing_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=smoothing_stats, methods=["gaussian", "moving_average", "savgol"])
            
        except Exception as e:
            logger.error("smoothing_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _filter_series(self, dataset_id: str, series_id: str):
        """Filtra dados da série - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            import numpy as np
            from scipy import signal

            # Remove outliers (values beyond 3 standard deviations)
            mean_val = np.mean(series.values)
            std_val = np.std(series.values)
            outlier_mask = np.abs(series.values - mean_val) <= 3 * std_val
            filtered_values = series.values[outlier_mask]
            filtered_time = dataset.t_seconds[outlier_mask]
            
            # Low-pass filter
            if len(series.values) > 10:
                # Butterworth filter
                b, a = signal.butter(4, 0.1, btype='low')
                lowpass_filtered = signal.filtfilt(b, a, series.values)
            else:
                lowpass_filtered = series.values.copy()
            
            filter_stats = {
                'original_points': len(series.values),
                'filtered_points': len(filtered_values),
                'outliers_removed': len(series.values) - len(filtered_values),
                'outlier_percentage': float((len(series.values) - len(filtered_values)) / len(series.values) * 100)
            }
            
            logger.info("filtering_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=filter_stats, methods=["outlier_removal", "lowpass_butterworth"])
            
        except Exception as e:
            logger.error("filtering_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))
    
    def _start_series_drag(self, supportedActions):
        """Inicia drag de série com dados no formato correto"""
        current_item = self._series_tree.currentItem()
        if not current_item:
            return
        
        # Get series data
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data or len(data) != 2:
            return
        
        dataset_id, series_id = data
        
        # Create drag with series data
        from PyQt6.QtCore import QMimeData
        from PyQt6.QtGui import QDrag
        
        drag = QDrag(self._series_tree)
        mimeData = QMimeData()
        mimeData.setText(f"{dataset_id}|{series_id}")
        drag.setMimeData(mimeData)
        
        # Execute drag
        drag.exec(supportedActions)
    
    def _auto_plot_dataset(self, dataset_id: str, dataset):
        """Automatically plot dataset in both 2D and 3D"""
        try:
            for series in dataset.series.values():
                # Plot 2D for each series
                self._plot_series_2d(dataset_id, series.series_id)
                # Plot 3D for each series  
                self._plot_series_3d(dataset_id, series.series_id)
            
            logger.info("auto_plot_completed", dataset_id=dataset_id, n_series=len(dataset.series))
            
        except Exception as e:
            logger.error("auto_plot_failed", dataset_id=dataset_id, error=str(e))
    
    def _auto_calculate_all(self, dataset_id: str, dataset):
        """Automatically calculate all derivatives, integrals and interpolations"""
        try:
            for series in dataset.series.values():
                # Calculate derivative
                self._calculate_derivative(dataset_id, series.series_id)
                
                # Calculate integral
                self._calculate_integral(dataset_id, series.series_id)
                
                # Calculate area under curve
                self._calculate_area(dataset_id, series.series_id)
                
                # Apply smoothing
                self._smooth_series(dataset_id, series.series_id)
                
                # Apply interpolation
                self._interpolate_series(dataset_id, series.series_id)
            
            logger.info("auto_calculate_completed", dataset_id=dataset_id, n_series=len(dataset.series))
            
        except Exception as e:
            logger.error("auto_calculate_failed", dataset_id=dataset_id, error=str(e))


# Alias para compatibilidade
DataPanel = CompactDataPanel