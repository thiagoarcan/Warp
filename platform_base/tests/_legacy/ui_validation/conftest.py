# -*- coding: utf-8 -*-
"""
Fixtures for UI Validation Tests
================================

Provides Qt fixtures and utilities for automated UI testing.
"""
from __future__ import annotations

import gc
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


if TYPE_CHECKING:
    from collections.abc import Generator

    from PyQt6.QtWidgets import QApplication, QWidget


# =============================================================================
# Constants
# =============================================================================

UI_FILES_DIR = Path(__file__).parent.parent.parent / "src" / "platform_base" / "desktop" / "ui_files"
RESOURCES_DIR = Path(__file__).parent.parent.parent / "src" / "platform_base" / "desktop" / "resources"


# =============================================================================
# Session-scoped fixtures
# =============================================================================

@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """Create a single QApplication instance for all tests."""
    # Set offscreen platform for CI
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    
    from PyQt6.QtWidgets import QApplication
    
    # Check if app already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(["--platform", "offscreen"])
    
    yield app
    
    # Cleanup
    app.processEvents()


@pytest.fixture(scope="session")
def ui_files_dir() -> Path:
    """Return path to UI files directory."""
    return UI_FILES_DIR


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    """Return path to resources directory."""
    return RESOURCES_DIR


@pytest.fixture(scope="session")
def all_ui_files(ui_files_dir: Path) -> list[Path]:
    """Get list of all .ui files in the project."""
    if not ui_files_dir.exists():
        pytest.skip(f"UI files directory not found: {ui_files_dir}")
    return list(ui_files_dir.glob("*.ui"))


@pytest.fixture(scope="session")
def ui_file_contents(all_ui_files: list[Path]) -> dict[str, ET.Element]:
    """Parse all UI files and return their XML roots."""
    contents = {}
    for ui_file in all_ui_files:
        try:
            tree = ET.parse(ui_file)
            contents[ui_file.name] = tree.getroot()
        except ET.ParseError:
            contents[ui_file.name] = None
    return contents


# =============================================================================
# Module-scoped fixtures
# =============================================================================

@pytest.fixture(scope="module")
def dataset_store():
    """Create DatasetStore for testing."""
    from platform_base.core.dataset_store import DatasetStore
    return DatasetStore()


@pytest.fixture(scope="module")
def session_state(dataset_store):
    """Create SessionState for testing."""
    from platform_base.desktop.session_state import SessionState
    return SessionState(dataset_store)


@pytest.fixture(scope="module")
def signal_hub():
    """Create SignalHub for testing."""
    from platform_base.desktop.signal_hub import SignalHub
    return SignalHub()


# =============================================================================
# Function-scoped fixtures
# =============================================================================

@pytest.fixture
def mock_session_state() -> MagicMock:
    """Create mock SessionState."""
    mock = MagicMock()
    mock.current_dataset = None
    mock.datasets = {}
    mock.selected_series = []
    mock.get_dataset.return_value = None
    return mock


@pytest.fixture
def mock_signal_hub() -> MagicMock:
    """Create mock SignalHub."""
    mock = MagicMock()
    mock.dataset_loaded = MagicMock()
    mock.series_selected = MagicMock()
    mock.plot_updated = MagicMock()
    return mock


@pytest.fixture
def temp_ui_file(tmp_path: Path) -> Path:
    """Create a temporary valid UI file for testing."""
    ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>TestDialog</class>
 <widget class="QDialog" name="TestDialog">
  <property name="geometry">
   <rect><x>0</x><y>0</y><width>400</width><height>300</height></rect>
  </property>
  <property name="windowTitle">
   <string>Test Dialog</string>
  </property>
  <widget class="QPushButton" name="testButton">
   <property name="geometry">
    <rect><x>150</x><y>130</y><width>100</width><height>30</height></rect>
   </property>
   <property name="text">
    <string>Test</string>
   </property>
  </widget>
 </widget>
</ui>'''
    ui_file = tmp_path / "test_dialog.ui"
    ui_file.write_text(ui_content, encoding="utf-8")
    return ui_file


@pytest.fixture
def widget_factory(qapp):
    """Factory for creating widgets with automatic cleanup."""
    created_widgets: list[QWidget] = []
    
    def _create_widget(widget_class: type, *args, **kwargs) -> QWidget:
        widget = widget_class(*args, **kwargs)
        created_widgets.append(widget)
        return widget
    
    yield _create_widget
    
    # Cleanup all created widgets
    for widget in created_widgets:
        try:
            widget.close()
            widget.deleteLater()
        except RuntimeError:
            pass  # Widget already deleted
    
    qapp.processEvents()
    gc.collect()


@pytest.fixture
def load_ui_widget(qapp):
    """Load a widget from .ui file."""
    from PyQt6 import uic
    from PyQt6.QtWidgets import QWidget
    
    def _load(ui_path: Path, base_class: type = QWidget) -> QWidget:
        widget = base_class()
        uic.loadUi(str(ui_path), widget)
        return widget
    
    return _load


# =============================================================================
# Utility functions for tests
# =============================================================================

def get_all_widgets(parent: QWidget) -> list[QWidget]:
    """Recursively get all child widgets."""
    widgets = []
    for child in parent.findChildren(QWidget):
        widgets.append(child)
    return widgets


def get_widget_by_name(parent: QWidget, name: str) -> QWidget | None:
    """Find widget by object name."""
    from PyQt6.QtWidgets import QWidget
    return parent.findChild(QWidget, name)


def count_widgets_by_type(parent: QWidget, widget_type: type) -> int:
    """Count widgets of a specific type."""
    return len(parent.findChildren(widget_type))


def validate_ui_xml(ui_path: Path) -> tuple[bool, str]:
    """Validate UI file XML structure."""
    try:
        tree = ET.parse(ui_path)
        root = tree.getroot()
        
        if root.tag != "ui":
            return False, "Root element must be 'ui'"
        
        widget = root.find("widget")
        if widget is None:
            return False, "No widget element found"
        
        return True, "Valid"
    except ET.ParseError as e:
        return False, f"XML parse error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def get_widgets_from_ui_xml(ui_path: Path) -> list[dict[str, str]]:
    """Extract widget definitions from UI XML."""
    widgets = []
    try:
        tree = ET.parse(ui_path)
        for widget in tree.iter("widget"):
            widgets.append({
                "class": widget.get("class", ""),
                "name": widget.get("name", ""),
            })
    except ET.ParseError:
        pass
    return widgets


def get_connections_from_ui_xml(ui_path: Path) -> list[dict[str, str]]:
    """Extract signal/slot connections from UI XML."""
    connections = []
    try:
        tree = ET.parse(ui_path)
        for conn in tree.iter("connection"):
            connections.append({
                "sender": conn.findtext("sender", ""),
                "signal": conn.findtext("signal", ""),
                "receiver": conn.findtext("receiver", ""),
                "slot": conn.findtext("slot", ""),
            })
    except ET.ParseError:
        pass
    return connections


# =============================================================================
# Markers
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "gui: marks tests that require Qt display")
    config.addinivalue_line("markers", "smoke: marks critical path tests")
    config.addinivalue_line("markers", "integration: marks integration tests")
