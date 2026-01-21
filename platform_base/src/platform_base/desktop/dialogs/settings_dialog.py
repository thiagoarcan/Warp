"""
SettingsDialog - Application settings dialog for Platform Base v2.0

Provides interface for configuring application settings.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QGroupBox, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit,
    QFileDialog, QLabel, QSlider, QWidget,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings
from PyQt6.QtGui import QFont

from platform_base.desktop.session_state import SessionState
from platform_base.utils.logging import get_logger

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
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Light", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(9)
        appearance_layout.addRow("Font Size:", self.font_size_spin)
        
        # DPI scaling
        self.dpi_check = QCheckBox("Enable high DPI scaling")
        appearance_layout.addRow("Display:", self.dpi_check)
        
        layout.addWidget(appearance_group)
        
        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setValue(5)
        self.autosave_spin.setSuffix(" minutes")
        behavior_layout.addRow("Auto-save interval:", self.autosave_spin)
        
        # Confirm on exit
        self.confirm_exit_check = QCheckBox("Confirm before exiting")
        behavior_layout.addRow("Exit:", self.confirm_exit_check)
        
        # Remember window state
        self.remember_window_check = QCheckBox("Remember window position and size")
        behavior_layout.addRow("Window:", self.remember_window_check)
        
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
        memory_group = QGroupBox("Memory Management")
        memory_layout = QFormLayout(memory_group)
        
        # Memory cache size
        self.memory_cache_spin = QSpinBox()
        self.memory_cache_spin.setRange(64, 8192)
        self.memory_cache_spin.setValue(512)
        self.memory_cache_spin.setSuffix(" MB")
        memory_layout.addRow("Memory Cache Size:", self.memory_cache_spin)
        
        # Max datasets in memory
        self.max_datasets_spin = QSpinBox()
        self.max_datasets_spin.setRange(1, 100)
        self.max_datasets_spin.setValue(10)
        memory_layout.addRow("Max Datasets in Memory:", self.max_datasets_spin)
        
        layout.addWidget(memory_group)
        
        # Disk cache group
        cache_group = QGroupBox("Disk Cache")
        cache_layout = QFormLayout(cache_group)
        
        # Enable disk cache
        self.disk_cache_check = QCheckBox("Enable disk cache")
        cache_layout.addRow("Cache:", self.disk_cache_check)
        
        # Cache directory
        cache_dir_layout = QHBoxLayout()
        self.cache_dir_edit = QLineEdit()
        cache_dir_layout.addWidget(self.cache_dir_edit)
        
        self.browse_cache_btn = QPushButton("Browse...")
        self.browse_cache_btn.clicked.connect(self._browse_cache_dir)
        cache_dir_layout.addWidget(self.browse_cache_btn)
        
        cache_layout.addRow("Cache Directory:", cache_dir_layout)
        
        # Cache size limit
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 100000)
        self.cache_size_spin.setValue(1000)
        self.cache_size_spin.setSuffix(" MB")
        cache_layout.addRow("Cache Size Limit:", self.cache_size_spin)
        
        layout.addWidget(cache_group)
        
        # Processing group
        processing_group = QGroupBox("Processing")
        processing_layout = QFormLayout(processing_group)
        
        # Number of worker threads
        self.worker_threads_spin = QSpinBox()
        self.worker_threads_spin.setRange(1, 16)
        self.worker_threads_spin.setValue(4)
        processing_layout.addRow("Worker Threads:", self.worker_threads_spin)
        
        # Use numba acceleration
        self.numba_check = QCheckBox("Use Numba acceleration (requires restart)")
        processing_layout.addRow("Acceleration:", self.numba_check)
        
        layout.addWidget(processing_group)
        
        layout.addStretch()
        
        # Connect cache enable to controls
        self.disk_cache_check.toggled.connect(self._on_cache_enabled)
        self._on_cache_enabled(False)
    
    def _browse_cache_dir(self):
        """Browse for cache directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Cache Directory", self.cache_dir_edit.text()
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
        level_group = QGroupBox("Logging Level")
        level_layout = QFormLayout(level_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        level_layout.addRow("Log Level:", self.log_level_combo)
        
        layout.addWidget(level_group)
        
        # Log destinations group
        destinations_group = QGroupBox("Log Destinations")
        destinations_layout = QFormLayout(destinations_group)
        
        # Console logging
        self.console_check = QCheckBox("Log to console")
        destinations_layout.addRow("Console:", self.console_check)
        
        # File logging
        self.file_check = QCheckBox("Log to file")
        destinations_layout.addRow("File:", self.file_check)
        
        # Log file path
        file_layout = QHBoxLayout()
        self.log_file_edit = QLineEdit()
        file_layout.addWidget(self.log_file_edit)
        
        self.browse_log_btn = QPushButton("Browse...")
        self.browse_log_btn.clicked.connect(self._browse_log_file)
        file_layout.addWidget(self.browse_log_btn)
        
        destinations_layout.addRow("Log File:", file_layout)
        
        layout.addWidget(destinations_group)
        
        # Log format group
        format_group = QGroupBox("Log Format")
        format_layout = QVBoxLayout(format_group)
        
        self.format_edit = QTextEdit()
        self.format_edit.setMaximumHeight(60)
        self.format_edit.setPlainText(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
            self, "Select Log File", self.log_file_edit.text(),
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
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


class SettingsDialog(QDialog):
    """
    Application settings dialog.
    
    Features:
    - Tabbed settings interface
    - General application settings
    - Performance and caching options
    - Logging configuration
    - Settings persistence with QSettings
    """
    
    def __init__(self, session_state: SessionState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.settings_tabs = []
        
        self._setup_ui()
        
        logger.debug("settings_dialog_initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Platform Base Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Settings tabs
        self.tabs = QTabWidget()
        
        # General tab
        self.general_tab = GeneralSettingsTab()
        self.tabs.addTab(self.general_tab, "General")
        self.settings_tabs.append(self.general_tab)
        
        # Performance tab
        self.performance_tab = PerformanceSettingsTab()
        self.tabs.addTab(self.performance_tab, "Performance")
        self.settings_tabs.append(self.performance_tab)
        
        # Logging tab
        self.logging_tab = LoggingSettingsTab()
        self.tabs.addTab(self.logging_tab, "Logging")
        self.settings_tabs.append(self.logging_tab)
        
        layout.addWidget(self.tabs)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.defaults_btn = QPushButton("Restore Defaults")
        self.defaults_btn.clicked.connect(self._restore_defaults)
        buttons_layout.addWidget(self.defaults_btn)
        
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(self.apply_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._ok_clicked)
        self.ok_btn.setDefault(True)
        buttons_layout.addWidget(self.ok_btn)
        
        layout.addLayout(buttons_layout)
    
    @pyqtSlot()
    def _restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self, "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all settings
            settings = QSettings()
            settings.clear()
            
            # Reload all tabs
            for tab in self.settings_tabs:
                tab._load_settings()
            
            QMessageBox.information(self, "Settings", "Default settings restored.")
    
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
            QMessageBox.critical(self, "Settings Error", f"Failed to apply settings:\\n{e}")
            logger.error("settings_apply_failed", error=str(e))
    
    @pyqtSlot()
    def _ok_clicked(self):
        """Apply settings and close dialog"""
        self._apply_settings()
        self.accept()
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get current cache configuration"""
        return {
            "enabled": self.performance_tab.disk_cache_check.isChecked(),
            "path": self.performance_tab.cache_dir_edit.text(),
            "size_limit_mb": self.performance_tab.cache_size_spin.value(),
            "memory_limit_mb": self.performance_tab.memory_cache_spin.value()
        }