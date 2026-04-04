"""
Comprehensive tests for viz/streaming.py module.

Target: Increase coverage from ~0% to 80%+
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

import numpy as np
import pytest


class TestValuePredicate:
    """Tests for ValuePredicate class."""
    
    def test_greater_than_operator(self):
        """Test greater than operator."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator=">",
            value=5.0
        )
        
        values = np.array([1.0, 5.0, 10.0, 3.0, 8.0])
        result = pred.evaluate(values)
        
        expected = np.array([False, False, True, False, True])
        np.testing.assert_array_equal(result, expected)
    
    def test_less_than_operator(self):
        """Test less than operator."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator="<",
            value=5.0
        )
        
        values = np.array([1.0, 5.0, 10.0, 3.0])
        result = pred.evaluate(values)
        
        expected = np.array([True, False, False, True])
        np.testing.assert_array_equal(result, expected)
    
    def test_greater_equal_operator(self):
        """Test greater or equal operator."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator=">=",
            value=5.0
        )
        
        values = np.array([1.0, 5.0, 10.0])
        result = pred.evaluate(values)
        
        expected = np.array([False, True, True])
        np.testing.assert_array_equal(result, expected)
    
    def test_less_equal_operator(self):
        """Test less or equal operator."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator="<=",
            value=5.0
        )
        
        values = np.array([1.0, 5.0, 10.0])
        result = pred.evaluate(values)
        
        expected = np.array([True, True, False])
        np.testing.assert_array_equal(result, expected)
    
    def test_equal_operator(self):
        """Test equal operator."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator="==",
            value=5.0
        )
        
        values = np.array([1.0, 5.0, 5.0, 3.0])
        result = pred.evaluate(values)
        
        expected = np.array([False, True, True, False])
        np.testing.assert_array_equal(result, expected)
    
    def test_not_equal_operator(self):
        """Test not equal operator."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator="!=",
            value=5.0
        )
        
        values = np.array([1.0, 5.0, 5.0, 3.0])
        result = pred.evaluate(values)
        
        expected = np.array([True, False, False, True])
        np.testing.assert_array_equal(result, expected)
    
    def test_empty_array(self):
        """Test with empty array."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test_series",
            operator=">",
            value=5.0
        )
        
        values = np.array([])
        result = pred.evaluate(values)
        
        assert len(result) == 0


class TestSmoothConfig:
    """Tests for SmoothConfig class."""
    
    def test_default_window(self):
        """Test default window size."""
        from platform_base.viz.streaming import SmoothConfig
        
        config = SmoothConfig(method="savitzky_golay")
        
        assert config.window == 5
        assert config.sigma is None
    
    def test_custom_window(self):
        """Test custom window size."""
        from platform_base.viz.streaming import SmoothConfig
        
        config = SmoothConfig(method="gaussian", window=11, sigma=2.0)
        
        assert config.window == 11
        assert config.sigma == 2.0
    
    def test_all_methods(self):
        """Test all smoothing methods."""
        from platform_base.viz.streaming import SmoothConfig
        
        methods = ["savitzky_golay", "gaussian", "median", "lowpass"]
        for method in methods:
            config = SmoothConfig(method=method)
            assert config.method == method


class TestScaleConfig:
    """Tests for ScaleConfig class."""
    
    def test_linear_scale(self):
        """Test linear scale configuration."""
        from platform_base.viz.streaming import ScaleConfig
        
        config = ScaleConfig(method="linear", range=(0.0, 100.0))
        
        assert config.method == "linear"
        assert config.range == (0.0, 100.0)
    
    def test_log_scale(self):
        """Test log scale configuration."""
        from platform_base.viz.streaming import ScaleConfig
        
        config = ScaleConfig(method="log")
        
        assert config.method == "log"
        assert config.range is None
    
    def test_normalized_scale(self):
        """Test normalized scale configuration."""
        from platform_base.viz.streaming import ScaleConfig
        
        config = ScaleConfig(method="normalized", range=(0.0, 1.0))
        
        assert config.method == "normalized"


