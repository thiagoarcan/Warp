"""Tests for streaming multi-view synchronization"""
import numpy as np
import pytest
from datetime import timedelta
from typing import List

from platform_base.viz.streaming import (
    StreamingEngine,
    StreamingState,
    StreamFilters,
    TimeInterval,
    ValuePredicate,
    ViewSubscription,
    TickUpdate,
    PlayState
)


class TestStreamingEngineSetup:
    """Tests for StreamingEngine data setup"""
    
    def test_setup_with_time_points(self):
        """Engine should store time points and compute eligible indices"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test_session")
        
        t = np.linspace(0, 100, 1000)
        engine.setup_data(t)
        
        assert engine.total_points == 1000
        assert len(engine.eligible_indices) == 1000  # No filters
    
    def test_setup_with_series_data(self):
        """Engine should store series data"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test_session")
        
        t = np.linspace(0, 100, 100)
        series = {
            "temp": np.sin(t),
            "pressure": np.cos(t)
        }
        engine.setup_data(t, series)
        
        assert "temp" in engine.series_data
        assert "pressure" in engine.series_data


class TestEligibilityFilters:
    """Tests for eligibility filtering"""
    
    def test_time_include_filter(self):
        """Time include filter should limit eligible indices"""
        filters = StreamFilters(
            time_include=[TimeInterval(start=20, end=80)]
        )
        state = StreamingState(filters=filters)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)  # 0, 1, 2, ..., 100
        engine.setup_data(t)
        
        # Only indices 20-80 should be eligible (61 points)
        assert len(engine.eligible_indices) == 61
    
    def test_time_exclude_filter(self):
        """Time exclude filter should remove indices"""
        filters = StreamFilters(
            time_exclude=[TimeInterval(start=40, end=60)]
        )
        state = StreamingState(filters=filters)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t)
        
        # 101 - 21 excluded points = 80 eligible
        assert len(engine.eligible_indices) == 80
    
    def test_hide_nan_filter(self):
        """Hide NaN filter should exclude NaN values"""
        filters = StreamFilters(hide_nan=True)
        state = StreamingState(filters=filters)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 100)
        values = np.sin(t)
        values[20:30] = np.nan
        
        engine.setup_data(t, {"series1": values})
        
        # 100 - 10 NaN points = 90 eligible
        assert len(engine.eligible_indices) == 90
    
    def test_value_predicate_filter(self):
        """Value predicate filter should filter based on values"""
        predicate = ValuePredicate(series_id="temp", operator=">", value=0)
        filters = StreamFilters(
            value_predicates={"temp": predicate}
        )
        state = StreamingState(filters=filters)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 2 * np.pi, 100)
        values = np.sin(t)  # ~50% positive
        
        engine.setup_data(t, {"temp": values})
        
        # Approximately half should be eligible
        assert 40 < len(engine.eligible_indices) < 60


class TestPlaybackControls:
    """Tests for playback control methods"""
    
    def test_play_starts_playback(self):
        """Play should set playing state"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        engine.play()
        
        assert state.play_state.is_playing
        assert not state.play_state.is_paused
        assert not state.play_state.is_stopped
    
    def test_pause_pauses_playback(self):
        """Pause should set paused state"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        engine.play()
        engine.pause()
        
        assert not state.play_state.is_playing
        assert state.play_state.is_paused
    
    def test_stop_resets_position(self):
        """Stop should reset to beginning"""
        state = StreamingState(current_time_index=50)
        engine = StreamingEngine(state, session_id="test")
        
        engine.stop()
        
        assert state.current_time_index == 0
        assert state.play_state.is_stopped
    
    def test_seek_changes_position(self):
        """Seek should move to specific time"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t)
        
        engine.seek(50.0)
        
        assert state.current_time_index == 50


class TestTickAdvancement:
    """Tests for tick advancement"""
    
    def test_tick_advances_index(self):
        """Tick should advance current index when playing"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t)
        engine.play()
        
        initial_idx = state.current_time_index
        engine.tick()
        
        assert state.current_time_index > initial_idx
    
    def test_tick_respects_speed(self):
        """Tick should advance by speed amount"""
        state = StreamingState(speed=5.0)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t)
        engine.play()
        
        engine.tick()
        
        assert state.current_time_index == 5
    
    def test_tick_loops_when_enabled(self):
        """Tick should loop back when loop is enabled"""
        state = StreamingState(loop=True, current_time_index=100)  # At the end
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t)
        engine.play()
        
        update = engine.tick()
        
        # Should loop to beginning (index 0 after looping from 101)
        assert state.current_time_index == 0
    
    def test_tick_stops_at_end_without_loop(self):
        """Tick should stop at end when loop is disabled"""
        state = StreamingState(loop=False, current_time_index=100)  # At the end
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t)
        engine.play()
        
        update = engine.tick()
        
        # Should be at the last valid index and stopped
        assert state.current_time_index == 100
        assert not state.play_state.is_playing


