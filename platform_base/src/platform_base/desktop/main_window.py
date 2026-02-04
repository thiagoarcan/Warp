"""
MainWindow - Main PyQt6 desktop window for Platform Base v2.0

Implements the main application window with dockable panels layout.
Replaces Dash web interface with native desktop interface.

Interface carregada do arquivo mainWindow.ui via UiLoaderMixin.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSettings, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
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
from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class MainWindow(QMainWindow, UiLoaderMixin):
    """
    Main application window.

    Features:
    - Dockable panel layout (Data, Visualization, Configuration, Results)
    - Menu bar with standard actions
    - Tool bar for quick access
    - Status bar with progress indication
    - Auto-save session state
    - Keyboard shortcuts
    
    Interface carregada do arquivo mainWindow.ui.
    """
    
    # Arquivo .ui que define a interface base
    UI_FILE = "mainWindow.ui"

    def __init__(self, session_state: SessionState, signal_hub: SignalHub):
        super().__init__()

        self.session_state = session_state
        self.signal_hub = signal_hub

        # Initialize undo/redo manager (lazy import to avoid loading matplotlib at startup)
        from platform_base.ui.undo_redo import get_undo_manager
        self.undo_manager = get_undo_manager()

        # Initialize processing worker manager
        from platform_base.desktop.workers.processing_worker import (
            ProcessingWorkerManager,
        )
        self.processing_manager = ProcessingWorkerManager(
            session_state.dataset_store, signal_hub
        )

        # Carregar interface do arquivo .ui
        if self._load_ui():
            # Configurar UI carregada do .ui
            self._setup_ui_from_file()
        else:
            # Fallback para criação programática
            logger.warning("ui_load_failed_using_fallback", cls="MainWindow")
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

        logger.info("main_window_initialized")

    def _setup_ui_from_file(self):
        """Configura a UI carregada do arquivo .ui"""
        # Inserir painéis reais nos placeholders do .ui
        self._insert_panels_into_placeholders()
        
        # Conectar actions do .ui aos métodos
        self._connect_ui_actions()
        
        # Configurar status bar
        self._setup_status_bar_widgets()
        
        logger.debug("main_window_ui_from_file_configured")
    
    def _insert_panels_into_placeholders(self):
        """Insere os painéis reais nos placeholders definidos no .ui"""
        
        # Data Panel - placeholder: dataPanelPlaceholder no dataDock
        self.data_panel = DataPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'dataDock') and hasattr(self, 'dataPanelPlaceholder'):
            layout = QVBoxLayout(self.dataPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.data_panel)
            self.data_dock = self.dataDock
        else:
            # Criar dock programaticamente se não existir no .ui
            self.data_dock = QDockWidget(tr("Data Panel"), self)
            self.data_dock.setWidget(self.data_panel)
            self.data_dock.setObjectName("DataPanel")
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.data_dock)
        
        # Visualization Panel - placeholder: vizPanelPlaceholder no centralWidget
        self.viz_panel = VizPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'vizPanelPlaceholder'):
            layout = QVBoxLayout(self.vizPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.viz_panel)
        else:
            # Fallback: adicionar ao central widget
            central_layout = QHBoxLayout()
            central_layout.addWidget(self.viz_panel)
            self.centralWidget().setLayout(central_layout)
        
        # Config Panel - placeholder: configPanelPlaceholder no configDock
        self.config_panel = ConfigPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'configDock') and hasattr(self, 'configPanelPlaceholder'):
            layout = QVBoxLayout(self.configPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.config_panel)
            self.config_dock = self.configDock
        else:
            self.config_dock = QDockWidget(tr("Configuration Panel"), self)
            self.config_dock.setWidget(self.config_panel)
            self.config_dock.setObjectName("ConfigPanel")
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config_dock)
        
        # Operations Panel - placeholder: operationsPanelPlaceholder no operationsDock
        from platform_base.ui.panels.operations_panel import OperationsPanel
        self.operations_panel = OperationsPanel(self.session_state)
        if hasattr(self, 'operationsDock') and hasattr(self, 'operationsPanelPlaceholder'):
            layout = QVBoxLayout(self.operationsPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.operations_panel)
            self.operations_dock = self.operationsDock
        else:
            self.operations_dock = QDockWidget(tr("Operations Panel"), self)
            self.operations_dock.setWidget(self.operations_panel)
            self.operations_dock.setObjectName("OperationsPanel")
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.operations_dock)
        
        # Tabify config e operations
        self.tabifyDockWidget(self.config_dock, self.operations_dock)
        self.config_dock.raise_()
        
        # Streaming Panel - placeholder: streamingPanelPlaceholder no streamingDock
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
            self.streaming_dock = QDockWidget(tr("Streaming Controls"), self)
            self.streaming_dock.setWidget(self.streaming_panel)
            self.streaming_dock.setObjectName("StreamingPanel")
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.streaming_dock)
        
        # Results Panel - placeholder: resultsPanelPlaceholder no resultsDock
        self.results_panel = ResultsPanel(self.session_state, self.signal_hub)
        if hasattr(self, 'resultsDock') and hasattr(self, 'resultsPanelPlaceholder'):
            layout = QVBoxLayout(self.resultsPanelPlaceholder)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.results_panel)
            self.results_dock = self.resultsDock
        else:
            self.results_dock = QDockWidget(tr("Results Panel"), self)
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
            self.undo_action = QAction(tr("&Undo"), self)
            self.undo_action.setEnabled(False)
        
        if hasattr(self, 'actionRedo'):
            self.redo_action = self.actionRedo
            self.actionRedo.triggered.connect(self._redo_operation)
        else:
            self.redo_action = QAction(tr("&Redo"), self)
            self.redo_action.setEnabled(False)
        
        if hasattr(self, 'actionFindSeries'):
            self.actionFindSeries.triggered.connect(self._find_series)
        
        # View menu actions
        if hasattr(self, 'actionRefreshData'):
            self.actionRefreshData.triggered.connect(self._refresh_data)
        if hasattr(self, 'actionFullscreen'):
            self.actionFullscreen.triggered.connect(self._toggle_fullscreen)
        if hasattr(self, 'actionThemeLight'):
            self.actionThemeLight.triggered.connect(lambda: self._set_theme("light"))
        if hasattr(self, 'actionThemeDark'):
            self.actionThemeDark.triggered.connect(lambda: self._set_theme("dark"))
        if hasattr(self, 'actionThemeAuto'):
            self.actionThemeAuto.triggered.connect(lambda: self._set_theme("auto"))
        
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
        
        # Adicionar toggle actions dos painéis ao menu View/Panels
        if hasattr(self, 'menuPanels'):
            self.menuPanels.addAction(self.data_dock.toggleViewAction())
            self.menuPanels.addAction(self.config_dock.toggleViewAction())
            self.menuPanels.addAction(self.operations_dock.toggleViewAction())
            self.menuPanels.addAction(self.streaming_dock.toggleViewAction())
            self.menuPanels.addAction(self.results_dock.toggleViewAction())
        
        logger.debug("ui_actions_connected")
    
    def _setup_status_bar_widgets(self):
        """Configura widgets adicionais na status bar"""
        # statusBar pode ser um atributo (do .ui) ou um método (fallback)
        if hasattr(self, 'statusBar') and isinstance(self.statusBar, QWidget):
            status_bar = self.statusBar
        else:
            status_bar = super().statusBar()
        
        # Status label
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Memory usage label
        self.memory_label = QLabel()
        status_bar.addPermanentWidget(self.memory_label)
        
        # Update memory usage periodically
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self._update_memory_usage)
        self.memory_timer.start(5000)

    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Platform Base v2.0 - Time Series Analysis")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        # Set window properties
        self.setDockNestingEnabled(True)
        self.setTabPosition(Qt.DockWidgetArea.AllDockWidgetAreas,
                           QTabWidget.TabPosition.North)

        # Create central widget (will hold main visualization)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        logger.debug("main_window_configured")

    def _create_dockable_panels(self):
        """Create dockable panels for different functionalities"""

        # Data Management Panel (Left)
        self.data_panel = DataPanel(self.session_state, self.signal_hub)
        self.data_dock = QDockWidget(tr("Data Panel"), self)
        self.data_dock.setWidget(self.data_panel)
        self.data_dock.setObjectName("DataPanel")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.data_dock)

        # Visualization Panel (Center - in central widget)
        self.viz_panel = VizPanel(self.session_state, self.signal_hub)
        central_layout = QHBoxLayout()
        central_layout.addWidget(self.viz_panel)
        self.centralWidget().setLayout(central_layout)

        # Configuration Panel (Right)
        self.config_panel = ConfigPanel(self.session_state, self.signal_hub)
        self.config_dock = QDockWidget(tr("Configuration Panel"), self)
        self.config_dock.setWidget(self.config_panel)
        self.config_dock.setObjectName("ConfigPanel")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config_dock)

        # Operations Panel (Right - tabbed with Config) - lazy import to avoid matplotlib at startup
        from platform_base.ui.panels.operations_panel import OperationsPanel
        self.operations_panel = OperationsPanel(self.session_state)
        self.operations_dock = QDockWidget(tr("Operations Panel"), self)
        self.operations_dock.setWidget(self.operations_panel)
        self.operations_dock.setObjectName("OperationsPanel")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.operations_dock)

        # Tabify operations with config panel
        self.tabifyDockWidget(self.config_dock, self.operations_dock)
        self.config_dock.raise_()  # Show config panel by default

        # Streaming Panel (Bottom - for playback controls)
        from platform_base.ui.panels.streaming_panel import StreamingPanel
        self.streaming_panel = StreamingPanel()
        self.streaming_panel.position_changed.connect(self._on_streaming_position_changed)
        self.streaming_panel.state_changed.connect(self._on_streaming_state_changed)
        self.streaming_dock = QDockWidget(tr("Streaming Controls"), self)
        self.streaming_dock.setWidget(self.streaming_panel)
        self.streaming_dock.setObjectName("StreamingPanel")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.streaming_dock)

        # Results Panel (Bottom)
        self.results_panel = ResultsPanel(self.session_state, self.signal_hub)
        self.results_dock = QDockWidget(tr("Results Panel"), self)
        self.results_dock.setWidget(self.results_panel)
        self.results_dock.setObjectName("ResultsPanel")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.results_dock)

        # Stack operations panel below config panel
        self.splitDockWidget(self.config_dock, self.operations_dock, Qt.Orientation.Vertical)

        # Tabify bottom panels
        self.tabifyDockWidget(self.streaming_dock, self.results_dock)

        # Initially show streaming panel
        self.streaming_dock.raise_()

        logger.debug("dockable_panels_created")

    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu(tr("&File"))

        # New Session
        new_action = QAction(tr("&New Session"), self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip(tr("Create a new session (Ctrl+N)"))
        new_action.triggered.connect(self._new_session)
        file_menu.addAction(new_action)

        # Open Session
        open_action = QAction(tr("&Open Session..."), self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip(tr("Open an existing session (Ctrl+O)"))
        open_action.triggered.connect(self._open_session)
        file_menu.addAction(open_action)

        # Save Session
        save_action = QAction(tr("&Save Session..."), self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip(tr("Save current session (Ctrl+S)"))
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # Load Data
        load_data_action = QAction(tr("&Load Data..."), self)
        load_data_action.setShortcut(QKeySequence("Ctrl+L"))
        load_data_action.setStatusTip(tr("Load data from file (Ctrl+L)"))
        load_data_action.triggered.connect(self._load_data)
        file_menu.addAction(load_data_action)

        # Export Data
        export_data_action = QAction(tr("&Export Data..."), self)
        export_data_action.setShortcut(QKeySequence("Ctrl+E"))
        export_data_action.setStatusTip(tr("Export data to file (Ctrl+E)"))
        export_data_action.triggered.connect(self._export_data)
        file_menu.addAction(export_data_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction(tr("E&xit"), self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip(tr("Exit application (Ctrl+Q)"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu(tr("&Edit"))

        # Undo
        self.undo_action = QAction(tr("&Undo"), self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setStatusTip(tr("Undo last operation (Ctrl+Z)"))
        self.undo_action.setEnabled(False)  # Enabled when undo stack implemented
        self.undo_action.triggered.connect(self._undo_operation)
        edit_menu.addAction(self.undo_action)

        # Redo
        self.redo_action = QAction(tr("&Redo"), self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setStatusTip(tr("Redo last undone operation (Ctrl+Y)"))
        self.redo_action.setEnabled(False)  # Enabled when undo stack implemented
        self.redo_action.triggered.connect(self._redo_operation)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        # Find/Filter Series
        find_action = QAction(tr("&Find Series..."), self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.setStatusTip(tr("Find/filter series (Ctrl+F)"))
        find_action.triggered.connect(self._find_series)
        edit_menu.addAction(find_action)


        # View Menu
        view_menu = menubar.addMenu(tr("&View"))

        # Panel visibility toggles
        view_menu.addAction(self.data_dock.toggleViewAction())
        view_menu.addAction(self.config_dock.toggleViewAction())
        view_menu.addAction(self.operations_dock.toggleViewAction())
        view_menu.addAction(self.results_dock.toggleViewAction())

        view_menu.addSeparator()

        # Refresh Data
        refresh_action = QAction(tr("&Refresh Data"), self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.setStatusTip(tr("Refresh/reload current data (F5)"))
        refresh_action.triggered.connect(self._refresh_data)
        view_menu.addAction(refresh_action)

        # Fullscreen
        fullscreen_action = QAction(tr("&Fullscreen"), self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.setStatusTip(tr("Toggle fullscreen mode (F11)"))
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        view_menu.addSeparator()

        # Theme selection
        theme_light = QAction(tr("Light Theme"), self)
        theme_light.setStatusTip(tr("Switch to light theme"))
        theme_light.triggered.connect(lambda: self._set_theme("light"))
        view_menu.addAction(theme_light)

        theme_dark = QAction(tr("Dark Theme"), self)
        theme_dark.setStatusTip(tr("Switch to dark theme"))
        theme_dark.triggered.connect(lambda: self._set_theme("dark"))
        view_menu.addAction(theme_dark)

        theme_auto = QAction(tr("Auto Theme"), self)
        theme_auto.setStatusTip(tr("Use system theme"))
        theme_auto.triggered.connect(lambda: self._set_theme("auto"))
        view_menu.addAction(theme_auto)

        # Tools Menu
        tools_menu = menubar.addMenu(tr("&Tools"))

        # Settings
        settings_action = QAction(tr("&Settings..."), self)
        settings_action.setStatusTip(tr("Application settings"))
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # Help Menu
        help_menu = menubar.addMenu(tr("&Help"))

        # Contextual Help
        help_contextual_action = QAction(tr("&Contextual Help"), self)
        help_contextual_action.setShortcut(QKeySequence("F1"))
        help_contextual_action.setStatusTip(tr("Show help for current context (F1)"))
        help_contextual_action.triggered.connect(self._show_contextual_help)
        help_menu.addAction(help_contextual_action)

        # Keyboard Shortcuts
        shortcuts_action = QAction(tr("&Keyboard Shortcuts"), self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+?"))
        shortcuts_action.setStatusTip(tr("Show all keyboard shortcuts"))
        shortcuts_action.triggered.connect(self._show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        # About
        about_action = QAction(tr("&About..."), self)
        about_action.setStatusTip(tr("About Platform Base"))
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        logger.debug("menu_bar_created")

    def _create_tool_bar(self):
        """Create main toolbar"""
        toolbar = QToolBar(tr("Main"), self)
        self.addToolBar(toolbar)

        # Load Data
        load_action = QAction(tr("Load Data"), self)
        load_action.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_DialogOpenButton))
        load_action.triggered.connect(self._load_data)
        toolbar.addAction(load_action)

        toolbar.addSeparator()

        # New Session
        new_action = QAction(tr("New"), self)
        new_action.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon))
        new_action.triggered.connect(self._new_session)
        toolbar.addAction(new_action)

        # Save Session
        save_action = QAction("Save", self)
        save_action.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_DialogSaveButton))
        save_action.triggered.connect(self._save_session)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Settings
        settings_action = QAction("Settings", self)
        settings_action.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_ComputerIcon))
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

        logger.debug("tool_bar_created")

    def _create_status_bar(self):
        """Create status bar"""
        status_bar = self.statusBar()

        # Status label
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_bar.addPermanentWidget(self.progress_bar)

        # Memory usage label
        self.memory_label = QLabel()
        status_bar.addPermanentWidget(self.memory_label)

        # Update memory usage periodically
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self._update_memory_usage)
        self.memory_timer.start(5000)  # Update every 5 seconds

        logger.debug("status_bar_created")

    def _setup_keyboard_shortcuts(self):
        """Setup additional keyboard shortcuts not in menus"""
        from PyQt6.QtGui import QShortcut

        # Delete key - Remove selected series
        delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        delete_shortcut.activated.connect(self._delete_selected_series)
        delete_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Escape - Cancel current operation
        escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        escape_shortcut.activated.connect(self._cancel_operation)
        escape_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Ctrl+W - Close current view/tab
        close_tab_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
        close_tab_shortcut.activated.connect(self._close_current_view)
        close_tab_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Ctrl+Tab - Next tab/view
        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut.activated.connect(self._next_view)
        next_tab_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        # Ctrl+Shift+Tab - Previous tab/view
        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut.activated.connect(self._previous_view)
        prev_tab_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        logger.debug("keyboard_shortcuts_configured")

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

        # Operations panel signals (BUG-004 FIX)
        self.operations_panel.operation_requested.connect(self._handle_operation_request)
        self.operations_panel.export_requested.connect(self._handle_export_request)
        
        # Streaming signal - conecta streaming do OperationsPanel ao VizPanel
        self.operations_panel.streaming_data_updated.connect(self._on_streaming_data_updated)

        # Connect undo/redo manager signals to update menu actions
        self.undo_manager.can_undo_changed.connect(self.undo_action.setEnabled)
        self.undo_manager.can_redo_changed.connect(self.redo_action.setEnabled)
        self.undo_manager.undo_text_changed.connect(
            lambda text: self.undo_action.setText(f"&Undo {text}" if text else "&Undo")
        )
        self.undo_manager.redo_text_changed.connect(
            lambda text: self.redo_action.setText(f"&Redo {text}" if text else "&Redo")
        )

        logger.debug("signals_connected")

    # Slot implementations
    @pyqtSlot()
    def _new_session(self):
        """Create new session"""
        reply = QMessageBox.question(
            self, "New Session",
            "Create new session? Current session will be lost if not saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.session_state.clear_session()
            self.status_label.setText("New session created")
            logger.info("new_session_created")

    @pyqtSlot()
    def _open_session(self):
        """Open session from file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Session", "",
            "Session Files (*.json);;All Files (*)",
        )

        if filepath:
            if self.session_state.load_session(filepath):
                self.status_label.setText(f"Session loaded: {Path(filepath).name}")
                logger.info("session_opened", filepath=filepath)
            else:
                QMessageBox.warning(self, "Error", "Failed to load session file.")

    @pyqtSlot()
    def _save_session(self):
        """Save session to file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Session", "",
            "Session Files (*.json);;All Files (*)",
        )

        if filepath:
            if self.session_state.save_session(filepath):
                self.status_label.setText(f"Session saved: {Path(filepath).name}")
                logger.info("session_saved", filepath=filepath)
            else:
                QMessageBox.warning(self, "Error", "Failed to save session file.")

    @pyqtSlot()
    def _load_data(self):
        """Open load data dialog"""
        try:
            dialog = UploadDialog(self.session_state, self.signal_hub, self)
            dialog.exec()
        except Exception as e:
            logger.exception("load_data_dialog_failed", error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to open load data dialog:\\n{e}")

    @pyqtSlot()
    def _show_settings(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self.session_state, self)
            dialog.exec()
        except Exception as e:
            logger.exception("settings_dialog_failed", error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to open settings dialog:\\n{e}")

    @pyqtSlot()
    def _show_about(self):
        """Show about dialog"""
        try:
            dialog = AboutDialog(self)
            dialog.exec()
        except Exception as e:
            logger.exception("about_dialog_failed", error=str(e))
            QMessageBox.information(self, "About", "Platform Base v2.0\\nTime Series Analysis Tool")

    def _set_theme(self, theme: str):
        """Set application theme"""
        self.session_state.set_theme(theme)
        # Theme change will be handled by session state signal

    @pyqtSlot(object)
    def _on_selection_changed(self, selection_state):
        """Handle selection state changes"""
        dataset_id = selection_state.dataset_id
        n_series = len(selection_state.series_ids)

        if dataset_id:
            self.status_label.setText(f"Dataset: {dataset_id} | Series: {n_series}")
        else:
            self.status_label.setText("No data selected")

    @pyqtSlot(object)
    def _on_ui_state_changed(self, ui_state):
        """Handle UI state changes"""
        # Update panel visibility
        for panel, visible in ui_state.panel_visibility.items():
            if panel == "data":
                self.data_dock.setVisible(visible)
            elif panel == "results":
                self.results_dock.setVisible(visible)

        # Apply theme changes if needed
        if hasattr(self, "_current_theme") and self._current_theme != ui_state.theme:
            self._apply_theme(ui_state.theme)
        self._current_theme = ui_state.theme

    def _apply_theme(self, theme: str):
        """Apply theme to application"""
        # Theme application logic would go here
        # For now, just log the change
        logger.info("theme_applied", theme=theme)

    @pyqtSlot(str, str)
    def _on_operation_started(self, operation_type: str, operation_id: str):
        """Handle operation started - create and start the appropriate worker"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Running {operation_type}...")

        # Get current selection and parameters
        selection = self.session_state.selection
        if not selection.dataset_id or not selection.series_ids:
            self.status_label.setText("No data selected")
            self.progress_bar.setVisible(False)
            return

        dataset_id = selection.dataset_id
        series_id = selection.series_ids[0] if selection.series_ids else None

        # Get operation parameters from processing state
        processing_state = self.session_state.processing
        operation_info = processing_state.active_operations.get(operation_id, {})
        params = operation_info.get("parameters", {})

        try:
            # Start the appropriate worker based on operation type
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
                # Handle derivative operations directly
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, operation_type, params
                )
            elif operation_type == "integral":
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, "integral", params
                )
            elif operation_type == "area":
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, "area", params
                )
            elif operation_type in ("smoothing", "remove_outliers"):
                # Handle filtering operations via calculus worker
                self.processing_manager.start_calculus(
                    operation_id, dataset_id, series_id, operation_type, params
                )
            else:
                logger.warning("unknown_operation_type", operation_type=operation_type)
                self.status_label.setText(f"Unknown operation: {operation_type}")
                self.progress_bar.setVisible(False)

            logger.info("worker_started_from_ui",
                       operation_type=operation_type, operation_id=operation_id)

        except Exception as e:
            logger.exception("operation_start_failed", error=str(e))
            self.status_label.setText(f"Operation failed: {e}")
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
        self.status_label.setText("Operation completed")

        # Show results panel if hidden
        self.results_dock.show()

        # Update results panel with result info
        if isinstance(result, dict):
            operation_type = result.get("operation", "unknown")
            series_id = result.get("series_id")
            series_name = result.get("series_name", series_id)

            # Add result to results panel
            if hasattr(self.results_panel, "add_result"):
                self.results_panel.add_result(operation_id, result)

            # If a new series was created, update data panel and optionally plot it
            if series_id:
                # Refresh data panel to show new series
                if hasattr(self.data_panel, "refresh_data"):
                    self.data_panel.refresh_data()
                elif hasattr(self.data_panel, "_refresh_tree"):
                    self.data_panel._refresh_tree()

                # Automatically plot the new series
                selection = self.session_state.selection
                if selection.dataset_id:
                    # Add new series to visualization
                    try:
                        dataset = self.session_state.dataset_store.get_dataset(selection.dataset_id)
                        if series_id in dataset.series:
                            new_series = dataset.series[series_id]
                            self.viz_panel.add_series(
                                selection.dataset_id,
                                series_id,
                                new_series,
                                dataset.timestamps if hasattr(dataset, 'timestamps') else dataset.t_seconds
                            )
                            logger.info("new_series_plotted", series_id=series_id)
                    except Exception as e:
                        logger.warning("failed_to_auto_plot_series", error=str(e))

            logger.info("operation_result_displayed",
                       operation_id=operation_id,
                       operation_type=operation_type,
                       series_id=series_id)

    @pyqtSlot(str, str)
    def _on_operation_failed(self, operation_id: str, error_message: str):
        """Handle operation failed"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Operation failed")

        QMessageBox.warning(self, "Operation Failed",
                           f"Operation {operation_id} failed:\\n{error_message}")

    @pyqtSlot(str, str)
    def _on_error_occurred(self, error_type: str, error_message: str):
        """Handle general errors"""
        logger.error("ui_error_occurred", error_type=error_type, message=error_message)
        QMessageBox.critical(self, error_type, error_message)

    @pyqtSlot(str)
    def _on_status_updated(self, message: str):
        """Handle status updates"""
        self.status_label.setText(message)

    @pyqtSlot(str, dict)
    def _handle_operation_request(self, operation_name: str, params: dict):
        """
        Handle operation request from OperationsPanel.
        
        This connects the UI to the processing backend.
        """
        logger.info("operation_requested", operation=operation_name, params=params)

        # Validate that we have data selected
        selection = self.session_state.get_selected_series()
        if not selection:
            QMessageBox.warning(
                self,
                "No Data Selected",
                "Please select a data series before performing this operation."
            )
            return

        try:
            # Get the selected dataset and series
            dataset_id = selection[0].dataset_id if hasattr(selection[0], 'dataset_id') else None
            series_id = selection[0].series_id if hasattr(selection[0], 'series_id') else None

            if not dataset_id or not series_id:
                # Try alternate selection format
                if isinstance(selection, dict):
                    dataset_id = selection.get('dataset_id')
                    series_id = selection.get('series_id')

            if not dataset_id or not series_id:
                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "Could not determine selected series. Please select a series from the data panel."
                )
                return

            # Start the processing operation
            self.processing_manager.start_operation(
                operation_type=operation_name,
                dataset_id=dataset_id,
                series_id=series_id,
                params=params
            )

            # Show feedback
            self.status_label.setText(f"Processing: {operation_name}...")
            self.progress_bar.setVisible(True)

            # Activate results panel to show results when complete
            self.results_dock.raise_()

        except Exception as e:
            logger.exception("operation_request_failed", operation=operation_name, error=str(e))
            QMessageBox.critical(
                self,
                "Operation Failed",
                f"Failed to start operation '{operation_name}':\\n{str(e)}"
            )

    @pyqtSlot(str, dict)
    def _handle_export_request(self, format_type: str, options: dict):
        """
        Handle export request from OperationsPanel.
        """
        logger.info("export_requested", format=format_type, options=options)

        # Get output path from user
        file_filters = {
            'csv': "CSV Files (*.csv)",
            'excel': "Excel Files (*.xlsx)",
            'parquet': "Parquet Files (*.parquet)",
            'hdf5': "HDF5 Files (*.h5 *.hdf5)",
            'json': "JSON Files (*.json)",
        }

        file_filter = file_filters.get(format_type, "All Files (*.*)")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export as {format_type.upper()}",
            "",
            file_filter
        )

        if file_path:
            self.status_label.setText(f"Exporting to {format_type}...")
            logger.info("export_started", path=file_path, format=format_type)

            # Get current dataset and series selection
            current_selection = self.session_state.get_active_selection() if hasattr(self.session_state, 'get_active_selection') else None
            dataset_id = current_selection.get('dataset_id') if current_selection else None
            series_ids = current_selection.get('series_ids') if current_selection else None

            if not dataset_id and hasattr(self.data_panel, 'get_selected_dataset_id'):
                dataset_id = self.data_panel.get_selected_dataset_id()

            if not dataset_id:
                QMessageBox.warning(
                    self,
                    "No Data Selected",
                    "Please select a dataset or series to export."
                )
                self.status_label.setText("Export cancelled - no data selected")
                return

            # Start export worker
            from platform_base.desktop.workers.export_worker import DataExportWorker

            export_config = {
                'delimiter': options.get('delimiter', ','),
                'encoding': options.get('encoding', 'utf-8'),
                'include_metadata': options.get('include_metadata', True),
            }

            self.export_worker = DataExportWorker(
                dataset_store=self.signal_hub.dataset_store if hasattr(self.signal_hub, 'dataset_store') else None,
                dataset_id=dataset_id,
                series_ids=series_ids,
                output_path=file_path,
                format_type=format_type,
                export_config=export_config
            )

            # Connect worker signals
            self.export_worker.progress.connect(self.progress_bar.setValue)
            self.export_worker.status_updated.connect(self.status_label.setText)
            self.export_worker.error.connect(lambda e: QMessageBox.critical(self, "Export Error", str(e)))
            self.export_worker.finished.connect(self._on_export_finished)

            # Start export
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.export_worker.start()

    @pyqtSlot()
    def _on_export_finished(self):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Export completed successfully")
        logger.info("export_completed")
        QMessageBox.information(
            self,
            "Export Complete",
            "Data exported successfully."
        )

    @pyqtSlot(str, object, object)
    def _on_streaming_data_updated(self, series_id: str, x_data, y_data):
        """
        Handle streaming data update from OperationsPanel.
        Updates VizPanel with new data chunk for real-time visualization.
        """
        try:
            # Atualizar o gráfico 2D atual no VizPanel
            if hasattr(self.viz_panel, 'plot_tabs'):
                current_tab = self.viz_panel.plot_tabs.currentWidget()
                
                # Se for um Plot2DWidget, atualizar diretamente
                from platform_base.desktop.widgets.viz_panel import Plot2DWidget

                # Buscar Plot2DWidget no tab atual ou criar um se não existir
                plot_widget = None
                if isinstance(current_tab, Plot2DWidget):
                    plot_widget = current_tab
                else:
                    # Procurar Plot2DWidget dentro do widget atual
                    for child in current_tab.findChildren(Plot2DWidget) if current_tab else []:
                        plot_widget = child
                        break
                
                # Se não encontrar, criar um novo plot tab
                if plot_widget is None:
                    # Criar novo tab de streaming
                    plot_widget = Plot2DWidget(self.session_state, self.signal_hub)
                    plot_widget.setLabel("left", "Value")
                    plot_widget.setLabel("bottom", "Time")
                    self.viz_panel.plot_tabs.addTab(plot_widget, "📡 Streaming")
                    self.viz_panel.plot_tabs.setCurrentWidget(plot_widget)
                    self.viz_panel.active_plots["streaming"] = {
                        "widget": plot_widget,
                        "type": "2d",
                        "series": {}
                    }
                
                # Atualizar dados da série
                if series_id in plot_widget._series_data:
                    # Série já existe - atualizar dados
                    plot_item = plot_widget._series_data[series_id]["plot_item"]
                    plot_item.setData(x_data, y_data)
                else:
                    # Nova série - adicionar ao gráfico
                    series_index = len(plot_widget._series_data)
                    plot_widget.add_series(series_id, x_data, y_data, series_index, series_id)
                
                # Auto-range para ajustar visualização
                plot_widget.enableAutoRange()
                
        except Exception as e:
            logger.exception("streaming_update_failed", error=str(e))

    def _update_memory_usage(self):
        """Update memory usage display"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.setText(f"Memory: {memory_mb:.1f} MB")
        except ImportError:
            # psutil not available
            self.memory_label.setText("")

    # New action handlers for enhanced keyboard shortcuts

    @pyqtSlot()
    def _export_data(self):
        """Export data to file"""
        logger.info("export_data_requested")
        
        # Get current dataset selection
        dataset_id = None
        series_ids = None
        
        if hasattr(self.data_panel, 'get_selected_dataset_id'):
            dataset_id = self.data_panel.get_selected_dataset_id()
        
        if hasattr(self.data_panel, 'get_selected_series_ids'):
            series_ids = self.data_panel.get_selected_series_ids()
        
        if not dataset_id:
            QMessageBox.warning(
                self, "No Data Selected",
                "Please select a dataset to export."
            )
            return
        
        # Show file dialog for export
        file_filters = (
            "CSV Files (*.csv);;Excel Files (*.xlsx);;Parquet Files (*.parquet);;"
            "HDF5 Files (*.h5 *.hdf5);;All Files (*.*)"
        )
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Data", "", file_filters
        )
        
        if not file_path:
            return
        
        # Determine format from filter or extension
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
            if not file_path.endswith('.csv'):
                file_path += '.csv'
        
        # Start export worker
        self.status_label.setText(f"Exporting to {format_type}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
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
        
        # Connect worker signals
        self._export_worker.progress.connect(lambda p, m: (
            self.progress_bar.setValue(p),
            self.status_label.setText(m)
        ))
        self._export_worker.error.connect(lambda e: (
            QMessageBox.critical(self, "Export Error", str(e)),
            self.progress_bar.setVisible(False)
        ))
        self._export_worker.finished.connect(lambda: (
            self.progress_bar.setVisible(False),
            self.status_label.setText("Export completed"),
            QMessageBox.information(self, "Export Complete", f"Data exported to:\n{file_path}")
        ))
        
        self._export_worker.start()
        logger.info("export_started", path=file_path, format=format_type)

    @pyqtSlot()
    def _undo_operation(self):
        """Undo last operation"""
        if self.undo_manager.can_undo():
            undo_text = self.undo_manager.undo_text()
            self.undo_manager.undo()
            self.status_label.setText(f"Undo: {undo_text}")
            logger.info("undo_executed", operation=undo_text)
        else:
            self.status_label.setText("Nothing to undo")
            logger.debug("undo_requested_but_unavailable")

    @pyqtSlot()
    def _redo_operation(self):
        """Redo last undone operation"""
        if self.undo_manager.can_redo():
            redo_text = self.undo_manager.redo_text()
            self.undo_manager.redo()
            self.status_label.setText(f"Redo: {redo_text}")
            logger.info("redo_executed", operation=redo_text)
        else:
            self.status_label.setText("Nothing to redo")
            logger.debug("redo_requested_but_unavailable")

    @pyqtSlot()
    def _find_series(self):
        """Find/filter series in data panel"""
        self.status_label.setText("Find series")
        logger.info("find_series_requested")
        
        # Focus data panel search if it exists
        if hasattr(self.data_panel, "show_search"):
            self.data_panel.show_search()
            return
            
        # Try to find search field in data panel
        if hasattr(self.data_panel, "_search_edit"):
            self.data_panel._search_edit.setFocus()
            self.data_panel._search_edit.selectAll()
            return
        
        # Try to find filter edit
        if hasattr(self.data_panel, "_filter_edit"):
            self.data_panel._filter_edit.setFocus()
            self.data_panel._filter_edit.selectAll()
            return
        
        # Ensure data panel is visible and try generic focus
        if hasattr(self, 'data_dock'):
            self.data_dock.raise_()
            self.data_dock.setFocus()
            
        # Show search dialog as fallback
        from PyQt6.QtWidgets import QInputDialog
        
        search_text, ok = QInputDialog.getText(
            self, "Find Series",
            "Enter series name to search:"
        )
        
        if ok and search_text:
            # Try to apply filter to data panel
            if hasattr(self.data_panel, "filter_series"):
                self.data_panel.filter_series(search_text)
            elif hasattr(self.data_panel, "set_filter"):
                self.data_panel.set_filter(search_text)
            self.status_label.setText(f"Filtering: '{search_text}'")

    @pyqtSlot()
    def _refresh_data(self):
        """Refresh/reload current data from source file"""
        self.status_label.setText("Refreshing data...")
        logger.info("refresh_data_requested")
        
        # Get current dataset
        dataset_id = None
        if hasattr(self.data_panel, 'get_selected_dataset_id'):
            dataset_id = self.data_panel.get_selected_dataset_id()
        
        if not dataset_id:
            self.status_label.setText("No dataset selected")
            QMessageBox.warning(
                self, "No Dataset",
                "Please select a dataset to refresh."
            )
            return
        
        try:
            # Get dataset info
            dataset = self.session_state.dataset_store.get_dataset(dataset_id)
            source_path = dataset.source.filepath if hasattr(dataset.source, 'filepath') else None
            
            if source_path and Path(source_path).exists():
                # Reload from source
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                # Emit signal to reload - data panel handles actual reload
                if hasattr(self.signal_hub, 'dataset_reload_requested'):
                    self.signal_hub.dataset_reload_requested.emit(dataset_id)
                elif hasattr(self.data_panel, 'reload_dataset'):
                    self.data_panel.reload_dataset(dataset_id)
                else:
                    # Manual reload via data panel
                    self.signal_hub.status_updated.emit(f"Reloading {dataset_id}...")
                    
                self.progress_bar.setValue(100)
                self.progress_bar.setVisible(False)
                self.status_label.setText(f"Refreshed: {dataset_id}")
                logger.info("dataset_refreshed", dataset_id=dataset_id)
            else:
                # No source file - just refresh views
                self.signal_hub.status_updated.emit("Views refreshed")
                self.status_label.setText("Views refreshed (no source file)")
                logger.info("views_refreshed", dataset_id=dataset_id)
                
            # Update all connected views
            if hasattr(self.signal_hub, 'data_changed'):
                self.signal_hub.data_changed.emit()
            if hasattr(self.viz_panel, 'refresh'):
                self.viz_panel.refresh()
                
        except Exception as e:
            logger.exception("refresh_failed", error=str(e))
            self.status_label.setText("Refresh failed")
            self.progress_bar.setVisible(False)
            QMessageBox.warning(
                self, "Refresh Failed",
                f"Could not refresh data:\n{e!s}"
            )

    @pyqtSlot()
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.status_label.setText("Exited fullscreen")
            logger.info("fullscreen_disabled")
        else:
            self.showFullScreen()
            self.status_label.setText("Entered fullscreen (F11 to exit)")
            logger.info("fullscreen_enabled")

    @pyqtSlot()
    def _show_contextual_help(self):
        """Show contextual help for current widget
        
        Identifies the focused widget and displays relevant help content.
        """
        from PyQt6.QtWidgets import QApplication

        # Get currently focused widget
        focused = QApplication.focusWidget()
        
        # Help content mapping based on widget type and object name
        help_content = {
            # Panel types
            "DataPanel": {
                "title": "Data Panel Help",
                "content": """<h3>Data Panel</h3>
<p>The Data Panel displays all loaded datasets and their series.</p>
<h4>Features:</h4>
<ul>
<li><b>Search:</b> Type to filter series by name</li>
<li><b>Selection:</b> Click to select series for visualization</li>
<li><b>Multi-select:</b> Use Ctrl+Click for multiple selections</li>
<li><b>Right-click:</b> Context menu with additional options</li>
</ul>
<h4>Shortcuts:</h4>
<ul>
<li><b>Ctrl+F:</b> Focus search field</li>
<li><b>Ctrl+A:</b> Select all series</li>
<li><b>Delete:</b> Remove selected series</li>
</ul>"""
            },
            "VizPanel": {
                "title": "Visualization Panel Help",
                "content": """<h3>Visualization Panel</h3>
<p>Create and customize plots and visualizations.</p>
<h4>Plot Types:</h4>
<ul>
<li><b>Time Series:</b> Line plots over time</li>
<li><b>Scatter Plot:</b> X-Y relationship plots</li>
<li><b>Heatmap:</b> Correlation matrices</li>
<li><b>3D Plots:</b> Surface and trajectory views</li>
</ul>
<h4>Interactions:</h4>
<ul>
<li><b>Pan:</b> Click and drag</li>
<li><b>Zoom:</b> Scroll wheel or select region</li>
<li><b>Right-click:</b> Plot context menu</li>
</ul>"""
            },
            "ResultsPanel": {
                "title": "Results Panel Help",
                "content": """<h3>Results Panel</h3>
<p>View statistical analysis and operation results.</p>
<h4>Tabs:</h4>
<ul>
<li><b>Statistics:</b> Min, max, mean, std, etc.</li>
<li><b>Distribution:</b> Histogram and distribution stats</li>
<li><b>Correlation:</b> Cross-series correlation</li>
</ul>"""
            },
            "StreamingControls": {
                "title": "Streaming Controls Help",
                "content": """<h3>Streaming Controls</h3>
<p>Control time-series playback and animation.</p>
<h4>Controls:</h4>
<ul>
<li><b>Play/Pause:</b> Start/stop streaming</li>
<li><b>Speed:</b> Adjust playback speed</li>
<li><b>Window:</b> Set visible time window</li>
<li><b>Loop:</b> Enable continuous playback</li>
</ul>"""
            },
        }
        
        # Default help content
        default_help = {
            "title": "Platform Base Help",
            "content": """<h3>Platform Base - Time Series Analysis</h3>
<p>Welcome to Platform Base! Press F1 on any panel for contextual help.</p>
<h4>Quick Start:</h4>
<ol>
<li><b>Load Data:</b> Ctrl+L to load CSV, Excel, or Parquet files</li>
<li><b>Select Series:</b> Click series in Data Panel</li>
<li><b>Visualize:</b> Use Visualization panel to create plots</li>
<li><b>Analyze:</b> Right-click plots for analysis options</li>
</ol>
<h4>Key Shortcuts:</h4>
<ul>
<li><b>F1:</b> This help dialog</li>
<li><b>F5:</b> Refresh data</li>
<li><b>F11:</b> Fullscreen</li>
<li><b>Ctrl+Z/Y:</b> Undo/Redo</li>
</ul>"""
        }
        
        # Find help content for focused widget
        help_info = default_help
        
        if focused is not None:
            # Check widget and its parents for matching help
            widget = focused
            while widget is not None:
                widget_class = widget.__class__.__name__
                widget_name = widget.objectName()
                
                # Check by class name
                if widget_class in help_content:
                    help_info = help_content[widget_class]
                    break
                # Check by object name
                if widget_name in help_content:
                    help_info = help_content[widget_name]
                    break
                    
                widget = widget.parent()
        
        # Show help dialog
        msg = QMessageBox(self)
        msg.setWindowTitle(help_info["title"])
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_info["content"])
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        self.status_label.setText(f"Help: {help_info['title']}")
        logger.info("contextual_help_shown", title=help_info["title"])

    @pyqtSlot()
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """
<h2>Keyboard Shortcuts</h2>

<h3>File Operations</h3>
<table>
<tr><td><b>Ctrl+N</b></td><td>New Session</td></tr>
<tr><td><b>Ctrl+O</b></td><td>Open Session</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save Session</td></tr>
<tr><td><b>Ctrl+L</b></td><td>Load Data</td></tr>
<tr><td><b>Ctrl+E</b></td><td>Export Data</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Quit</td></tr>
</table>

<h3>Edit Operations</h3>
<table>
<tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
<tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>
<tr><td><b>Ctrl+F</b></td><td>Find Series</td></tr>
<tr><td><b>Delete</b></td><td>Remove Selected Series</td></tr>
</table>

<h3>View Controls</h3>
<table>
<tr><td><b>F5</b></td><td>Refresh Data</td></tr>
<tr><td><b>F11</b></td><td>Toggle Fullscreen</td></tr>
<tr><td><b>Ctrl+W</b></td><td>Close Current View</td></tr>
<tr><td><b>Ctrl+Tab</b></td><td>Next View</td></tr>
<tr><td><b>Ctrl+Shift+Tab</b></td><td>Previous View</td></tr>
</table>

<h3>Help</h3>
<table>
<tr><td><b>F1</b></td><td>Contextual Help</td></tr>
<tr><td><b>Ctrl+?</b></td><td>Show This Dialog</td></tr>
<tr><td><b>Esc</b></td><td>Cancel Operation</td></tr>
</table>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(shortcuts_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        logger.info("keyboard_shortcuts_shown")

    @pyqtSlot()
    def _delete_selected_series(self):
        """Delete selected series"""
        self.status_label.setText("Delete series")
        logger.info("delete_series_requested")
        # Delegate to data panel
        if hasattr(self.data_panel, "delete_selected"):
            self.data_panel.delete_selected()
        else:
            QMessageBox.information(
                self, "Delete Series",
                "Select a series in the Data Panel and press Delete to remove it.",
            )

    @pyqtSlot()
    def _cancel_operation(self):
        """Cancel current operation"""
        self.status_label.setText("Operation cancelled")
        logger.info("operation_cancelled")
        # Emit signal to cancel any ongoing operations
        if hasattr(self.signal_hub, "operation_cancelled"):
            self.signal_hub.operation_cancelled.emit()

    @pyqtSlot()
    def _close_current_view(self):
        """Close current view/tab"""
        self.status_label.setText("Close view")
        logger.info("close_view_requested")
        # Delegate to viz panel
        if hasattr(self.viz_panel, "close_current_view"):
            self.viz_panel.close_current_view()

    @pyqtSlot()
    def _next_view(self):
        """Switch to next view/tab"""
        logger.info("next_view_requested")
        # Delegate to viz panel
        if hasattr(self.viz_panel, "next_view"):
            self.viz_panel.next_view()

    @pyqtSlot()
    def _previous_view(self):
        """Switch to previous view/tab"""
        logger.info("previous_view_requested")
        # Delegate to viz panel
        if hasattr(self.viz_panel, "previous_view"):
            self.viz_panel.previous_view()

    def _auto_save_session(self):
        """Auto-save session periodically"""
        try:
            # Create auto-save directory
            autosave_dir = Path.home() / ".platform_base" / "autosave"
            autosave_dir.mkdir(parents=True, exist_ok=True)

            # Save session
            timestamp = self.session_state.modified_at.strftime("%Y%m%d_%H%M%S")
            filepath = autosave_dir / f"autosave_{timestamp}.json"

            self.session_state.save_session(str(filepath))
            logger.debug("session_auto_saved", filepath=str(filepath))

        except Exception as e:
            logger.warning("auto_save_failed", error=str(e))

    def save_session_on_exit(self):
        """Save session when application exits"""
        try:
            # Save final session state
            self._auto_save_session()

            # Save window geometry
            settings = QSettings()
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("windowState", self.saveState())

            logger.info("session_saved_on_exit")

        except Exception as e:
            logger.exception("exit_save_failed", error=str(e))

    # Streaming handlers
    @pyqtSlot(int)
    def _on_streaming_position_changed(self, position: int):
        """Handle streaming position changes - update visualization"""
        try:
            # Update time window in session state
            selection = self.session_state.selection
            if selection.dataset_id:
                dataset = self.session_state.dataset_store.get_dataset(selection.dataset_id)
                total_points = len(dataset.t_seconds)

                if total_points > 0:
                    # Calculate time position from frame position
                    time_position = dataset.t_seconds[min(position, total_points - 1)]

                    # Get window size from streaming panel
                    window_frames = self.streaming_panel._window_spin.value() if hasattr(self.streaming_panel, '_window_spin') else 100
                    window_size = (dataset.t_seconds[-1] - dataset.t_seconds[0]) * window_frames / total_points

                    # Update visualization with sliding window
                    from platform_base.core.models import TimeWindow
                    window = TimeWindow(
                        start=max(0, time_position - window_size / 2),
                        end=min(dataset.t_seconds[-1], time_position + window_size / 2)
                    )
                    self.session_state.set_time_window(window)

                    # Emit signal for viz panel update
                    self.signal_hub.streaming_time_changed.emit(time_position)

            self.status_label.setText(f"Position: {position}")
        except Exception as e:
            logger.exception("streaming_position_update_failed", error=str(e))

    @pyqtSlot(object)
    def _on_streaming_state_changed(self, state):
        """Handle streaming state changes"""
        from platform_base.ui.panels.streaming_panel import PlaybackState

        if state == PlaybackState.PLAYING:
            self.signal_hub.streaming_started.emit()
            self.status_label.setText("Streaming: Playing")
        elif state == PlaybackState.PAUSED:
            self.signal_hub.streaming_paused.emit()
            self.status_label.setText("Streaming: Paused")
        elif state == PlaybackState.STOPPED:
            self.signal_hub.streaming_stopped.emit()
            self.status_label.setText("Streaming: Stopped")

        logger.debug("streaming_state_changed", state=state)

    def _update_streaming_panel_data(self):
        """Update streaming panel with current dataset"""
        selection = self.session_state.selection
        if selection.dataset_id:
            try:
                dataset = self.session_state.dataset_store.get_dataset(selection.dataset_id)
                total_frames = len(dataset.t_seconds)
                self.streaming_panel.set_total_frames(total_frames)
                logger.debug("streaming_panel_updated", total_frames=total_frames)
            except Exception as e:
                logger.exception("streaming_panel_update_failed", error=str(e))

    def closeEvent(self, event):
        """Handle window close event"""
        # Ask user to confirm if unsaved changes
        reply = QMessageBox.question(
            self, "Quit Application",
            "Are you sure you want to quit?\\nAny unsaved work will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.save_session_on_exit()
            event.accept()
        else:
            event.ignore()
