"""
Comprehensive tests for ui/context_menu.py module.

Tests context menu dialogs and actions including zoom, selection, analysis,
filters, export, and annotation features.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestCompareSeriesDialog:
    """Tests for CompareSeriesDialog class."""
    
    @pytest.fixture
    def available_series(self):
        """Sample series list."""
        return ["Series A", "Series B", "Series C"]
    
    def test_create_dialog(self, qtbot, available_series):
        """Test creating compare series dialog."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Comparar Séries"
    
    def test_dialog_min_width(self, qtbot, available_series):
        """Test dialog minimum width."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.minimumWidth() == 400
    
    def test_series_combos_populated(self, qtbot, available_series):
        """Test series combos are populated."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.series1_combo.count() == 3
        assert dialog.series2_combo.count() == 3
    
    def test_series2_default_index(self, qtbot, available_series):
        """Test second series has different default index."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.series2_combo.currentIndex() == 1
    
    def test_correlation_check_default(self, qtbot, available_series):
        """Test correlation checkbox is checked by default."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.correlation_check.isChecked()
    
    def test_rmse_check_default(self, qtbot, available_series):
        """Test RMSE checkbox is checked by default."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.rmse_check.isChecked()
    
    def test_mae_check_default(self, qtbot, available_series):
        """Test MAE checkbox is checked by default."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.mae_check.isChecked()
    
    def test_dtw_check_not_default(self, qtbot, available_series):
        """Test DTW checkbox is not checked by default."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert not dialog.dtw_check.isChecked()
    
    def test_result_text_readonly(self, qtbot, available_series):
        """Test result text is read-only."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        assert dialog.result_text.isReadOnly()
    
    def test_compare_generates_results(self, qtbot, available_series):
        """Test compare generates results."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        dialog = CompareSeriesDialog(available_series)
        qtbot.addWidget(dialog)
        dialog._compare()
        text = dialog.result_text.toPlainText()
        assert "Correlação" in text or "RMSE" in text


class TestSmoothingDialog:
    """Tests for SmoothingDialog class."""
    
    def test_create_dialog(self, qtbot):
        """Test creating smoothing dialog."""
        from platform_base.ui.context_menu import SmoothingDialog
        dialog = SmoothingDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Suavização Visual"
    
    def test_method_options(self, qtbot):
        """Test available smoothing methods."""
        from platform_base.ui.context_menu import SmoothingDialog
        dialog = SmoothingDialog()
        qtbot.addWidget(dialog)
        methods = [dialog.method_combo.itemText(i) for i in range(dialog.method_combo.count())]
        assert "Gaussian" in methods
        assert "Moving Average" in methods
        assert "Savitzky-Golay" in methods
        assert "Median" in methods
    
    def test_window_spin_defaults(self, qtbot):
        """Test window spin box defaults."""
        from platform_base.ui.context_menu import SmoothingDialog
        dialog = SmoothingDialog()
        qtbot.addWidget(dialog)
        assert dialog.window_spin.minimum() == 3
        assert dialog.window_spin.maximum() == 101
        assert dialog.window_spin.value() == 5
    
    def test_sigma_spin_defaults(self, qtbot):
        """Test sigma spin box defaults."""
        from platform_base.ui.context_menu import SmoothingDialog
        dialog = SmoothingDialog()
        qtbot.addWidget(dialog)
        assert dialog.sigma_spin.minimum() == 0.1
        assert dialog.sigma_spin.maximum() == 10.0
        assert dialog.sigma_spin.value() == 1.0
    
    def test_get_config(self, qtbot):
        """Test get_config returns dictionary."""
        from platform_base.ui.context_menu import SmoothingDialog
        dialog = SmoothingDialog()
        qtbot.addWidget(dialog)
        config = dialog.get_config()
        assert isinstance(config, dict)
        assert "method" in config
        assert "window_size" in config
        assert "sigma" in config
    
    def test_get_config_method_format(self, qtbot):
        """Test method is formatted correctly."""
        from platform_base.ui.context_menu import SmoothingDialog
        dialog = SmoothingDialog()
        qtbot.addWidget(dialog)
        dialog.method_combo.setCurrentText("Moving Average")
        config = dialog.get_config()
        assert config["method"] == "moving_average"


class TestAnnotationDialog:
    """Tests for AnnotationDialog class."""
    
    def test_create_dialog(self, qtbot):
        """Test creating annotation dialog."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Adicionar Anotação"
    
    def test_dialog_min_width(self, qtbot):
        """Test dialog minimum width."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog()
        qtbot.addWidget(dialog)
        assert dialog.minimumWidth() == 400
    
    def test_initial_position(self, qtbot):
        """Test dialog with initial position."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog(x_pos=10.5, y_pos=20.3)
        qtbot.addWidget(dialog)
        assert dialog.x_spin.value() == 10.5
        assert dialog.y_spin.value() == 20.3
    
    def test_arrow_check_default(self, qtbot):
        """Test arrow checkbox default."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog()
        qtbot.addWidget(dialog)
        assert dialog.arrow_check.isChecked()
    
    def test_color_options(self, qtbot):
        """Test available color options."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog()
        qtbot.addWidget(dialog)
        colors = [dialog.color_combo.itemText(i) for i in range(dialog.color_combo.count())]
        assert "Vermelho" in colors
        assert "Azul" in colors
        assert "Verde" in colors
    
    def test_get_annotation(self, qtbot):
        """Test get_annotation returns dictionary."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog()
        qtbot.addWidget(dialog)
        annotation = dialog.get_annotation()
        assert isinstance(annotation, dict)
        assert "x" in annotation
        assert "y" in annotation
        assert "text" in annotation
        assert "show_arrow" in annotation
        assert "color" in annotation
    
    def test_get_annotation_color_mapping(self, qtbot):
        """Test color mapping in get_annotation."""
        from platform_base.ui.context_menu import AnnotationDialog
        dialog = AnnotationDialog()
        qtbot.addWidget(dialog)
        dialog.color_combo.setCurrentText("Vermelho")
        annotation = dialog.get_annotation()
        assert annotation["color"] == "#e74c3c"


class TestPlotContextMenu:
    """Tests for PlotContextMenu class."""
    
    @pytest.fixture
    def mock_plot_widget(self, qtbot):
        """Create mock plot widget."""
        from PyQt6.QtWidgets import QWidget
        return QWidget()
    
    def test_create_menu(self, qtbot, mock_plot_widget):
        """Test creating plot context menu."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        assert menu.plot_widget == mock_plot_widget
    
    def test_menu_has_zoom_submenu(self, qtbot, mock_plot_widget):
        """Test menu has zoom submenu."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        actions = menu.actions()
        action_texts = [a.text() for a in actions if a.menu()]
        assert any("Zoom" in text for text in action_texts)
    
    def test_menu_has_selection_submenu(self, qtbot, mock_plot_widget):
        """Test menu has selection submenu."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        actions = menu.actions()
        action_texts = [a.text() for a in actions if a.menu()]
        assert any("Seleção" in text for text in action_texts)
    
    def test_menu_has_analysis_submenu(self, qtbot, mock_plot_widget):
        """Test menu has analysis submenu."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        actions = menu.actions()
        action_texts = [a.text() for a in actions if a.menu()]
        assert any("Análise" in text for text in action_texts)
    
    def test_menu_has_export_submenu(self, qtbot, mock_plot_widget):
        """Test menu has export submenu."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        actions = menu.actions()
        action_texts = [a.text() for a in actions if a.menu()]
        assert any("Exportar" in text for text in action_texts)
    
    def test_annotations_list_initialized(self, qtbot, mock_plot_widget):
        """Test annotations list is initialized."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        assert hasattr(menu, '_annotations')
        assert menu._annotations == []
    
    def test_visual_smoothing_default(self, qtbot, mock_plot_widget):
        """Test visual smoothing default state."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        assert menu._visual_smoothing_enabled is False
    
    def test_hide_interpolated_default(self, qtbot, mock_plot_widget):
        """Test hide interpolated default state."""
        from platform_base.ui.context_menu import PlotContextMenu
        menu = PlotContextMenu(mock_plot_widget)
        qtbot.addWidget(menu)
        assert menu._hide_interpolated is False


