"""
Unit tests for Selection Manager module.

Tests for:
- SelectionCriteria classes
- SelectionState management
- SelectionManager operations
"""

import numpy as np
import pytest
from PyQt6.QtCore import QRectF

from platform_base.desktop.selection.selection_manager import (
    ConditionalSelection,
    GraphicalSelection,
    SelectionCriteria,
    SelectionMode,
    SelectionState,
    SelectionType,
    TemporalSelection,
)


class TestSelectionType:
    """Tests for SelectionType enum"""

    def test_temporal_type(self):
        assert SelectionType.TEMPORAL.value == "temporal"

    def test_graphical_type(self):
        assert SelectionType.GRAPHICAL.value == "graphical"

    def test_conditional_type(self):
        assert SelectionType.CONDITIONAL.value == "conditional"

    def test_combined_type(self):
        assert SelectionType.COMBINED.value == "combined"


class TestSelectionMode:
    """Tests for SelectionMode enum"""

    def test_replace_mode(self):
        assert SelectionMode.REPLACE.value == "replace"

    def test_add_mode(self):
        assert SelectionMode.ADD.value == "add"

    def test_subtract_mode(self):
        assert SelectionMode.SUBTRACT.value == "subtract"

    def test_intersect_mode(self):
        assert SelectionMode.INTERSECT.value == "intersect"


class TestSelectionCriteria:
    """Tests for base SelectionCriteria"""

    def test_base_criteria_creation(self):
        criteria = SelectionCriteria(
            selection_type=SelectionType.TEMPORAL,
            mode=SelectionMode.REPLACE
        )
        assert criteria.selection_type == SelectionType.TEMPORAL
        assert criteria.mode == SelectionMode.REPLACE

    def test_base_matches_point_returns_false(self):
        """Base class should return False for any point"""
        criteria = SelectionCriteria(selection_type=SelectionType.TEMPORAL)
        assert criteria.matches_point(0.0, 0.0) is False
        assert criteria.matches_point(100.0, 50.0) is False


class TestTemporalSelection:
    """Tests for TemporalSelection criteria"""

    def test_temporal_selection_creation(self):
        selection = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            start_time=0.0,
            end_time=10.0
        )
        assert selection.start_time == 0.0
        assert selection.end_time == 10.0
        assert selection.selection_type == SelectionType.TEMPORAL

    def test_temporal_selection_swaps_inverted_times(self):
        """Should swap if start > end"""
        selection = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            start_time=10.0,
            end_time=0.0
        )
        assert selection.start_time == 0.0
        assert selection.end_time == 10.0

    def test_matches_point_inside_range(self):
        selection = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            start_time=0.0,
            end_time=10.0
        )
        assert selection.matches_point(5.0, 0.0) is True
        assert selection.matches_point(0.0, 0.0) is True
        assert selection.matches_point(10.0, 0.0) is True

    def test_matches_point_outside_range(self):
        selection = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            start_time=0.0,
            end_time=10.0
        )
        assert selection.matches_point(-1.0, 0.0) is False
        assert selection.matches_point(11.0, 0.0) is False

    def test_duration_property(self):
        selection = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            start_time=5.0,
            end_time=15.0
        )
        assert selection.duration == 10.0


