"""
Comprehensive tests for ui/accessibility.py module.

Tests accessibility features including keyboard navigation, screen reader support,
high contrast mode, and shortcut management.
"""

from dataclasses import dataclass
from enum import Enum
from unittest.mock import MagicMock, PropertyMock, patch

import pytest


# Test ContrastMode enum
class TestContrastMode:
    """Tests for ContrastMode enum."""
    
    def test_normal_mode_exists(self):
        """Test NORMAL contrast mode exists."""
        from platform_base.ui.accessibility import ContrastMode
        assert hasattr(ContrastMode, 'NORMAL')
    
    def test_high_contrast_mode_exists(self):
        """Test HIGH_CONTRAST mode exists."""
        from platform_base.ui.accessibility import ContrastMode
        assert hasattr(ContrastMode, 'HIGH_CONTRAST')
    
    def test_high_contrast_dark_mode_exists(self):
        """Test HIGH_CONTRAST_DARK mode exists."""
        from platform_base.ui.accessibility import ContrastMode
        assert hasattr(ContrastMode, 'HIGH_CONTRAST_DARK')
    
    def test_modes_are_unique(self):
        """Test all modes have unique values."""
        from platform_base.ui.accessibility import ContrastMode
        values = [mode.value for mode in ContrastMode]
        assert len(values) == len(set(values))
    
    def test_contrast_mode_is_enum(self):
        """Test ContrastMode is an Enum."""
        from platform_base.ui.accessibility import ContrastMode
        assert issubclass(ContrastMode, Enum)


class TestAccessibilityConfig:
    """Tests for AccessibilityConfig dataclass."""
    
    def test_default_config_creation(self):
        """Test creating config with defaults."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        assert config.enable_keyboard_navigation is True
        assert config.tab_order_logical is True
        assert config.show_focus_indicators is True
    
    def test_focus_indicator_defaults(self):
        """Test focus indicator default values."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        assert config.focus_indicator_width == 2
        assert config.focus_indicator_color == "#0078D4"
    
    def test_screen_reader_defaults(self):
        """Test screen reader default values."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        assert config.enable_screen_reader is True
        assert config.announce_on_focus is True
        assert config.verbose_descriptions is False
    
    def test_contrast_defaults(self):
        """Test contrast default values."""
        from platform_base.ui.accessibility import AccessibilityConfig, ContrastMode
        config = AccessibilityConfig()
        assert config.contrast_mode == ContrastMode.NORMAL
        assert config.minimum_contrast_ratio == 4.5  # WCAG AA
    
    def test_zoom_defaults(self):
        """Test zoom default values."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        assert config.enable_ui_zoom is True
        assert config.zoom_level == 1.0
        assert config.min_zoom == 1.0
        assert config.max_zoom == 2.0
    
    def test_audio_feedback_default(self):
        """Test audio feedback default."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        assert config.enable_audio_feedback is False
    
    def test_skip_links_default(self):
        """Test skip links default."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        assert config.enable_skip_links is True
    
    def test_custom_config_values(self):
        """Test creating config with custom values."""
        from platform_base.ui.accessibility import AccessibilityConfig, ContrastMode
        config = AccessibilityConfig(
            enable_keyboard_navigation=False,
            contrast_mode=ContrastMode.HIGH_CONTRAST,
            zoom_level=1.5,
            enable_audio_feedback=True,
        )
        assert config.enable_keyboard_navigation is False
        assert config.contrast_mode == ContrastMode.HIGH_CONTRAST
        assert config.zoom_level == 1.5
        assert config.enable_audio_feedback is True


class TestShortcutDefinition:
    """Tests for ShortcutDefinition dataclass."""
    
    def test_create_basic_shortcut(self):
        """Test creating basic shortcut definition."""
        from platform_base.ui.accessibility import ShortcutDefinition
        shortcut = ShortcutDefinition(
            key_sequence="Ctrl+O",
            action_name="file_open",
            description="Abrir arquivo",
        )
        assert shortcut.key_sequence == "Ctrl+O"
        assert shortcut.action_name == "file_open"
        assert shortcut.description == "Abrir arquivo"
    
    def test_shortcut_default_category(self):
        """Test shortcut default category."""
        from platform_base.ui.accessibility import ShortcutDefinition
        shortcut = ShortcutDefinition(
            key_sequence="Ctrl+S",
            action_name="file_save",
            description="Salvar",
        )
        assert shortcut.category == "General"
    
    def test_shortcut_default_enabled(self):
        """Test shortcut default enabled state."""
        from platform_base.ui.accessibility import ShortcutDefinition
        shortcut = ShortcutDefinition(
            key_sequence="Ctrl+Z",
            action_name="edit_undo",
            description="Desfazer",
        )
        assert shortcut.enabled is True
    
    def test_shortcut_custom_category(self):
        """Test shortcut with custom category."""
        from platform_base.ui.accessibility import ShortcutDefinition
        shortcut = ShortcutDefinition(
            key_sequence="Space",
            action_name="stream_play",
            description="Play",
            category="Streaming",
        )
        assert shortcut.category == "Streaming"
    
    def test_shortcut_disabled(self):
        """Test creating disabled shortcut."""
        from platform_base.ui.accessibility import ShortcutDefinition
        shortcut = ShortcutDefinition(
            key_sequence="F12",
            action_name="debug_mode",
            description="Debug",
            enabled=False,
        )
        assert shortcut.enabled is False


