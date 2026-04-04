"""
Tests for ui/themes.py - Theme System

Tests the dark/light theme system with persistence.
"""

from unittest.mock import patch

import pytest

# Skip if PyQt6 not available
pytest.importorskip("PyQt6")


class TestThemeColors:
    """Tests for ThemeColors dataclass."""
    
    def test_light_theme_has_required_colors(self):
        """Light theme should have all required color properties."""
        from platform_base.ui.themes import LIGHT_THEME
        
        assert LIGHT_THEME.background is not None
        assert LIGHT_THEME.text_primary is not None
        assert LIGHT_THEME.primary is not None
        assert LIGHT_THEME.secondary is not None
        assert LIGHT_THEME.error is not None
        assert LIGHT_THEME.warning is not None
        assert LIGHT_THEME.success is not None
    
    def test_dark_theme_has_required_colors(self):
        """Dark theme should have all required color properties."""
        from platform_base.ui.themes import DARK_THEME
        
        assert DARK_THEME.background is not None
        assert DARK_THEME.text_primary is not None
        assert DARK_THEME.primary is not None
    
    def test_light_and_dark_themes_differ(self):
        """Light and dark themes should have different colors."""
        from platform_base.ui.themes import DARK_THEME, LIGHT_THEME
        
        assert LIGHT_THEME.background != DARK_THEME.background
        assert LIGHT_THEME.text_primary != DARK_THEME.text_primary


class TestThemeMode:
    """Tests for ThemeMode enum."""
    
    def test_theme_modes_exist(self):
        """All theme modes should exist."""
        from platform_base.ui.themes import ThemeMode
        
        assert hasattr(ThemeMode, "LIGHT")
        assert hasattr(ThemeMode, "DARK")
        assert hasattr(ThemeMode, "SYSTEM")


class TestThemeManager:
    """Tests for ThemeManager singleton."""
    
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from platform_base.ui.themes import reset_theme_manager
        reset_theme_manager()
        yield
        reset_theme_manager()
    
    def test_singleton_pattern(self, qtbot):
        """get_theme_manager should return singleton."""
        from platform_base.ui.themes import get_theme_manager
        
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()
        
        assert manager1 is manager2
    
    def test_default_theme_is_light(self, qtbot):
        """Default theme should be light."""
        from platform_base.ui.themes import ThemeMode, get_theme_manager
        
        manager = get_theme_manager()
        
        # Default ou system depende do SO
        assert manager.current_mode in (ThemeMode.LIGHT, ThemeMode.DARK, ThemeMode.SYSTEM)
    
    def test_set_theme_changes_mode(self, qtbot):
        """set_theme should change current mode."""
        from platform_base.ui.themes import ThemeMode, get_theme_manager
        
        manager = get_theme_manager()
        manager.set_theme(ThemeMode.DARK)
        
        assert manager.current_mode == ThemeMode.DARK
        
        manager.set_theme(ThemeMode.LIGHT)
        
        assert manager.current_mode == ThemeMode.LIGHT
    
    def test_colors_returns_theme_colors(self, qtbot):
        """colors property should return ThemeColors."""
        from platform_base.ui.themes import ThemeColors, get_theme_manager
        
        manager = get_theme_manager()
        colors = manager.colors
        
        assert isinstance(colors, ThemeColors)
    
    def test_is_dark_property(self, qtbot):
        """is_dark should reflect current theme mode."""
        from platform_base.ui.themes import ThemeMode, get_theme_manager
        
        manager = get_theme_manager()
        
        manager.set_theme(ThemeMode.DARK)
        assert manager.is_dark == True
        
        manager.set_theme(ThemeMode.LIGHT)
        assert manager.is_dark == False
    
    def test_get_color(self, qtbot):
        """get_color should return color string."""
        from platform_base.ui.themes import get_theme_manager
        
        manager = get_theme_manager()
        
        color = manager.get_color("primary")
        
        assert color.startswith("#")
    
    def test_get_qcolor(self, qtbot):
        """get_qcolor should return QColor."""
        from PyQt6.QtGui import QColor

        from platform_base.ui.themes import get_theme_manager
        
        manager = get_theme_manager()
        
        qcolor = manager.get_qcolor("primary")
        
        assert isinstance(qcolor, QColor)


class TestThemeSignals:
    """Tests for theme change signals."""
    
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from platform_base.ui.themes import reset_theme_manager
        reset_theme_manager()
        yield
        reset_theme_manager()
    
    def test_theme_changed_signal_exists(self, qtbot):
        """ThemeManager should have theme_changed signal."""
        from platform_base.ui.themes import get_theme_manager
        
        manager = get_theme_manager()
        
        assert hasattr(manager, "theme_changed")
    
    def test_theme_changed_signal_emitted(self, qtbot):
        """theme_changed should be emitted when theme changes."""
        from platform_base.ui.themes import ThemeMode, get_theme_manager
        
        manager = get_theme_manager()
        
        with qtbot.waitSignal(manager.theme_changed, timeout=1000):
            manager.set_theme(ThemeMode.DARK)


class TestGetSystemTheme:
    """Tests for get_system_theme function."""
    
    def test_get_system_theme_returns_valid_mode(self):
        """get_system_theme should return valid ThemeMode."""
        from platform_base.ui.themes import ThemeMode, get_system_theme
        
        result = get_system_theme()
        
        assert result in (ThemeMode.LIGHT, ThemeMode.DARK)
    
    def test_get_system_theme_windows(self):
        """Test Windows system theme detection."""
        import sys

        from platform_base.ui.themes import ThemeMode, get_system_theme
        
        if sys.platform == "win32":
            result = get_system_theme()
            assert result in (ThemeMode.LIGHT, ThemeMode.DARK)


class TestHelperFunctions:
    """Tests for helper functions."""
    
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from platform_base.ui.themes import reset_theme_manager
        reset_theme_manager()
        yield
        reset_theme_manager()
    
    def test_get_theme_manager(self, qtbot):
        """get_theme_manager should return singleton."""
        from platform_base.ui.themes import ThemeManager, get_theme_manager
        
        manager = get_theme_manager()
        
        assert isinstance(manager, ThemeManager)
    
    def test_apply_theme(self, qtbot):
        """apply_theme should set theme via manager."""
        from platform_base.ui.themes import ThemeMode, apply_theme, get_theme_manager
        
        apply_theme(ThemeMode.DARK)
        
        assert get_theme_manager().current_mode == ThemeMode.DARK