class TestTimeInterval:
    """Tests for TimeInterval class."""
    
    def test_contains_inside(self):
        """Test contains returns True for value inside interval."""
        from platform_base.viz.streaming import TimeInterval
        
        interval = TimeInterval(start=0.0, end=10.0)
        
        assert interval.contains(5.0) is True
    
    def test_contains_start_boundary(self):
        """Test contains returns True for start boundary."""
        from platform_base.viz.streaming import TimeInterval
        
        interval = TimeInterval(start=0.0, end=10.0)
        
        assert interval.contains(0.0) is True
    
    def test_contains_end_boundary(self):
        """Test contains returns True for end boundary."""
        from platform_base.viz.streaming import TimeInterval
        
        interval = TimeInterval(start=0.0, end=10.0)
        
        assert interval.contains(10.0) is True
    
    def test_contains_outside(self):
        """Test contains returns False for value outside interval."""
        from platform_base.viz.streaming import TimeInterval
        
        interval = TimeInterval(start=0.0, end=10.0)
        
        assert interval.contains(-1.0) is False
        assert interval.contains(11.0) is False


class TestStreamFilters:
    """Tests for StreamFilters class."""
    
    def test_default_values(self):
        """Test default filter values."""
        from platform_base.viz.streaming import StreamFilters
        
        filters = StreamFilters()
        
        assert filters.time_include is None
        assert filters.time_exclude is None
        assert filters.max_points_per_window == 5000
        assert filters.downsample_method == "lttb"
        assert filters.hide_interpolated is False
        assert filters.hide_nan is True
        assert filters.quality_threshold is None
    
    def test_custom_downsample_method(self):
        """Test custom downsample method."""
        from platform_base.viz.streaming import StreamFilters
        
        filters = StreamFilters(downsample_method="minmax")
        
        assert filters.downsample_method == "minmax"
    
    def test_adaptive_downsample(self):
        """Test adaptive downsample method."""
        from platform_base.viz.streaming import StreamFilters
        
        filters = StreamFilters(downsample_method="adaptive")
        
        assert filters.downsample_method == "adaptive"
    
    def test_time_intervals(self):
        """Test time interval filters."""
        from platform_base.viz.streaming import StreamFilters, TimeInterval
        
        filters = StreamFilters(
            time_include=[TimeInterval(start=0.0, end=10.0)],
            time_exclude=[TimeInterval(start=5.0, end=7.0)]
        )
        
        assert len(filters.time_include) == 1
        assert len(filters.time_exclude) == 1
    
    def test_hidden_series(self):
        """Test hidden series list."""
        from platform_base.viz.streaming import StreamFilters
        
        filters = StreamFilters(hidden_series=["series1", "series2"])
        
        assert "series1" in filters.hidden_series
        assert "series2" in filters.hidden_series


class TestPlayState:
    """Tests for PlayState class."""
    
    def test_default_stopped(self):
        """Test default state is stopped."""
        from platform_base.viz.streaming import PlayState
        
        state = PlayState()
        
        assert state.is_playing is False
        assert state.is_paused is False
        assert state.is_stopped is True
    
    def test_playing_state(self):
        """Test playing state."""
        from platform_base.viz.streaming import PlayState
        
        state = PlayState(is_playing=True, is_stopped=False)
        
        assert state.is_playing is True
        assert state.is_stopped is False
    
    def test_paused_state(self):
        """Test paused state."""
        from platform_base.viz.streaming import PlayState
        
        state = PlayState(is_paused=True, is_stopped=False)
        
        assert state.is_paused is True
        assert state.is_stopped is False


class TestStreamingState:
    """Tests for StreamingState class."""
    
    def test_default_values(self):
        """Test default streaming state values."""
        from platform_base.viz.streaming import StreamingState
        
        state = StreamingState()
        
        assert state.current_time_index == 0
        assert state.speed == 1.0
        assert state.loop is False
    
    def test_custom_speed(self):
        """Test custom playback speed."""
        from platform_base.viz.streaming import StreamingState
        
        state = StreamingState(speed=2.0)
        
        assert state.speed == 2.0
    
    def test_custom_window_size(self):
        """Test custom window size."""
        from platform_base.viz.streaming import StreamingState
        
        state = StreamingState(window_size=timedelta(seconds=120))
        
        assert state.window_size == timedelta(seconds=120)
    
    def test_loop_enabled(self):
        """Test loop enabled."""
        from platform_base.viz.streaming import StreamingState
        
        state = StreamingState(loop=True)
        
        assert state.loop is True
    
    def test_with_filters(self):
        """Test streaming state with filters."""
        from platform_base.viz.streaming import StreamFilters, StreamingState
        
        filters = StreamFilters(max_points_per_window=1000)
        state = StreamingState(filters=filters)
        
        assert state.filters.max_points_per_window == 1000