class TestGraphicalSelection:
    """Tests for GraphicalSelection criteria"""

    def test_graphical_selection_creation(self):
        rect = QRectF(0.0, 0.0, 10.0, 10.0)
        selection = GraphicalSelection(
            selection_type=SelectionType.GRAPHICAL,
            region=rect
        )
        assert selection.selection_type == SelectionType.GRAPHICAL

    def test_matches_point_inside_region(self):
        # QRectF(x, y, width, height) - creates region from (0,0) to (10,10)
        rect = QRectF(0.0, 0.0, 10.0, 10.0)
        selection = GraphicalSelection(
            selection_type=SelectionType.GRAPHICAL,
            region=rect
        )
        # Points inside
        assert selection.matches_point(5.0, 5.0) is True
        assert selection.matches_point(0.0, 0.0) is True

    def test_matches_point_outside_region(self):
        rect = QRectF(0.0, 0.0, 10.0, 10.0)
        selection = GraphicalSelection(
            selection_type=SelectionType.GRAPHICAL,
            region=rect
        )
        # Points outside
        assert selection.matches_point(-1.0, 5.0) is False
        assert selection.matches_point(15.0, 5.0) is False

    def test_matches_point_with_none_region(self):
        selection = GraphicalSelection(selection_type=SelectionType.GRAPHICAL)
        assert selection.matches_point(5.0, 5.0) is False

    def test_time_range_property(self):
        rect = QRectF(5.0, 0.0, 10.0, 10.0)  # x=5, width=10, so range is 5-15
        selection = GraphicalSelection(
            selection_type=SelectionType.GRAPHICAL,
            region=rect
        )
        time_range = selection.time_range
        assert time_range[0] == 5.0
        assert time_range[1] == 15.0  # left + width

    def test_time_range_with_none_region(self):
        selection = GraphicalSelection(selection_type=SelectionType.GRAPHICAL)
        assert selection.time_range == (0.0, 0.0)

    def test_value_range_property(self):
        rect = QRectF(0.0, 2.0, 10.0, 8.0)  # y=2, height=8, so range is 2-10
        selection = GraphicalSelection(
            selection_type=SelectionType.GRAPHICAL,
            region=rect
        )
        value_range = selection.value_range
        # In Qt, bottom() = y + height, top() = y for QRectF
        assert value_range[0] == 10.0  # bottom = y + height
        assert value_range[1] == 2.0   # top = y

    def test_value_range_with_none_region(self):
        selection = GraphicalSelection(selection_type=SelectionType.GRAPHICAL)
        assert selection.value_range == (0.0, 0.0)


class TestConditionalSelection:
    """Tests for ConditionalSelection criteria"""

    def test_conditional_selection_creation(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="value > 5"
        )
        assert selection.selection_type == SelectionType.CONDITIONAL
        assert selection.condition == "value > 5"

    def test_simple_value_condition(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="value > 5"
        )
        assert selection.matches_point(0.0, 10.0) is True
        assert selection.matches_point(0.0, 3.0) is False

    def test_time_based_condition(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="t > 10"
        )
        assert selection.matches_point(15.0, 0.0) is True
        assert selection.matches_point(5.0, 0.0) is False

    def test_combined_condition(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="t > 5 and value < 10"
        )
        assert selection.matches_point(10.0, 5.0) is True
        assert selection.matches_point(3.0, 5.0) is False
        assert selection.matches_point(10.0, 15.0) is False

    def test_math_functions_in_condition(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="abs(value) < 5"
        )
        assert selection.matches_point(0.0, 3.0) is True
        assert selection.matches_point(0.0, -3.0) is True
        assert selection.matches_point(0.0, 10.0) is False

    def test_invalid_condition_returns_false(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="invalid_function(value)"
        )
        # Should not raise, but return False
        assert selection.matches_point(0.0, 5.0) is False


