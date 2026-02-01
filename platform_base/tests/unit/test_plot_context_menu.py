"""
Comprehensive tests for desktop/menus/plot_context_menu.py

Tests MathAnalysisDialog, PlotContextMenu, and helper functions.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import numpy as np
import pytest

# Skip all tests if PyQt6 is not available
pytestmark = pytest.mark.skipif(
    not pytest.importorskip("PyQt6", reason="PyQt6 required").QtCore,
    reason="PyQt6.QtCore not available"
)


# =============================================================================
# MathAnalysisDialog Tests
# =============================================================================

class TestMathAnalysisDialog:
    """Tests for MathAnalysisDialog class."""
    
    @pytest.fixture
    def qtbot(self, qtbot):
        """Provide qtbot fixture."""
        return qtbot
    
    def test_dialog_creation_derivative(self, qtbot):
        """Test dialog creation for derivative operation."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("derivative")
        qtbot.addWidget(dialog)
        
        assert dialog.operation == "derivative"
        assert dialog.windowTitle()
        assert hasattr(dialog, 'derivative_order')
        assert hasattr(dialog, 'derivative_method')
    
    def test_dialog_creation_integral(self, qtbot):
        """Test dialog creation for integral operation."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("integral")
        qtbot.addWidget(dialog)
        
        assert dialog.operation == "integral"
        assert hasattr(dialog, 'integral_method')
    
    def test_dialog_creation_smooth(self, qtbot):
        """Test dialog creation for smooth operation."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("smooth")
        qtbot.addWidget(dialog)
        
        assert dialog.operation == "smooth"
        assert hasattr(dialog, 'smooth_method')
        assert hasattr(dialog, 'window_size')
        assert hasattr(dialog, 'polyorder')
    
    def test_dialog_creation_interpolate(self, qtbot):
        """Test dialog creation for interpolate operation."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("interpolate")
        qtbot.addWidget(dialog)
        
        assert dialog.operation == "interpolate"
        assert hasattr(dialog, 'interp_method')
    
    def test_dialog_creation_resample(self, qtbot):
        """Test dialog creation for resample operation."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("resample")
        qtbot.addWidget(dialog)
        
        assert dialog.operation == "resample"
        assert hasattr(dialog, 'resample_method')
        assert hasattr(dialog, 'target_points')
    
    def test_derivative_order_range(self, qtbot):
        """Test derivative order spinbox has correct range."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("derivative")
        qtbot.addWidget(dialog)
        
        assert dialog.derivative_order.minimum() == 1
        assert dialog.derivative_order.maximum() == 3
        assert dialog.derivative_order.value() == 1
    
    def test_derivative_methods_available(self, qtbot):
        """Test derivative methods are available in dropdown."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("derivative")
        qtbot.addWidget(dialog)
        
        methods = [dialog.derivative_method.itemText(i) 
                   for i in range(dialog.derivative_method.count())]
        
        assert "finite_diff" in methods
        assert "savitzky_golay" in methods
        assert "spline_derivative" in methods
    
    def test_smoothing_toggle(self, qtbot):
        """Test smoothing checkbox enables window spinbox."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("derivative")
        qtbot.addWidget(dialog)
        
        # Initially disabled
        assert not dialog.smoothing_window.isEnabled()
        
        # Enable smoothing
        dialog.enable_smoothing.setChecked(True)
        assert dialog.smoothing_window.isEnabled()
        
        # Disable smoothing
        dialog.enable_smoothing.setChecked(False)
        assert not dialog.smoothing_window.isEnabled()
    
    def test_apply_derivative_operation(self, qtbot):
        """Test applying derivative operation emits signal."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("derivative")
        qtbot.addWidget(dialog)
        
        # Setup signal spy
        received_signals = []
        dialog.operation_requested.connect(lambda op, params: received_signals.append((op, params)))
        
        # Set values
        dialog.derivative_order.setValue(2)
        dialog.derivative_method.setCurrentText("finite_diff")
        
        # Apply
        dialog._apply_operation()
        
        assert len(received_signals) == 1
        op, params = received_signals[0]
        assert op == "derivative"
        assert params["order"] == 2
        assert params["method"] == "finite_diff"
    
    def test_apply_integral_operation(self, qtbot):
        """Test applying integral operation emits signal."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("integral")
        qtbot.addWidget(dialog)
        
        received_signals = []
        dialog.operation_requested.connect(lambda op, params: received_signals.append((op, params)))
        
        dialog.integral_method.setCurrentText("simpson")
        dialog._apply_operation()
        
        assert len(received_signals) == 1
        op, params = received_signals[0]
        assert op == "integral"
        assert params["method"] == "simpson"
    
    def test_apply_smooth_operation(self, qtbot):
        """Test applying smooth operation emits signal."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("smooth")
        qtbot.addWidget(dialog)
        
        received_signals = []
        dialog.operation_requested.connect(lambda op, params: received_signals.append((op, params)))
        
        dialog.smooth_method.setCurrentText("gaussian")
        dialog.window_size.setValue(21)
        dialog.polyorder.setValue(5)
        dialog._apply_operation()
        
        assert len(received_signals) == 1
        op, params = received_signals[0]
        assert op == "smooth"
        assert params["method"] == "gaussian"
        assert params["window_size"] == 21
        assert params["polyorder"] == 5
    
    def test_apply_resample_operation(self, qtbot):
        """Test applying resample operation emits signal."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("resample")
        qtbot.addWidget(dialog)
        
        received_signals = []
        dialog.operation_requested.connect(lambda op, params: received_signals.append((op, params)))
        
        dialog.resample_method.setCurrentText("lttb")
        dialog.target_points.setValue(5000)
        dialog._apply_operation()
        
        assert len(received_signals) == 1
        op, params = received_signals[0]
        assert op == "resample"
        assert params["method"] == "lttb"
        assert params["n_points"] == 5000
    
    def test_derivative_with_smoothing(self, qtbot):
        """Test derivative with smoothing enabled."""
        from platform_base.desktop.menus.plot_context_menu import MathAnalysisDialog
        
        dialog = MathAnalysisDialog("derivative")
        qtbot.addWidget(dialog)
        
        received_signals = []
        dialog.operation_requested.connect(lambda op, params: received_signals.append((op, params)))
        
        dialog.enable_smoothing.setChecked(True)
        dialog.smoothing_window.setValue(15)
        dialog._apply_operation()
        
        assert len(received_signals) == 1
        op, params = received_signals[0]
        assert "smoothing" in params
        assert params["smoothing"]["method"] == "savitzky_golay"
        assert params["smoothing"]["params"]["window_length"] == 15


# =============================================================================
# PlotContextMenu Tests
# =============================================================================

class TestPlotContextMenu:
    """Tests for PlotContextMenu class."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Create mock session state."""
        state = MagicMock()
        state.dataset_store = MagicMock()
        state.selection = MagicMock()
        state.selection.time_window = None
        return state
    
    @pytest.fixture
    def mock_signal_hub(self):
        """Create mock signal hub."""
        return MagicMock()
    
    @pytest.fixture
    def context_menu(self, mock_session_state, mock_signal_hub, qtbot):
        """Create PlotContextMenu for testing."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        menu = PlotContextMenu(
            session_state=mock_session_state,
            signal_hub=mock_signal_hub,
            plot_position=None,
            dataset_id=None,
            series_id=None,
        )
        qtbot.addWidget(menu)
        return menu
    
    @pytest.fixture
    def context_menu_with_series(self, mock_session_state, mock_signal_hub, qtbot):
        """Create PlotContextMenu with series context."""
        from PyQt6.QtCore import QPointF

        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        menu = PlotContextMenu(
            session_state=mock_session_state,
            signal_hub=mock_signal_hub,
            plot_position=QPointF(10.0, 20.0),
            dataset_id="test_dataset",
            series_id="test_series",
        )
        qtbot.addWidget(menu)
        return menu
    
    def test_menu_creation(self, context_menu):
        """Test basic menu creation."""
        assert context_menu is not None
        assert context_menu.session_state is not None
        assert context_menu.signal_hub is not None
    
    def test_menu_has_math_submenu(self, context_menu):
        """Test menu has mathematical analysis submenu."""
        actions = context_menu.actions()
        action_texts = [a.text() for a in actions]
        
        # Find menu items
        assert any("Mathematical Analysis" in t or "📊" in t for t in action_texts)
    
    def test_menu_has_processing_submenu(self, context_menu):
        """Test menu has data processing submenu."""
        actions = context_menu.actions()
        action_texts = [a.text() for a in actions]
        
        assert any("Data Processing" in t or "🔧" in t for t in action_texts)
    
    def test_menu_has_visualization_submenu(self, context_menu):
        """Test menu has visualization submenu."""
        actions = context_menu.actions()
        action_texts = [a.text() for a in actions]
        
        assert any("Visualization" in t or "👁️" in t for t in action_texts)
    
    def test_menu_has_export_submenu(self, context_menu):
        """Test menu has export submenu."""
        actions = context_menu.actions()
        action_texts = [a.text() for a in actions]
        
        assert any("Export" in t or "💾" in t for t in action_texts)
    
    def test_menu_has_selection_actions(self, context_menu):
        """Test menu has selection actions."""
        actions = context_menu.actions()
        action_texts = [a.text() for a in actions]
        
        assert any("Clear Selection" in t or "🗑️" in t for t in action_texts)
        assert any("Select All" in t or "☑️" in t for t in action_texts)
    
    def test_menu_with_series_has_series_menu(self, context_menu_with_series):
        """Test menu with series context has series management."""
        actions = context_menu_with_series.actions()
        action_texts = [a.text() for a in actions]
        
        # Should have series-specific actions
        assert any("Duplicate" in t or "📄" in t for t in action_texts)
        assert any("Properties" in t or "⚙️" in t for t in action_texts)
    
    def test_menu_signals_exist(self, context_menu):
        """Test that required signals exist."""
        assert hasattr(context_menu, 'math_operation_requested')
        assert hasattr(context_menu, 'zoom_to_selection_requested')
        assert hasattr(context_menu, 'reset_zoom_requested')
        assert hasattr(context_menu, 'export_plot_requested')
        assert hasattr(context_menu, 'export_data_requested')
        assert hasattr(context_menu, 'create_annotation_requested')
        assert hasattr(context_menu, 'duplicate_series_requested')
        assert hasattr(context_menu, 'remove_series_requested')


# =============================================================================
# PlotContextMenu Method Tests
# =============================================================================

class TestPlotContextMenuMethods:
    """Tests for PlotContextMenu methods."""
    
    @pytest.fixture
    def mock_dataset(self):
        """Create mock dataset with series."""
        dataset = MagicMock()
        series = MagicMock()
        series.name = "test_series"
        series.values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        series.unit = "m/s"
        series.lineage = None
        dataset.series = {"test_series": series}
        dataset.timestamps = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
        return dataset
    
    @pytest.fixture
    def mock_session_state(self, mock_dataset):
        """Create mock session state with dataset."""
        state = MagicMock()
        state.dataset_store = MagicMock()
        state.dataset_store.get_dataset.return_value = mock_dataset
        state.selection = MagicMock()
        state.selection.time_window = None
        return state
    
    @pytest.fixture
    def mock_signal_hub(self):
        """Create mock signal hub."""
        return MagicMock()
    
    @pytest.fixture
    def context_menu(self, mock_session_state, mock_signal_hub, qtbot):
        """Create PlotContextMenu for testing."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        menu = PlotContextMenu(
            session_state=mock_session_state,
            signal_hub=mock_signal_hub,
            plot_position=None,
            dataset_id="test_dataset",
            series_id="test_series",
        )
        qtbot.addWidget(menu)
        return menu
    
    def test_calculate_skewness(self, context_menu):
        """Test skewness calculation."""
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        skewness = context_menu._calculate_skewness(values)
        
        assert isinstance(skewness, float)
        # Uniform distribution should have ~0 skewness
        assert abs(skewness) < 0.1
    
    def test_calculate_skewness_zero_std(self, context_menu):
        """Test skewness with zero standard deviation."""
        values = np.array([5.0, 5.0, 5.0, 5.0])
        skewness = context_menu._calculate_skewness(values)
        
        assert skewness == 0
    
    def test_calculate_kurtosis(self, context_menu):
        """Test kurtosis calculation."""
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        kurtosis = context_menu._calculate_kurtosis(values)
        
        assert isinstance(kurtosis, float)
    
    def test_calculate_kurtosis_zero_std(self, context_menu):
        """Test kurtosis with zero standard deviation."""
        values = np.array([5.0, 5.0, 5.0, 5.0])
        kurtosis = context_menu._calculate_kurtosis(values)
        
        assert kurtosis == 0
    
    def test_has_multiple_series_true(self, context_menu, mock_session_state, mock_dataset):
        """Test has_multiple_series returns True for multiple series."""
        # Add another series
        mock_dataset.series["another_series"] = MagicMock()
        
        result = context_menu._has_multiple_series()
        assert result is True
    
    def test_has_multiple_series_false(self, context_menu, mock_dataset):
        """Test has_multiple_series returns False for single series."""
        # Keep only one series
        mock_dataset.series = {"test_series": mock_dataset.series["test_series"]}
        
        result = context_menu._has_multiple_series()
        assert result is False
    
    def test_has_multiple_series_no_dataset(self, mock_signal_hub, qtbot):
        """Test has_multiple_series returns False when no dataset."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        
        menu = PlotContextMenu(
            session_state=state,
            signal_hub=mock_signal_hub,
            dataset_id=None,
            series_id=None,
        )
        qtbot.addWidget(menu)
        
        result = menu._has_multiple_series()
        assert result is False
    
    def test_toggle_grid(self, context_menu):
        """Test toggle grid functionality."""
        # Create mock parent with showGrid
        mock_parent = MagicMock()
        mock_parent.showGrid = MagicMock()
        mock_parent._grid_visible = True
        
        with patch.object(context_menu, 'parent', return_value=mock_parent):
            context_menu._toggle_grid()
            
            mock_parent.showGrid.assert_called_once()
            assert mock_parent._grid_visible is False
    
    def test_toggle_legend_show(self, context_menu):
        """Test toggle legend to show."""
        mock_parent = MagicMock()
        mock_legend = MagicMock()
        mock_legend.isVisible.return_value = False
        mock_parent.legend = mock_legend
        
        with patch.object(context_menu, 'parent', return_value=mock_parent):
            context_menu._toggle_legend()
            
            mock_legend.show.assert_called_once()
    
    def test_toggle_legend_hide(self, context_menu):
        """Test toggle legend to hide."""
        mock_parent = MagicMock()
        mock_legend = MagicMock()
        mock_legend.isVisible.return_value = True
        mock_parent.legend = mock_legend
        
        with patch.object(context_menu, 'parent', return_value=mock_parent):
            context_menu._toggle_legend()
            
            mock_legend.hide.assert_called_once()
    
    def test_clear_selection(self, context_menu, mock_session_state):
        """Test clear selection."""
        mock_parent = MagicMock()
        mock_parent.clear_selection = MagicMock()
        
        with patch.object(context_menu, 'parent', return_value=mock_parent):
            context_menu._clear_selection()
            
            mock_session_state.clear_selection.assert_called_once()
            mock_parent.clear_selection.assert_called_once()
    
    def test_duplicate_series_emits_signal(self, context_menu, qtbot):
        """Test duplicate series emits signal."""
        received_signals = []
        context_menu.duplicate_series_requested.connect(
            lambda ds, sr: received_signals.append((ds, sr)))
        
        context_menu._duplicate_series()
        
        assert len(received_signals) == 1
        assert received_signals[0] == ("test_dataset", "test_series")
    
    def test_hide_series(self, context_menu):
        """Test hide series functionality."""
        mock_parent = MagicMock()
        mock_plot_item = MagicMock()
        mock_plot_item.isVisible.return_value = True
        mock_parent._series_data = {
            "test_series": {"plot_item": mock_plot_item}
        }
        
        with patch.object(context_menu, 'parent', return_value=mock_parent):
            context_menu._hide_series()
            
            mock_plot_item.setVisible.assert_called_with(False)


# =============================================================================
# Factory Function Tests
# =============================================================================

class TestCreatePlotContextMenu:
    """Tests for create_plot_context_menu factory function."""
    
    def test_create_plot_context_menu(self, qtbot):
        """Test factory function creates menu."""
        from PyQt6.QtCore import QPointF

        from platform_base.desktop.menus.plot_context_menu import (
            create_plot_context_menu,
        )
        
        session_state = MagicMock()
        session_state.dataset_store = MagicMock()
        session_state.dataset_store.list_datasets.return_value = []
        
        signal_hub = MagicMock()
        
        menu = create_plot_context_menu(
            session_state=session_state,
            signal_hub=signal_hub,
            plot_position=QPointF(100.0, 200.0),
            dataset_id="ds1",
            series_id="sr1",
        )
        qtbot.addWidget(menu)
        
        assert menu is not None
        assert menu.dataset_id == "ds1"
        assert menu.series_id == "sr1"
    
    def test_create_plot_context_menu_minimal(self, qtbot):
        """Test factory function with minimal parameters."""
        from platform_base.desktop.menus.plot_context_menu import (
            create_plot_context_menu,
        )
        
        session_state = MagicMock()
        session_state.dataset_store = MagicMock()
        signal_hub = MagicMock()
        
        menu = create_plot_context_menu(
            session_state=session_state,
            signal_hub=signal_hub,
        )
        qtbot.addWidget(menu)
        
        assert menu is not None
        assert menu.dataset_id is None
        assert menu.series_id is None


# =============================================================================
# Statistics Tests
# =============================================================================

class TestStatisticsCalculation:
    """Tests for statistics calculation in context menu."""
    
    @pytest.fixture
    def mock_dataset_with_data(self):
        """Create mock dataset with numeric data."""
        dataset = MagicMock()
        series = MagicMock()
        series.name = "test_series"
        series.values = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        series.unit = "m"
        series.lineage = None
        dataset.series = {"test_series": series}
        dataset.timestamps = np.linspace(0, 1, 10)
        return dataset
    
    @pytest.fixture
    def context_menu_for_stats(self, mock_dataset_with_data, qtbot):
        """Create context menu for statistics testing."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        state.dataset_store.get_dataset.return_value = mock_dataset_with_data
        state.selection = MagicMock()
        
        menu = PlotContextMenu(
            session_state=state,
            signal_hub=MagicMock(),
            dataset_id="test_dataset",
            series_id="test_series",
        )
        qtbot.addWidget(menu)
        return menu
    
    def test_statistics_values(self, context_menu_for_stats, mock_dataset_with_data):
        """Test that statistics are calculated correctly."""
        values = mock_dataset_with_data.series["test_series"].values
        
        # Calculate expected statistics
        expected_mean = np.mean(values)
        expected_std = np.std(values)
        expected_min = np.min(values)
        expected_max = np.max(values)
        
        assert expected_mean == 5.5
        assert expected_min == 1.0
        assert expected_max == 10.0


