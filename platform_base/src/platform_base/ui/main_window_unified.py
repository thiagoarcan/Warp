"""
ModernMainWindow Unificada - Interface moderna PyQt6 com todas as funcionalidades

Combina as melhores características de:
- desktop/main_window.py: QDockWidget, SessionState+SignalHub, Undo/Redo, Workers
- ui/main_window.py: 5 temas visuais, drag-and-drop, interface moderna

Layout:
- Dockable panels (Data, Config, Operations, Streaming, Results)
- 5 temas visuais profissionais (Light, Dark, Ocean, Forest, Sunset)
- Sistema drag-and-drop para gráficos
- Undo/Redo completo
- ProcessingWorkerManager para operações assíncronas
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings, QSize, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QActionGroup, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.dialogs.about_dialog import AboutDialog
from platform_base.desktop.dialogs.settings_dialog import SettingsDialog
from platform_base.desktop.dialogs.upload_dialog import UploadDialog
from platform_base.desktop.widgets.config_panel import ConfigPanel
from platform_base.desktop.widgets.data_panel import DataPanel
from platform_base.desktop.widgets.results_panel import ResultsPanel
from platform_base.desktop.widgets.viz_panel import VizPanel
from platform_base.ui.themes import AVAILABLE_THEMES, ThemeMode, get_theme_manager
from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class ModernMainWindow(QMainWindow, UiLoaderMixin):
    """
    Interface principal moderna unificada com todas as funcionalidades.

    Características:
    - Layout QDockWidget com painéis acopláveis (Data, Config, Operations, Streaming, Results)
    - 5 temas visuais: Light, Dark, Ocean, Forest, Sunset
    - SessionState + SignalHub para comunicação entre componentes
    - Undo/Redo Manager completo
    - ProcessingWorkerManager para operações assíncronas
    - Toolbar horizontal com ícones intuitivos
    - Sistema drag-and-drop para visualizações
    - Tradução completa PT-BR
    - Persistência de layout com QSettings
    
    Interface carregada do arquivo .ui via UiLoaderMixin quando disponível.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "modernMainWindow.ui"

    # Chave para QSettings
    SETTINGS_ORG = "TRANSPETRO"
    SETTINGS_APP = "PlatformBase"

    def __init__(self, session_state: SessionState, signal_hub: SignalHub):
        super().__init__()

        self.session_state = session_state
        self.signal_hub = signal_hub
        self._theme_manager = get_theme_manager()
        self._theme_actions: dict = {}

        # Initialize undo/redo manager
        from platform_base.ui.undo_redo import get_undo_manager
        self.undo_manager = get_undo_manager()

        # Initialize processing worker manager
        from platform_base.desktop.workers.processing_worker import (
            ProcessingWorkerManager,
        )
        self.processing_manager = ProcessingWorkerManager(
            session_state.dataset_store, signal_hub
        )

        # Panel references
        self.data_panel: DataPanel | None = None
        self.viz_panel: VizPanel | None = None
        self.config_panel: ConfigPanel | None = None
        self.operations_panel = None
        self.streaming_panel = None
        self.results_panel: ResultsPanel | None = None

        # Dock references
        self.data_dock: QDockWidget | None = None
        self.config_dock: QDockWidget | None = None
        self.operations_dock: QDockWidget | None = None
        self.streaming_dock: QDockWidget | None = None
        self.results_dock: QDockWidget | None = None

        # Status bar widgets
        self.status_label: QLabel | None = None
        self.progress_bar: QProgressBar | None = None
        self.memory_label: QLabel | None = None

        # Carregar interface do arquivo .ui ou criar programaticamente
        if self._load_ui():
            self._setup_ui_from_file()
        else:
            logger.warning("ui_load_failed_using_fallback", cls="ModernMainWindow")
            self._setup_window()
            self._create_dockable_panels()
            self._create_menu_bar()
            self._create_tool_bar()
            self._create_status_bar()

        self._setup_keyboard_shortcuts()
        self._connect_signals()

        # Auto-save timer
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self._auto_save_session)
        self._auto_save_timer.start(300000)  # Save every 5 minutes

        # Memory usage timer
        self._memory_timer = QTimer()
        self._memory_timer.timeout.connect(self._update_memory_usage)
        self._memory_timer.start(5000)

        # Restore layout
        self._restore_layout()

        # Connect theme changes
        self._theme_manager.theme_changed.connect(self._on_theme_changed)

        logger.info("modern_main_window_initialized")

    # =========================================================================
    # UI SETUP - ARQUIVO .UI
    # =========================================================================

    def _setup_ui_from_file(self):
        """Configura a UI carregada do arquivo .ui"""
        self._insert_panels_into_placeholders()
        self._connect_ui_actions()
        self._setup_status_bar_widgets()
        logger.debug("main_window_ui_from_file_configured")

    def _insert_panels_into_placeholders(self):
        """Insere os painéis reais nos placeholders definidos no .ui"""
        
        # Data Panel
        self.data_panel = DataPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'dataDock') and hasattr(self, 'dataPanelPlaceholder'):
            layout = QVBoxLayout(self.dataPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.data_panel)
            self.data_dock = self.dataDock
        else:
            self.data_dock = QDockWidget(tr("📊 Painel de Dados"), self)
            self.data_dock.setWidget(self.data_panel)
            self.data_dock.setObjectName("DataPanel")
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.data_dock)

        # Visualization Panel (central widget)
        self.viz_panel = VizPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'vizPanelPlaceholder'):
            layout = QVBoxLayout(self.vizPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.viz_panel)
        else:
            central_layout = QHBoxLayout()
            central_layout.addWidget(self.viz_panel)
            self.centralWidget().setLayout(central_layout)

        # Config Panel
        self.config_panel = ConfigPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'configDock') and hasattr(self, 'configPanelPlaceholder'):
            layout = QVBoxLayout(self.configPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.config_panel)
            self.config_dock = self.configDock
        else:
            self.config_dock = QDockWidget(tr("⚙️ Configurações"), self)
            self.config_dock.setWidget(self.config_panel)
            self.config_dock.setObjectName("ConfigPanel")
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config_dock)

        # Operations Panel
        from platform_base.ui.panels.operations_panel import OperationsPanel
        self.operations_panel = OperationsPanel(self.session_state)
        if hasattr(self, 'operationsDock') and hasattr(self, 'operationsPanelPlaceholder'):
            layout = QVBoxLayout(self.operationsPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.operations_panel)
            self.operations_dock = self.operationsDock
        else:
            self.operations_dock = QDockWidget(tr("⚡ Operações"), self)
            self.operations_dock.setWidget(self.operations_panel)
            self.operations_dock.setObjectName("OperationsPanel")
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.operations_dock)

        # Tabify config e operations
        self.tabifyDockWidget(self.config_dock, self.operations_dock)
        self.config_dock.raise_()

        # Streaming Panel
        from platform_base.ui.panels.streaming_panel import StreamingPanel
        self.streaming_panel = StreamingPanel()
        self.streaming_panel.position_changed.connect(self._on_streaming_position_changed)
        self.streaming_panel.state_changed.connect(self._on_streaming_state_changed)
        if hasattr(self, 'streamingDock') and hasattr(self, 'streamingPanelPlaceholder'):
            layout = QVBoxLayout(self.streamingPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.streaming_panel)
            self.streaming_dock = self.streamingDock
        else:
            self.streaming_dock = QDockWidget(tr("📡 Streaming"), self)
            self.streaming_dock.setWidget(self.streaming_panel)
            self.streaming_dock.setObjectName("StreamingPanel")
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.streaming_dock)

        # Results Panel
        self.results_panel = ResultsPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'resultsDock') and hasattr(self, 'resultsPanelPlaceholder'):
            layout = QVBoxLayout(self.resultsPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.results_panel)
            self.results_dock = self.resultsDock
        else:
            self.results_dock = QDockWidget(tr("📈 Resultados"), self)
            self.results_dock.setWidget(self.results_panel)
            self.results_dock.setObjectName("ResultsPanel")
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.results_dock)

        # Tabify bottom panels
        self.tabifyDockWidget(self.streaming_dock, self.results_dock)
        self.streaming_dock.raise_()

        logger.debug("panels_inserted_into_placeholders")

    def _connect_ui_actions(self):
        """Conecta as QActions do .ui aos métodos da classe"""
        
        # File menu actions
        if hasattr(self, 'actionNewSession'):
            self.actionNewSession.triggered.connect(self._new_session)
        if hasattr(self, 'actionOpenSession'):
            self.actionOpenSession.triggered.connect(self._open_session)
        if hasattr(self, 'actionSaveSession'):
            self.actionSaveSession.triggered.connect(self._save_session)
        if hasattr(self, 'actionLoadData'):
            self.actionLoadData.triggered.connect(self._load_data)
        if hasattr(self, 'actionExportData'):
            self.actionExportData.triggered.connect(self._export_data)
        if hasattr(self, 'actionExit'):
            self.actionExit.triggered.connect(self.close)

        # Edit menu actions
        if hasattr(self, 'actionUndo'):
            self.undo_action = self.actionUndo
            self.actionUndo.triggered.connect(self._undo_operation)
        else:
            self.undo_action = QAction(tr("&Desfazer"), self)
            self.undo_action.setEnabled(False)

        if hasattr(self, 'actionRedo'):
            self.redo_action = self.actionRedo
            self.actionRedo.triggered.connect(self._redo_operation)
        else:
            self.redo_action = QAction(tr("&Refazer"), self)
            self.redo_action.setEnabled(False)

        if hasattr(self, 'actionFindSeries'):
            self.actionFindSeries.triggered.connect(self._find_series)

        # View menu actions
        if hasattr(self, 'actionRefreshData'):
            self.actionRefreshData.triggered.connect(self._refresh_data)
        if hasattr(self, 'actionFullscreen'):
            self.actionFullscreen.triggered.connect(self._toggle_fullscreen)

        # Panel toggles
        if hasattr(self, 'menuPanels'):
            self.menuPanels.addAction(self.data_dock.toggleViewAction())
            self.menuPanels.addAction(self.config_dock.toggleViewAction())
            self.menuPanels.addAction(self.operations_dock.toggleViewAction())
            self.menuPanels.addAction(self.streaming_dock.toggleViewAction())
            self.menuPanels.addAction(self.results_dock.toggleViewAction())

        # Tools menu actions
        if hasattr(self, 'actionSettings'):
            self.actionSettings.triggered.connect(self._show_settings)

        # Help menu actions
        if hasattr(self, 'actionContextualHelp'):
            self.actionContextualHelp.triggered.connect(self._show_contextual_help)
        if hasattr(self, 'actionKeyboardShortcuts'):
            self.actionKeyboardShortcuts.triggered.connect(self._show_keyboard_shortcuts)
        if hasattr(self, 'actionAbout'):
            self.actionAbout.triggered.connect(self._show_about)

        logger.debug("ui_actions_connected")

    def _setup_status_bar_widgets(self):
        """Configura widgets adicionais na status bar"""
        status_bar = self.statusBar()

        self.status_label = QLabel("🟢 Pronto")
        status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)

        self.memory_label = QLabel()
        status_bar.addPermanentWidget(self.memory_label)

    # =========================================================================
    # UI SETUP - PROGRAMÁTICO (FALLBACK)
    # =========================================================================

    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Platform Base v2.0 - Análise de Séries Temporais")
        self.setMinimumSize(1280, 720)
        self.resize(1920, 1080)

        self.setDockNestingEnabled(True)
        self.setTabPosition(Qt.DockWidgetArea.AllDockWidgetAreas,
                           QTabWidget.TabPosition.North)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        logger.debug("main_window_configured")

    def _create_dockable_panels(self):
        """Create dockable panels for different functionalities"""

        # Data Panel (Left)
        self.data_panel = DataPanel(self.session_state, self.signal_hub)
        self.data_dock = QDockWidget(tr("📊 Painel de Dados"), self)
        self.data_dock.setWidget(self.data_panel)
        self.data_dock.setObjectName("DataPanel")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.data_dock)

        # Visualization Panel (Center)
        self.viz_panel = VizPanel(self.session_state, self.signal_hub)
        central_layout = QHBoxLayout()
        central_layout.addWidget(self.viz_panel)
        self.centralWidget().setLayout(central_layout)

        # Config Panel (Right)
        self.config_panel = ConfigPanel(self.session_state, self.signal_hub)
        self.config_dock = QDockWidget(tr("⚙️ Configurações"), self)
        self.config_dock.setWidget(self.config_panel)
        self.config_dock.setObjectName("ConfigPanel")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config_dock)

        # Operations Panel (Right - tabbed with Config)
        from platform_base.ui.panels.operations_panel import OperationsPanel
        self.operations_panel = OperationsPanel(self.session_state)
        self.operations_dock = QDockWidget(tr("⚡ Operações"), self)
        self.operations_dock.setWidget(self.operations_panel)
        self.operations_dock.setObjectName("OperationsPanel")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.operations_dock)

        self.tabifyDockWidget(self.config_dock, self.operations_dock)
        self.config_dock.raise_()

        # Streaming Panel (Bottom)
        from platform_base.ui.panels.streaming_panel import StreamingPanel
        self.streaming_panel = StreamingPanel()
        self.streaming_panel.position_changed.connect(self._on_streaming_position_changed)
        self.streaming_panel.state_changed.connect(self._on_streaming_state_changed)
        self.streaming_dock = QDockWidget(tr("📡 Streaming"), self)
        self.streaming_dock.setWidget(self.streaming_panel)
        self.streaming_dock.setObjectName("StreamingPanel")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.streaming_dock)

        # Results Panel (Bottom)
        self.results_panel = ResultsPanel(self.session_state, self.signal_hub)
        self.results_dock = QDockWidget(tr("📈 Resultados"), self)
        self.results_dock.setWidget(self.results_panel)
        self.results_dock.setObjectName("ResultsPanel")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.results_dock)

        self.tabifyDockWidget(self.streaming_dock, self.results_dock)
        self.streaming_dock.raise_()

        logger.debug("dockable_panels_created")

    def _create_menu_bar(self):
        """Create application menu bar with themes"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu(tr("📁 &Arquivo"))

        new_action = QAction(tr("📄 &Nova Sessão"), self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_session)
        file_menu.addAction(new_action)

        open_action = QAction(tr("📂 &Abrir Sessão..."), self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_session)
        file_menu.addAction(open_action)

        save_action = QAction(tr("💾 &Salvar Sessão..."), self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        load_data_action = QAction(tr("📊 &Carregar Dados..."), self)
        load_data_action.setShortcut(QKeySequence("Ctrl+L"))
        load_data_action.triggered.connect(self._load_data)
        file_menu.addAction(load_data_action)

        export_data_action = QAction(tr("📤 &Exportar Dados..."), self)
        export_data_action.setShortcut(QKeySequence("Ctrl+E"))
        export_data_action.triggered.connect(self._export_data)
        file_menu.addAction(export_data_action)

        file_menu.addSeparator()

        exit_action = QAction(tr("🚪 &Sair"), self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu(tr("✏️ &Editar"))

        self.undo_action = QAction(tr("⏪ &Desfazer"), self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self._undo_operation)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction(tr("⏩ &Refazer"), self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self._redo_operation)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        find_action = QAction(tr("🔍 &Buscar Série..."), self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._find_series)
        edit_menu.addAction(find_action)

        # View Menu
        view_menu = menubar.addMenu(tr("👁️ &Visualizar"))

        # Panel visibility toggles
        panels_menu = view_menu.addMenu(tr("📋 Painéis"))
        panels_menu.addAction(self.data_dock.toggleViewAction())
        panels_menu.addAction(self.config_dock.toggleViewAction())
        panels_menu.addAction(self.operations_dock.toggleViewAction())
        panels_menu.addAction(self.streaming_dock.toggleViewAction())
        panels_menu.addAction(self.results_dock.toggleViewAction())

        view_menu.addSeparator()

        refresh_action = QAction(tr("🔄 &Atualizar Dados"), self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._refresh_data)
        view_menu.addAction(refresh_action)

        fullscreen_action = QAction(tr("📺 &Tela Cheia"), self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Themes Menu
        themes_menu = menubar.addMenu(tr("🎨 &Temas"))

        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

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

            if self._theme_manager.current_mode == theme_map[theme_id]:
                action.setChecked(True)

        themes_menu.addSeparator()

        system_theme_action = QAction(tr("🖥️ Seguir Sistema"), self)
        system_theme_action.setCheckable(True)
        system_theme_action.setData(ThemeMode.SYSTEM)
        system_theme_action.triggered.connect(self._on_theme_action_triggered)
        theme_group.addAction(system_theme_action)
        themes_menu.addAction(system_theme_action)
        self._theme_actions["system"] = system_theme_action

        if self._theme_manager.current_mode == ThemeMode.SYSTEM:
            system_theme_action.setChecked(True)

        # Tools Menu
        tools_menu = menubar.addMenu(tr("🔧 &Ferramentas"))

        settings_action = QAction(tr("⚙️ &Configurações..."), self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # Help Menu
        help_menu = menubar.addMenu(tr("❓ &Ajuda"))

        help_contextual = QAction(tr("📖 Ajuda &Contextual"), self)
        help_contextual.setShortcut(QKeySequence("F1"))
        help_contextual.triggered.connect(self._show_contextual_help)
        help_menu.addAction(help_contextual)

        shortcuts_action = QAction(tr("⌨️ &Atalhos de Teclado"), self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+?"))
        shortcuts_action.triggered.connect(self._show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        about_action = QAction(tr("ℹ️ &Sobre..."), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        logger.debug("menu_bar_created")

    def _create_tool_bar(self):
        """Create main toolbar"""
        toolbar = QToolBar(tr("Ferramentas"), self)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        load_action = QAction("📊", self)
        load_action.setText(tr("Carregar"))
        load_action.setToolTip(tr("Carregar dados (Ctrl+L)"))
        load_action.triggered.connect(self._load_data)
        toolbar.addAction(load_action)

        toolbar.addSeparator()

        new_action = QAction("📄", self)
        new_action.setText(tr("Novo"))
        new_action.setToolTip(tr("Nova sessão (Ctrl+N)"))
        new_action.triggered.connect(self._new_session)
        toolbar.addAction(new_action)

        save_action = QAction("💾", self)
        save_action.setText(tr("Salvar"))
        save_action.setToolTip(tr("Salvar sessão (Ctrl+S)"))
        save_action.triggered.connect(self._save_session)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        export_action = QAction("📤", self)
        export_action.setText(tr("Exportar"))
        export_action.setToolTip(tr("Exportar dados (Ctrl+E)"))
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        settings_action = QAction("⚙️", self)
        settings_action.setText(tr("Config"))
        settings_action.setToolTip(tr("Configurações"))
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

        logger.debug("tool_bar_created")

    def _create_status_bar(self):
        """Create status bar"""
        status_bar = self.statusBar()

        self.status_label = QLabel("🟢 Pronto")
        status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)

        self.memory_label = QLabel()
        status_bar.addPermanentWidget(self.memory_label)

        logger.debug("status_bar_created")

    # =========================================================================
    # KEYBOARD SHORTCUTS
    # =========================================================================

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Delete key
        delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        delete_shortcut.activated.connect(self._delete_selected_series)
        delete_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Escape - Cancel
        escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        escape_shortcut.activated.connect(self._cancel_operation)
        escape_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Ctrl+W - Close view
        close_tab_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
        close_tab_shortcut.activated.connect(self._close_current_view)
        close_tab_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Ctrl+Tab - Next tab
        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut.activated.connect(self._next_view)
        next_tab_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Ctrl+Shift+Tab - Previous tab
        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut.activated.connect(self._previous_view)
        prev_tab_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        logger.debug("keyboard_shortcuts_configured")

    # =========================================================================
    # SIGNALS CONNECTION
    # =========================================================================

    def _connect_signals(self):
        """Connect signals from session state and signal hub"""

        # Session state signals
        self.session_state.selection_changed.connect(self._on_selection_changed)
        self.session_state.ui_state_changed.connect(self._on_ui_state_changed)

        # Signal hub signals
        self.signal_hub.operation_started.connect(self._on_operation_started)
        self.signal_hub.operation_progress.connect(self._on_operation_progress)
        self.signal_hub.operation_completed.connect(self._on_operation_completed)
        self.signal_hub.operation_failed.connect(self._on_operation_failed)
        self.signal_hub.error_occurred.connect(self._on_error_occurred)
        self.signal_hub.status_updated.connect(self._on_status_updated)

        # Operations panel signals
        if self.operations_panel:
            self.operations_panel.operation_requested.connect(self._handle_operation_request)
            self.operations_panel.export_requested.connect(self._handle_export_request)
            if hasattr(self.operations_panel, 'streaming_data_updated'):
                self.operations_panel.streaming_data_updated.connect(self._on_streaming_data_updated)

        # Undo/redo manager signals
        self.undo_manager.can_undo_changed.connect(self.undo_action.setEnabled)
        self.undo_manager.can_redo_changed.connect(self.redo_action.setEnabled)
        self.undo_manager.undo_text_changed.connect(
            lambda text: self.undo_action.setText(f"⏪ Desfazer {text}" if text else "⏪ Desfazer")
        )
        self.undo_manager.redo_text_changed.connect(
            lambda text: self.redo_action.setText(f"⏩ Refazer {text}" if text else "⏩ Refazer")
        )

        logger.debug("signals_connected")

    # =========================================================================
    # SLOT IMPLEMENTATIONS - FILE OPERATIONS
    # =========================================================================

    @pyqtSlot()
    def _new_session(self):
        """Create new session"""
        reply = QMessageBox.question(
            self, tr("📄 Nova Sessão"),
            tr("Criar nova sessão? A sessão atual será perdida se não salva."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.session_state.clear_session()
            self.status_label.setText("📄 Nova sessão criada")
            logger.info("new_session_created")

    @pyqtSlot()
    def _open_session(self):
        """Open session from file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("📂 Abrir Sessão"), "",
            tr("Arquivos de Sessão (*.json);;Todos os Arquivos (*)"),
        )

        if filepath:
            if self.session_state.load_session(filepath):
                self.status_label.setText(f"✅ Sessão carregada: {Path(filepath).name}")
                logger.info("session_opened", filepath=filepath)
            else:
                QMessageBox.warning(self, tr("Erro"), tr("Falha ao carregar arquivo de sessão."))

    @pyqtSlot()
    def _save_session(self):
        """Save session to file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr("💾 Salvar Sessão"), "",
            tr("Arquivos de Sessão (*.json);;Todos os Arquivos (*)"),
        )

        if filepath:
            if self.session_state.save_session(filepath):
                self.status_label.setText(f"✅ Sessão salva: {Path(filepath).name}")
                logger.info("session_saved", filepath=filepath)
            else:
                QMessageBox.warning(self, tr("Erro"), tr("Falha ao salvar arquivo de sessão."))

    @pyqtSlot()
    def _load_data(self):
        """Open load data dialog"""
        try:
            dialog = UploadDialog(self.session_state, self.signal_hub, self)
            dialog.exec()
        except Exception as e:
            logger.exception("load_data_dialog_failed", error=str(e))
            QMessageBox.critical(self, tr("Erro"), f"Falha ao abrir diálogo:\n{e}")

    @pyqtSlot()
    def _export_data(self):
        """Export data to file"""
        dataset_id = None
        series_ids = None

        if hasattr(self.data_panel, 'get_selected_dataset_id'):
            dataset_id = self.data_panel.get_selected_dataset_id()
        if hasattr(self.data_panel, 'get_selected_series_ids'):
            series_ids = self.data_panel.get_selected_series_ids()

        if not dataset_id:
            QMessageBox.warning(self, tr("Aviso"), tr("Selecione um dataset para exportar."))
            return

        file_filters = (
            "CSV (*.csv);;Excel (*.xlsx);;Parquet (*.parquet);;HDF5 (*.h5 *.hdf5);;Todos (*.*)"
        )

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, tr("📤 Exportar Dados"), "", file_filters
        )

        if not file_path:
            return

        # Determine format
        if "CSV" in selected_filter or file_path.endswith('.csv'):
            format_type = "csv"
        elif "Excel" in selected_filter or file_path.endswith('.xlsx'):
            format_type = "xlsx"
        elif "Parquet" in selected_filter or file_path.endswith('.parquet'):
            format_type = "parquet"
        elif "HDF5" in selected_filter or file_path.endswith(('.h5', '.hdf5')):
            format_type = "hdf5"
        else:
            format_type = "csv"

        self.status_label.setText(f"📤 Exportando para {format_type}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        try:
            from platform_base.desktop.workers.export_worker import DataExportWorker

            export_config = {
                'delimiter': ',',
                'encoding': 'utf-8',
                'include_metadata': True,
            }

            self._export_worker = DataExportWorker(
                dataset_store=self.session_state.dataset_store,
                dataset_id=dataset_id,
                series_ids=series_ids,
                output_path=file_path,
                format_type=format_type,
                export_config=export_config
            )

            self._export_worker.progress.connect(lambda p, m: (
                self.progress_bar.setValue(p),
                self.status_label.setText(m)
            ))
            self._export_worker.error.connect(lambda e: (
                QMessageBox.critical(self, tr("Erro"), str(e)),
                self.progress_bar.setVisible(False)
            ))
            self._export_worker.finished.connect(lambda: (
                self.progress_bar.setVisible(False),
                self.status_label.setText("✅ Exportação concluída"),
                QMessageBox.information(self, tr("Sucesso"), f"Dados exportados para:\n{file_path}")
            ))

            self._export_worker.start()
            logger.info("export_started", path=file_path, format=format_type)

        except Exception as e:
            logger.exception("export_failed", error=str(e))
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, tr("Erro"), f"Falha na exportação:\n{e}")

    # =========================================================================
    # SLOT IMPLEMENTATIONS - EDIT OPERATIONS
    # =========================================================================

    @pyqtSlot()
    def _undo_operation(self):
        """Undo last operation"""
        if self.undo_manager.can_undo():
            undo_text = self.undo_manager.undo_text()
            self.undo_manager.undo()
            self.status_label.setText(f"⏪ Desfeito: {undo_text}")
            logger.info("undo_executed", operation=undo_text)
        else:
            self.status_label.setText("⚠️ Nada para desfazer")

    @pyqtSlot()
    def _redo_operation(self):
        """Redo last undone operation"""
        if self.undo_manager.can_redo():
            redo_text = self.undo_manager.redo_text()
            self.undo_manager.redo()
            self.status_label.setText(f"⏩ Refeito: {redo_text}")
            logger.info("redo_executed", operation=redo_text)
        else:
            self.status_label.setText("⚠️ Nada para refazer")

    @pyqtSlot()
    def _find_series(self):
        """Find/filter series"""
        if hasattr(self.data_panel, "_search_edit"):
            self.data_panel._search_edit.setFocus()
            self.data_panel._search_edit.selectAll()
            return

        if hasattr(self, 'data_dock'):
            self.data_dock.raise_()
            self.data_dock.setFocus()

        from PyQt6.QtWidgets import QInputDialog
        search_text, ok = QInputDialog.getText(
            self, tr("🔍 Buscar Série"),
            tr("Nome da série:")
        )

        if ok and search_text:
            if hasattr(self.data_panel, "filter_series"):
                self.data_panel.filter_series(search_text)
            self.status_label.setText(f"🔍 Buscando: '{search_text}'")

    # =========================================================================
    # SLOT IMPLEMENTATIONS - VIEW OPERATIONS
    # =========================================================================

    @pyqtSlot()
    def _refresh_data(self):
        """Refresh data"""
        self.status_label.setText("🔄 Atualizando...")
        if hasattr(self.viz_panel, 'refresh'):
            self.viz_panel.refresh()
        if hasattr(self.signal_hub, 'data_changed'):
            self.signal_hub.data_changed.emit()
        self.status_label.setText("✅ Dados atualizados")
        logger.info("data_refreshed")

    @pyqtSlot()
    def _toggle_fullscreen(self):
        """Toggle fullscreen"""
        if self.isFullScreen():
            self.showNormal()
            self.status_label.setText("📐 Modo normal")
        else:
            self.showFullScreen()
            self.status_label.setText("📺 Tela cheia (F11 para sair)")

    @pyqtSlot()
    def _delete_selected_series(self):
        """Delete selected series"""
        if hasattr(self.data_panel, "delete_selected"):
            self.data_panel.delete_selected()
        else:
            QMessageBox.information(
                self, tr("Remover Série"),
                tr("Selecione uma série no Painel de Dados e pressione Delete.")
            )

    @pyqtSlot()
    def _cancel_operation(self):
        """Cancel current operation"""
        self.status_label.setText("⛔ Operação cancelada")
        self.progress_bar.setVisible(False)
        if hasattr(self.signal_hub, "operation_cancelled"):
            self.signal_hub.operation_cancelled.emit()

    @pyqtSlot()
    def _close_current_view(self):
        """Close current view"""
        if hasattr(self.viz_panel, "close_current_view"):
            self.viz_panel.close_current_view()

    @pyqtSlot()
    def _next_view(self):
        """Next view"""
        if hasattr(self.viz_panel, "next_view"):
            self.viz_panel.next_view()

    @pyqtSlot()
    def _previous_view(self):
        """Previous view"""
        if hasattr(self.viz_panel, "previous_view"):
            self.viz_panel.previous_view()

    # =========================================================================
    # SLOT IMPLEMENTATIONS - DIALOGS
    # =========================================================================

    @pyqtSlot()
    def _show_settings(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self.session_state, self)
            dialog.exec()
        except Exception as e:
            logger.exception("settings_dialog_failed", error=str(e))
            QMessageBox.information(self, tr("Configurações"), tr("Painel em desenvolvimento"))

    @pyqtSlot()
    def _show_about(self):
        """Show about dialog"""
        try:
            dialog = AboutDialog(self)
            dialog.exec()
        except Exception as e:
            logger.exception("about_dialog_failed", error=str(e))
            QMessageBox.about(
                self, tr("Sobre"),
                """
                <h3>🚀 Platform Base v2.0</h3>
                <p><b>Análise de Séries Temporais</b></p>
                <p>TRANSPETRO</p>
                """
            )

    @pyqtSlot()
    def _show_contextual_help(self):
        """Show contextual help"""
        QMessageBox.information(
            self, tr("Ajuda"),
            tr("""
            <h3>Platform Base v2.0</h3>
            <p>Use F1 em qualquer painel para ajuda contextual.</p>
            <h4>Atalhos principais:</h4>
            <ul>
            <li><b>Ctrl+L:</b> Carregar dados</li>
            <li><b>Ctrl+S:</b> Salvar sessão</li>
            <li><b>Ctrl+Z/Y:</b> Desfazer/Refazer</li>
            <li><b>F5:</b> Atualizar</li>
            <li><b>F11:</b> Tela cheia</li>
            </ul>
            """)
        )

    @pyqtSlot()
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        <h2>⌨️ Atalhos de Teclado</h2>
        
        <h3>Arquivo</h3>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>Nova Sessão</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Abrir Sessão</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Salvar Sessão</td></tr>
        <tr><td><b>Ctrl+L</b></td><td>Carregar Dados</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Exportar Dados</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Sair</td></tr>
        </table>
        
        <h3>Editar</h3>
        <table>
        <tr><td><b>Ctrl+Z</b></td><td>Desfazer</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Refazer</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Buscar Série</td></tr>
        <tr><td><b>Delete</b></td><td>Remover Seleção</td></tr>
        </table>
        
        <h3>Visualizar</h3>
        <table>
        <tr><td><b>F5</b></td><td>Atualizar</td></tr>
        <tr><td><b>F11</b></td><td>Tela Cheia</td></tr>
        <tr><td><b>Ctrl+Tab</b></td><td>Próxima Aba</td></tr>
        <tr><td><b>Ctrl+Shift+Tab</b></td><td>Aba Anterior</td></tr>
        </table>
        
        <h3>Ajuda</h3>
        <table>
        <tr><td><b>F1</b></td><td>Ajuda Contextual</td></tr>
        <tr><td><b>Esc</b></td><td>Cancelar Operação</td></tr>
        </table>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("⌨️ Atalhos de Teclado"))
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(shortcuts_text)
        msg.exec()

    # =========================================================================
    # SIGNAL HUB HANDLERS
    # =========================================================================

    @pyqtSlot(str, str)
    def _on_operation_started(self, operation_type: str, operation_id: str):
        """Handle operation started"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"⚡ Executando {operation_type}...")

        # Start appropriate worker
        selection = self.session_state.selection
        if not selection.dataset_id or not selection.series_ids:
            self.status_label.setText("⚠️ Nenhum dado selecionado")
            self.progress_bar.setVisible(False)
            return

        dataset_id = selection.dataset_id
        series_id = selection.series_ids[0] if selection.series_ids else None

        processing_state = self.session_state.processing
        operation_info = processing_state.active_operations.get(operation_id, {})
        params = operation_info.get("parameters", {})

        try:
            if operation_type == "interpolation":
                method = params.get("method", "linear")
                self.processing_manager.start_interpolation(
                    operation_id, dataset_id, series_id, method, params
                )
            elif operation_type == "calculus":
                operation = params.get("operation", "derivative_1st")
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, operation, params
                )
            elif operation_type == "synchronization":
                series_ids = list(selection.series_ids)
                method = params.get("method", "dtw")
                self.processing_manager.start_synchronization(
                    operation_id, dataset_id, series_ids, method, params
                )
            elif operation_type in ("derivative", "derivative_1st", "derivative_2nd", "derivative_3rd"):
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, operation_type, params
                )
            elif operation_type == "integral":
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, "integral", params
                )
            elif operation_type in ("smoothing", "remove_outliers"):
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, operation_type, params
                )
            else:
                logger.warning("unknown_operation_type", operation_type=operation_type)
                self.status_label.setText(f"⚠️ Operação desconhecida: {operation_type}")
                self.progress_bar.setVisible(False)

        except Exception as e:
            logger.exception("operation_start_failed", error=str(e))
            self.status_label.setText(f"❌ Falha: {e}")
            self.progress_bar.setVisible(False)
            self.signal_hub.operation_failed.emit(operation_id, str(e))

    @pyqtSlot(str, int)
    def _on_operation_progress(self, operation_id: str, progress: int):
        """Handle operation progress"""
        self.progress_bar.setValue(progress)

    @pyqtSlot(str, object)
    def _on_operation_completed(self, operation_id: str, result):
        """Handle operation completed"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ Operação concluída")

        self.results_dock.show()
        self.results_dock.raise_()

        if isinstance(result, dict):
            series_id = result.get("series_id")
            if hasattr(self.results_panel, "add_result"):
                self.results_panel.add_result(operation_id, result)
            if series_id and hasattr(self.data_panel, "refresh_data"):
                self.data_panel.refresh_data()

    @pyqtSlot(str, str)
    def _on_operation_failed(self, operation_id: str, error_message: str):
        """Handle operation failed"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Operação falhou")
        QMessageBox.warning(self, tr("Erro"), f"Operação {operation_id} falhou:\n{error_message}")

    @pyqtSlot(str, str)
    def _on_error_occurred(self, error_type: str, error_message: str):
        """Handle general errors"""
        logger.error("ui_error", error_type=error_type, message=error_message)
        QMessageBox.critical(self, error_type, error_message)

    @pyqtSlot(str)
    def _on_status_updated(self, message: str):
        """Handle status updates"""
        self.status_label.setText(message)

    def _on_selection_changed(self):
        """Handle selection changes"""
        selection_state = self.session_state.selection
        dataset_id = selection_state.dataset_id
        n_series = len(selection_state.series_ids)

        if dataset_id:
            self.status_label.setText(f"📊 Dataset: {dataset_id} | Séries: {n_series}")
        else:
            self.status_label.setText("📊 Nenhum dado selecionado")

    @pyqtSlot(object)
    def _on_ui_state_changed(self, ui_state):
        """Handle UI state changes"""
        for panel, visible in ui_state.panel_visibility.items():
            if panel == "data":
                self.data_dock.setVisible(visible)
            elif panel == "results":
                self.results_dock.setVisible(visible)

    @pyqtSlot(str, dict)
    def _handle_operation_request(self, operation_name: str, params: dict):
        """Handle operation request from OperationsPanel"""
        logger.info("operation_requested", operation=operation_name, params=params)

        selection = self.session_state.get_selected_series()
        if not selection:
            QMessageBox.warning(
                self, tr("Aviso"),
                tr("Selecione uma série antes de realizar esta operação.")
            )
            return

        try:
            dataset_id = selection[0].dataset_id if hasattr(selection[0], 'dataset_id') else None
            series_id = selection[0].series_id if hasattr(selection[0], 'series_id') else None

            if not dataset_id or not series_id:
                QMessageBox.warning(self, tr("Aviso"), tr("Seleção inválida."))
                return

            self.processing_manager.start_operation(
                operation_type=operation_name,
                dataset_id=dataset_id,
                series_id=series_id,
                params=params
            )

            self.status_label.setText(f"⚡ Processando: {operation_name}...")
            self.progress_bar.setVisible(True)
            self.results_dock.raise_()

        except Exception as e:
            logger.exception("operation_request_failed", error=str(e))
            QMessageBox.critical(self, tr("Erro"), f"Falha: {e}")

    @pyqtSlot(str, dict)
    def _handle_export_request(self, format_type: str, options: dict):
        """Handle export request"""
        logger.info("export_requested", format=format_type, options=options)

        file_filters = {
            'csv': "CSV (*.csv)",
            'excel': "Excel (*.xlsx)",
            'parquet': "Parquet (*.parquet)",
            'hdf5': "HDF5 (*.h5 *.hdf5)",
            'json': "JSON (*.json)",
        }

        file_filter = file_filters.get(format_type, "Todos (*.*)")

        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Exportar como {format_type.upper()}", "", file_filter
        )

        if file_path:
            self.status_label.setText(f"📤 Exportando para {format_type}...")

    @pyqtSlot(str, object, object)
    def _on_streaming_data_updated(self, series_id: str, x_data, y_data):
        """Handle streaming data update"""
        try:
            if hasattr(self.viz_panel, 'update_streaming_data'):
                self.viz_panel.update_streaming_data(series_id, x_data, y_data)
        except Exception as e:
            logger.exception("streaming_update_failed", error=str(e))

    # =========================================================================
    # STREAMING HANDLERS
    # =========================================================================

    @pyqtSlot(int)
    def _on_streaming_position_changed(self, position: int):
        """Handle streaming position changes"""
        try:
            selection = self.session_state.selection
            if selection.dataset_id:
                dataset = self.session_state.dataset_store.get_dataset(selection.dataset_id)
                total_points = len(dataset.t_seconds)

                if total_points > 0:
                    time_position = dataset.t_seconds[min(position, total_points - 1)]
                    if hasattr(self.signal_hub, 'streaming_time_changed'):
                        self.signal_hub.streaming_time_changed.emit(time_position)

            self.status_label.setText(f"📡 Posição: {position}")
        except Exception as e:
            logger.exception("streaming_position_failed", error=str(e))

    @pyqtSlot(object)
    def _on_streaming_state_changed(self, state):
        """Handle streaming state changes"""
        from platform_base.ui.panels.streaming_panel import PlaybackState

        if state == PlaybackState.PLAYING:
            if hasattr(self.signal_hub, 'streaming_started'):
                self.signal_hub.streaming_started.emit()
            self.status_label.setText("▶️ Streaming: Reproduzindo")
        elif state == PlaybackState.PAUSED:
            if hasattr(self.signal_hub, 'streaming_paused'):
                self.signal_hub.streaming_paused.emit()
            self.status_label.setText("⏸️ Streaming: Pausado")
        elif state == PlaybackState.STOPPED:
            if hasattr(self.signal_hub, 'streaming_stopped'):
                self.signal_hub.streaming_stopped.emit()
            self.status_label.setText("⏹️ Streaming: Parado")

    # =========================================================================
    # THEME MANAGEMENT
    # =========================================================================

    def _on_theme_action_triggered(self):
        """Handle theme menu action"""
        action = self.sender()
        if action and action.data():
            theme_mode = action.data()
            self._theme_manager.set_theme(theme_mode)

            theme_names = {
                ThemeMode.LIGHT: "☀️ Clássico",
                ThemeMode.DARK: "🌙 Noturno",
                ThemeMode.OCEAN: "🌊 Oceano",
                ThemeMode.FOREST: "🌲 Floresta",
                ThemeMode.SUNSET: "🌅 Pôr do Sol",
                ThemeMode.SYSTEM: "🖥️ Sistema",
            }
            self.status_label.setText(f"🎨 Tema: {theme_names.get(theme_mode, 'Desconhecido')}")
            logger.info("theme_changed", theme=theme_mode.name)

    def _on_theme_changed(self, mode: ThemeMode):
        """Handle theme changed signal"""
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

    # =========================================================================
    # LAYOUT PERSISTENCE
    # =========================================================================

    def _save_layout(self):
        """Save layout to QSettings"""
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        settings.setValue("mainwindow/geometry", self.saveGeometry())
        settings.setValue("mainwindow/state", self.saveState())
        settings.setValue("mainwindow/maximized", self.isMaximized())
        settings.setValue("mainwindow/fullscreen", self.isFullScreen())
        settings.sync()
        logger.debug("layout_saved")

    def _restore_layout(self):
        """Restore layout from QSettings"""
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)

        geometry = settings.value("mainwindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = settings.value("mainwindow/state")
        if state:
            self.restoreState(state)

        was_maximized = settings.value("mainwindow/maximized", False, type=bool)
        was_fullscreen = settings.value("mainwindow/fullscreen", False, type=bool)

        if was_fullscreen:
            self.showFullScreen()
        elif was_maximized:
            self.showMaximized()

        logger.debug("layout_restored")

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _update_memory_usage(self):
        """Update memory usage display"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.setText(f"💾 {memory_mb:.1f} MB")
        except ImportError:
            self.memory_label.setText("")

    def _auto_save_session(self):
        """Auto-save session periodically"""
        try:
            autosave_dir = Path.home() / ".platform_base" / "autosave"
            autosave_dir.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = autosave_dir / f"autosave_{timestamp}.json"

            self.session_state.save_session(str(filepath))

            # Keep last 5 auto-saves
            autosave_files = sorted(autosave_dir.glob("autosave_*.json"))
            for old_file in autosave_files[:-5]:
                old_file.unlink()

            logger.debug("session_auto_saved", filepath=str(filepath))

        except Exception as e:
            logger.warning("auto_save_failed", error=str(e))

    def save_session_on_exit(self):
        """Save session when application exits"""
        try:
            self._auto_save_session()
            self._save_layout()
            logger.info("session_saved_on_exit")
        except Exception as e:
            logger.exception("exit_save_failed", error=str(e))

    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, tr("🚪 Fechar Aplicação"),
            tr("Salvar sessão antes de sair?"),
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

        self._save_layout()
        self._auto_save_timer.stop()
        self._memory_timer.stop()

        logger.info("application_closing")
        event.accept()


# Alias para compatibilidade
MainWindow = ModernMainWindow