class TestPlotContextMenuZoomActions:
    """Tests for zoom actions in PlotContextMenu."""
    
    @pytest.fixture
    def menu_with_mock_widget(self, qtbot):
        """Create menu with mock widget."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import PlotContextMenu
        widget = QWidget()
        menu = PlotContextMenu(widget)
        qtbot.addWidget(menu)
        return menu
    
    def test_zoom_in_method_exists(self, menu_with_mock_widget):
        """Test _zoom_in method exists."""
        assert hasattr(menu_with_mock_widget, '_zoom_in')
    
    def test_zoom_out_method_exists(self, menu_with_mock_widget):
        """Test _zoom_out method exists."""
        assert hasattr(menu_with_mock_widget, '_zoom_out')
    
    def test_reset_view_method_exists(self, menu_with_mock_widget):
        """Test _reset_view method exists."""
        assert hasattr(menu_with_mock_widget, '_reset_view')
    
    def test_fit_to_x_method_exists(self, menu_with_mock_widget):
        """Test _fit_to_x method exists."""
        assert hasattr(menu_with_mock_widget, '_fit_to_x')
    
    def test_fit_to_y_method_exists(self, menu_with_mock_widget):
        """Test _fit_to_y method exists."""
        assert hasattr(menu_with_mock_widget, '_fit_to_y')


class TestPlotContextMenuSelectionActions:
    """Tests for selection actions in PlotContextMenu."""
    
    @pytest.fixture
    def menu_with_mock_widget(self, qtbot):
        """Create menu with mock widget."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import PlotContextMenu
        widget = QWidget()
        menu = PlotContextMenu(widget)
        qtbot.addWidget(menu)
        return menu
    
    def test_select_region_method_exists(self, menu_with_mock_widget):
        """Test _select_region method exists."""
        assert hasattr(menu_with_mock_widget, '_select_region')
    
    def test_select_all_method_exists(self, menu_with_mock_widget):
        """Test _select_all method exists."""
        assert hasattr(menu_with_mock_widget, '_select_all')
    
    def test_clear_selection_method_exists(self, menu_with_mock_widget):
        """Test _clear_selection method exists."""
        assert hasattr(menu_with_mock_widget, '_clear_selection')
    
    def test_extract_selection_method_exists(self, menu_with_mock_widget):
        """Test _extract_selection method exists."""
        assert hasattr(menu_with_mock_widget, '_extract_selection')


