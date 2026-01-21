"""
MainWindow - Main PyQt6 desktop window for Platform Base v2.0

Implements the main application window with dockable panels layout.
Replaces Dash web interface with native desktop interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QDockWidget, QMenuBar, QStatusBar, QToolBar,
    QFileDialog, QMessageBox, QProgressBar,
    QLabel, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QSettings
from PyQt6.QtGui import QKeySequence, QAction, QIcon

from platform_base.desktop.session_state import SessionState
from platform_base.desktop.signal_hub import SignalHub
from platform_base.desktop.widgets.data_panel import DataPanel
from platform_base.desktop.widgets.viz_panel import VizPanel
from platform_base.desktop.widgets.config_panel import ConfigPanel
from platform_base.desktop.widgets.results_panel import ResultsPanel
from platform_base.desktop.dialogs.upload_dialog import UploadDialog
from platform_base.desktop.dialogs.settings_dialog import SettingsDialog
from platform_base.desktop.dialogs.about_dialog import AboutDialog
from platform_base.utils.logging import get_logger
from platform_base.utils.errors import PlatformError

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Features:
    - Dockable panel layout (Data, Visualization, Configuration, Results)
    - Menu bar with standard actions
    - Tool bar for quick access
    - Status bar with progress indication
    - Auto-save session state
    - Keyboard shortcuts
    """
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub):
        super().__init__()
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        
        # Initialize UI components
        self._setup_window()
        self._create_dockable_panels()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._connect_signals()
        
        # Auto-save timer
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self._auto_save_session)
        self._auto_save_timer.start(300000)  # Save every 5 minutes
        
        logger.info("main_window_initialized")
    
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
        self.data_dock = QDockWidget("Data", self)
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
        self.config_dock = QDockWidget("Configuration", self)
        self.config_dock.setWidget(self.config_panel)
        self.config_dock.setObjectName("ConfigPanel")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config_dock)
        
        # Results Panel (Bottom)
        self.results_panel = ResultsPanel(self.session_state, self.signal_hub)
        self.results_dock = QDockWidget("Results", self)
        self.results_dock.setWidget(self.results_panel)
        self.results_dock.setObjectName("ResultsPanel")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.results_dock)
        
        # Initially hide results panel
        self.results_dock.hide()
        
        logger.debug("dockable_panels_created")
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # New Session
        new_action = QAction("&New Session", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_session)
        file_menu.addAction(new_action)
        
        # Open Session
        open_action = QAction("&Open Session...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_session)
        file_menu.addAction(open_action)
        
        # Save Session
        save_action = QAction("&Save Session...", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Load Data
        load_data_action = QAction("&Load Data...", self)
        load_data_action.setShortcut(QKeySequence("Ctrl+L"))
        load_data_action.triggered.connect(self._load_data)
        file_menu.addAction(load_data_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        # Panel visibility toggles
        view_menu.addAction(self.data_dock.toggleViewAction())
        view_menu.addAction(self.config_dock.toggleViewAction())
        view_menu.addAction(self.results_dock.toggleViewAction())
        
        view_menu.addSeparator()
        
        # Theme selection
        theme_light = QAction("Light Theme", self)
        theme_light.triggered.connect(lambda: self._set_theme("light"))
        view_menu.addAction(theme_light)
        
        theme_dark = QAction("Dark Theme", self)
        theme_dark.triggered.connect(lambda: self._set_theme("dark"))
        view_menu.addAction(theme_dark)
        
        theme_auto = QAction("Auto Theme", self)
        theme_auto.triggered.connect(lambda: self._set_theme("auto"))
        view_menu.addAction(theme_auto)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        # About
        about_action = QAction("&About...", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        logger.debug("menu_bar_created")
    
    def _create_tool_bar(self):
        """Create main toolbar"""
        toolbar = QToolBar("Main", self)
        self.addToolBar(toolbar)
        
        # Load Data
        load_action = QAction("Load Data", self)
        load_action.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_DialogOpenButton))
        load_action.triggered.connect(self._load_data)
        toolbar.addAction(load_action)
        
        toolbar.addSeparator()
        
        # New Session
        new_action = QAction("New", self)
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
        
        logger.debug("signals_connected")
    
    # Slot implementations
    @pyqtSlot()
    def _new_session(self):
        """Create new session"""
        reply = QMessageBox.question(
            self, "New Session",
            "Create new session? Current session will be lost if not saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
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
            "Session Files (*.json);;All Files (*)"
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
            "Session Files (*.json);;All Files (*)"
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
            logger.error("load_data_dialog_failed", error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to open load data dialog:\\n{e}")
    
    @pyqtSlot()
    def _show_settings(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self.session_state, self)
            dialog.exec()
        except Exception as e:
            logger.error("settings_dialog_failed", error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to open settings dialog:\\n{e}")
    
    @pyqtSlot()
    def _show_about(self):
        """Show about dialog"""
        try:
            dialog = AboutDialog(self)
            dialog.exec()
        except Exception as e:
            logger.error("about_dialog_failed", error=str(e))
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
        if hasattr(self, '_current_theme') and self._current_theme != ui_state.theme:
            self._apply_theme(ui_state.theme)
        self._current_theme = ui_state.theme
    
    def _apply_theme(self, theme: str):
        """Apply theme to application"""
        # Theme application logic would go here
        # For now, just log the change
        logger.info("theme_applied", theme=theme)
    
    @pyqtSlot(str, str)
    def _on_operation_started(self, operation_type: str, operation_id: str):
        """Handle operation started"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Running {operation_type}...")
    
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
            logger.error("exit_save_failed", error=str(e))
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Ask user to confirm if unsaved changes
        reply = QMessageBox.question(
            self, "Quit Application",
            "Are you sure you want to quit?\\nAny unsaved work will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.save_session_on_exit()
            event.accept()
        else:
            event.ignore()