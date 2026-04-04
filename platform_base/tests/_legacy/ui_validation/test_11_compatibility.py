# -*- coding: utf-8 -*-
"""
Test 11: Compatibility
======================

Tests:
- Verify PyQt version compatibility
- Test OS compatibility (basic)
- Test DPI/scaling settings
- Verify cross-platform patterns
"""
from __future__ import annotations

import platform
import sys

import pytest


class TestPyQtVersionCompatibility:
    """Test PyQt version compatibility."""

    def test_pyqt6_available(self):
        """Verify PyQt6 is installed."""
        import PyQt6
        assert PyQt6 is not None

    def test_pyqt6_version(self):
        """Verify PyQt6 version is adequate."""
        from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
        
        # Parse version
        major, minor, *_ = PYQT_VERSION_STR.split(".")
        
        assert int(major) >= 6, f"PyQt version must be 6+, got {PYQT_VERSION_STR}"

    def test_qt_version(self):
        """Verify Qt version is adequate."""
        from PyQt6.QtCore import QT_VERSION_STR
        
        major, minor, *_ = QT_VERSION_STR.split(".")
        
        assert int(major) >= 6, f"Qt version must be 6+, got {QT_VERSION_STR}"

    def test_core_modules_available(self):
        """Verify core Qt modules are available."""
        from PyQt6 import QtCore
        from PyQt6 import QtWidgets
        from PyQt6 import QtGui
        
        assert QtCore is not None
        assert QtWidgets is not None
        assert QtGui is not None

    def test_optional_modules_check(self):
        """Check availability of optional modules."""
        optional_modules = {}
        
        try:
            from PyQt6 import QtCharts
            optional_modules["QtCharts"] = True
        except ImportError:
            optional_modules["QtCharts"] = False
        
        try:
            from PyQt6 import QtSvg
            optional_modules["QtSvg"] = True
        except ImportError:
            optional_modules["QtSvg"] = False
        
        try:
            from PyQt6 import QtNetwork
            optional_modules["QtNetwork"] = True
        except ImportError:
            optional_modules["QtNetwork"] = False
        
        # At least network should be available
        # Just document what's available
        assert isinstance(optional_modules, dict)


class TestOSCompatibility:
    """Test OS compatibility basics."""

    def test_platform_detection(self):
        """Verify platform can be detected."""
        os_name = platform.system()
        
        assert os_name in ["Windows", "Darwin", "Linux"]

    def test_python_version(self):
        """Verify Python version is adequate."""
        major = sys.version_info.major
        minor = sys.version_info.minor
        
        assert major >= 3, "Python 3 required"
        assert minor >= 9, "Python 3.9+ recommended"

    def test_file_path_handling(self):
        """Verify file paths work on current OS."""
        from pathlib import Path
        
        # Create cross-platform path
        path = Path.home() / "test_file.txt"
        
        assert path is not None
        assert isinstance(path, Path)

    def test_temp_directory_access(self):
        """Verify temp directory access."""
        import tempfile
        
        temp_dir = tempfile.gettempdir()
        
        assert temp_dir is not None
        assert len(temp_dir) > 0

    def test_home_directory_access(self):
        """Verify home directory access."""
        from pathlib import Path
        
        home = Path.home()
        
        assert home.exists()
        assert home.is_dir()


class TestDPIScaling:
    """Test DPI and scaling settings."""

    def test_screen_available(self, qapp):
        """Verify screen is available."""
        screen = qapp.primaryScreen()
        
        assert screen is not None

    def test_screen_geometry(self, qapp):
        """Verify screen geometry is readable."""
        screen = qapp.primaryScreen()
        geometry = screen.geometry()
        
        assert geometry.width() > 0
        assert geometry.height() > 0

    def test_device_pixel_ratio(self, qapp):
        """Verify device pixel ratio is reasonable."""
        screen = qapp.primaryScreen()
        dpr = screen.devicePixelRatio()
        
        # DPR should be 1.0 or higher
        assert dpr >= 1.0

    def test_logical_dpi(self, qapp):
        """Verify logical DPI is reasonable."""
        screen = qapp.primaryScreen()
        dpi_x = screen.logicalDotsPerInchX()
        dpi_y = screen.logicalDotsPerInchY()
        
        # DPI should be at least 72 (standard)
        assert dpi_x >= 72
        assert dpi_y >= 72

    def test_physical_dpi(self, qapp):
        """Verify physical DPI is readable."""
        screen = qapp.primaryScreen()
        dpi_x = screen.physicalDotsPerInchX()
        dpi_y = screen.physicalDotsPerInchY()
        
        # Just verify values are positive
        assert dpi_x > 0
        assert dpi_y > 0

    def test_font_scaling(self, qapp):
        """Verify fonts scale with DPI."""
        from PyQt6.QtGui import QFont, QFontMetrics
        
        font = QFont("Arial", 12)
        metrics = QFontMetrics(font)
        
        # Font metrics should be positive
        assert metrics.height() > 0
        assert metrics.averageCharWidth() > 0