class TestAccessibleWidget:
    """Tests for AccessibleWidget wrapper class."""
    
    @pytest.fixture
    def mock_widget(self, qtbot):
        """Create mock widget for testing."""
        from PyQt6.QtWidgets import QPushButton
        widget = QPushButton("Test")
        return widget
    
    def test_create_accessible_widget(self, mock_widget):
        """Test creating accessible widget wrapper."""
        from platform_base.ui.accessibility import AccessibleWidget
        wrapper = AccessibleWidget(
            widget=mock_widget,
            accessible_name="Test Button",
            accessible_description="A test button",
        )
        assert wrapper.widget == mock_widget
        assert wrapper._accessible_name == "Test Button"
        assert wrapper._accessible_description == "A test button"
    
    def test_widget_accessible_name_set(self, mock_widget):
        """Test widget accessible name is set."""
        from platform_base.ui.accessibility import AccessibleWidget
        wrapper = AccessibleWidget(
            widget=mock_widget,
            accessible_name="My Button",
        )
        assert mock_widget.accessibleName() == "My Button"
    
    def test_widget_accessible_description_set(self, mock_widget):
        """Test widget accessible description is set."""
        from platform_base.ui.accessibility import AccessibleWidget
        wrapper = AccessibleWidget(
            widget=mock_widget,
            accessible_name="Button",
            accessible_description="Click to submit",
        )
        assert mock_widget.accessibleDescription() == "Click to submit"
    
    def test_update_description(self, mock_widget):
        """Test updating accessible description."""
        from platform_base.ui.accessibility import AccessibleWidget
        wrapper = AccessibleWidget(
            widget=mock_widget,
            accessible_name="Button",
            accessible_description="Old description",
        )
        wrapper.update_description("New description")
        assert wrapper._accessible_description == "New description"
        assert mock_widget.accessibleDescription() == "New description"


class TestKeyboardNavigationManager:
    """Tests for KeyboardNavigationManager class."""
    
    @pytest.fixture
    def mock_main_window(self, qtbot):
        """Create mock main window."""
        from PyQt6.QtWidgets import QMainWindow
        window = QMainWindow()
        return window
    
    @pytest.fixture
    def config(self):
        """Create accessibility config."""
        from platform_base.ui.accessibility import AccessibilityConfig
        return AccessibilityConfig()
    
    def test_create_navigation_manager(self, mock_main_window, config):
        """Test creating keyboard navigation manager."""
        from platform_base.ui.accessibility import KeyboardNavigationManager
        manager = KeyboardNavigationManager(mock_main_window, config)
        assert manager.main_window == mock_main_window
        assert manager.config == config
    
    def test_initial_regions_empty(self, mock_main_window, config):
        """Test initial regions list is empty."""
        from platform_base.ui.accessibility import KeyboardNavigationManager
        manager = KeyboardNavigationManager(mock_main_window, config)
        assert len(manager._regions) == 0
    
    def test_register_region(self, mock_main_window, config, qtbot):
        """Test registering navigation region."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.accessibility import KeyboardNavigationManager
        
        manager = KeyboardNavigationManager(mock_main_window, config)
        widget = QWidget()
        manager.register_region("Test Region", widget)
        assert len(manager._regions) == 1
        assert manager._regions[0] == ("Test Region", widget)
    
    def test_register_multiple_regions(self, mock_main_window, config, qtbot):
        """Test registering multiple navigation regions."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.accessibility import KeyboardNavigationManager
        
        manager = KeyboardNavigationManager(mock_main_window, config)
        widget1 = QWidget()
        widget2 = QWidget()
        widget3 = QWidget()
        
        manager.register_region("Menu", widget1)
        manager.register_region("Data Panel", widget2)
        manager.register_region("Viz Panel", widget3)
        
        assert len(manager._regions) == 3
    
    def test_focus_history_max_limit(self, mock_main_window, config):
        """Test focus history has max limit."""
        from platform_base.ui.accessibility import KeyboardNavigationManager
        manager = KeyboardNavigationManager(mock_main_window, config)
        assert manager._max_history == 50
    
    def test_has_focus_changed_signal(self, mock_main_window, config):
        """Test manager has focus_changed signal."""
        from platform_base.ui.accessibility import KeyboardNavigationManager
        manager = KeyboardNavigationManager(mock_main_window, config)
        assert hasattr(manager, 'focus_changed')
    
    def test_has_navigation_region_changed_signal(self, mock_main_window, config):
        """Test manager has navigation_region_changed signal."""
        from platform_base.ui.accessibility import KeyboardNavigationManager
        manager = KeyboardNavigationManager(mock_main_window, config)
        assert hasattr(manager, 'navigation_region_changed')


