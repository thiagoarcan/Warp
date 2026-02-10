"""
Tests for ui/mixins.py - UI Mixin Classes

Tests for UiLoaderMixin and DialogLoaderMixin.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest


class TestUiLoaderMixin:
    """Tests for UiLoaderMixin class"""

    def test_ui_file_default_none(self):
        """Test that UI_FILE is None by default"""
        from platform_base.ui.mixins import UiLoaderMixin
        
        assert UiLoaderMixin.UI_FILE is None

    def test_load_ui_raises_without_ui_file(self, qtbot):
        """Test that _load_ui raises ValueError if UI_FILE not set"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            pass
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        
        with pytest.raises(ValueError, match="must define UI_FILE"):
            widget._load_ui()

    def test_load_ui_raises_for_non_widget(self):
        """Test that _load_ui raises TypeError for non-QWidget"""
        from platform_base.ui.mixins import UiLoaderMixin
        
        class NotAWidget(UiLoaderMixin):
            UI_FILE = "test_file"
        
        obj = NotAWidget()
        
        with pytest.raises(TypeError, match="must inherit from QWidget"):
            obj._load_ui()

    @patch('platform_base.ui.mixins.load_ui')
    def test_load_ui_calls_loader(self, mock_load_ui, qtbot):
        """Test that _load_ui calls load_ui function"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = "test_panel"
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        widget._load_ui()
        
        mock_load_ui.assert_called_once_with("test_panel", widget)

    @patch('platform_base.ui.mixins.load_ui')
    def test_load_ui_with_path(self, mock_load_ui, qtbot):
        """Test _load_ui with nested path"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = "panels/my_panel"
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        widget._load_ui()
        
        mock_load_ui.assert_called_once_with("panels/my_panel", widget)

    def test_ui_file_class_attribute_inherited(self):
        """Test that UI_FILE can be overridden in subclass"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class BaseWidget(QWidget, UiLoaderMixin):
            UI_FILE = "base_widget"
        
        class DerivedWidget(BaseWidget):
            UI_FILE = "derived_widget"
        
        assert BaseWidget.UI_FILE == "base_widget"
        assert DerivedWidget.UI_FILE == "derived_widget"


class TestDialogLoaderMixin:
    """Tests for DialogLoaderMixin class"""

    def test_inherits_from_ui_loader_mixin(self):
        """Test that DialogLoaderMixin inherits from UiLoaderMixin"""
        from platform_base.ui.mixins import DialogLoaderMixin, UiLoaderMixin
        
        assert issubclass(DialogLoaderMixin, UiLoaderMixin)

    def test_setup_dialog_buttons_with_button_box(self, qtbot):
        """Test _setup_dialog_buttons connects button_box signals"""
        from PyQt6.QtWidgets import QDialog

        from platform_base.ui.mixins import DialogLoaderMixin
        
        class TestDialog(QDialog, DialogLoaderMixin):
            UI_FILE = "test_dialog"
        
        dialog = TestDialog()
        qtbot.addWidget(dialog)
        
        # Create mock button_box
        mock_button_box = MagicMock()
        dialog.button_box = mock_button_box
        
        dialog._setup_dialog_buttons()
        
        # Verify connections
        mock_button_box.accepted.connect.assert_called()
        mock_button_box.rejected.connect.assert_called()

    def test_setup_dialog_buttons_without_button_box(self, qtbot):
        """Test _setup_dialog_buttons handles missing button_box"""
        from PyQt6.QtWidgets import QDialog

        from platform_base.ui.mixins import DialogLoaderMixin
        
        class TestDialog(QDialog, DialogLoaderMixin):
            UI_FILE = "test_dialog"
        
        dialog = TestDialog()
        qtbot.addWidget(dialog)
        
        # Should not raise even without button_box
        dialog._setup_dialog_buttons()


class TestMixinIntegration:
    """Integration tests for UI mixins"""

    @patch('platform_base.ui.mixins.load_ui')
    def test_typical_widget_usage(self, mock_load_ui, qtbot):
        """Test typical usage pattern for a widget"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class DataPanel(QWidget, UiLoaderMixin):
            UI_FILE = "panels/data_panel"
            
            def __init__(self):
                super().__init__()
                self._load_ui()
                self._setup_custom()
            
            def _setup_custom(self):
                self.custom_setup_done = True
        
        panel = DataPanel()
        qtbot.addWidget(panel)
        
        assert panel.custom_setup_done
        mock_load_ui.assert_called_once()

    @patch('platform_base.ui.mixins.load_ui')
    def test_typical_dialog_usage(self, mock_load_ui, qtbot):
        """Test typical usage pattern for a dialog"""
        from PyQt6.QtWidgets import QDialog

        from platform_base.ui.mixins import DialogLoaderMixin
        
        class SettingsDialog(QDialog, DialogLoaderMixin):
            UI_FILE = "dialogs/settings"
            
            def __init__(self, parent=None):
                super().__init__(parent)
                self._load_ui()
                # Mock button_box since load_ui is mocked
                self.button_box = MagicMock()
                self._setup_dialog_buttons()
        
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)
        
        mock_load_ui.assert_called_once()
        dialog.button_box.accepted.connect.assert_called()

    def test_mixin_does_not_require_init(self):
        """Test that mixin can be used without calling super().__init__"""
        from platform_base.ui.mixins import UiLoaderMixin

        # Just importing and using as type hint should work
        class SomeClass(UiLoaderMixin):
            UI_FILE = "test"
        
        obj = SomeClass()
        assert obj.UI_FILE == "test"


