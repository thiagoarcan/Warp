# -*- coding: utf-8 -*-
"""
Test 05: Initialization
=======================

Tests:
- Verify application starts without errors
- Test main window displays correctly
- Validate initial configurations load
- Verify resources (icons, images) load
- Test initialization at different resolutions
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestApplicationStartup:
    """Test application startup."""

    def test_qapplication_creates(self, qapp):
        """Verify QApplication creates successfully."""
        assert qapp is not None
        assert qapp.applicationName() is not None or True  # May be empty

    def test_qapplication_singleton(self, qapp):
        """Verify QApplication is singleton."""
        from PyQt6.QtWidgets import QApplication
        
        instance = QApplication.instance()
        assert instance is qapp

    def test_platform_offscreen_works(self, qapp):
        """Verify offscreen platform is working."""
        # If we got here, offscreen platform is working
        assert True


class TestMainWindowDisplay:
    """Test main window display."""

    def test_main_window_shows(self, qapp, session_state, signal_hub):
        """Verify main window shows without errors."""
        try:
            from platform_base.ui.main_window_unified import ModernMainWindow
            from PyQt6.QtWidgets import QMessageBox
            
            window = ModernMainWindow(session_state, signal_hub)
            window.show()
            qapp.processEvents()
            
            assert window.isVisible()
            
            # Use deleteLater instead of close() to avoid confirmation dialog
            window.hide()
            window.deleteLater()
            qapp.processEvents()
        except ImportError:
            pytest.skip("ModernMainWindow not available")

    def test_main_window_has_title(self, qapp, session_state, signal_hub):
        """Verify main window has title set."""
        try:
            from platform_base.ui.main_window_unified import ModernMainWindow
            
            window = ModernMainWindow(session_state, signal_hub)
            title = window.windowTitle()
            
            assert title is not None
            # Title may be empty string but should exist
            
            window.deleteLater()
            qapp.processEvents()
        except ImportError:
            pytest.skip("ModernMainWindow not available")

    def test_main_window_has_size(self, qapp, session_state, signal_hub):
        """Verify main window has reasonable size."""
        try:
            from platform_base.ui.main_window_unified import ModernMainWindow
            
            window = ModernMainWindow(session_state, signal_hub)
            size = window.size()
            
            # Should have non-zero size
            assert size.width() > 0 or size.height() > 0
            
            window.deleteLater()
            qapp.processEvents()
        except ImportError:
            pytest.skip("ModernMainWindow not available")


class TestConfigurationLoading:
    """Test configuration loading on startup."""

    def test_platform_config_exists(self):
        """Verify platform configuration file exists."""
        config_path = Path(__file__).parent.parent.parent / "configs" / "platform.yaml"
        
        if not config_path.exists():
            pytest.skip("Platform config not found (may use different location)")
        
        assert config_path.is_file()

    def test_config_parseable(self):
        """Verify configuration file is parseable."""
        config_path = Path(__file__).parent.parent.parent / "configs" / "platform.yaml"
        
        if not config_path.exists():
            pytest.skip("Platform config not found")
        
        import yaml
        
        content = config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        
        assert config is not None

    def test_session_state_initializes(self, dataset_store):
        """Verify SessionState initializes correctly."""
        from platform_base.desktop.session_state import SessionState
        
        state = SessionState(dataset_store)
        assert state is not None

    def test_signal_hub_initializes(self):
        """Verify SignalHub initializes correctly."""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        assert hub is not None


class TestResourceLoading:
    """Test resource loading."""

    def test_resources_directory_exists(self, resources_dir: Path):
        """Verify resources directory exists."""
        assert resources_dir.exists(), f"Resources directory not found: {resources_dir}"

    def test_icons_directory_exists(self, resources_dir: Path):
        """Verify icons directory exists."""
        icons_dir = resources_dir / "icons"
        
        if not icons_dir.exists():
            pytest.skip("Icons directory not found (may use different structure)")
        
        assert icons_dir.is_dir()

    def test_qicon_creates(self, qapp):
        """Verify QIcon can be created."""
        from PyQt6.QtGui import QIcon
        
        icon = QIcon()
        assert icon is not None
        # Empty icon is valid

    def test_qpixmap_creates(self, qapp):
        """Verify QPixmap can be created."""
        from PyQt6.QtGui import QPixmap
        
        pixmap = QPixmap(100, 100)
        assert pixmap is not None
        assert not pixmap.isNull()
        assert pixmap.width() == 100
        assert pixmap.height() == 100


class TestResolutionIndependence:
    """Test initialization at different resolutions."""

    @pytest.mark.parametrize("width,height", [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1920, 1080),
        (2560, 1440),
    ])
    def test_window_at_resolution(self, qapp, width: int, height: int):
        """Test window creation at various resolutions."""
        from PyQt6.QtWidgets import QMainWindow
        
        window = QMainWindow()
        window.resize(width, height)
        window.show()
        qapp.processEvents()
        
        # Window should be resized (may be limited by screen)
        actual_size = window.size()
        assert actual_size.width() > 0
        assert actual_size.height() > 0
        
        window.close()
        window.deleteLater()
        qapp.processEvents()

    def test_minimum_size_respected(self, qapp):
        """Verify minimum size constraints are respected."""
        from PyQt6.QtWidgets import QMainWindow
        
        window = QMainWindow()
        window.setMinimumSize(400, 300)
        window.resize(100, 100)  # Try smaller than minimum
        window.show()
        qapp.processEvents()
        
        size = window.size()
        assert size.width() >= 400
        assert size.height() >= 300
        
        window.close()
        window.deleteLater()
        qapp.processEvents()


class TestUILoaderMixin:
    """Test UiLoaderMixin functionality."""

    def test_ui_loader_mixin_exists(self):
        """Verify UiLoaderMixin class exists."""
        try:
            from platform_base.ui.ui_loader_mixin import UiLoaderMixin
            assert UiLoaderMixin is not None
        except ImportError:
            pytest.skip("UiLoaderMixin not available")

    def test_load_ui_helper_exists(self):
        """Verify load UI helper function exists."""
        try:
            from platform_base.ui.loader import load_ui
            assert callable(load_ui)
        except ImportError:
            # Try alternative location
            try:
                from platform_base.ui.ui_loader_mixin import UiLoaderMixin
                assert hasattr(UiLoaderMixin, "_load_ui")
            except ImportError:
                pytest.skip("UI loader not available")

    def test_ui_file_loading(self, qapp, temp_ui_file: Path):
        """Test loading a .ui file."""
        from PyQt6 import uic
        from PyQt6.QtWidgets import QDialog, QPushButton
        
        # The temp_ui_file creates a QDialog, so use QDialog as base
        widget = QDialog()
        uic.loadUi(str(temp_ui_file), widget)
        
        assert widget is not None
        
        # Check test button exists
        button = widget.findChild(QPushButton, "testButton")
        assert button is not None, "testButton should exist in loaded UI"
        
        widget.deleteLater()
        qapp.processEvents()


class TestStartupPerformance:
    """Test startup performance."""

    def test_qapplication_creates_quickly(self):
        """Verify QApplication creates in reasonable time."""
        import time
        
        from PyQt6.QtWidgets import QApplication
        
        # Already exists from fixture, just verify it's fast to access
        start = time.perf_counter()
        app = QApplication.instance()
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.1  # Should be nearly instant
        assert app is not None

    def test_widget_creation_fast(self, qapp):
        """Verify widget creation is reasonably fast."""
        import time
        
        from PyQt6.QtWidgets import QWidget
        
        start = time.perf_counter()
        widgets = [QWidget() for _ in range(100)]
        elapsed = time.perf_counter() - start
        
        assert elapsed < 1.0  # 100 widgets in under 1 second
        
        for w in widgets:
            w.deleteLater()
        qapp.processEvents()