class TestPlotContextMenuAnalysisActions:
    """Tests for analysis actions in PlotContextMenu."""
    
    @pytest.fixture
    def menu_with_mock_widget(self, qtbot):
        """Create menu with mock widget."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import PlotContextMenu
        widget = QWidget()
        menu = PlotContextMenu(widget)
        qtbot.addWidget(menu)
        return menu
    
    def test_show_stats_method_exists(self, menu_with_mock_widget):
        """Test _show_stats method exists."""
        assert hasattr(menu_with_mock_widget, '_show_stats')
    
    def test_compare_series_method_exists(self, menu_with_mock_widget):
        """Test _compare_series method exists."""
        assert hasattr(menu_with_mock_widget, '_compare_series')
    
    def test_detect_peaks_method_exists(self, menu_with_mock_widget):
        """Test _detect_peaks method exists."""
        assert hasattr(menu_with_mock_widget, '_detect_peaks')
    
    def test_find_crossings_method_exists(self, menu_with_mock_widget):
        """Test _find_crossings method exists."""
        assert hasattr(menu_with_mock_widget, '_find_crossings')


class TestPlotContextMenuFilterActions:
    """Tests for filter actions in PlotContextMenu."""
    
    @pytest.fixture
    def menu_with_mock_widget(self, qtbot):
        """Create menu with mock widget."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import PlotContextMenu
        widget = QWidget()
        menu = PlotContextMenu(widget)
        qtbot.addWidget(menu)
        return menu
    
    def test_toggle_hide_interpolated_method_exists(self, menu_with_mock_widget):
        """Test _toggle_hide_interpolated method exists."""
        assert hasattr(menu_with_mock_widget, '_toggle_hide_interpolated')
    
    def test_apply_visual_smoothing_method_exists(self, menu_with_mock_widget):
        """Test _apply_visual_smoothing method exists."""
        assert hasattr(menu_with_mock_widget, '_apply_visual_smoothing')
    
    def test_toggle_grid_method_exists(self, menu_with_mock_widget):
        """Test _toggle_grid method exists."""
        assert hasattr(menu_with_mock_widget, '_toggle_grid')
    
    def test_toggle_legend_method_exists(self, menu_with_mock_widget):
        """Test _toggle_legend method exists."""
        assert hasattr(menu_with_mock_widget, '_toggle_legend')


