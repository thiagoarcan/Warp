"""
MainWindow - Interface moderna PyQt6 para análise de séries temporais

Layout moderno com:
- Toolbar horizontal com ícones e tooltips
- Painéis compactos e organizados
- Sistema drag-and-drop para gráficos
- Interface responsiva e moderna
- 5 temas visuais profissionais
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings, QSize, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QActionGroup, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.ui.panels.data_panel import DataPanel
from platform_base.ui.panels.operations_panel import OperationsPanel
from platform_base.ui.panels.viz_panel import VizPanel
from platform_base.ui.themes import AVAILABLE_THEMES, ThemeMode, get_theme_manager
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.ui.state import SessionState


logger = get_logger(__name__)


class ModernMainWindow(QMainWindow, UiLoaderMixin):
    """
    Interface principal moderna com design clean e funcional

    Características:
    - Layout responsivo com painéis organizados
    - Toolbar horizontal com ícones intuitivos
    - Sistema drag-and-drop para visualizações
    - Tradução completa PT-BR
    - Design moderno seguindo guidelines de UX
    - Persistência de layout com QSettings
    - 5 temas visuais: Light, Dark, Ocean, Forest, Sunset
    
    Interface carregada do arquivo .ui via UiLoaderMixin quando disponível.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/modernMainWindow.ui"

    # Chave para QSettings
    SETTINGS_ORG = "TRANSPETRO"
    SETTINGS_APP = "PlatformBase"

    def __init__(self, session_state: SessionState):
        super().__init__()

        self.session_state = session_state
        self._main_splitter: QSplitter | None = None  # Referência ao splitter principal
        self._theme_manager = get_theme_manager()  # Gerenciador de temas

        # Components
        self._data_panel: DataPanel | None = None
        self._viz_panel: VizPanel | None = None
        self._operations_panel: OperationsPanel | None = None
        self._progress_bar: QProgressBar | None = None
        self._status_label: QLabel | None = None
        self._theme_actions: dict = {}  # Ações do menu de temas

        # Auto-save timer
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._auto_save_session)
        self._autosave_timer.start(300000)  # 5 minutes

        # Initialize UI - QMainWindow precisa de setup programático
        # devido a toolbars, menus e statusbar
        self._setup_modern_ui()
        self._setup_connections()
        self._setup_icons()

        # Restore layout after UI is setup
        self._restore_layout()

        # Conecta mudança de tema
        self._theme_manager.theme_changed.connect(self._on_theme_changed)

        logger.info("modern_main_window_initialized", ui_loaded=getattr(self, '_ui_loaded', False))

    def _setup_modern_ui(self):
        """Configura interface moderna e responsiva para Full HD (1920x1080)"""
        # Window properties - Full HD otimizado
        self.setWindowTitle("Platform Base v2.0 - Análise de Séries Temporais")
        self.setMinimumSize(1280, 720)  # Mínimo HD
        self.resize(1920, 1080)  # Full HD padrão
        
        # Tentar maximizar se a tela suportar
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            if available.width() >= 1920 and available.height() >= 1080:
                self.showMaximized()
            elif available.width() >= 1600:
                self.resize(int(available.width() * 0.95), int(available.height() * 0.9))
                self.move(int(available.width() * 0.025), int(available.height() * 0.05))

        # O tema vai aplicar o stylesheet global
        # Não definir stylesheet aqui para evitar conflitos

        # Create central layout
        self._setup_central_layout()

        # Create interface components
        self._create_modern_toolbar()
        self._create_modern_menu()
        self._create_modern_statusbar()

        logger.debug("modern_ui_setup_completed")

    def _setup_central_layout(self):
        """Layout central otimizado com máxima eficiência de espaço"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout com margens mínimas
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)

        # Create main splitter (horizontal) - TOTALMENTE REDIMENSIONÁVEL
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter.setChildrenCollapsible(False)  # Não colapsar
        self._main_splitter.setHandleWidth(6)  # Handle funcional
        self._main_splitter.setOpaqueResize(True)  # Feedback visual
        main_layout.addWidget(self._main_splitter)

        # Left panel: Data management
        left_frame = QFrame()
        left_frame.setMinimumWidth(150)
        left_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_frame.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(2)

        self._data_panel = DataPanel(self.session_state)
        self._data_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self._data_panel)

        # Center panel: Visualizations
        center_frame = QFrame()
        center_frame.setMinimumWidth(300)
        center_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        center_frame.setObjectName("centerPanel")
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(4, 4, 4, 4)
        center_layout.setSpacing(2)

        self._viz_panel = VizPanel(self.session_state)
        self._viz_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center_layout.addWidget(self._viz_panel)

        # Right panel: Operations
        right_frame = QFrame()
        right_frame.setMinimumWidth(150)
        right_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_frame.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(2)

        self._operations_panel = OperationsPanel(self.session_state)
        self._operations_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self._operations_panel)

        # Add panels to splitter
        self._main_splitter.addWidget(left_frame)
        self._main_splitter.addWidget(center_frame)
        self._main_splitter.addWidget(right_frame)

        # Proporções: Left(15%) - Center(65%) - Right(20%)
        self._main_splitter.setStretchFactor(0, 15)
        self._main_splitter.setStretchFactor(1, 65)
        self._main_splitter.setStretchFactor(2, 20)

        # Tamanhos iniciais para Full HD
        self._main_splitter.setSizes([285, 1235, 380])

    def _create_modern_toolbar(self):
        """Toolbar moderna horizontal com ícones intuitivos"""
        toolbar = self.addToolBar("Ferramentas")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Arquivo
        open_action = QAction("📁", self)
        open_action.setText("Abrir")
        open_action.setToolTip("Abrir dataset (Ctrl+O)")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_dataset)
        toolbar.addAction(open_action)

        save_action = QAction("💾", self)
        save_action.setText("Salvar")
        save_action.setToolTip("Salvar sessão (Ctrl+S)")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_session)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Visualização
        plot_2d_action = QAction("📊", self)
        plot_2d_action.setText("Gráfico 2D")
        plot_2d_action.setToolTip("Criar gráfico 2D")
        plot_2d_action.triggered.connect(self._create_2d_plot)
        toolbar.addAction(plot_2d_action)

        plot_3d_action = QAction("📈", self)
        plot_3d_action.setText("Gráfico 3D")
        plot_3d_action.setToolTip("Criar gráfico 3D")
        plot_3d_action.triggered.connect(self._create_3d_plot)
        toolbar.addAction(plot_3d_action)

        toolbar.addSeparator()

        # Operações
        interpolate_action = QAction("⚡", self)
        interpolate_action.setText("Interpolar")
        interpolate_action.setToolTip("Interpolar série selecionada")
        interpolate_action.triggered.connect(self._interpolate_series)
        toolbar.addAction(interpolate_action)

        derivative_action = QAction("📐", self)
        derivative_action.setText("Derivada")
        derivative_action.setToolTip("Calcular derivada")
        derivative_action.triggered.connect(self._calculate_derivative)
        toolbar.addAction(derivative_action)

        integral_action = QAction("∫", self)
        integral_action.setText("Integral")
        integral_action.setToolTip("Calcular integral")
        integral_action.triggered.connect(self._calculate_integral)
        toolbar.addAction(integral_action)

        toolbar.addSeparator()

        # Exportar
        export_action = QAction("📤", self)
        export_action.setText("Exportar")
        export_action.setToolTip("Exportar dados processados")
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)

        # Configurações
        settings_action = QAction("⚙️", self)
        settings_action.setText("Config")
        settings_action.setToolTip("Configurações da aplicação")
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

    def _create_modern_menu(self):
        """Menu moderno com tradução completa PT-BR e suporte a temas"""
        menubar = self.menuBar()
        # Stylesheet do menu é controlado pelo tema global

        # Menu Arquivo
        file_menu = menubar.addMenu("📁 &Arquivo")

        open_action = QAction("📁 &Abrir Dataset...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Abrir arquivo de dados (CSV, Excel, Parquet, HDF5)")
        open_action.triggered.connect(self._open_dataset)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("💾 &Salvar Sessão...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)

        load_action = QAction("📂 &Carregar Sessão...", self)
        load_action.triggered.connect(self._load_session)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_action = QAction("📤 &Exportar Dados...", self)
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("🚪 &Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Visualizar
        view_menu = menubar.addMenu("👁️ &Visualizar")

        new_2d_action = QAction("📊 Novo Gráfico &2D", self)
        new_2d_action.setShortcut("Ctrl+2")
        new_2d_action.triggered.connect(self._create_2d_plot)
        view_menu.addAction(new_2d_action)

        new_3d_action = QAction("📈 Novo Gráfico &3D", self)
        new_3d_action.setShortcut("Ctrl+3")
        new_3d_action.triggered.connect(self._create_3d_plot)
        view_menu.addAction(new_3d_action)

        view_menu.addSeparator()

        reset_layout_action = QAction("🔄 &Resetar Layout", self)
        reset_layout_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_layout_action)

        # Menu Operações
        ops_menu = menubar.addMenu("⚡ &Operações")

        interpolate_action = QAction("🔗 &Interpolar Série...", self)
        interpolate_action.triggered.connect(self._interpolate_series)
        ops_menu.addAction(interpolate_action)

        derivative_action = QAction("📐 &Derivada...", self)
        derivative_action.triggered.connect(self._calculate_derivative)
        ops_menu.addAction(derivative_action)

        integral_action = QAction("∫ &Integral...", self)
        integral_action.triggered.connect(self._calculate_integral)
        ops_menu.addAction(integral_action)

        # Menu Ferramentas
        tools_menu = menubar.addMenu("🔧 &Ferramentas")

        cache_action = QAction("🗑️ Limpar &Cache", self)
        cache_action.triggered.connect(self._clear_cache)
        tools_menu.addAction(cache_action)

        settings_action = QAction("⚙️ &Configurações...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # Menu Temas 🎨
        themes_menu = menubar.addMenu("🎨 &Temas")
        
        # Grupo de ações para seleção exclusiva
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        
        # Adiciona cada tema disponível
        theme_map = {
            "light": ThemeMode.LIGHT,
            "dark": ThemeMode.DARK,
            "ocean": ThemeMode.OCEAN,
            "forest": ThemeMode.FOREST,
            "sunset": ThemeMode.SUNSET,
        }
        
        for theme_id, theme_info in AVAILABLE_THEMES.items():
            action = QAction(theme_info["name"], self)
            action.setCheckable(True)
            action.setStatusTip(theme_info["description"])
            action.setData(theme_map[theme_id])
            action.triggered.connect(self._on_theme_action_triggered)
            theme_group.addAction(action)
            themes_menu.addAction(action)
            self._theme_actions[theme_id] = action
            
            # Marca o tema atual como selecionado
            if self._theme_manager.current_mode == theme_map[theme_id]:
                action.setChecked(True)
        
        themes_menu.addSeparator()
        
        # Opção de seguir sistema
        system_theme_action = QAction("🖥️ Seguir Sistema", self)
        system_theme_action.setCheckable(True)
        system_theme_action.setData(ThemeMode.SYSTEM)
        system_theme_action.triggered.connect(self._on_theme_action_triggered)
        theme_group.addAction(system_theme_action)
        themes_menu.addAction(system_theme_action)
        self._theme_actions["system"] = system_theme_action
        
        if self._theme_manager.current_mode == ThemeMode.SYSTEM:
            system_theme_action.setChecked(True)

        # Menu Ajuda
        help_menu = menubar.addMenu("❓ &Ajuda")

        about_action = QAction("ℹ️ &Sobre...", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_modern_statusbar(self):
        """Status bar moderna com informações relevantes"""
        statusbar = self.statusBar()

        # Status principal
        self._status_label = QLabel("🟢 Pronto")
        statusbar.addWidget(self._status_label)

        # Progress bar moderna (estilo controlado pelo tema)
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumWidth(200)
        statusbar.addPermanentWidget(self._progress_bar)

        # Dataset info
        dataset_label = QLabel("📊 Nenhum dataset")
        statusbar.addPermanentWidget(dataset_label)

        # Session info
        session_label = QLabel(f"🔑 {self.session_state.session_id[:8]}...")
        statusbar.addPermanentWidget(session_label)

    def _setup_icons(self):
        """Configura ícones para ações"""
        # Icons will be text emojis for now, can be replaced with actual icon files

    def _setup_connections(self):
        """Configura conexões entre componentes"""
        # Connect session state signals
        self.session_state.operation_started.connect(self._on_operation_started)
        self.session_state.operation_finished.connect(self._on_operation_finished)
        self.session_state.operation_progress.connect(self._on_operation_progress)
        self.session_state.dataset_changed.connect(self._on_dataset_changed)

        # Connect panel signals
        if self._data_panel:
            self._data_panel.dataset_loaded.connect(self._on_dataset_loaded)
            if self._viz_panel and hasattr(self._viz_panel, "create_plot_for_series"):
                self._data_panel.plot_requested.connect(self._viz_panel.create_plot_for_series)

        # Connect operations panel signals
        if self._operations_panel:
            self._operations_panel.operation_requested.connect(self._handle_operation_request)
            self._operations_panel.export_requested.connect(self._handle_export_request)
        
        # Connect viz panel calculation requests to operations panel
        if self._viz_panel and self._operations_panel:
            if hasattr(self._viz_panel, "calculation_requested"):
                self._viz_panel.calculation_requested.connect(self._handle_viz_calculation_request)

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

        logger.debug("modern_connections_setup_completed")

    def _setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado conforme auditoria UX"""

        # Undo/Redo - Ctrl+Z/Ctrl+Y
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self._undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self._redo)

        # Também suporta Ctrl+Shift+Z para redo (padrão Mac/Linux)
        redo_alt_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_alt_shortcut.activated.connect(self._redo)

        # Export - Ctrl+E
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self._export_data)

        # Interpolate - Ctrl+I
        interpolate_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        interpolate_shortcut.activated.connect(self._interpolate_series)

        # Derivative - Ctrl+D
        derivative_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        derivative_shortcut.activated.connect(self._calculate_derivative)

        # Integral - Ctrl+Shift+I (Ctrl+I já usado por interpolação)
        integral_shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
        integral_shortcut.activated.connect(self._calculate_integral)

        # Refresh/Update - F5
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._refresh_view)

        # Delete selection - Delete
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self._delete_selection)

        # Cancel operation - Escape
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self._cancel_operation)

        # Fullscreen - F11
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self._toggle_fullscreen)

        # Focus on data panel - F1
        data_panel_shortcut = QShortcut(QKeySequence("F1"), self)
        data_panel_shortcut.activated.connect(lambda: self._data_panel.setFocus() if self._data_panel else None)

        # Focus on viz panel - F2
        viz_panel_shortcut = QShortcut(QKeySequence("F2"), self)
        viz_panel_shortcut.activated.connect(lambda: self._viz_panel.setFocus() if self._viz_panel else None)

        # Focus on operations panel - F3
        ops_panel_shortcut = QShortcut(QKeySequence("F3"), self)
        ops_panel_shortcut.activated.connect(lambda: self._operations_panel.setFocus() if self._operations_panel else None)

        # New dataset - Ctrl+N
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self._new_session)

        # Select all - Ctrl+A
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self._select_all_series)

        logger.debug("keyboard_shortcuts_configured")

    def _undo(self):
        """Desfazer última operação"""
        if hasattr(self.session_state, "undo") and callable(self.session_state.undo):
            if self.session_state.undo():
                self._status_label.setText("⏪ Desfeito")
            else:
                self._status_label.setText("⚠️ Nada para desfazer")
        else:
            self._status_label.setText("⚠️ Undo não disponível")

    def _redo(self):
        """Refazer operação desfeita"""
        if hasattr(self.session_state, "redo") and callable(self.session_state.redo):
            if self.session_state.redo():
                self._status_label.setText("⏩ Refeito")
            else:
                self._status_label.setText("⚠️ Nada para refazer")
        else:
            self._status_label.setText("⚠️ Redo não disponível")

    def _refresh_view(self):
        """Atualiza visualizações"""
        if self._viz_panel:
            self._viz_panel.refresh()
        self._status_label.setText("🔄 Visualização atualizada")

    def _delete_selection(self):
        """Remove séries selecionadas"""
        # Verifica se há séries selecionadas
        if not self.session_state.current_dataset:
            return

        reply = QMessageBox.question(
            self,
            "🗑️ Remover Seleção",
            "Remover séries selecionadas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get current dataset
                current_dataset_id = self.session_state.current_dataset
                if not current_dataset_id:
                    self._status_label.setText("⚠️ Nenhum dataset ativo")
                    return

                # Get selected series from data panel
                if not self._data_panel:
                    self._status_label.setText("⚠️ Painel de dados não disponível")
                    return

                selected_ids = self._data_panel.get_selected_series_ids()
                if not selected_ids:
                    self._status_label.setText("⚠️ Nenhuma série selecionada")
                    return

                # Get dataset and remove series
                dataset = self.session_state.get_dataset(current_dataset_id)
                if not dataset:
                    self._status_label.setText("⚠️ Dataset não encontrado")
                    return

                # Remove each selected series
                removed_count = 0
                for series_id in selected_ids:
                    if series_id in dataset.series:
                        del dataset.series[series_id]
                        removed_count += 1

                if removed_count > 0:
                    # Update dataset in store and local cache
                    self.session_state._loaded_datasets[current_dataset_id] = dataset
                    # Emit signal to notify UI of changes
                    self.session_state.dataset_changed.emit(current_dataset_id)
                    self._status_label.setText(f"✅ {removed_count} série(s) removida(s)")
                    logger.info("series_removed", dataset_id=current_dataset_id, count=removed_count)
                else:
                    self._status_label.setText("⚠️ Nenhuma série foi removida")

            except Exception as e:
                logger.error("series_removal_failed", error=str(e), exc_info=True)
                self._status_label.setText(f"❌ Erro ao remover séries: {e}")

    def _cancel_operation(self):
        """Cancela operação em andamento"""
        if hasattr(self.session_state, "cancel_current_operation"):
            self.session_state.cancel_current_operation()
            self._status_label.setText("⛔ Operação cancelada")
        else:
            self._status_label.setText("🟢 Pronto")
            self._progress_bar.setVisible(False)

    def _toggle_fullscreen(self):
        """Alterna modo tela cheia"""
        if self.isFullScreen():
            self.showNormal()
            self._status_label.setText("📐 Modo normal")
        else:
            self.showFullScreen()
            self._status_label.setText("📺 Tela cheia (F11 para sair)")

    def _new_session(self):
        """Cria nova sessão"""
        reply = QMessageBox.question(
            self,
            "📄 Nova Sessão",
            "Criar nova sessão? Dados não salvos serão perdidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.session_state, "clear_session"):
                self.session_state.clear_session()
            self._status_label.setText("📄 Nova sessão criada")

    def _select_all_series(self):
        """Seleciona todas as séries"""
        if hasattr(self.session_state, "select_all_series"):
            self.session_state.select_all_series()
            self._status_label.setText("✓ Todas as séries selecionadas")


    # Signal handlers
    @pyqtSlot(str)
    def _on_operation_started(self, operation_name: str):
        """Handler para início de operação"""
        self._status_label.setText(f"⚡ Executando: {operation_name}")
        self._status_label.setStyleSheet("color: #fd7e14; font-weight: bold;")
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, 0)

        logger.debug("operation_started", operation=operation_name)

    @pyqtSlot(float, str)
    def _on_operation_progress(self, percent: float, message: str):
        """Handler para progresso de operação"""
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(int(percent))

        if message:
            self._status_label.setText(f"⚡ {message}")

    @pyqtSlot(str, bool)
    def _on_operation_finished(self, operation_name: str, success: bool):
        """Handler para fim de operação"""
        if success:
            self._status_label.setText(f"✅ {operation_name} concluída")
            self._status_label.setStyleSheet("color: #198754; font-weight: bold;")
        else:
            self._status_label.setText(f"❌ {operation_name} falhou")
            self._status_label.setStyleSheet("color: #dc3545; font-weight: bold;")

        self._progress_bar.setVisible(False)

        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: (
            self._status_label.setText("🟢 Pronto"),
            self._status_label.setStyleSheet("color: #198754; font-weight: bold;"),
        ))

        logger.debug("operation_finished", operation=operation_name, success=success)

    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Handler para mudança de dataset"""
        if dataset_id:
            # Get filename from dataset
            dataset = self.session_state._dataset_store.get_dataset(dataset_id)
            if dataset and hasattr(dataset, "source_file"):
                filename = Path(dataset.source_file).name
                self._status_label.setText(f"📊 Dataset: {filename}")
            else:
                self._status_label.setText(f"📊 Dataset: {dataset_id}")
        else:
            self._status_label.setText("📊 Nenhum dataset")

    @pyqtSlot(str)
    def _on_dataset_loaded(self, dataset_id: str):
        """Handler para dataset carregado"""
        dataset = self.session_state._dataset_store.get_dataset(dataset_id)
        if dataset and hasattr(dataset, "source_file"):
            filename = Path(dataset.source_file).name
            self._status_label.setText(f"✅ Carregado: {filename}")

    @pyqtSlot(str, dict)
    def _handle_operation_request(self, operation_name: str, params: dict):
        """
        Handler para requisições de operações matemáticas do OperationsPanel.
        
        Conecta a UI ao backend de processamento.
        """
        logger.info("operation_requested", operation=operation_name, params=params)

        # Obter série selecionada do combobox do operations panel
        series_id = None
        dataset_id = self.session_state.current_dataset
        
        if self._operations_panel and hasattr(self._operations_panel, '_series_combo'):
            series_id = self._operations_panel._series_combo.currentData()
        
        if not dataset_id or not series_id:
            QMessageBox.warning(
                self,
                "⚠️ Nenhuma Série Selecionada",
                "Por favor, selecione uma série no painel de operações antes de realizar o cálculo."
            )
            return

        try:
            # Obter dataset e série
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                QMessageBox.warning(
                    self,
                    "⚠️ Dados Inválidos",
                    "Não foi possível encontrar a série selecionada."
                )
                return
                
            series = dataset.series[series_id]
            
            # Processar operação
            self.session_state.start_operation(f"Calculando {operation_name}...")
            
            try:
                result = self._execute_operation(operation_name, series, dataset, params)
                
                if result is not None:
                    # Adicionar resultado como nova série
                    new_series_id = f"{series_id}_{operation_name}"
                    self._add_result_series(dataset_id, new_series_id, result, operation_name)
                    self.session_state.finish_operation(True, f"✅ {operation_name} calculada com sucesso")
                else:
                    self.session_state.finish_operation(False, f"❌ {operation_name} não retornou resultado")
                    
            except Exception as e:
                self.session_state.finish_operation(False, f"❌ Erro: {e}")
                raise

        except Exception as e:
            logger.exception("operation_request_failed", operation=operation_name, error=str(e))
            QMessageBox.critical(
                self,
                "❌ Operação Falhou",
                f"Falha ao executar '{operation_name}':\n{str(e)}"
            )

    def _execute_operation(self, operation_name: str, series, dataset, params: dict):
        """Executa a operação matemática especificada"""
        import numpy as np
        
        values = series.values
        t_seconds = dataset.t_seconds
        
        if operation_name == "derivative":
            order = params.get("order", 1)
            method = params.get("method", "finite_diff")
            
            if method == "finite_diff":
                # Derivada numérica simples
                result = np.gradient(values, t_seconds)
                for _ in range(order - 1):
                    result = np.gradient(result, t_seconds)
            elif method == "savitzky_golay":
                from scipy.signal import savgol_filter
                window = params.get("window_length", 7)
                # Garantir que window seja ímpar
                if window % 2 == 0:
                    window += 1
                result = savgol_filter(values, window, polyorder=min(3, window-1), deriv=order)
            else:
                result = np.gradient(values, t_seconds)
                
            return result
            
        elif operation_name == "integral":
            method = params.get("method", "trapezoid")
            
            if method == "trapezoid":
                from scipy import integrate
                result = integrate.cumulative_trapezoid(values, t_seconds, initial=0)
            elif method == "simpson":
                # Simpson precisa de número ímpar de pontos
                from scipy import integrate
                result = integrate.cumulative_trapezoid(values, t_seconds, initial=0)
            else:  # cumulative
                result = np.cumsum(values) * np.gradient(t_seconds).mean()
                
            return result
            
        elif operation_name == "smoothing":
            method = params.get("method", "moving_average")
            window = params.get("window", 5)
            
            if method == "moving_average":
                result = np.convolve(values, np.ones(window)/window, mode='same')
            elif method == "gaussian":
                from scipy.ndimage import gaussian_filter1d
                sigma = params.get("sigma", 2.0)
                result = gaussian_filter1d(values, sigma)
            else:
                result = values.copy()
                
            return result
            
        elif operation_name == "remove_outliers":
            threshold = params.get("threshold", 3.0)
            mean = np.mean(values)
            std = np.std(values)
            mask = np.abs(values - mean) < threshold * std
            result = np.where(mask, values, np.nan)
            # Interpolar NaNs
            nans = np.isnan(result)
            if np.any(nans):
                result[nans] = np.interp(
                    np.flatnonzero(nans),
                    np.flatnonzero(~nans),
                    result[~nans]
                )
            return result
        
        elif operation_name == "fft":
            # Transformada Rápida de Fourier
            from scipy import signal
            
            window_type = params.get("window", "hann")
            detrend = params.get("detrend", True)
            
            # Remover tendência se solicitado
            data = values.copy()
            if detrend:
                data = signal.detrend(data)
            
            # Aplicar janela se especificada
            n = len(data)
            if window_type and window_type != "none":
                if window_type == "hann":
                    window = np.hanning(n)
                elif window_type == "hamming":
                    window = np.hamming(n)
                elif window_type == "blackman":
                    window = np.blackman(n)
                elif window_type == "bartlett":
                    window = np.bartlett(n)
                else:
                    window = np.ones(n)
                data = data * window
            
            # Calcular FFT
            fft_result = np.fft.fft(data)
            
            # Retornar magnitude (metade positiva)
            n_half = n // 2
            magnitude = np.abs(fft_result[:n_half]) * 2.0 / n
            
            return magnitude
        
        elif operation_name == "filter":
            from scipy import signal
            
            filter_type = params.get("filter_type", "lowpass")
            cutoff = params.get("cutoff_frequency", 0.1)
            order = params.get("filter_order", 4)
            method = params.get("method", "butter")
            
            # Calcular frequência de amostragem
            dt = np.mean(np.diff(t_seconds)) if len(t_seconds) > 1 else 1.0
            fs = 1.0 / dt
            nyq = fs / 2.0
            
            # Normalizar frequência de corte
            if isinstance(cutoff, tuple):
                wn = (cutoff[0] / nyq, cutoff[1] / nyq)
            else:
                wn = cutoff / nyq
            
            # Limitar wn para evitar erros
            if isinstance(wn, tuple):
                wn = (max(0.001, min(0.999, wn[0])), max(0.001, min(0.999, wn[1])))
            else:
                wn = max(0.001, min(0.999, wn))
            
            # Criar filtro
            if method == "butter":
                b, a = signal.butter(order, wn, btype=filter_type)
            elif method == "cheby1":
                b, a = signal.cheby1(order, 0.5, wn, btype=filter_type)
            elif method == "cheby2":
                b, a = signal.cheby2(order, 20, wn, btype=filter_type)
            elif method == "ellip":
                b, a = signal.ellip(order, 0.5, 20, wn, btype=filter_type)
            else:
                b, a = signal.butter(order, wn, btype=filter_type)
            
            # Aplicar filtro
            result = signal.filtfilt(b, a, values)
            
            return result
            
        else:
            logger.warning(f"Unknown operation: {operation_name}")
            return None

    def _add_result_series(self, dataset_id: str, series_id: str, values, operation_name: str):
        """Adiciona resultado como nova série no dataset"""
        from datetime import datetime, timezone

        import numpy as np
        from pint import UnitRegistry

        from platform_base.core.models import (
            InterpolationInfo,
            Lineage,
            Series,
            SeriesMetadata,
        )
        
        ureg = UnitRegistry()
        
        dataset = self.session_state.get_dataset(dataset_id)
        if not dataset:
            return
            
        # Criar nova série
        new_series = Series(
            series_id=series_id,
            name=f"{series_id}",
            unit=ureg.dimensionless,
            values=np.array(values),
            interpolation_info=InterpolationInfo(
                is_interpolated=np.zeros(len(values), dtype=bool),
                method_used=np.array([operation_name] * len(values), dtype='<U32'),
            ),
            metadata=SeriesMetadata(
                original_name=series_id,
                source_column=operation_name,
                description=f"Resultado de {operation_name}",
            ),
            lineage=Lineage(
                origin_series=[],
                operation=operation_name,
                parameters={},
                timestamp=datetime.now(timezone.utc),
                version="2.0.0",
            ),
        )
        
        # Adicionar ao dataset
        dataset.series[series_id] = new_series
        
        # Emitir sinal de mudança
        self.session_state.dataset_changed.emit(dataset_id)
        
        logger.info(f"result_series_added: {series_id}")

    @pyqtSlot(str, str, str, dict)
    def _handle_viz_calculation_request(self, dataset_name: str, series_id: str, calc_type: str, params: dict):
        """Handler para requisições de cálculo vindas do menu de contexto do gráfico"""
        logger.info("viz_calculation_requested", calc_type=calc_type, series=series_id, params=params)
        
        # Mapear calc_type para operation_name
        operation_map = {
            "derivative": "derivative",
            "integral": "integral",
            "area": "area_under_curve",
            "interpolation": "interpolation",
            "filter": "smoothing",
        }
        
        operation_name = operation_map.get(calc_type, calc_type)
        
        # Encontrar dataset_id pelo nome do dataset
        dataset_id = None
        all_datasets = self.session_state.get_all_datasets()
        for ds_id, ds in all_datasets.items():
            if hasattr(ds, "source") and ds.source and ds.source.filename:
                if Path(ds.source.filename).stem == dataset_name:
                    dataset_id = ds_id
                    break
            if ds_id == dataset_name:
                dataset_id = ds_id
                break
        
        if not dataset_id:
            # Usar dataset atual se não encontrou
            dataset_id = self.session_state.current_dataset
        
        if not dataset_id:
            QMessageBox.warning(
                self,
                "⚠️ Nenhum Dataset",
                "Não foi possível identificar o dataset para o cálculo."
            )
            return
        
        # Delegar para handler principal
        self._handle_operation_request(operation_name, params)

    @pyqtSlot(str, dict)
    def _handle_export_request(self, format_type: str, options: dict):
        """Handler para requisições de exportação"""
        logger.info("export_requested", format=format_type, options=options)

        # Mapear filtros de arquivo
        file_filters = {
            'csv': "Arquivos CSV (*.csv)",
            'excel': "Arquivos Excel (*.xlsx)",
            'parquet': "Arquivos Parquet (*.parquet)",
            'hdf5': "Arquivos HDF5 (*.h5 *.hdf5)",
            'json': "Arquivos JSON (*.json)",
        }

        file_filter = file_filters.get(format_type, "Todos os Arquivos (*.*)")
        
        # Obter dataset atual
        dataset_id = self.session_state.current_dataset
        if not dataset_id:
            QMessageBox.warning(
                self,
                "⚠️ Nenhum Dataset",
                "Por favor, carregue um dataset antes de exportar."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Exportar como {format_type.upper()}",
            "",
            file_filter
        )

        if file_path:
            try:
                self._export_to_file(dataset_id, file_path, format_type, options)
                self._status_label.setText(f"✅ Exportado: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Erro na Exportação",
                    f"Falha ao exportar:\n{str(e)}"
                )

    def _export_to_file(self, dataset_id: str, file_path: str, format_type: str, options: dict):
        """Exporta dataset para arquivo"""
        import pandas as pd
        
        dataset = self.session_state.get_dataset(dataset_id)
        if not dataset:
            raise ValueError("Dataset não encontrado")
            
        # Criar DataFrame
        data = {"timestamp": dataset.t_datetime}
        for series_id, series in dataset.series.items():
            data[series_id] = series.values
            
        df = pd.DataFrame(data)
        
        # Exportar conforme formato
        if format_type == "csv":
            df.to_csv(file_path, index=False)
        elif format_type == "excel":
            df.to_excel(file_path, index=False)
        elif format_type == "parquet":
            df.to_parquet(file_path, index=False)
        elif format_type == "hdf5":
            df.to_hdf(file_path, key="data", mode="w")
        elif format_type == "json":
            df.to_json(file_path, orient="records", date_format="iso")
        else:
            raise ValueError(f"Formato não suportado: {format_type}")
            
        logger.info(f"export_completed: {file_path}")

    # Action handlers
    def _open_dataset(self):
        """Abre diálogo para carregar dataset"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("📁 Abrir Dataset")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters([
            "Todos os formatos (*.csv *.xlsx *.parquet *.h5)",
            "CSV (*.csv)",
            "Excel (*.xlsx *.xls)",
            "Parquet (*.parquet *.pq)",
            "HDF5 (*.h5 *.hdf5)",
        ])

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths and self._data_panel:
                self._data_panel.load_dataset(file_paths[0])

    def _save_session(self):
        """Salva sessão atual"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("💾 Salvar Sessão")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilters(["Sessões (*.json)"])

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                try:
                    self.session_state.save_session(file_paths[0])
                    self._status_label.setText("✅ Sessão salva")
                except Exception as e:
                    self._show_error("Erro ao Salvar", f"Falha ao salvar:\n{e}")

    def _load_session(self):
        """Carrega sessão"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("📂 Carregar Sessão")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters(["Sessões (*.json)"])

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                try:
                    self.session_state.load_session(file_paths[0])
                    self._status_label.setText("✅ Sessão carregada")
                except Exception as e:
                    self._show_error("Erro ao Carregar", f"Falha ao carregar:\n{e}")

    def _create_2d_plot(self):
        """Cria novo gráfico 2D"""
        if self._viz_panel:
            self._viz_panel.create_2d_plot()

    def _create_3d_plot(self):
        """Cria novo gráfico 3D"""
        if self._viz_panel:
            self._viz_panel.create_3d_plot()

    def _interpolate_series(self):
        """Interpola série selecionada"""
        if self._operations_panel:
            self._operations_panel.show_interpolation_dialog()

    def _calculate_derivative(self):
        """Calcula derivada"""
        if self._operations_panel:
            self._operations_panel.show_derivative_dialog()

    def _calculate_integral(self):
        """Calcula integral"""
        if self._operations_panel:
            self._operations_panel.show_integral_dialog()

    def _export_data(self):
        """Exporta dados"""
        if not self.session_state.current_dataset:
            self._show_info("Exportar", "Nenhum dataset para exportar")
            return

        if self._operations_panel:
            self._operations_panel.show_export_dialog()

    def _show_settings(self):
        """Mostra configurações"""
        self._show_info("Configurações", "Painel de configurações em desenvolvimento")

    def _reset_layout(self):
        """Restaura layout para configuração otimizada"""
        if self._main_splitter:
            # Use absolute sizes for more precise control
            self._main_splitter.setSizes([240, 800, 200])  # Otimizado para eficiência
            logger.info("layout_reset_completed", sizes="240-800-200")

        # Reset window geometry
        self.resize(1800, 1100)

        self._status_label.setText("🔄 Layout otimizado restaurado")
        self._status_label.setStyleSheet("color: #198754; font-weight: bold;")

    def _save_layout(self):
        """Salva layout e geometria da janela com QSettings"""
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)

        # Save window geometry
        settings.setValue("mainwindow/geometry", self.saveGeometry())
        # NÃO salvar mainwindow/state - pode interferir com splitter ao restaurar
        # settings.setValue("mainwindow/state", self.saveState())
        settings.setValue("mainwindow/maximized", self.isMaximized())
        settings.setValue("mainwindow/fullscreen", self.isFullScreen())

        # Save splitter sizes apenas (não salvar splitter_state que pode corromper)
        if self._main_splitter:
            settings.setValue("mainwindow/splitter_sizes", self._main_splitter.sizes())
            # NÃO salvar splitter_state - pode causar travamento ao restaurar

        # Save panel visibility/collapsed states
        if self._data_panel:
            settings.setValue("panels/data_panel_visible", self._data_panel.isVisible())
        if self._viz_panel:
            settings.setValue("panels/viz_panel_visible", self._viz_panel.isVisible())
        if self._operations_panel:
            settings.setValue("panels/operations_panel_visible", self._operations_panel.isVisible())

        # Save operations panel tab index if it has tabs
        if self._operations_panel and hasattr(self._operations_panel, "currentIndex"):
            settings.setValue("panels/operations_tab_index", self._operations_panel.currentIndex())

        settings.sync()
        logger.debug("layout_saved")

    def _restore_layout(self):
        """Restaura layout e geometria da janela com QSettings"""
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)

        # Restore window geometry
        geometry = settings.value("mainwindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # NÃO restaurar mainwindow/state - pode interferir com o splitter
        # O restoreState() da QMainWindow afeta toolbars e pode travar o layout
        # state = settings.value("mainwindow/state")
        # if state:
        #     self.restoreState(state)

        # Restore maximized/fullscreen state
        was_maximized = settings.value("mainwindow/maximized", False, type=bool)
        was_fullscreen = settings.value("mainwindow/fullscreen", False, type=bool)

        if was_fullscreen:
            self.showFullScreen()
        elif was_maximized:
            self.showMaximized()

        # Restore splitter sizes - NÃO usar restoreState() que pode estar corrompido
        if self._main_splitter:
            splitter_sizes = settings.value("mainwindow/splitter_sizes")
            if splitter_sizes:
                # Convert to list of ints
                try:
                    sizes = [int(s) for s in splitter_sizes]
                    # Garantir tamanhos mínimos razoáveis
                    min_sizes = [200, 600, 200]  # Tamanhos mínimos para cada painel
                    sizes = [max(size, min_size) for size, min_size in zip(sizes, min_sizes)]
                    self._main_splitter.setSizes(sizes)
                except (ValueError, TypeError):
                    # Em caso de erro, usar tamanhos padrão
                    self._main_splitter.setSizes([300, 1000, 300])
            else:
                # Sem sizes salvos, usar padrão
                self._main_splitter.setSizes([300, 1000, 300])
            
            # NÃO restaurar splitter_state - pode estar corrompido e travar o splitter
            # O setSizes() acima é suficiente para restaurar as proporções

        # Sempre forçar todos os painéis visíveis
        if self._data_panel:
            self._data_panel.setVisible(True)
            self._data_panel.show()
        if self._viz_panel:
            self._viz_panel.setVisible(True)
            self._viz_panel.show()
        if self._operations_panel:
            self._operations_panel.setVisible(True)
            self._operations_panel.show()

        # Restore operations panel tab index if applicable
        if self._operations_panel and hasattr(self._operations_panel, "setCurrentIndex"):
            tab_index = settings.value("panels/operations_tab_index", 0, type=int)
            self._operations_panel.setCurrentIndex(tab_index)

        # Garantir que todos os widgets filhos dos painéis estejam visíveis
        self._ensure_panel_widgets_visible()

        logger.debug("layout_restored")

    def _ensure_panel_widgets_visible(self):
        """Garante que todos os widgets dos painéis estejam visíveis
        
        CORREÇÃO: Após restaurar o layout, alguns widgets podem ficar ocultos
        devido a estados salvos anteriormente. Este método percorre a hierarquia
        de widgets e garante que todos estejam visíveis.
        """
        def show_all_children(widget):
            """Recursivamente mostra todos os widgets filhos"""
            if widget is None:
                return
            
            # Mostra este widget
            widget.setVisible(True)
            widget.show()
            
            # Processa todos os filhos
            for child in widget.findChildren(QWidget):
                if hasattr(child, 'setVisible'):
                    child.setVisible(True)
                    child.show()
        
        # Aplicar aos painéis principais
        if self._data_panel:
            show_all_children(self._data_panel)
            
        if self._viz_panel:
            show_all_children(self._viz_panel)
            
        if self._operations_panel:
            show_all_children(self._operations_panel)
        
        # Forçar atualização do layout
        if self._main_splitter:
            self._main_splitter.update()
        
        self.update()
        logger.debug("panel_widgets_visibility_ensured")

    def _clear_cache(self):
        """Limpa cache"""
        reply = QMessageBox.question(
            self,
            "🗑️ Limpar Cache",
            "Limpar todos os dados em cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.session_state._dataset_store.clear_cache()
                self._status_label.setText("✅ Cache limpo")
            except Exception as e:
                self._show_error("Erro", f"Falha ao limpar cache:\n{e}")

    def _show_about(self):
        """Sobre a aplicação"""
        QMessageBox.about(
            self,
            "ℹ️ Sobre Platform Base",
            """
            <h3>🚀 Platform Base v2.0</h3>
            <p><b>Plataforma Moderna de Análise de Séries Temporais</b></p>
            <p>Desenvolvido para TRANSPETRO</p>
            <br>
            <p><b>📊 Recursos:</b></p>
            <ul>
            <li>🔍 Análise exploratória avançada</li>
            <li>📈 Visualização 2D/3D interativa</li>
            <li>⚡ Interpolação e sincronização</li>
            <li>📐 Operações matemáticas (derivadas, integrais)</li>
            <li>🎯 Interface moderna e intuitiva</li>
            <li>🚀 Streaming temporal em tempo real</li>
            </ul>
            <br>
            <p><b>Tecnologias:</b> Python 3.10+, PyQt6, NumPy, Pandas</p>
            """,
        )

    def _show_error(self, title: str, message: str):
        """Mostra erro"""
        QMessageBox.critical(self, f"❌ {title}", message)

    def _show_info(self, title: str, message: str):
        """Mostra informação"""
        QMessageBox.information(self, f"ℹ️ {title}", message)

    # =========================================================================
    # GERENCIAMENTO DE TEMAS
    # =========================================================================
    
    def _on_theme_action_triggered(self):
        """Chamado quando um tema é selecionado no menu"""
        action = self.sender()
        if action and action.data():
            theme_mode = action.data()
            self._theme_manager.set_theme(theme_mode)
            
            # Mensagem de confirmação
            theme_names = {
                ThemeMode.LIGHT: "☀️ Clássico",
                ThemeMode.DARK: "🌙 Noturno",
                ThemeMode.OCEAN: "🌊 Oceano",
                ThemeMode.FOREST: "🌲 Floresta",
                ThemeMode.SUNSET: "🌅 Pôr do Sol",
                ThemeMode.SYSTEM: "🖥️ Sistema",
            }
            self._status_label.setText(f"🎨 Tema: {theme_names.get(theme_mode, 'Desconhecido')}")
            logger.info("theme_changed_by_user", theme=theme_mode.name)
    
    def _on_theme_changed(self, mode: ThemeMode):
        """Chamado quando o tema muda (para atualizar checkmarks no menu)"""
        # Atualiza os checkmarks
        theme_map_reverse = {
            ThemeMode.LIGHT: "light",
            ThemeMode.DARK: "dark",
            ThemeMode.OCEAN: "ocean",
            ThemeMode.FOREST: "forest",
            ThemeMode.SUNSET: "sunset",
            ThemeMode.SYSTEM: "system",
        }
        
        theme_id = theme_map_reverse.get(mode)
        if theme_id and theme_id in self._theme_actions:
            self._theme_actions[theme_id].setChecked(True)

    def _auto_save_session(self):
        """Auto-save da sessão"""
        try:
            autosave_dir = Path.home() / ".platform_base" / "autosave"
            autosave_dir.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            autosave_path = autosave_dir / f"autosave_{timestamp}.json"

            self.session_state.save_session(str(autosave_path))

            # Keep last 5 auto-saves
            autosave_files = sorted(autosave_dir.glob("autosave_*.json"))
            for old_file in autosave_files[:-5]:
                old_file.unlink()

            logger.debug("auto_save_completed", path=str(autosave_path))

        except Exception as e:
            logger.warning("auto_save_failed", error=str(e))

    def save_session_on_exit(self):
        """Salva sessão ao sair"""
        try:
            exit_save_dir = Path.home() / ".platform_base"
            exit_save_dir.mkdir(parents=True, exist_ok=True)

            exit_save_path = exit_save_dir / "last_session.json"
            self.session_state.save_session(str(exit_save_path))

            logger.info("exit_session_saved", path=str(exit_save_path))

        except Exception as e:
            logger.exception("exit_session_save_failed", error=str(e))

    def closeEvent(self, event):
        """Handler de fechamento"""
        reply = QMessageBox.question(
            self,
            "🚪 Fechar Aplicação",
            "Salvar sessão antes de sair?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return

        if reply == QMessageBox.StandardButton.Save:
            self.save_session_on_exit()

        # Always save layout (even on discard)
        self._save_layout()

        self._autosave_timer.stop()
        logger.info("application_closing")
        event.accept()


# Alias para compatibilidade
MainWindow = ModernMainWindow