class TestMultiViewSync:
    """Tests for multi-view synchronization"""
    
    def test_subscribe_adds_view(self):
        """Subscribe should add view to subscribers"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        subscription = ViewSubscription(view_id="view1")
        engine.subscribe(subscription)
        
        assert "view1" in engine._subscribers
    
    def test_unsubscribe_removes_view(self):
        """Unsubscribe should remove view from subscribers"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        subscription = ViewSubscription(view_id="view1")
        engine.subscribe(subscription)
        engine.unsubscribe("view1")
        
        assert "view1" not in engine._subscribers
    
    def test_tick_notifies_subscribers(self):
        """Tick should call subscriber callbacks"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t, {"temp": np.sin(t)})
        
        received_updates: List[TickUpdate] = []
        
        def callback(update: TickUpdate):
            received_updates.append(update)
        
        subscription = ViewSubscription(view_id="view1", callback=callback)
        engine.subscribe(subscription)
        engine.play()
        
        engine.tick()
        
        assert len(received_updates) == 1
        assert received_updates[0].session_id == "test"
    
    def test_subscriber_series_filter(self):
        """Subscriber with series filter should receive filtered data"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t, {
            "temp": np.sin(t),
            "pressure": np.cos(t)
        })
        
        received_data = {}
        
        def callback(update: TickUpdate):
            received_data.update(update.window_data)
        
        subscription = ViewSubscription(
            view_id="view1",
            callback=callback,
            series_filter=["temp"]  # Only temp
        )
        engine.subscribe(subscription)
        engine.play()
        
        engine.tick()
        
        # Should only have temp
        assert "temp" in received_data or len(received_data) == 0
        assert "pressure" not in received_data
    
    def test_sync_views_sends_current_state(self):
        """sync_views should send current state to specified views"""
        state = StreamingState(current_time_index=50)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t, {"temp": np.sin(t)})  # Need series data for window
        
        received_updates: List[TickUpdate] = []
        
        def callback(update: TickUpdate):
            received_updates.append(update)
        
        subscription = ViewSubscription(view_id="view1", callback=callback)
        engine.subscribe(subscription)
        
        # Verify subscription was added
        assert "view1" in engine._subscribers
        
        engine.sync_views(["view1"])
        
        # Check that callback was called
        assert len(received_updates) >= 1, f"Expected at least 1 update, got {len(received_updates)}. Subscribers: {list(engine._subscribers.keys())}"
        assert received_updates[0].current_time_index == 50


class TestWindowData:
    """Tests for window data extraction"""
    
    def test_window_data_contains_series(self):
        """Window data should contain configured series"""
        state = StreamingState(
            window_size=timedelta(seconds=20)
        )
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t, {"temp": np.sin(t)})
        
        state.current_time_index = 50
        
        data, time = engine._get_window_data()
        
        assert "temp" in data
        assert len(time) > 0
    
    def test_hidden_series_excluded(self):
        """Hidden series should be excluded from window data"""
        filters = StreamFilters(hidden_series=["pressure"])
        state = StreamingState(filters=filters)
        engine = StreamingEngine(state, session_id="test")
        
        t = np.linspace(0, 100, 101)
        engine.setup_data(t, {
            "temp": np.sin(t),
            "pressure": np.cos(t)
        })
        
        state.current_time_index = 50
        
        data, _ = engine._get_window_data()
        
        assert "temp" in data
        assert "pressure" not in data


class TestLTTBDownsampling:
    """Tests for LTTB downsampling"""
    
    def test_lttb_reduces_points(self):
        """LTTB should reduce number of points"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        x = np.linspace(0, 100, 1000)
        y = np.sin(x)
        
        x_ds, y_ds = engine._downsample_lttb(x, y, 100)
        
        assert len(x_ds) == 100
        assert len(y_ds) == 100
    
    def test_lttb_preserves_endpoints(self):
        """LTTB should preserve first and last points"""
        state = StreamingState()
        engine = StreamingEngine(state, session_id="test")
        
        x = np.linspace(0, 100, 1000)
        y = np.sin(x)
        
        x_ds, y_ds = engine._downsample_lttb(x, y, 100)
        
        assert x_ds[0] == x[0]
        assert x_ds[-1] == x[-1]
        assert y_ds[0] == y[0]
        assert y_ds[-1] == y[-1]