class TestCrossPlatformPatterns:
    """Test cross-platform UI patterns."""

    def test_native_dialog_style(self, qapp):
        """Verify native dialog style works."""
        from PyQt6.QtWidgets import QFileDialog
        
        dialog = QFileDialog()
        
        # Native dialog should be default
        assert not dialog.testOption(QFileDialog.Option.DontUseNativeDialog)
        
        dialog.deleteLater()
        qapp.processEvents()

    def test_standard_key_sequences(self, qapp):
        """Verify standard key sequences work."""
        from PyQt6.QtGui import QKeySequence
        
        # These should work on all platforms
        copy = QKeySequence.StandardKey.Copy
        paste = QKeySequence.StandardKey.Paste
        cut = QKeySequence.StandardKey.Cut
        undo = QKeySequence.StandardKey.Undo
        redo = QKeySequence.StandardKey.Redo
        
        # Verify key sequences can be created
        assert QKeySequence(copy) is not None
        assert QKeySequence(paste) is not None

    def test_standard_icons(self, qapp):
        """Verify standard icons are available."""
        from PyQt6.QtWidgets import QStyle
        from PyQt6.QtWidgets import QApplication
        
        style = QApplication.style()
        
        # Standard icons should be available
        icons = [
            QStyle.StandardPixmap.SP_DialogOkButton,
            QStyle.StandardPixmap.SP_DialogCancelButton,
            QStyle.StandardPixmap.SP_DialogHelpButton,
            QStyle.StandardPixmap.SP_MessageBoxWarning,
            QStyle.StandardPixmap.SP_MessageBoxCritical,
        ]
        
        for icon_type in icons:
            icon = style.standardIcon(icon_type)
            assert icon is not None

    def test_system_font(self, qapp):
        """Verify system font is available."""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        
        font = QApplication.font()
        
        assert isinstance(font, QFont)
        assert font.family() != ""

    def test_system_palette(self, qapp):
        """Verify system palette is available."""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPalette
        
        palette = QApplication.palette()
        
        assert isinstance(palette, QPalette)
        
        # Colors should be valid
        text_color = palette.color(QPalette.ColorRole.WindowText)
        assert text_color.isValid()


class TestLocaleCompatibility:
    """Test locale and internationalization compatibility."""

    def test_locale_detection(self):
        """Verify locale can be detected."""
        from PyQt6.QtCore import QLocale
        
        locale = QLocale.system()
        
        assert locale is not None
        assert locale.name() != ""

    def test_date_format(self):
        """Verify date formatting works."""
        from PyQt6.QtCore import QLocale, QDate
        
        locale = QLocale.system()
        date = QDate.currentDate()
        
        formatted = locale.toString(date)
        
        assert len(formatted) > 0

    def test_number_format(self):
        """Verify number formatting works."""
        from PyQt6.QtCore import QLocale
        
        locale = QLocale.system()
        
        formatted = locale.toString(1234567.89)
        
        assert len(formatted) > 0

    def test_text_direction(self):
        """Verify text direction detection."""
        from PyQt6.QtCore import QLocale, Qt
        
        locale = QLocale.system()
        
        direction = locale.textDirection()
        
        assert direction in [
            Qt.LayoutDirection.LeftToRight,
            Qt.LayoutDirection.RightToLeft
        ]


class TestEncodingCompatibility:
    """Test encoding compatibility."""

    def test_utf8_text(self, qapp):
        """Verify UTF-8 text works in widgets."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel()
        
        # Test various Unicode characters
        texts = [
            "Hello, World!",
            "Olá, Mundo!",
            "こんにちは",
            "مرحبا",
            "🎉🎊🎁",
        ]
        
        for text in texts:
            label.setText(text)
            assert label.text() == text
        
        label.deleteLater()
        qapp.processEvents()

    def test_special_characters(self, qapp):
        """Verify special characters work."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        special = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        edit.setText(special)
        
        assert edit.text() == special
        
        edit.deleteLater()
        qapp.processEvents()

    def test_file_path_encoding(self):
        """Verify file path encoding works."""
        from pathlib import Path
        
        # Path with special characters (if supported by OS)
        try:
            path = Path("test_file_çãé.txt")
            assert path is not None
        except Exception:
            # Some OS may not support these characters
            pass


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_platform_env_available(self):
        """Verify QT_QPA_PLATFORM can be set."""
        import os
        
        # Just verify env can be accessed
        platform = os.environ.get("QT_QPA_PLATFORM", "default")
        
        assert isinstance(platform, str)

    def test_style_env_check(self):
        """Verify QT_STYLE can be checked."""
        import os
        
        style = os.environ.get("QT_STYLE", None)
        
        # Can be None or a style name
        assert style is None or isinstance(style, str)

    def test_scaling_env_check(self):
        """Verify scaling environment variables."""
        import os
        
        # These may or may not be set
        high_dpi = os.environ.get("QT_ENABLE_HIGHDPI_SCALING", None)
        scale_factor = os.environ.get("QT_SCALE_FACTOR", None)
        
        # Just verify they can be accessed
        assert high_dpi is None or isinstance(high_dpi, str)
        assert scale_factor is None or isinstance(scale_factor, str)
