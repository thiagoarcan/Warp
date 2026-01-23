"""
DataPanel - Painel moderno e compacto para gerenciamento de dados

Características:
- Layout compacto e organizado
- Interface em PT-BR completo
- Visualização clara com ícones
- Melhor utilização do espaço
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QGroupBox, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QTabWidget, QTextEdit, QProgressBar, QComboBox, QSpinBox, QCheckBox,
    QFormLayout, QMessageBox, QHeaderView, QAbstractItemView, QFrame,
    QSplitter, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QMutex, QMutexLocker, QSize, QPoint
from PyQt6.QtGui import QFont, QIcon, QPalette, QAction

from platform_base.ui.state import SessionState
from platform_base.ui.workers.file_worker import FileLoadWorker
from platform_base.io.loader import LoadConfig, get_file_info
from platform_base.core.models import Dataset, SeriesID
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
        
        # Worker thread management
        self._worker_thread: Optional[QThread] = None
        self._worker: Optional[FileLoadWorker] = None
        self._worker_mutex = QMutex()
        
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
        
        # Dataset Info (muito compacto)
        dataset_group = QGroupBox("📋 Dataset")
        dataset_layout = QFormLayout(dataset_group)
        dataset_layout.setVerticalSpacing(2)
        dataset_layout.setHorizontalSpacing(6)
        
        self._dataset_name_label = QLabel("Nenhum dataset")
        self._dataset_name_label.setStyleSheet("font-weight: normal; color: #6c757d;")
        
        self._dataset_stats_label = QLabel("0 séries • 0 pontos")
        self._dataset_stats_label.setStyleSheet("font-weight: normal; color: #6c757d; font-size: 11px;")
        
        dataset_layout.addRow("📄 Arquivo:", self._dataset_name_label)
        dataset_layout.addRow("📊 Resumo:", self._dataset_stats_label)
        
        info_layout.addWidget(dataset_group)
        
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
        """Diálogo de seleção de múltiplos arquivos modernizado"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("📁 Carregar Dataset(s)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Múltiplos arquivos
        file_dialog.setNameFilters([
            "Todos os formatos (*.csv *.xlsx *.parquet *.h5)",
            "CSV (*.csv)",
            "Excel (*.xlsx *.xls)", 
            "Parquet (*.parquet *.pq)",
            "HDF5 (*.h5 *.hdf5)"
        ])
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                # Carregar múltiplos arquivos
                for file_path in file_paths:
                    self.load_dataset(file_path)
    
    def load_dataset(self, file_path: str):
        """Carrega dataset usando worker thread"""
        with QMutexLocker(self._worker_mutex):
            # Stop any existing worker
            if self._worker_thread and self._worker_thread.isRunning():
                self._worker_thread.quit()
                self._worker_thread.wait()
            
            # Get load configuration (simplificada para agora)
            load_config = LoadConfig()
            
            # Create worker thread
            self._worker_thread = QThread()
            self._worker = FileLoadWorker(file_path, load_config)
            self._worker.moveToThread(self._worker_thread)
            
            # Connect worker signals
            self._worker_thread.started.connect(self._worker.load_file)
            self._worker.progress.connect(self._on_load_progress)
            self._worker.finished.connect(self._on_load_finished)
            self._worker.error.connect(self._on_load_error)
            
            # Cleanup on finish
            self._worker.finished.connect(self._worker_thread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._worker_thread.finished.connect(self._worker_thread.deleteLater)
            
            # Start loading
            filename = Path(file_path).name
            self.session_state.start_operation(f"Carregando {filename}")
            self._worker_thread.start()
            
            logger.info("dataset_load_started", file_path=file_path)
    
    @pyqtSlot(int, str)
    def _on_load_progress(self, percent: int, message: str):
        """Handler para progresso"""
        self.session_state.update_operation_progress(percent, message)
    
    @pyqtSlot(object)  # Dataset object
    def _on_load_finished(self, dataset: Dataset):
        """Handler para carregamento concluído"""
        try:
            # Store filename in dataset and set dataset_id to filename
            if hasattr(self._worker, 'file_path'):
                dataset.source_file = self._worker.file_path
                # Use filename as dataset ID (more user-friendly)
                filename = Path(self._worker.file_path).stem
                dataset.dataset_id = filename
            
            # Add dataset to session
            dataset_id = self.session_state.add_dataset(dataset)
            
            self.session_state.finish_operation(True, f"Dataset {filename} carregado")
            self.dataset_loaded.emit(dataset_id)
            
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
    
    def _update_dataset_info(self):
        """Atualiza informações do dataset"""
        if not self._current_dataset:
            self._dataset_name_label.setText("Nenhum dataset")
            self._dataset_stats_label.setText("0 séries • 0 pontos")
            return
        
        # Nome do arquivo se disponível
        if hasattr(self._current_dataset, 'source_file') and self._current_dataset.source_file:
            filename = Path(self._current_dataset.source_file).name
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
        
        # Preparar colunas: Tempo, Valor, Derivada1, Área, Derivada2, etc.
        base_columns = ["⏱️ Tempo", "📅 Data/Hora"]
        series_columns = []
        calc_columns = []
        
        for series in self._current_dataset.series.values():
            series_columns.append(f"📊 {series.name}")
            # Adicionar colunas de cálculos se existirem
            calc_columns.extend([
                f"📐 d{series.name}/dt",
                f"∫ ∫{series.name}dt",
                f"📐📐 d²{series.name}/dt²"
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
            
            # Cálculos (placeholders por enquanto - implementar quando tiver cálculos reais)
            for i in range(len(calc_columns)):
                item = QTableWidgetItem("―")
                item.setForeground(Qt.GlobalColor.lightGray)
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
        """Plota série em gráfico 2D"""
        # Emitir sinal para o viz panel criar o gráfico
        self.series_selected.emit(dataset_id, series_id)
        logger.info("plot_2d_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _plot_series_3d(self, dataset_id: str, series_id: str):
        """Plota série em gráfico 3D"""
        # Implementar plotagem 3D
        logger.info("plot_3d_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _interpolate_series(self, dataset_id: str, series_id: str):
        """Interpola série selecionada"""
        logger.info("interpolation_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _calculate_derivative(self, dataset_id: str, series_id: str):
        """Calcula derivada da série"""
        logger.info("derivative_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _calculate_integral(self, dataset_id: str, series_id: str):
        """Calcula integral da série"""
        logger.info("integral_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _calculate_area(self, dataset_id: str, series_id: str):
        """Calcula área sob a curva"""
        logger.info("area_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _smooth_series(self, dataset_id: str, series_id: str):
        """Suaviza série"""
        logger.info("smoothing_requested", dataset_id=dataset_id, series_id=series_id)
    
    def _filter_series(self, dataset_id: str, series_id: str):
        """Filtra dados da série"""
        logger.info("filtering_requested", dataset_id=dataset_id, series_id=series_id)
    
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