class TestPlotContextMenuExportActions:
    """Tests for export actions in PlotContextMenu."""
    
    @pytest.fixture
    def menu_with_mock_widget(self, qtbot):
        """Create menu with mock widget."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import PlotContextMenu
        widget = QWidget()
        menu = PlotContextMenu(widget)
        qtbot.addWidget(menu)
        return menu
    
    def test_export_plot_method_exists(self, menu_with_mock_widget):
        """Test _export_plot method exists."""
        assert hasattr(menu_with_mock_widget, '_export_plot')
    
    def test_export_selection_data_method_exists(self, menu_with_mock_widget):
        """Test _export_selection_data method exists."""
        assert hasattr(menu_with_mock_widget, '_export_selection_data')


class TestModuleImports:
    """Tests for module imports."""
    
    def test_import_context_menu_module(self):
        """Test context_menu module can be imported."""
        from platform_base.ui import context_menu
        assert context_menu is not None
    
    def test_import_compare_series_dialog(self):
        """Test CompareSeriesDialog can be imported."""
        from platform_base.ui.context_menu import CompareSeriesDialog
        assert CompareSeriesDialog is not None
    
    def test_import_smoothing_dialog(self):
        """Test SmoothingDialog can be imported."""
        from platform_base.ui.context_menu import SmoothingDialog
        assert SmoothingDialog is not None
    
    def test_import_annotation_dialog(self):
        """Test AnnotationDialog can be imported."""
        from platform_base.ui.context_menu import AnnotationDialog
        assert AnnotationDialog is not None
    
    def test_import_plot_context_menu(self):
        """Test PlotContextMenu can be imported."""
        from platform_base.ui.context_menu import PlotContextMenu
        assert PlotContextMenu is not None


class TestDialogParentRelationship:
    """Tests for dialog parent relationship."""
    
    def test_compare_dialog_with_parent(self, qtbot):
        """Test creating compare dialog with parent."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import CompareSeriesDialog
        parent = QWidget()
        dialog = CompareSeriesDialog(["A", "B"], parent=parent)
        qtbot.addWidget(dialog)
        assert dialog.parent() == parent
    
    def test_smoothing_dialog_with_parent(self, qtbot):
        """Test creating smoothing dialog with parent."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import SmoothingDialog
        parent = QWidget()
        dialog = SmoothingDialog(parent=parent)
        qtbot.addWidget(dialog)
        assert dialog.parent() == parent
    
    def test_annotation_dialog_with_parent(self, qtbot):
        """Test creating annotation dialog with parent."""
        from PyQt6.QtWidgets import QWidget

        from platform_base.ui.context_menu import AnnotationDialog
        parent = QWidget()
        dialog = AnnotationDialog(parent=parent)
        qtbot.addWidget(dialog)
        assert dialog.parent() == parent