class TestMixinEdgeCases:
    """Edge case tests for UI mixins"""

    def test_ui_file_empty_string(self, qtbot):
        """Test UI_FILE as empty string"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = ""
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        
        # Empty string should be treated as not defined
        with pytest.raises(ValueError):
            widget._load_ui()

    @patch('platform_base.ui.mixins.load_ui', side_effect=FileNotFoundError("not found"))
    def test_load_ui_file_not_found(self, mock_load_ui, qtbot):
        """Test handling of missing .ui file"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = "nonexistent"
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        
        with pytest.raises(FileNotFoundError):
            widget._load_ui()

    @patch('platform_base.ui.mixins.load_ui')
    def test_multiple_load_ui_calls(self, mock_load_ui, qtbot):
        """Test calling _load_ui multiple times"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = "test"
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        
        widget._load_ui()
        widget._load_ui()
        
        # Should be called twice
        assert mock_load_ui.call_count == 2

    def test_class_without_ui_file_attribute(self):
        """Test class that doesn't define UI_FILE uses default"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            pass
        
        # Should use parent's UI_FILE which is None
        assert TestWidget.UI_FILE is None


class TestMixinLogging:
    """Tests for mixin logging behavior"""

    @patch('platform_base.ui.mixins.load_ui')
    @patch('platform_base.ui.mixins.logger')
    def test_load_ui_logs_debug(self, mock_logger, mock_load_ui, qtbot):
        """Test that _load_ui logs debug message"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = "test_widget"
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        widget._load_ui()
        
        mock_logger.debug.assert_called()

    @patch('platform_base.ui.mixins.load_ui')
    @patch('platform_base.ui.mixins.logger')
    def test_load_ui_logs_info_on_success(self, mock_logger, mock_load_ui, qtbot):
        """Test that _load_ui logs info on success"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            UI_FILE = "test_widget"
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        widget._load_ui()
        
        mock_logger.info.assert_called()

    @patch('platform_base.ui.mixins.logger')
    def test_load_ui_logs_error_on_missing_ui_file(self, mock_logger, qtbot):
        """Test that _load_ui logs error when UI_FILE not set"""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.mixins import UiLoaderMixin
        
        class TestWidget(QWidget, UiLoaderMixin):
            pass
        
        widget = TestWidget()
        qtbot.addWidget(widget)
        
        with pytest.raises(ValueError):
            widget._load_ui()
        
        mock_logger.error.assert_called()

