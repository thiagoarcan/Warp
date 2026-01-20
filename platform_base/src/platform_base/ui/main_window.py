"""
MainWindow - Janela principal PyQt6 conforme especificação seção 12.3

Arquitetura de painéis:
- DataPanel (esquerda): Gerenciamento de datasets e séries
- VizPanel (centro): Visualização principal
- OperationsPanel (direita): Operações e configurações
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QSplitter, QMenuBar, QStatusBar, QToolBar,
    QFileDialog, QMessageBox, QProgressBar,
    QLabel, QApplication
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QKeySequence, QAction, QIcon

from platform_base.ui.state import SessionState
from platform_base.ui.panels.data_panel import DataPanel
from platform_base.ui.panels.viz_panel import VizPanel
from platform_base.ui.panels.operations_panel import OperationsPanel
from platform_base.utils.logging import get_logger
from platform_base.utils.errors import PlatformError

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação PyQt6
    
    Implementa layout conforme especificação:
    - Menu bar com ações principais
    - Tool bar para acesso rápido
    - Status bar com progresso
    - Splitter layout com 3 painéis principais
    - Auto-save de sessão
    """
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        
        self.session_state = session_state
        
        # Components
        self._data_panel: Optional[DataPanel] = None
        self._viz_panel: Optional[VizPanel] = None
        self._operations_panel: Optional[OperationsPanel] = None
        self._progress_bar: Optional[QProgressBar] = None
        self._status_label: Optional[QLabel] = None
        
        # Auto-save timer
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._auto_save_session)
        self._autosave_timer.start(300000)  # 5 minutes
        
        # Initialize UI
        self._setup_ui()
        self._setup_connections()
        
        logger.info("main_window_initialized")
    
    def _setup_ui(self):
        """Configura interface conforme especificação seção 12.3"""
        # Window properties
        self.setWindowTitle("Platform Base v2.0 - Análise de Séries Temporais")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Create central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create panels
        self._data_panel = DataPanel(self.session_state)
        self._viz_panel = VizPanel(self.session_state)
        self._operations_panel = OperationsPanel(self.session_state)
        
        # Add panels to splitter
        splitter.addWidget(self._data_panel)
        splitter.addWidget(self._viz_panel)
        splitter.addWidget(self._operations_panel)
        
        # Set splitter proportions: Data(20%) - Viz(60%) - Operations(20%)
        splitter.setStretchFactor(0, 20)
        splitter.setStretchFactor(1, 60)
        splitter.setStretchFactor(2, 20)
        
        # Create menus and toolbars
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        
        logger.debug("main_window_ui_setup_completed")
    
    def _create_menu_bar(self):
        """Cria barra de menu"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&Arquivo")
        
        # Open action
        open_action = QAction("&Abrir Dataset...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Abrir arquivo de dados")
        open_action.triggered.connect(self._open_dataset)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save session action
        save_session_action = QAction("&Salvar Sessão...", self)
        save_session_action.setShortcut(QKeySequence.StandardKey.Save)
        save_session_action.setStatusTip("Salvar estado atual da sessão")
        save_session_action.triggered.connect(self._save_session)
        file_menu.addAction(save_session_action)
        
        # Load session action
        load_session_action = QAction("&Carregar Sessão...", self)
        load_session_action.setStatusTip("Carregar sessão salva")
        load_session_action.triggered.connect(self._load_session)
        file_menu.addAction(load_session_action)
        
        file_menu.addSeparator()
        
        # Export action
        export_action = QAction("&Exportar Dados...", self)
        export_action.setStatusTip("Exportar dados processados")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Sair da aplicação")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu("&Visualizar")
        
        # Reset layout action
        reset_layout_action = QAction("&Resetar Layout", self)
        reset_layout_action.setStatusTip("Restaurar layout padrão")
        reset_layout_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Ferramentas")
        
        # Clear cache action
        clear_cache_action = QAction("&Limpar Cache", self)
        clear_cache_action.setStatusTip("Limpar cache de dados")
        clear_cache_action.triggered.connect(self._clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Ajuda")
        
        # About action
        about_action = QAction("&Sobre...", self)
        about_action.setStatusTip("Sobre Platform Base")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """Cria barra de ferramentas"""
        toolbar = self.addToolBar("Principal")
        toolbar.setMovable(False)
        
        # Open dataset button
        open_action = QAction("Abrir", self)
        open_action.setStatusTip("Abrir dataset")
        open_action.triggered.connect(self._open_dataset)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Save session button
        save_action = QAction("Salvar", self)
        save_action.setStatusTip("Salvar sessão")
        save_action.triggered.connect(self._save_session)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Export button
        export_action = QAction("Exportar", self)
        export_action.setStatusTip("Exportar dados")
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)
    
    def _create_status_bar(self):
        """Cria barra de status"""
        statusbar = self.statusBar()
        
        # Status label
        self._status_label = QLabel("Pronto")
        statusbar.addWidget(self._status_label)
        
        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumWidth(200)
        statusbar.addPermanentWidget(self._progress_bar)
        
        # Session info
        session_label = QLabel(f"Sessão: {self.session_state.session_id}")
        statusbar.addPermanentWidget(session_label)
    
    def _setup_connections(self):
        """Configura conexões de sinais entre componentes"""
        # Connect session state signals
        self.session_state.operation_started.connect(self._on_operation_started)
        self.session_state.operation_finished.connect(self._on_operation_finished)
        self.session_state.dataset_changed.connect(self._on_dataset_changed)
        
        # Connect panel signals
        if self._data_panel:
            self._data_panel.dataset_loaded.connect(self._on_dataset_loaded)
        
        logger.debug("main_window_connections_setup_completed")
    
    # Slots for session state signals
    @pyqtSlot(str)
    def _on_operation_started(self, operation_name: str):
        """Handler para início de operação"""
        self._status_label.setText(f"Executando: {operation_name}")
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Disable actions during operation
        self.setEnabled(False)
        
        logger.debug("operation_started_ui", operation=operation_name)
    
    @pyqtSlot(str, bool)
    def _on_operation_finished(self, operation_name: str, success: bool):
        """Handler para fim de operação"""
        status = "concluída" if success else "falhou"
        self._status_label.setText(f"Operação {operation_name} {status}")
        
        self._progress_bar.setVisible(False)
        self.setEnabled(True)
        
        # Clear status after 3 seconds
        QTimer.singleShot(3000, lambda: self._status_label.setText("Pronto"))
        
        logger.debug("operation_finished_ui", operation=operation_name, success=success)
    
    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Handler para mudança de dataset"""
        if dataset_id:
            self._status_label.setText(f"Dataset ativo: {dataset_id}")
        else:
            self._status_label.setText("Nenhum dataset ativo")
    
    @pyqtSlot(str)
    def _on_dataset_loaded(self, dataset_id: str):
        """Handler para dataset carregado"""
        self._status_label.setText(f"Dataset carregado: {dataset_id}")
    
    # Menu actions
    def _open_dataset(self):
        """Abre diálogo para carregar dataset"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Abrir Dataset")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters([
            "Todos os formatos suportados (*.csv *.xlsx *.parquet *.h5)",
            "CSV files (*.csv)",
            "Excel files (*.xlsx *.xls)",
            "Parquet files (*.parquet *.pq)",
            "HDF5 files (*.h5 *.hdf5)",
            "Todos os arquivos (*.*)"
        ])
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths and self._data_panel:
                self._data_panel.load_dataset(file_paths[0])
    
    def _save_session(self):
        """Salva sessão atual"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Salvar Sessão")
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilters(["Sessões (*.json)", "Todos os arquivos (*.*)"])
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                try:
                    self.session_state.save_session(file_paths[0])
                    self._status_label.setText("Sessão salva com sucesso")
                except Exception as e:
                    self._show_error("Erro ao Salvar", f"Falha ao salvar sessão:\n{e}")
    
    def _load_session(self):
        """Carrega sessão salva"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Carregar Sessão")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters(["Sessões (*.json)", "Todos os arquivos (*.*)"])
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                try:
                    self.session_state.load_session(file_paths[0])
                    self._status_label.setText("Sessão carregada com sucesso")
                except Exception as e:
                    self._show_error("Erro ao Carregar", f"Falha ao carregar sessão:\n{e}")
    
    def _export_data(self):
        """Exporta dados processados"""
        if not self.session_state.current_dataset:
            self._show_info("Exportar Dados", "Nenhum dataset ativo para exportar.")
            return
        
        # Delegate to operations panel
        if self._operations_panel:
            self._operations_panel.show_export_dialog()
    
    def _reset_layout(self):
        """Restaura layout padrão"""
        # Reset splitter proportions
        if hasattr(self, 'centralWidget'):
            splitter = self.centralWidget().layout().itemAt(0).widget()
            if isinstance(splitter, QSplitter):
                total_width = splitter.width()
                splitter.setSizes([
                    int(total_width * 0.2),  # Data panel
                    int(total_width * 0.6),  # Viz panel  
                    int(total_width * 0.2)   # Operations panel
                ])
        
        self._status_label.setText("Layout restaurado")
    
    def _clear_cache(self):
        """Limpa cache da aplicação"""
        reply = QMessageBox.question(
            self, 
            "Limpar Cache",
            "Isso irá limpar todos os dados em cache. Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear dataset store cache
                self.session_state._dataset_store.clear_cache()
                self._status_label.setText("Cache limpo com sucesso")
            except Exception as e:
                self._show_error("Erro", f"Falha ao limpar cache:\n{e}")
    
    def _show_about(self):
        """Mostra diálogo sobre a aplicação"""
        QMessageBox.about(
            self,
            "Sobre Platform Base",
            """
            <h3>Platform Base v2.0</h3>
            <p>Plataforma de Análise Exploratória de Séries Temporais</p>
            <p>Desenvolvido para TRANSPETRO</p>
            <br>
            <p><b>Recursos principais:</b></p>
            <ul>
            <li>Análise de séries temporais irregulares</li>
            <li>Interpolação e sincronização avançada</li>
            <li>Visualização 2D/3D interativa</li>
            <li>Operações matemáticas (derivadas, integrais)</li>
            <li>Streaming temporal</li>
            </ul>
            """
        )
    
    def _show_error(self, title: str, message: str):
        """Mostra diálogo de erro"""
        QMessageBox.critical(self, title, message)
    
    def _show_info(self, title: str, message: str):
        """Mostra diálogo de informação"""
        QMessageBox.information(self, title, message)
    
    def _auto_save_session(self):
        """Auto-save periódico da sessão"""
        try:
            # Create auto-save directory
            autosave_dir = Path.home() / ".platform_base" / "autosave"
            autosave_dir.mkdir(parents=True, exist_ok=True)
            
            # Save session with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            autosave_path = autosave_dir / f"autosave_{timestamp}.json"
            
            self.session_state.save_session(str(autosave_path))
            
            # Keep only last 5 auto-saves
            autosave_files = sorted(autosave_dir.glob("autosave_*.json"))
            for old_file in autosave_files[:-5]:
                old_file.unlink()
            
            logger.debug("auto_save_session_completed", path=str(autosave_path))
            
        except Exception as e:
            logger.warning("auto_save_session_failed", error=str(e))
    
    def save_session_on_exit(self):
        """Salva sessão no fechamento da aplicação"""
        try:
            # Create exit save
            exit_save_dir = Path.home() / ".platform_base"
            exit_save_dir.mkdir(parents=True, exist_ok=True)
            
            exit_save_path = exit_save_dir / "last_session.json"
            self.session_state.save_session(str(exit_save_path))
            
            logger.info("exit_session_saved", path=str(exit_save_path))
            
        except Exception as e:
            logger.error("exit_session_save_failed", error=str(e))
    
    def closeEvent(self, event):
        """Override para handling de fechamento"""
        reply = QMessageBox.question(
            self,
            "Fechar Aplicação",
            "Deseja salvar a sessão atual antes de sair?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        
        if reply == QMessageBox.StandardButton.Save:
            self.save_session_on_exit()
        
        # Stop auto-save timer
        self._autosave_timer.stop()
        
        logger.info("main_window_closing")
        event.accept()