"""
Tests for ui/dialogs/__init__.py - Dialogs Package

Tests for dialog exports and imports.
"""

import pytest


class TestDialogsExports:
    """Tests for dialogs package exports"""

    def test_filter_dialog_import(self):
        """Test FilterDialog can be imported"""
        from platform_base.ui.dialogs import FilterDialog
        
        assert FilterDialog is not None

    def test_settings_dialog_import(self):
        """Test SettingsDialog can be imported"""
        from platform_base.ui.dialogs import SettingsDialog
        
        assert SettingsDialog is not None

    def test_smoothing_dialog_import(self):
        """Test SmoothingDialog can be imported"""
        from platform_base.ui.dialogs import SmoothingDialog
        
        assert SmoothingDialog is not None

    def test_app_settings_import(self):
        """Test AppSettings can be imported"""
        from platform_base.ui.dialogs import AppSettings
        
        assert AppSettings is not None

    def test_show_filter_dialog_import(self):
        """Test show_filter_dialog function can be imported"""
        from platform_base.ui.dialogs import show_filter_dialog
        
        assert callable(show_filter_dialog)

    def test_show_settings_dialog_import(self):
        """Test show_settings_dialog function can be imported"""
        from platform_base.ui.dialogs import show_settings_dialog
        
        assert callable(show_settings_dialog)

    def test_show_smoothing_dialog_import(self):
        """Test show_smoothing_dialog function can be imported"""
        from platform_base.ui.dialogs import show_smoothing_dialog
        
        assert callable(show_smoothing_dialog)

    def test_load_app_settings_import(self):
        """Test load_app_settings function can be imported"""
        from platform_base.ui.dialogs import load_app_settings
        
        assert callable(load_app_settings)


class TestDialogsAll:
    """Tests for __all__ exports"""

    def test_all_exists(self):
        """Test __all__ is defined"""
        from platform_base.ui import dialogs
        
        assert hasattr(dialogs, "__all__")

    def test_all_contains_filter_dialog(self):
        """Test __all__ contains FilterDialog"""
        from platform_base.ui.dialogs import __all__
        
        assert "FilterDialog" in __all__

    def test_all_contains_settings_dialog(self):
        """Test __all__ contains SettingsDialog"""
        from platform_base.ui.dialogs import __all__
        
        assert "SettingsDialog" in __all__

    def test_all_contains_smoothing_dialog(self):
        """Test __all__ contains SmoothingDialog"""
        from platform_base.ui.dialogs import __all__
        
        assert "SmoothingDialog" in __all__

    def test_all_contains_functions(self):
        """Test __all__ contains convenience functions"""
        from platform_base.ui.dialogs import __all__
        
        assert "show_filter_dialog" in __all__
        assert "show_settings_dialog" in __all__
        assert "show_smoothing_dialog" in __all__
        assert "load_app_settings" in __all__

    def test_all_length(self):
        """Test __all__ has expected number of exports"""
        from platform_base.ui.dialogs import __all__

        # Should have: FilterDialog, SettingsDialog, SmoothingDialog,
        #              AppSettings, show_filter_dialog, show_settings_dialog,
        #              show_smoothing_dialog, load_app_settings
        assert len(__all__) == 8


class TestDialogsImportStar:
    """Tests for star imports"""

    def test_import_star_filter(self):
        """Test FilterDialog available after star import simulation"""
        import platform_base.ui.dialogs as dialogs
        
        assert hasattr(dialogs, "FilterDialog")

    def test_import_star_settings(self):
        """Test SettingsDialog available after star import simulation"""
        import platform_base.ui.dialogs as dialogs
        
        assert hasattr(dialogs, "SettingsDialog")

    def test_import_star_smoothing(self):
        """Test SmoothingDialog available after star import simulation"""
        import platform_base.ui.dialogs as dialogs
        
        assert hasattr(dialogs, "SmoothingDialog")


class TestDialogsPackageStructure:
    """Tests for package structure"""

    def test_dialogs_is_package(self):
        """Test that dialogs is a proper package"""
        import platform_base.ui.dialogs

        # Should have __path__ (package indicator)
        assert hasattr(platform_base.ui.dialogs, "__path__")

    def test_dialogs_docstring(self):
        """Test that dialogs has docstring"""
        import platform_base.ui.dialogs
        
        assert platform_base.ui.dialogs.__doc__ is not None
        assert len(platform_base.ui.dialogs.__doc__) > 0