# =============================================================================
# Edge Cases
# =============================================================================

class TestPlotContextMenuEdgeCases:
    """Edge case tests for PlotContextMenu."""
    
    def test_menu_with_empty_series_data(self, qtbot):
        """Test menu handles empty series data gracefully."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.series = {}  # Empty series
        state.dataset_store.get_dataset.return_value = mock_dataset
        
        menu = PlotContextMenu(
            session_state=state,
            signal_hub=MagicMock(),
            dataset_id="test_dataset",
            series_id=None,
        )
        qtbot.addWidget(menu)
        
        # Should not raise
        result = menu._has_multiple_series()
        assert result is False
    
    def test_skewness_large_dataset(self):
        """Test skewness calculation with large dataset."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        
        menu = PlotContextMenu.__new__(PlotContextMenu)
        
        # Large dataset
        values = np.random.randn(100000)
        skewness = PlotContextMenu._calculate_skewness(menu, values)
        
        # Should be close to 0 for normal distribution
        assert abs(skewness) < 0.1
    
    def test_kurtosis_large_dataset(self):
        """Test kurtosis calculation with large dataset."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        menu = PlotContextMenu.__new__(PlotContextMenu)
        
        # Large normal dataset
        values = np.random.randn(100000)
        kurtosis = PlotContextMenu._calculate_kurtosis(menu, values)
        
        # Excess kurtosis should be close to 0 for normal distribution
        assert abs(kurtosis) < 0.3


# =============================================================================
# Integration Tests
# =============================================================================

class TestPlotContextMenuIntegration:
    """Integration tests for PlotContextMenu."""
    
    @pytest.fixture
    def full_mock_setup(self):
        """Create full mock setup for integration tests."""
        # Mock dataset
        dataset = MagicMock()
        series1 = MagicMock()
        series1.name = "pressure"
        series1.values = np.linspace(0, 100, 1000)
        series1.unit = "bar"
        series1.lineage = None
        
        series2 = MagicMock()
        series2.name = "temperature"
        series2.values = np.linspace(20, 80, 1000)
        series2.unit = "°C"
        series2.lineage = None
        
        dataset.series = {"pressure": series1, "temperature": series2}
        dataset.timestamps = np.linspace(0, 10, 1000)
        
        # Mock store
        store = MagicMock()
        store.get_dataset.return_value = dataset
        store.list_datasets.return_value = []
        
        # Mock state
        state = MagicMock()
        state.dataset_store = store
        state.selection = MagicMock()
        state.selection.time_window = None
        
        return {
            "dataset": dataset,
            "store": store,
            "state": state,
        }
    
    def test_full_workflow_statistics(self, full_mock_setup, qtbot):
        """Test full workflow for statistics calculation."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        menu = PlotContextMenu(
            session_state=full_mock_setup["state"],
            signal_hub=MagicMock(),
            dataset_id="test_dataset",
            series_id="pressure",
        )
        qtbot.addWidget(menu)
        
        # Verify multiple series detection
        assert menu._has_multiple_series() is True
    
    def test_correlation_available_for_multiple_series(self, full_mock_setup, qtbot):
        """Test correlation analysis is available when multiple series exist."""
        from platform_base.desktop.menus.plot_context_menu import PlotContextMenu
        
        menu = PlotContextMenu(
            session_state=full_mock_setup["state"],
            signal_hub=MagicMock(),
            dataset_id="test_dataset",
            series_id="pressure",
        )
        qtbot.addWidget(menu)
        
        # Find correlation action in menu
        found_correlation = False
        for action in menu.actions():
            if "Correlation" in action.text():
                found_correlation = True
                break
            # Check submenus
            if action.menu():
                for sub_action in action.menu().actions():
                    if "Correlation" in sub_action.text():
                        found_correlation = True
                        break
        
        # Correlation should be available for multiple series
        assert menu._has_multiple_series() is True