class TestShortcutManager:
    """Tests for ShortcutManager class."""
    
    @pytest.fixture
    def mock_main_window(self, qtbot):
        """Create mock main window."""
        from PyQt6.QtWidgets import QMainWindow
        window = QMainWindow()
        return window
    
    def test_create_shortcut_manager(self, mock_main_window):
        """Test creating shortcut manager."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        assert manager.main_window == mock_main_window
    
    def test_default_shortcuts_registered(self, mock_main_window):
        """Test default shortcuts are registered."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        assert len(manager._shortcuts) > 0
    
    def test_has_file_shortcuts(self, mock_main_window):
        """Test file shortcuts are registered."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        # Check for common file shortcuts
        shortcuts_by_action = {
            d.action_name: key 
            for key, (d, _) in manager._shortcuts.items()
        }
        assert "file_open" in shortcuts_by_action
        assert "file_save" in shortcuts_by_action
    
    def test_has_edit_shortcuts(self, mock_main_window):
        """Test edit shortcuts are registered."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        shortcuts_by_action = {
            d.action_name: key 
            for key, (d, _) in manager._shortcuts.items()
        }
        assert "edit_undo" in shortcuts_by_action
        assert "edit_redo" in shortcuts_by_action
    
    def test_has_shortcut_activated_signal(self, mock_main_window):
        """Test manager has shortcut_activated signal."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        assert hasattr(manager, 'shortcut_activated')
    
    def test_has_shortcut_conflict_signal(self, mock_main_window):
        """Test manager has shortcut_conflict signal."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        assert hasattr(manager, 'shortcut_conflict')
    
    def test_register_handler(self, mock_main_window):
        """Test registering action handler."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        
        handler_called = []
        def test_handler():
            handler_called.append(True)
        
        manager.register_handler("test_action", test_handler)
        assert "test_action" in manager._action_handlers
    
    def test_get_shortcut_for_action(self, mock_main_window):
        """Test getting shortcut key for action."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        
        # Should find Ctrl+O for file_open
        key = manager.get_shortcut("file_open")
        assert key == "Ctrl+O"
    
    def test_get_shortcut_nonexistent(self, mock_main_window):
        """Test getting shortcut for nonexistent action."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        
        key = manager.get_shortcut("nonexistent_action")
        assert key is None
    
    def test_get_shortcuts_by_category(self, mock_main_window):
        """Test getting shortcuts organized by category."""
        from platform_base.ui.accessibility import ShortcutManager
        manager = ShortcutManager(mock_main_window)
        
        categorized = manager.get_shortcuts_by_category()
        assert isinstance(categorized, dict)
        assert "Arquivo" in categorized
        assert "Editar" in categorized


class TestHighContrastMode:
    """Tests for HighContrastMode class."""
    
    def test_high_contrast_class_exists(self):
        """Test HighContrastMode class exists."""
        from platform_base.ui.accessibility import HighContrastMode
        assert HighContrastMode is not None
    
    def test_high_contrast_light_palette(self):
        """Test HIGH_CONTRAST_LIGHT palette exists."""
        from platform_base.ui.accessibility import HighContrastMode
        assert hasattr(HighContrastMode, 'HIGH_CONTRAST_LIGHT')
        palette = HighContrastMode.HIGH_CONTRAST_LIGHT
        assert "window" in palette
        assert "text" in palette
    
    def test_light_palette_has_white_background(self):
        """Test light palette has white background."""
        from platform_base.ui.accessibility import HighContrastMode
        palette = HighContrastMode.HIGH_CONTRAST_LIGHT
        assert palette["window"] == "#FFFFFF"
    
    def test_light_palette_has_black_text(self):
        """Test light palette has black text."""
        from platform_base.ui.accessibility import HighContrastMode
        palette = HighContrastMode.HIGH_CONTRAST_LIGHT
        assert palette["text"] == "#000000"


class TestModuleImports:
    """Tests for module imports and exports."""
    
    def test_import_accessibility_module(self):
        """Test accessibility module can be imported."""
        from platform_base.ui import accessibility
        assert accessibility is not None
    
    def test_import_contrast_mode(self):
        """Test ContrastMode can be imported."""
        from platform_base.ui.accessibility import ContrastMode
        assert ContrastMode is not None
    
    def test_import_accessibility_config(self):
        """Test AccessibilityConfig can be imported."""
        from platform_base.ui.accessibility import AccessibilityConfig
        assert AccessibilityConfig is not None
    
    def test_import_shortcut_definition(self):
        """Test ShortcutDefinition can be imported."""
        from platform_base.ui.accessibility import ShortcutDefinition
        assert ShortcutDefinition is not None
    
    def test_import_accessible_widget(self):
        """Test AccessibleWidget can be imported."""
        from platform_base.ui.accessibility import AccessibleWidget
        assert AccessibleWidget is not None
    
    def test_import_keyboard_navigation_manager(self):
        """Test KeyboardNavigationManager can be imported."""
        from platform_base.ui.accessibility import KeyboardNavigationManager
        assert KeyboardNavigationManager is not None
    
    def test_import_shortcut_manager(self):
        """Test ShortcutManager can be imported."""
        from platform_base.ui.accessibility import ShortcutManager
        assert ShortcutManager is not None
    
    def test_import_high_contrast_mode(self):
        """Test HighContrastMode can be imported."""
        from platform_base.ui.accessibility import HighContrastMode
        assert HighContrastMode is not None


class TestDefaultShortcuts:
    """Tests for DEFAULT_SHORTCUTS constant."""
    
    def test_default_shortcuts_exist(self):
        """Test DEFAULT_SHORTCUTS constant exists."""
        from platform_base.ui.accessibility import ShortcutManager
        assert hasattr(ShortcutManager, 'DEFAULT_SHORTCUTS')
        assert len(ShortcutManager.DEFAULT_SHORTCUTS) > 0
    
    def test_file_shortcuts_in_defaults(self):
        """Test file shortcuts are in defaults."""
        from platform_base.ui.accessibility import ShortcutManager
        action_names = [s.action_name for s in ShortcutManager.DEFAULT_SHORTCUTS]
        assert "file_open" in action_names
        assert "file_save" in action_names
        assert "file_export" in action_names
    
    def test_edit_shortcuts_in_defaults(self):
        """Test edit shortcuts are in defaults."""
        from platform_base.ui.accessibility import ShortcutManager
        action_names = [s.action_name for s in ShortcutManager.DEFAULT_SHORTCUTS]
        assert "edit_undo" in action_names
        assert "edit_redo" in action_names
        assert "edit_copy" in action_names
    
    def test_streaming_shortcuts_in_defaults(self):
        """Test streaming shortcuts are in defaults."""
        from platform_base.ui.accessibility import ShortcutManager
        action_names = [s.action_name for s in ShortcutManager.DEFAULT_SHORTCUTS]
        assert "stream_play_pause" in action_names
        assert "stream_stop" in action_names
    
    def test_navigation_shortcuts_in_defaults(self):
        """Test navigation shortcuts are in defaults."""
        from platform_base.ui.accessibility import ShortcutManager
        action_names = [s.action_name for s in ShortcutManager.DEFAULT_SHORTCUTS]
        assert "nav_next_region" in action_names
        assert "nav_prev_region" in action_names
    
    def test_help_shortcuts_in_defaults(self):
        """Test help shortcuts are in defaults."""
        from platform_base.ui.accessibility import ShortcutManager
        action_names = [s.action_name for s in ShortcutManager.DEFAULT_SHORTCUTS]
        assert "help_context" in action_names
    
    def test_all_shortcuts_have_descriptions(self):
        """Test all shortcuts have descriptions."""
        from platform_base.ui.accessibility import ShortcutManager
        for shortcut in ShortcutManager.DEFAULT_SHORTCUTS:
            assert shortcut.description, f"Missing description for {shortcut.action_name}"
    
    def test_all_shortcuts_have_categories(self):
        """Test all shortcuts have categories."""
        from platform_base.ui.accessibility import ShortcutManager
        for shortcut in ShortcutManager.DEFAULT_SHORTCUTS:
            assert shortcut.category, f"Missing category for {shortcut.action_name}"


class TestWCAGCompliance:
    """Tests for WCAG compliance."""
    
    def test_minimum_contrast_ratio_wcag_aa(self):
        """Test default contrast ratio meets WCAG AA."""
        from platform_base.ui.accessibility import AccessibilityConfig
        config = AccessibilityConfig()
        # WCAG AA requires 4.5:1 for normal text
        assert config.minimum_contrast_ratio >= 4.5
    
    def test_high_contrast_colors_are_distinct(self):
        """Test high contrast colors are distinct."""
        from platform_base.ui.accessibility import HighContrastMode
        palette = HighContrastMode.HIGH_CONTRAST_LIGHT
        # Background and text should be very different
        assert palette["window"] != palette["text"]
        assert palette["button"] != palette["button_text"]
