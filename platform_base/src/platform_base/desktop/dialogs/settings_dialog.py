"""
SettingsDialog - Application settings dialog for Platform Base v2.0

Provides interface for configuring application settings.

Interface carregada de: desktop/ui_files/settingsDialog.ui
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QSettings, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState


logger = get_logger(__name__)


class GeneralSettingsTab(QWidget):
    """General application settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Appearance group
        appearance_group = QGroupBox(tr("Appearance"))
        appearance_layout = QFormLayout(appearance_group)

        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([tr("Auto"), tr("Light"), tr("Dark")])
        appearance_layout.addRow(tr("Theme:"), self.theme_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(9)
        appearance_layout.addRow(tr("Font Size:"), self.font_size_spin)

        # DPI scaling
        self.dpi_check = QCheckBox(tr("Enable high DPI scaling"))
        appearance_layout.addRow(tr("Display:"), self.dpi_check)

        layout.addWidget(appearance_group)

        # Behavior group
        behavior_group = QGroupBox(tr("Behavior"))
        behavior_layout = QFormLayout(behavior_group)

        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setValue(5)
        self.autosave_spin.setSuffix(tr(" minutes"))
        behavior_layout.addRow(tr("Auto-save interval:"), self.autosave_spin)

        # Confirm on exit
        self.confirm_exit_check = QCheckBox(tr("Confirm before exiting"))
        behavior_layout.addRow(tr("Exit:"), self.confirm_exit_check)

        # Remember window state
        self.remember_window_check = QCheckBox(tr("Remember window position and size"))
        behavior_layout.addRow(tr("Window:"), self.remember_window_check)

        layout.addWidget(behavior_group)

        layout.addStretch()

    def _load_settings(self):
        """Load settings from QSettings"""
        settings = QSettings()

        # Load theme
        theme = settings.value("appearance/theme", "Auto")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        # Load font size
        font_size = settings.value("appearance/font_size", 9, type=int)
        self.font_size_spin.setValue(font_size)

        # Load DPI
        dpi_enabled = settings.value("appearance/high_dpi", True, type=bool)
        self.dpi_check.setChecked(dpi_enabled)

        # Load behavior settings
        autosave = settings.value("behavior/autosave_minutes", 5, type=int)
        self.autosave_spin.setValue(autosave)

        confirm_exit = settings.value("behavior/confirm_exit", True, type=bool)
        self.confirm_exit_check.setChecked(confirm_exit)

        remember_window = settings.value("behavior/remember_window", True, type=bool)
        self.remember_window_check.setChecked(remember_window)

    def save_settings(self):
        """Save settings to QSettings"""
        settings = QSettings()

        # Save appearance
        settings.setValue("appearance/theme", self.theme_combo.currentText())
        settings.setValue("appearance/font_size", self.font_size_spin.value())
        settings.setValue("appearance/high_dpi", self.dpi_check.isChecked())

        # Save behavior
        settings.setValue("behavior/autosave_minutes", self.autosave_spin.value())
        settings.setValue("behavior/confirm_exit", self.confirm_exit_check.isChecked())
        settings.setValue("behavior/remember_window", self.remember_window_check.isChecked())


class PerformanceSettingsTab(QWidget):
    """Performance and caching settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Memory group
        memory_group = QGroupBox(tr("Memory Management"))
        memory_layout = QFormLayout(memory_group)

        # Memory cache size
        self.memory_cache_spin = QSpinBox()
        self.memory_cache_spin.setRange(64, 8192)
        self.memory_cache_spin.setValue(512)
        self.memory_cache_spin.setSuffix(tr(" MB"))
        memory_layout.addRow(tr("Memory Cache Size:"), self.memory_cache_spin)

        # Max datasets in memory
        self.max_datasets_spin = QSpinBox()
        self.max_datasets_spin.setRange(1, 100)
        self.max_datasets_spin.setValue(10)
        memory_layout.addRow(tr("Max Datasets in Memory:"), self.max_datasets_spin)

        layout.addWidget(memory_group)

        # Disk cache group
        cache_group = QGroupBox(tr("Disk Cache"))
        cache_layout = QFormLayout(cache_group)

        # Enable disk cache
        self.disk_cache_check = QCheckBox(tr("Enable disk cache"))
        cache_layout.addRow(tr("Cache:"), self.disk_cache_check)

        # Cache directory
        cache_dir_layout = QHBoxLayout()
        self.cache_dir_edit = QLineEdit()
        cache_dir_layout.addWidget(self.cache_dir_edit)

        self.browse_cache_btn = QPushButton(tr("Browse..."))
        self.browse_cache_btn.clicked.connect(self._browse_cache_dir)
        cache_dir_layout.addWidget(self.browse_cache_btn)

        cache_layout.addRow(tr("Cache Directory:"), cache_dir_layout)

        # Cache size limit
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 100000)
        self.cache_size_spin.setValue(1000)
        self.cache_size_spin.setSuffix(tr(" MB"))
        cache_layout.addRow(tr("Cache Size Limit:"), self.cache_size_spin)

        layout.addWidget(cache_group)

        # Processing group
        processing_group = QGroupBox(tr("Processing"))
        processing_layout = QFormLayout(processing_group)

        # Number of worker threads
        self.worker_threads_spin = QSpinBox()
        self.worker_threads_spin.setRange(1, 16)
        self.worker_threads_spin.setValue(4)
        processing_layout.addRow(tr("Worker Threads:"), self.worker_threads_spin)

        # Use numba acceleration
        self.numba_check = QCheckBox(tr("Use Numba acceleration (requires restart)"))
        processing_layout.addRow(tr("Acceleration:"), self.numba_check)

        layout.addWidget(processing_group)

        layout.addStretch()

        # Connect cache enable to controls
        self.disk_cache_check.toggled.connect(self._on_cache_enabled)
        self._on_cache_enabled(False)

    def _browse_cache_dir(self):
        """Browse for cache directory"""
        directory = QFileDialog.getExistingDirectory(
            self, tr("Select Cache Directory"), self.cache_dir_edit.text(),
        )
        if directory:
            self.cache_dir_edit.setText(directory)

    def _on_cache_enabled(self, enabled: bool):
        """Handle cache enable/disable"""
        self.cache_dir_edit.setEnabled(enabled)
        self.browse_cache_btn.setEnabled(enabled)
        self.cache_size_spin.setEnabled(enabled)

    def _load_settings(self):
        """Load performance settings"""
        settings = QSettings()

        # Memory settings
        memory_cache = settings.value("performance/memory_cache_mb", 512, type=int)
        self.memory_cache_spin.setValue(memory_cache)

        max_datasets = settings.value("performance/max_datasets", 10, type=int)
        self.max_datasets_spin.setValue(max_datasets)

        # Cache settings
        cache_enabled = settings.value("cache/enabled", True, type=bool)
        self.disk_cache_check.setChecked(cache_enabled)

        from pathlib import Path
        default_cache_dir = str(Path.home() / ".platform_base" / "cache")
        cache_dir = settings.value("cache/directory", default_cache_dir)
        self.cache_dir_edit.setText(cache_dir)

        cache_size = settings.value("cache/size_limit_mb", 1000, type=int)
        self.cache_size_spin.setValue(cache_size)

        # Processing settings
        worker_threads = settings.value("processing/worker_threads", 4, type=int)
        self.worker_threads_spin.setValue(worker_threads)

        numba_enabled = settings.value("processing/use_numba", True, type=bool)
        self.numba_check.setChecked(numba_enabled)

    def save_settings(self):
        """Save performance settings"""
        settings = QSettings()

        # Memory settings
        settings.setValue("performance/memory_cache_mb", self.memory_cache_spin.value())
        settings.setValue("performance/max_datasets", self.max_datasets_spin.value())

        # Cache settings
        settings.setValue("cache/enabled", self.disk_cache_check.isChecked())
        settings.setValue("cache/directory", self.cache_dir_edit.text())
        settings.setValue("cache/size_limit_mb", self.cache_size_spin.value())

        # Processing settings
        settings.setValue("processing/worker_threads", self.worker_threads_spin.value())
        settings.setValue("processing/use_numba", self.numba_check.isChecked())


class LoggingSettingsTab(QWidget):
    """Logging configuration settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Logging level group
        level_group = QGroupBox(tr("Logging Level"))
        level_layout = QFormLayout(level_group)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        level_layout.addRow(tr("Log Level:"), self.log_level_combo)

        layout.addWidget(level_group)

        # Log destinations group
        destinations_group = QGroupBox(tr("Log Destinations"))
        destinations_layout = QFormLayout(destinations_group)

        # Console logging
        self.console_check = QCheckBox(tr("Log to console"))
        destinations_layout.addRow(tr("Console:"), self.console_check)

        # File logging
        self.file_check = QCheckBox(tr("Log to file"))
        destinations_layout.addRow(tr("File:"), self.file_check)

        # Log file path
        file_layout = QHBoxLayout()
        self.log_file_edit = QLineEdit()
        file_layout.addWidget(self.log_file_edit)

        self.browse_log_btn = QPushButton(tr("Browse..."))
        self.browse_log_btn.clicked.connect(self._browse_log_file)
        file_layout.addWidget(self.browse_log_btn)

        destinations_layout.addRow(tr("Log File:"), file_layout)

        layout.addWidget(destinations_group)

        # Log format group
        format_group = QGroupBox(tr("Log Format"))
        format_layout = QVBoxLayout(format_group)

        self.format_edit = QTextEdit()
        self.format_edit.setMaximumHeight(60)
        self.format_edit.setPlainText(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        format_layout.addWidget(self.format_edit)

        layout.addWidget(format_group)

        layout.addStretch()

        # Connect file logging to controls
        self.file_check.toggled.connect(self._on_file_logging_enabled)
        self._on_file_logging_enabled(False)

    def _browse_log_file(self):
        """Browse for log file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr("Select Log File"), self.log_file_edit.text(),
            tr("Log Files (*.log);;Text Files (*.txt);;All Files (*)"),
        )
        if filepath:
            self.log_file_edit.setText(filepath)

    def _on_file_logging_enabled(self, enabled: bool):
        """Handle file logging enable/disable"""
        self.log_file_edit.setEnabled(enabled)
        self.browse_log_btn.setEnabled(enabled)

    def _load_settings(self):
        """Load logging settings"""
        settings = QSettings()

        # Log level
        log_level = settings.value("logging/level", "INFO")
        index = self.log_level_combo.findText(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)

        # Destinations
        console_enabled = settings.value("logging/console", True, type=bool)
        self.console_check.setChecked(console_enabled)

        file_enabled = settings.value("logging/file", False, type=bool)
        self.file_check.setChecked(file_enabled)

        from pathlib import Path
        default_log_file = str(Path.home() / ".platform_base" / "logs" / "app.log")
        log_file = settings.value("logging/file_path", default_log_file)
        self.log_file_edit.setText(log_file)

        # Format
        default_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        log_format = settings.value("logging/format", default_format)
        self.format_edit.setPlainText(log_format)

    def save_settings(self):
        """Save logging settings"""
        settings = QSettings()

        settings.setValue("logging/level", self.log_level_combo.currentText())
        settings.setValue("logging/console", self.console_check.isChecked())
        settings.setValue("logging/file", self.file_check.isChecked())
        settings.setValue("logging/file_path", self.log_file_edit.text())
        settings.setValue("logging/format", self.format_edit.toPlainText())


class SettingsDialog(QDialog, UiLoaderMixin):
    """
    Application settings dialog.

    Features:
    - Tabbed settings interface
    - General application settings
    - Performance and caching options
    - Logging configuration
    - Settings persistence with QSettings
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "settingsDialog.ui"

    def __init__(self, session_state: SessionState, parent: QWidget | None = None):
        super().__init__(parent)

        self.session_state = session_state
        self.settings_tabs = []

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

        logger.debug("settings_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui
        
        Conecta widgets definidos no arquivo .ui aos handlers Python.
        """
        try:
            self.tabs = self.findChild(QTabWidget, "settingsTabs")
            self.apply_btn = self.findChild(QPushButton, "applyButton")
            self.ok_btn = self.findChild(QPushButton, "okButton")
            self.cancel_btn = self.findChild(QPushButton, "cancelButton")
            
            if self.tabs is None:
                logger.debug("settings_dialog_ui_widgets_not_found")
                return
                
            if self.apply_btn:
                self.apply_btn.clicked.connect(self._apply_settings)
            if self.ok_btn:
                self.ok_btn.clicked.connect(self.accept)
            if self.cancel_btn:
                self.cancel_btn.clicked.connect(self.reject)
                
            logger.debug("settings_dialog_ui_loaded_from_file")
            
        except Exception as e:
            logger.warning(f"settings_dialog_ui_setup_failed: {e}")

    @pyqtSlot()
    def _restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self, tr("Restore Defaults"),
            tr("Are you sure you want to restore all settings to their default values?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear all settings
            settings = QSettings()
            settings.clear()

            # Reload all tabs
            for tab in self.settings_tabs:
                tab._load_settings()

            QMessageBox.information(self, tr("Settings"), tr("Default settings restored."))

    @pyqtSlot()
    def _apply_settings(self):
        """Apply current settings without closing"""
        try:
            # Save all settings
            for tab in self.settings_tabs:
                tab.save_settings()

            # Apply theme change immediately if needed
            current_theme = self.general_tab.theme_combo.currentText()
            self.session_state.set_theme(current_theme.lower())

            logger.info("settings_applied")

        except Exception as e:
            QMessageBox.critical(self, tr("Settings Error"), f"{tr('Failed to apply settings')}:\\n{e}")
            logger.exception("settings_apply_failed", error=str(e))

    @pyqtSlot()
    def _ok_clicked(self):
        """Apply settings and close dialog"""
        self._apply_settings()
        self.accept()

    def get_cache_config(self) -> dict[str, Any]:
        """Get current cache configuration"""
        return {
            "enabled": self.performance_tab.disk_cache_check.isChecked(),
            "path": self.performance_tab.cache_dir_edit.text(),
            "size_limit_mb": self.performance_tab.cache_size_spin.value(),
            "memory_limit_mb": self.performance_tab.memory_cache_spin.value(),
        }
