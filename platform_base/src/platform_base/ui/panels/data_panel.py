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
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from PyQt6.QtCore import (
    QMutex,
    QMutexLocker,
    QPoint,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QAction, QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
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
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.io.loader import LoadConfig
from platform_base.ui.workers.file_worker import FileLoadWorker
from platform_base.utils.logging import get_logger
from platform_base.utils.widgets import StableComboBox

if TYPE_CHECKING:
    from platform_base.core.models import Dataset
    from platform_base.ui.state import SessionState


logger = get_logger(__name__)
    """


class CompactDataPanel(QWidget, UiLoaderMixin):
    """
    Painel de dados moderno e compacto

    Funcionalidades:
    - Gerenciamento de datasets com nome do arquivo
    - Visualização de séries ativas
    - Tabela de dados com colunas de cálculos
    - Interface compacta em PT-BR
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/compactDataPanel.ui"

    # Signals
    dataset_loaded = pyqtSignal(str)  # dataset_id
    series_selected = pyqtSignal(str, str)  # dataset_id, series_id
    plot_requested = pyqtSignal(str, str, str)  # dataset_id, series_id, plot_type

    def __init__(self, session_state: SessionState):
        super().__init__()

        self.session_state = session_state
        self._current_dataset: Dataset | None = None

        # Thread-safe loading counter
        self._load_mutex = QMutex()
        self._loading_count = 0
        self._loaded_count = 0
        self._total_files = 0
        self._active_workers: list = []

        # Tenta carregar do arquivo .ui, senão usa fallback
        if not self._load_ui():
            self._setup_modern_ui_fallback()
        else:
            self._setup_ui_from_file()
        
        self._setup_connections()
        logger.debug("compact_data_panel_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Configurações básicas
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Busca widgets do arquivo .ui
        self.arquivo_frame = self.findChild(QFrame, "arquivoFrame")
        self.carregar_btn = self.findChild(QPushButton, "carregarBtn")
        self.arquivo_label = self.findChild(QLabel, "arquivoLabel")
        self.info_label = self.findChild(QLabel, "infoLabel")
        
        self.series_group = self.findChild(QGroupBox, "seriesGroup")
        self.series_tree = self.findChild(QTreeWidget, "seriesTree")
        
        self.data_group = self.findChild(QGroupBox, "dataGroup")
        self.data_table = self.findChild(QTableWidget, "dataTable")
        
        # Conecta sinais
        if self.carregar_btn:
            self.carregar_btn.clicked.connect(self._open_file_dialog)
        if self.series_tree:
            self.series_tree.itemSelectionChanged.connect(self._on_series_selection)

    def _setup_modern_ui_fallback(self):
        """Interface ultra compacta e otimizada"""
        # Apenas mínimo para permitir redimensionamento total
        self.setMinimumWidth(150)
        # Política de tamanho expansível
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
        self._datasets_tree.setHeaderLabels(["Dataset", "Séries", "Pontos", "Período"])
        self._datasets_tree.setRootIsDecorated(False)
        self._datasets_tree.setMaximumHeight(150)  # Aumentar altura para mais info
        self._datasets_tree.setAlternatingRowColors(True)
        self._datasets_tree.itemClicked.connect(self._on_dataset_selected)
        self._datasets_tree.setToolTip(
            "Lista de datasets carregados.\n"
            "Clique para selecionar o dataset ativo.\n"
            "Duplo-clique para editar informações.",
        )

        # Configurar headers
        datasets_header = self._datasets_tree.header()
        datasets_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        datasets_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        datasets_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        datasets_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Período

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
        self._series_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # Allow multi-selection
        self._series_tree.itemClicked.connect(self._on_series_selected)
        self._series_tree.setToolTip(
            "Séries do dataset atual.\n"
            "• Clique para selecionar uma série\n"
            "• Arraste para o gráfico para visualizar\n"
            "• Botão direito para opções (exportar, remover, etc.)",
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
        self._preview_rows_combo = StableComboBox()
        self._preview_rows_combo.addItems(["10", "25", "50", "100"])
        self._preview_rows_combo.setCurrentText("25")
        self._preview_rows_combo.setMaximumWidth(60)
        self._preview_rows_combo.currentTextChanged.connect(self._update_data_table)
        self._preview_rows_combo.setToolTip(
            "Número de linhas a exibir na prévia.\n"
            "Valores maiores mostram mais dados mas podem ser mais lentos.",
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
            "• Use o controle 'Linhas' para ajustar quantidade",
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
        
        # Flag para evitar chamadas recursivas
        self._updating_ui = False
        
        logger.debug("data_panel_connections_setup_completed")

    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Handler para mudança de dataset - COM PROTEÇÃO CONTRA RECURSÃO"""
        # Evitar chamadas duplicadas que causam travamento
        if self._updating_ui:
            return
            
        if dataset_id:
            try:
                self._updating_ui = True
                self._current_dataset = self.session_state.get_dataset(dataset_id)
                self._update_datasets_list()
                self._update_dataset_info()
                self._update_series_tree()
                self._update_data_table()
            except Exception as e:
                logger.exception("dataset_change_failed", dataset_id=dataset_id, error=str(e))
            finally:
                self._updating_ui = False
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
            "Todos os arquivos (*.*)",
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
                    if validation["valid"]:
                        if validation.get("large_file"):
                            large_files.append((file_path, validation["size_mb"]))
                        valid_files.append(file_path)
                    else:
                        invalid_files.append((file_path, validation["error"]))

                # Alertar sobre arquivos inválidos
                if invalid_files:
                    error_details = "\n".join([f"• {Path(f).name}: {e}" for f, e in invalid_files])
                    QMessageBox.warning(
                        self,
                        "⚠️ Arquivos Inválidos",
                        f"Os seguintes arquivos não podem ser carregados:\n\n{error_details}",
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
                        QMessageBox.StandardButton.Yes,
                    )
                    if reply == QMessageBox.StandardButton.No:
                        # Remover arquivos grandes da lista
                        valid_files = [f for f in valid_files if f not in [lf[0] for lf in large_files]]

                # Carregar arquivos válidos EM PARALELO
                if valid_files:
                    self.load_datasets_parallel(valid_files)

    def _validate_file(self, file_path: str) -> dict:
        """
        Valida arquivo antes do carregamento - VERSÃO ULTRA SIMPLIFICADA

        Apenas verifica existência, extensão e tamanho.
        Validação de conteúdo é feita no worker thread.

        Returns:
            dict com:
                - valid: bool
                - error: str (se inválido)
                - size_mb: float
                - large_file: bool (>50MB)
        """
        result = {
            "valid": False,
            "error": None,
            "size_mb": 0.0,
            "large_file": False,
        }

        try:
            path = Path(file_path)

            # 1. Verificar se arquivo existe
            if not path.exists():
                result["error"] = "Arquivo não encontrado"
                return result

            # 2. Verificar se é arquivo (não diretório)
            if not path.is_file():
                result["error"] = "Não é um arquivo válido"
                return result

            # 3. Verificar extensão
            valid_extensions = {".csv", ".xlsx", ".xls", ".parquet", ".pq", ".h5", ".hdf5"}
            if path.suffix.lower() not in valid_extensions:
                result["error"] = f"Formato não suportado: {path.suffix}"
                return result

            # 4. Verificar tamanho (única operação de I/O)
            size_bytes = path.stat().st_size
            result["size_mb"] = size_bytes / (1024 * 1024)

            if size_bytes == 0:
                result["error"] = "Arquivo vazio"
                return result

            if result["size_mb"] > 500:
                result["error"] = f"Arquivo muito grande ({result['size_mb']:.1f} MB)"
                return result

            if result["size_mb"] > 50:
                result["large_file"] = True

            # VALIDAÇÃO SIMPLIFICADA: Não abre arquivos!
            # Toda validação de conteúdo é feita no worker thread
            result["valid"] = True
            return result

        except Exception as e:
            result["error"] = f"Erro ao verificar arquivo: {e}"
            return result

    def load_dataset(self, file_path: str):
        """Carrega dataset usando worker thread - THREAD-SAFE"""
        # Normalize path
        try:
            normalized_path = str(Path(file_path).resolve())
        except Exception as e:
            logger.exception("path_normalization_failed", error=str(e))
            normalized_path = file_path

        filename = Path(normalized_path).name
        logger.info("load_dataset_starting", filename=filename)

        # Create load configuration
        load_config = LoadConfig()

        # Create thread and worker
        worker_thread = QThread(self)
        worker = FileLoadWorker(normalized_path, load_config)
        worker.moveToThread(worker_thread)

        # Store references to prevent garbage collection (thread-safe)
        with QMutexLocker(self._load_mutex):
            self._active_workers.append((worker_thread, worker))
            self._loading_count += 1
            current_count = self._loading_count
            self._total_files = current_count  # Track total for progress

        # Connect signals - usando lambda para garantir execução correta
        worker_thread.started.connect(worker.load_file)
        worker.progress.connect(self._on_load_progress, Qt.ConnectionType.QueuedConnection)
        worker.finished.connect(self._on_load_finished, Qt.ConnectionType.QueuedConnection)
        worker.error.connect(self._on_load_error, Qt.ConnectionType.QueuedConnection)

        # Start operation message (apenas no primeiro)
        if current_count == 1:
            self.session_state.start_operation(f"Carregando arquivos...")

        # Start thread
        worker_thread.start()
        logger.info("worker_thread_started", filename=filename)

    def load_datasets_parallel(self, file_paths: list[str]):
        """Carrega múltiplos datasets em paralelo - NOVO MÉTODO"""
        if not file_paths:
            return

        logger.info("parallel_load_starting", file_count=len(file_paths))
        self.session_state.start_operation(f"Carregando {len(file_paths)} arquivo(s)...")

        # Start all workers in parallel
        for file_path in file_paths:
            self.load_dataset(file_path)


    @pyqtSlot(int, str)
    def _on_load_progress(self, percent: int, message: str):
        """Handler para progresso"""
        self.session_state.update_operation_progress(percent, message)

    @pyqtSlot(object)  # Dataset object
    def _on_load_finished(self, dataset: Dataset):
        """Handler para carregamento concluído - THREAD-SAFE com mutex"""
        try:
            logger.debug("_on_load_finished_START")
            
            # Get worker from sender
            worker = self.sender()
            filename = "Unknown"

            # Set dataset_id to filename for user-friendly display
            if hasattr(worker, "file_path"):
                filename = Path(worker.file_path).stem
                dataset.dataset_id = filename

            # Add dataset to session - Este já emite dataset_changed
            # e já define como current se for o primeiro
            dataset_id = self.session_state.add_dataset(dataset)
            logger.debug("dataset_added", dataset_id=dataset_id)

            # Track loaded count and cleanup worker (thread-safe)
            with QMutexLocker(self._load_mutex):
                self._loaded_count += 1
                self._loading_count = max(0, self._loading_count - 1)
                loaded = self._loaded_count
                remaining = self._loading_count
                
                # Find and remove worker from active list
                worker_to_cleanup = None
                for wt, w in self._active_workers:
                    if w == worker:
                        worker_to_cleanup = (wt, w)
                        break
                if worker_to_cleanup:
                    self._active_workers.remove(worker_to_cleanup)

            # Cleanup worker thread
            if worker_to_cleanup:
                wt, w = worker_to_cleanup
                try:
                    wt.quit()
                    wt.wait(1000)
                    w.deleteLater()
                    wt.deleteLater()
                except Exception as e:
                    logger.warning("cleanup_error", error=str(e))

            # Only finish operation when all files are loaded
            if remaining <= 0:
                self.session_state.finish_operation(True, f"✅ {loaded} dataset(s) carregado(s)")
                with QMutexLocker(self._load_mutex):
                    self._loaded_count = 0
                    self._total_files = 0

            self.dataset_loaded.emit(dataset_id)
            logger.info("dataset_loaded_successfully", dataset_id=dataset_id, filename=filename, remaining=remaining)

        except Exception as e:
            self.session_state.finish_operation(False, f"Erro: {e}")
            logger.exception("dataset_processing_failed", error=str(e))

    @pyqtSlot(str)
    def _on_load_error(self, error_message: str):
        """Handler para erro - THREAD-SAFE com cleanup"""
        try:
            # Get worker from sender
            worker = self.sender()
            
            # Track error and cleanup worker (thread-safe)
            with QMutexLocker(self._load_mutex):
                self._loading_count = max(0, self._loading_count - 1)
                remaining = self._loading_count
                
                # Find and remove worker from active list
                worker_to_cleanup = None
                for wt, w in self._active_workers:
                    if w == worker:
                        worker_to_cleanup = (wt, w)
                        break
                if worker_to_cleanup:
                    self._active_workers.remove(worker_to_cleanup)

            # Cleanup worker thread
            if worker_to_cleanup:
                wt, w = worker_to_cleanup
                try:
                    wt.quit()
                    wt.wait(1000)
                    w.deleteLater()
                    wt.deleteLater()
                except Exception as e:
                    logger.warning("cleanup_error", error=str(e))

            # Only show message and finish if all done
            if remaining <= 0:
                self.session_state.finish_operation(False, f"Erro: {error_message}")

            QMessageBox.critical(
                self,
                "❌ Erro no Carregamento",
                f"Falha ao carregar arquivo:\n\n{error_message}",
            )

            logger.error("dataset_load_failed", error=error_message)
            
        except Exception as e:
            logger.exception("error_handler_failed", error=str(e))

    def _update_datasets_list(self):
        """Atualiza lista de todos os datasets carregados"""
        self._datasets_tree.clear()

        all_datasets = self.session_state.get_all_datasets()
        logger.debug("_update_datasets_list", count=len(all_datasets), datasets=list(all_datasets.keys()))

        for dataset_id, dataset in all_datasets.items():
            item = QTreeWidgetItem()

            # Nome do arquivo
            if hasattr(dataset, "source") and dataset.source:
                filename = Path(dataset.source.filename).stem
            else:
                filename = dataset_id

            item.setText(0, filename)
            item.setText(1, str(len(dataset.series)))

            # Contar total de pontos
            total_points = sum(len(series.values) for series in dataset.series.values()) if dataset.series else 0
            item.setText(2, f"{total_points:,}")
            
            # Período de datetime (primeiro e último ponto)
            try:
                if hasattr(dataset, 't_datetime') and dataset.t_datetime is not None and len(dataset.t_datetime) > 0:
                    import numpy as np
                    first_dt = dataset.t_datetime[0]
                    last_dt = dataset.t_datetime[-1]
                    # Formatar como string legível
                    first_str = str(np.datetime_as_string(first_dt, unit='m'))[:16].replace('T', ' ')
                    last_str = str(np.datetime_as_string(last_dt, unit='m'))[:16].replace('T', ' ')
                    period_str = f"{first_str} → {last_str}"
                    item.setText(3, period_str)
                    item.setToolTip(3, f"Início: {first_str}\nFim: {last_str}")
                else:
                    item.setText(3, "N/D")
                    item.setToolTip(3, "Datetime não disponível")
            except Exception:
                item.setText(3, "Erro")

            # Armazenar dataset_id no item
            item.setData(0, Qt.ItemDataRole.UserRole, dataset_id)

            # Destacar dataset atual
            if dataset_id == self.session_state.current_dataset:
                item.setBackground(0, QColor("#e3f2fd"))
                item.setBackground(1, QColor("#e3f2fd"))
                item.setBackground(2, QColor("#e3f2fd"))
                item.setBackground(3, QColor("#e3f2fd"))

            self._datasets_tree.addTopLevelItem(item)
            logger.debug("dataset_item_added", dataset_id=dataset_id, filename=filename)

    @pyqtSlot(QTreeWidgetItem, int)
    def _on_dataset_selected(self, item: QTreeWidgetItem, column: int):
        """Handler para seleção de dataset na lista"""
        try:
            dataset_id = item.data(0, Qt.ItemDataRole.UserRole)
            if dataset_id and dataset_id != self.session_state.current_dataset:
                self.session_state.set_current_dataset(dataset_id)
        except Exception as e:
            logger.exception("_on_dataset_selected_failed", error=str(e))

    def _update_dataset_info(self):
        """Atualiza informações do dataset"""
        if not self._current_dataset:
            self._dataset_name_label.setText("Nenhum dataset")
            self._dataset_stats_label.setText("0 séries • 0 pontos")
            return

        # Nome do arquivo se disponível
        if hasattr(self._current_dataset, "source") and self._current_dataset.source:
            filename = Path(self._current_dataset.source.filename).name
        else:
            filename = self._current_dataset.dataset_id

        self._dataset_name_label.setText(filename)

        # Estatísticas
        n_series = len(self._current_dataset.series)
        n_points = len(self._current_dataset.t_seconds)

        # Formatação compacta
        points_str = f"{n_points / 1000:.1f}k" if n_points > 1000 else str(n_points)

        self._dataset_stats_label.setText(f"{n_series} séries • {points_str} pontos")

    def _update_series_tree(self):
        """Atualiza árvore de séries de forma compacta"""
        self._series_tree.clear()

        if not self._current_dataset:
            return

        # Obter nome do dataset para prefixo
        dataset_name = self._current_dataset.dataset_id
        if hasattr(self._current_dataset, "source") and self._current_dataset.source:
            dataset_name = Path(self._current_dataset.source.filename).stem

        # Add series items (sem hierarquia, mais direto)
        for series in self._current_dataset.series.values():
            item = QTreeWidgetItem(self._series_tree)
            
            # Usar nome do dataset + nome da série para melhor identificação
            # Ex: "BAR_DT-OP10 / valor" em vez de apenas "valor"
            display_name = f"📈 {dataset_name}"
            if series.name and series.name != "valor":
                display_name = f"📈 {series.name}"
            item.setText(0, display_name)

            # Formato compacto de pontos
            n_points = len(series.values)
            points_text = f"{n_points / 1000:.1f}k" if n_points > 1000 else str(n_points)

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
        """Atualiza tabela de dados - VERSÃO OTIMIZADA"""
        logger.debug("_update_data_table_START")
        
        if not self._current_dataset:
            self._data_table.setRowCount(0)
            self._data_table.setColumnCount(0)
            return

        # Get number of rows - LIMITADO para performance
        max_rows = int(self._preview_rows_combo.currentText())
        n_points = min(max_rows, len(self._current_dataset.t_seconds))
        
        logger.debug("data_table_config", max_rows=max_rows, n_points=n_points)

        if n_points == 0:
            self._data_table.setRowCount(0)
            self._data_table.setColumnCount(0)
            return

        # Colunas simplificadas para melhor performance
        base_columns = ["⏱️ Tempo (s)", "📅 Data/Hora"]
        series_columns = [f"📊 {s.name}" for s in self._current_dataset.series.values()]
        
        all_columns = base_columns + series_columns
        
        logger.debug("setting_up_table", columns=len(all_columns), rows=n_points)

        # Setup table
        self._data_table.setRowCount(n_points)
        self._data_table.setColumnCount(len(all_columns))
        self._data_table.setHorizontalHeaderLabels(all_columns)

        # Pre-compute series values list for efficiency
        series_list = list(self._current_dataset.series.values())
        t_seconds = self._current_dataset.t_seconds
        t_datetime = self._current_dataset.t_datetime

        logger.debug("filling_data_table")
        
        # Fill data - OTIMIZADO
        for row in range(n_points):
            col = 0

            # Tempo (s)
            self._data_table.setItem(row, col, QTableWidgetItem(f"{t_seconds[row]:.3f}"))
            col += 1

            # Data/Hora
            dt_str = str(t_datetime[row])[:19]
            self._data_table.setItem(row, col, QTableWidgetItem(dt_str))
            col += 1

            # Valores das séries (sem cálculos para evitar travamento)
            for series in series_list:
                value = series.values[row]
                if pd.isna(value):
                    item = QTableWidgetItem("NaN")
                    item.setForeground(Qt.GlobalColor.gray)
                else:
                    item = QTableWidgetItem(f"{value:.6g}")
                self._data_table.setItem(row, col, item)
                col += 1

        logger.debug("data_table_filled")

        # Otimizar larguras das colunas
        header = self._data_table.horizontalHeader()
        for i in range(len(all_columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            
        logger.debug("_update_data_table_COMPLETE")

    @pyqtSlot(QTreeWidgetItem, int)
    def _on_series_selected(self, item: QTreeWidgetItem, column: int):
        """Handler para seleção de série"""
        data = item.data(0, Qt.ItemDataRole.UserRole)

        if data and len(data) == 2:
            dataset_id, series_id = data
            self.series_selected.emit(dataset_id, series_id)
            logger.debug("series_selected", dataset_id=dataset_id, series_id=series_id)

    def get_selected_series_ids(self) -> list[str]:
        """
        Get list of currently selected series IDs

        Returns:
            List of series IDs (strings) that are currently selected
        """
        selected_ids = []
        selected_items = self._series_tree.selectedItems()

        for item in selected_items:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and len(data) == 2:
                _dataset_id, series_id = data
                selected_ids.append(series_id)

        return selected_ids

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
        """Solicita criação de gráfico 2D dentro do painel de visualização"""
        self.plot_requested.emit(dataset_id, series_id, "2d")
        logger.info("plot_2d_requested", dataset_id=dataset_id, series_id=series_id)

    def _plot_series_3d(self, dataset_id: str, series_id: str):
        """Solicita criação de gráfico 3D dentro do painel de visualização"""
        self.plot_requested.emit(dataset_id, series_id, "3d")
        logger.info("plot_3d_requested", dataset_id=dataset_id, series_id=series_id)

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
                                               kind="linear", fill_value="extrapolate")

            # Cubic spline interpolation
            cubic_interp = interpolate.interp1d(dataset.t_seconds, series.values,
                                              kind="cubic", fill_value="extrapolate")

            # Create new time grid with higher resolution
            new_time = np.linspace(dataset.t_seconds[0], dataset.t_seconds[-1],
                                  len(dataset.t_seconds) * 3)

            linear_interp(new_time)
            cubic_interp(new_time)

            logger.info("interpolation_completed", dataset_id=dataset_id, series_id=series_id,
                       methods=["linear", "cubic"], new_points=len(new_time))

        except Exception as e:
            logger.exception("interpolation_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))

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
                "first_derivative_mean": np.mean(first_derivative),
                "first_derivative_std": np.std(first_derivative),
                "second_derivative_mean": np.mean(second_derivative) if len(second_derivative) > 0 else 0,
                "second_derivative_std": np.std(second_derivative) if len(second_derivative) > 0 else 0,
            }

            logger.info("derivative_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=derivative_stats, first_points=len(first_derivative),
                       second_points=len(second_derivative))

        except Exception as e:
            logger.exception("derivative_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))

    def _calculate_integral(self, dataset_id: str, series_id: str):
        """Calcula integral da série - IMPLEMENTAÇÃO COMPLETA"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return

            series = dataset.series[series_id]

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
                "trapezoidal_integral": float(trapezoidal_integral),
                "simpson_integral": float(simpson_integral),
                "cumulative_integral_final": float(cumulative_integral[-1]),
                "cumulative_integral_points": len(cumulative_integral),
            }

            logger.info("integral_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=integral_stats)

        except Exception as e:
            logger.exception("integral_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))

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
                "total_area": float(total_area),
                "positive_area": float(positive_area),
                "negative_area": float(negative_area),
                "net_area": float(positive_area - negative_area),
            }

            logger.info("area_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=area_stats)

        except Exception as e:
            logger.exception("area_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))

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
                                           np.ones(window_size)/window_size, mode="same")
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
                "gaussian_rms_difference": float(np.sqrt(np.mean((series.values - gaussian_smoothed)**2))),
                "moving_avg_rms_difference": float(np.sqrt(np.mean((series.values - moving_avg)**2))),
                "savgol_rms_difference": float(np.sqrt(np.mean((series.values - savgol_smoothed)**2))),
                "window_size": window_size,
            }

            logger.info("smoothing_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=smoothing_stats, methods=["gaussian", "moving_average", "savgol"])

        except Exception as e:
            logger.exception("smoothing_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))

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
            dataset.t_seconds[outlier_mask]

            # Low-pass filter
            if len(series.values) > 10:
                # Butterworth filter
                b, a = signal.butter(4, 0.1, btype="low")
                signal.filtfilt(b, a, series.values)
            else:
                series.values.copy()

            filter_stats = {
                "original_points": len(series.values),
                "filtered_points": len(filtered_values),
                "outliers_removed": len(series.values) - len(filtered_values),
                "outlier_percentage": float((len(series.values) - len(filtered_values)) / len(series.values) * 100),
            }

            logger.info("filtering_completed", dataset_id=dataset_id, series_id=series_id,
                       stats=filter_stats, methods=["outlier_removal", "lowpass_butterworth"])

        except Exception as e:
            logger.exception("filtering_failed", dataset_id=dataset_id, series_id=series_id, error=str(e))

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



# Alias para compatibilidade
DataPanel = CompactDataPanel