class TestSelectionState:
    """Tests for SelectionState class"""

    def test_selection_state_creation(self):
        state = SelectionState(dataset_id="test_dataset")
        assert state.dataset_id == "test_dataset"
        assert state.series_id is None
        assert state.selected_mask is None
        assert state.total_points == 0

    def test_selection_state_with_series_id(self):
        state = SelectionState(dataset_id="test_dataset", series_id="series_1")
        assert state.dataset_id == "test_dataset"
        assert state.series_id == "series_1"

    def test_set_data_size(self):
        state = SelectionState(dataset_id="test")
        state.set_data_size(100)
        assert state.total_points == 100
        assert len(state.selected_mask) == 100
        assert not state.selected_mask.any()  # All False initially

    def test_set_data_size_resets_on_change(self):
        state = SelectionState(dataset_id="test")
        state.set_data_size(100)
        state.selected_mask[0] = True
        state.set_data_size(50)  # Size changed
        assert state.total_points == 50
        assert len(state.selected_mask) == 50

    def test_apply_criteria_replace_mode(self):
        state = SelectionState(dataset_id="test")
        t_data = np.array([1.0, 5.0, 10.0, 15.0, 20.0])
        value_data = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

        criteria = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            mode=SelectionMode.REPLACE,
            start_time=4.0,
            end_time=16.0
        )

        state.apply_criteria(criteria, t_data, value_data)

        # Points at t=5, t=10, t=15 should be selected
        expected = np.array([False, True, True, True, False])
        np.testing.assert_array_equal(state.selected_mask, expected)

    def test_apply_criteria_add_mode(self):
        state = SelectionState(dataset_id="test")
        t_data = np.array([1.0, 5.0, 10.0, 15.0, 20.0])
        value_data = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

        # First selection
        criteria1 = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            mode=SelectionMode.REPLACE,
            start_time=0.0,
            end_time=2.0
        )
        state.apply_criteria(criteria1, t_data, value_data)
        assert state.selected_mask[0] == True

        # Add more
        criteria2 = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            mode=SelectionMode.ADD,
            start_time=18.0,
            end_time=22.0
        )
        state.apply_criteria(criteria2, t_data, value_data)

        # Both first and last should be selected
        assert state.selected_mask[0] == True
        assert state.selected_mask[4] == True

    def test_apply_criteria_mismatched_arrays_raises(self):
        state = SelectionState(dataset_id="test")
        t_data = np.array([1.0, 2.0, 3.0])
        value_data = np.array([0.0, 0.0])  # Different length

        criteria = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            start_time=0.0,
            end_time=5.0
        )

        with pytest.raises(ValueError, match="same length"):
            state.apply_criteria(criteria, t_data, value_data)


class TestSelectionStateAdvanced:
    """Advanced tests for SelectionState"""

    def test_subtract_mode(self):
        state = SelectionState(dataset_id="test")
        t_data = np.array([1.0, 5.0, 10.0, 15.0, 20.0])
        value_data = np.zeros(5)

        # Select all
        state.set_data_size(5)
        state.selected_mask[:] = True

        # Subtract middle
        criteria = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            mode=SelectionMode.SUBTRACT,
            start_time=4.0,
            end_time=16.0
        )
        state.apply_criteria(criteria, t_data, value_data)

        # First and last should remain selected
        expected = np.array([True, False, False, False, True])
        np.testing.assert_array_equal(state.selected_mask, expected)

    def test_intersect_mode(self):
        state = SelectionState(dataset_id="test")
        t_data = np.array([1.0, 5.0, 10.0, 15.0, 20.0])
        value_data = np.zeros(5)

        # Select first 4 points
        state.set_data_size(5)
        state.selected_mask[:4] = True

        # Intersect with last 4 points
        criteria = TemporalSelection(
            selection_type=SelectionType.TEMPORAL,
            mode=SelectionMode.INTERSECT,
            start_time=4.0,
            end_time=25.0
        )
        state.apply_criteria(criteria, t_data, value_data)

        # Only points 5, 10, 15 should remain (intersection)
        expected = np.array([False, True, True, True, False])
        np.testing.assert_array_equal(state.selected_mask, expected)


class TestConditionalSelectionAdvanced:
    """Advanced tests for ConditionalSelection with math functions"""

    def test_sqrt_condition(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="sqrt(value) < 3"
        )
        assert selection.matches_point(0.0, 4.0) is True  # sqrt(4) = 2 < 3
        assert selection.matches_point(0.0, 16.0) is False  # sqrt(16) = 4 > 3

    def test_trig_condition(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="sin(t) > 0"
        )
        assert selection.matches_point(np.pi / 2, 0.0) is True  # sin(pi/2) = 1
        assert selection.matches_point(np.pi * 1.5, 0.0) is False  # sin(3pi/2) = -1

    def test_pi_constant(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="t < pi"
        )
        assert selection.matches_point(3.0, 0.0) is True  # 3 < 3.14159...
        assert selection.matches_point(4.0, 0.0) is False  # 4 > 3.14159...

    def test_complex_expression(self):
        selection = ConditionalSelection(
            selection_type=SelectionType.CONDITIONAL,
            condition="abs(value - 10) < 2"
        )
        assert selection.matches_point(0.0, 9.0) is True
        assert selection.matches_point(0.0, 11.0) is True
        assert selection.matches_point(0.0, 5.0) is False