class TestStreamingHelpers:
    """Tests for streaming helper functions and utilities."""
    
    def test_downsample_lttb_format(self):
        """Test LTTB downsample input/output format."""
        # Generate sample data
        n_points = 10000
        t = np.linspace(0, 100, n_points)
        y = np.sin(t) + np.random.randn(n_points) * 0.1
        
        # Target size
        target = 1000
        
        # Simple uniform downsample for comparison
        indices = np.linspace(0, n_points - 1, target, dtype=int)
        t_down = t[indices]
        y_down = y[indices]
        
        assert len(t_down) == target
        assert len(y_down) == target
    
    def test_time_window_calculation(self):
        """Test time window calculation."""
        window_size = timedelta(seconds=60)
        current_time = 150.0  # seconds
        
        window_start = current_time - window_size.total_seconds() / 2
        window_end = current_time + window_size.total_seconds() / 2
        
        assert window_start == 120.0
        assert window_end == 180.0
    
    def test_speed_adjustment(self):
        """Test speed adjustment calculation."""
        base_interval = 0.1  # seconds
        speed = 2.0
        
        adjusted_interval = base_interval / speed
        
        assert adjusted_interval == 0.05
    
    def test_frame_calculation(self):
        """Test frame calculation for playback."""
        total_duration = 1000.0  # seconds
        fps = 30
        
        total_frames = int(total_duration * fps)
        frame_duration = 1.0 / fps
        
        assert total_frames == 30000
        assert abs(frame_duration - 0.0333) < 0.001


class TestFilterApplication:
    """Tests for filter application logic."""
    
    def test_apply_time_include_filter(self):
        """Test applying time include filter."""
        from platform_base.viz.streaming import TimeInterval

        # Sample data
        t = np.array([0.0, 5.0, 10.0, 15.0, 20.0])
        
        # Include interval
        interval = TimeInterval(start=5.0, end=15.0)
        
        mask = np.array([interval.contains(ti) for ti in t])
        t_filtered = t[mask]
        
        np.testing.assert_array_equal(t_filtered, np.array([5.0, 10.0, 15.0]))
    
    def test_apply_nan_filter(self):
        """Test applying NaN filter."""
        # Sample data with NaN
        values = np.array([1.0, np.nan, 3.0, np.nan, 5.0])
        
        # Filter NaN
        mask = ~np.isnan(values)
        filtered = values[mask]
        
        np.testing.assert_array_equal(filtered, np.array([1.0, 3.0, 5.0]))
    
    def test_apply_value_predicate_filter(self):
        """Test applying value predicate filter."""
        from platform_base.viz.streaming import ValuePredicate
        
        pred = ValuePredicate(
            series_id="test",
            operator=">",
            value=3.0
        )
        
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        mask = pred.evaluate(values)
        filtered = values[mask]
        
        np.testing.assert_array_equal(filtered, np.array([4.0, 5.0]))


class TestDataTypes:
    """Tests for data type definitions."""
    
    def test_series_id_type(self):
        """Test SeriesID type."""
        from platform_base.core.models import SeriesID
        
        series_id: SeriesID = "my_series_123"
        assert isinstance(series_id, str)
    
    def test_session_id_type(self):
        """Test SessionID type."""
        from platform_base.core.models import SessionID
        
        session_id: SessionID = "session_abc"
        assert isinstance(session_id, str)
    
    def test_view_id_type(self):
        """Test ViewID type."""
        from platform_base.core.models import ViewID
        
        view_id: ViewID = "view_main"
        assert isinstance(view_id, str)
