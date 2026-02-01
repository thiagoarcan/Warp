"""
Tests for streaming/temporal_sync.py module.

Tests temporal synchronization functionality including:
- StreamFrame dataclass
- SyncPoint dataclass
- TemporalSynchronizer class
- StreamingPlotManager class
"""

import time
from unittest.mock import MagicMock, Mock

import pytest

# =============================================================================
# StreamFrame Tests
# =============================================================================

class TestStreamFrame:
    """Tests for StreamFrame dataclass."""
    
    def test_create_stream_frame(self):
        """Test creating StreamFrame."""
        from platform_base.streaming.temporal_sync import StreamFrame
        
        frame = StreamFrame(
            timestamp=1.0,
            data={'value': 42},
            series_id='series_1',
            frame_number=0,
        )
        
        assert frame.timestamp == 1.0
        assert frame.data == {'value': 42}
        assert frame.series_id == 'series_1'
        assert frame.frame_number == 0
    
    def test_stream_frame_with_various_data_types(self):
        """Test StreamFrame with different data types."""
        import numpy as np

        from platform_base.streaming.temporal_sync import StreamFrame

        # With numpy array
        frame1 = StreamFrame(
            timestamp=1.0,
            data=np.array([1, 2, 3]),
            series_id='series_1',
            frame_number=0,
        )
        assert len(frame1.data) == 3
        
        # With list
        frame2 = StreamFrame(
            timestamp=2.0,
            data=[1, 2, 3, 4, 5],
            series_id='series_2',
            frame_number=1,
        )
        assert len(frame2.data) == 5
        
        # With dict
        frame3 = StreamFrame(
            timestamp=3.0,
            data={'x': 10, 'y': 20},
            series_id='series_3',
            frame_number=2,
        )
        assert frame3.data['x'] == 10


# =============================================================================
# SyncPoint Tests
# =============================================================================

class TestSyncPoint:
    """Tests for SyncPoint dataclass."""
    
    def test_create_sync_point(self):
        """Test creating SyncPoint."""
        from platform_base.streaming.temporal_sync import SyncPoint
        
        sync = SyncPoint(
            master_timestamp=100.0,
            slave_offsets={'slave1': 0.1, 'slave2': -0.05},
        )
        
        assert sync.master_timestamp == 100.0
        assert sync.slave_offsets['slave1'] == 0.1
        assert sync.slave_offsets['slave2'] == -0.05
    
    def test_sync_point_empty_offsets(self):
        """Test SyncPoint with no slaves."""
        from platform_base.streaming.temporal_sync import SyncPoint
        
        sync = SyncPoint(
            master_timestamp=50.0,
            slave_offsets={},
        )
        
        assert sync.master_timestamp == 50.0
        assert len(sync.slave_offsets) == 0


# =============================================================================
# TemporalSynchronizer Tests (Non-Qt Parts)
# =============================================================================

class TestTemporalSynchronizerInit:
    """Tests for TemporalSynchronizer initialization (no Qt event loop)."""
    
    @pytest.fixture
    def qapp(self, qtbot):
        """Qt application fixture."""
        return qtbot
    
    def test_init_synchronizer(self, qapp):
        """Test initializing TemporalSynchronizer."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer(
            master_series_id='master',
            buffer_size=500,
        )
        
        assert sync.master_series_id == 'master'
        assert sync.buffer_size == 500
        assert sync.is_streaming is False
        assert sync.is_synchronized is False
        assert sync.target_fps == 30.0
    
    def test_add_series(self, qapp):
        """Test adding series to synchronizer."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master', buffer_size=100)
        
        sync.add_series('series_1', time_offset=0.0)
        sync.add_series('series_2', time_offset=0.5)
        
        assert 'series_1' in sync._buffers
        assert 'series_2' in sync._buffers
    
    def test_remove_series(self, qapp):
        """Test removing series from synchronizer."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master', buffer_size=100)
        
        sync.add_series('series_1')
        sync.add_series('series_2')
        
        sync.remove_series('series_1')
        
        assert 'series_1' not in sync._buffers
        assert 'series_2' in sync._buffers
    
    def test_remove_nonexistent_series(self, qapp):
        """Test removing non-existent series."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master', buffer_size=100)
        
        # Should not raise
        sync.remove_series('nonexistent')
    
    def test_frame_interval_calculation(self, qapp):
        """Test frame interval is calculated from FPS."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        
        assert sync.target_fps == 30.0
        assert abs(sync.frame_interval - 1.0 / 30.0) < 0.001
    
    def test_initial_statistics(self, qapp):
        """Test initial statistics."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        stats = sync.get_statistics()
        
        assert stats['is_streaming'] is False
        assert stats['is_synchronized'] is False
        assert stats['target_fps'] == 30.0
        assert stats['frames_emitted'] == 0
        assert stats['frames_dropped'] == 0


class TestTemporalSynchronizerStreaming:
    """Tests for TemporalSynchronizer streaming operations."""
    
    @pytest.fixture
    def qapp(self, qtbot):
        """Qt application fixture."""
        return qtbot
    
    def test_start_streaming(self, qapp):
        """Test starting streaming."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        
        sync.start_streaming(fps=60.0)
        
        assert sync.is_streaming is True
        assert sync.target_fps == 60.0
        
        sync.stop_streaming()
    
    def test_stop_streaming(self, qapp):
        """Test stopping streaming."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        
        sync.start_streaming()
        sync.stop_streaming()
        
        assert sync.is_streaming is False
    
    def test_add_frame_when_not_streaming(self, qapp):
        """Test that frames are not added when not streaming."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        sync.add_series('series_1')
        
        # Should not add frame when not streaming
        sync.add_frame('series_1', 1.0, {'value': 42})
        
        assert len(sync._buffers['series_1']) == 0
    
    def test_add_frame_when_streaming(self, qapp):
        """Test adding frame while streaming."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        sync.add_series('series_1')
        
        sync.start_streaming()
        sync.add_frame('series_1', 1.0, {'value': 42})
        sync.stop_streaming()
        
        # Buffer is cleared on stop, so we can't check directly
        # Just verify no exceptions were raised
    
    def test_add_frame_creates_series_automatically(self, qapp):
        """Test that adding frame creates series if not exists."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        
        sync.start_streaming()
        sync.add_frame('new_series', 1.0, {'value': 42})
        
        assert 'new_series' in sync._buffers
        assert len(sync._buffers['new_series']) == 1
        
        sync.stop_streaming()
    
    def test_buffer_overflow(self, qapp):
        """Test buffer management on overflow."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master', buffer_size=5)
        sync.add_series('series_1')
        
        sync.start_streaming()
        
        # Add more frames than buffer size
        for i in range(10):
            sync.add_frame('series_1', float(i), {'value': i})
        
        # Buffer should not exceed buffer_size
        assert len(sync._buffers['series_1']) <= 5
        
        sync.stop_streaming()


class TestTemporalSynchronizerFrameFinding:
    """Tests for frame finding logic."""
    
    @pytest.fixture
    def qapp(self, qtbot):
        """Qt application fixture."""
        return qtbot
    
    def test_find_closest_frame(self, qapp):
        """Test _find_closest_frame method."""
        from platform_base.streaming.temporal_sync import (
            StreamFrame,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        
        # Create test buffer
        buffer = [
            StreamFrame(timestamp=1.0, data={}, series_id='s', frame_number=0),
            StreamFrame(timestamp=2.0, data={}, series_id='s', frame_number=1),
            StreamFrame(timestamp=3.0, data={}, series_id='s', frame_number=2),
            StreamFrame(timestamp=4.0, data={}, series_id='s', frame_number=3),
        ]
        
        # Test finding closest
        closest = sync._find_closest_frame(buffer, 2.3)
        assert closest is not None
        assert closest.timestamp == 2.0
        
        closest = sync._find_closest_frame(buffer, 2.7)
        assert closest is not None
        assert closest.timestamp == 3.0
        
        closest = sync._find_closest_frame(buffer, 1.0)
        assert closest is not None
        assert closest.timestamp == 1.0
    
    def test_find_closest_frame_empty_buffer(self, qapp):
        """Test _find_closest_frame with empty buffer."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master')
        
        result = sync._find_closest_frame([], 1.0)
        assert result is None


class TestTemporalSynchronizerStatistics:
    """Tests for statistics methods."""
    
    @pytest.fixture
    def qapp(self, qtbot):
        """Qt application fixture."""
        return qtbot
    
    def test_get_statistics(self, qapp):
        """Test get_statistics method."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master', buffer_size=100)
        sync.add_series('series_1')
        
        stats = sync.get_statistics()
        
        assert 'is_streaming' in stats
        assert 'is_synchronized' in stats
        assert 'target_fps' in stats
        assert 'frames_emitted' in stats
        assert 'frames_dropped' in stats
        assert 'buffer_stats' in stats
    
    def test_statistics_with_data(self, qapp):
        """Test statistics after adding data."""
        from platform_base.streaming.temporal_sync import TemporalSynchronizer
        
        sync = TemporalSynchronizer('master', buffer_size=100)
        
        # Set streaming directly to avoid timer
        sync.is_streaming = True
        sync.add_frame('series_1', 1.0, {'value': 1})
        sync.add_frame('series_1', 2.0, {'value': 2})
        
        stats = sync.get_statistics()
        
        assert 'series_1' in stats['buffer_stats']
        assert stats['buffer_stats']['series_1']['buffer_size'] == 2
        
        sync.is_streaming = False


# =============================================================================
# StreamingPlotManager Tests
# =============================================================================

class TestStreamingPlotManager:
    """Tests for StreamingPlotManager class."""
    
    @pytest.fixture
    def qapp(self, qtbot):
        """Qt application fixture."""
        return qtbot
    
    def test_create_plot_manager(self, qapp):
        """Test creating StreamingPlotManager."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        assert manager.synchronizer is sync
        assert len(manager.plot_widgets) == 0
    
    def test_add_plot(self, qapp):
        """Test adding plot widget."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        mock_widget = Mock()
        manager.add_plot('plot_1', mock_widget)
        
        assert 'plot_1' in manager.plot_widgets
        assert manager.plot_widgets['plot_1'] is mock_widget
    
    def test_remove_plot(self, qapp):
        """Test removing plot widget."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        mock_widget = Mock()
        manager.add_plot('plot_1', mock_widget)
        manager.remove_plot('plot_1')
        
        assert 'plot_1' not in manager.plot_widgets
    
    def test_remove_nonexistent_plot(self, qapp):
        """Test removing non-existent plot."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        # Should not raise
        manager.remove_plot('nonexistent')
    
    def test_on_frame_ready_calls_update(self, qapp):
        """Test _on_frame_ready updates plots."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        mock_widget = Mock()
        mock_widget.update_streaming_data = Mock()
        manager.add_plot('plot_1', mock_widget)
        
        # Simulate frame ready
        manager._on_frame_ready('series_1', {'value': 42})
        
        mock_widget.update_streaming_data.assert_called_once_with('series_1', {'value': 42})
    
    def test_on_frame_ready_handles_exception(self, qapp):
        """Test _on_frame_ready handles exceptions gracefully."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        mock_widget = Mock()
        mock_widget.update_streaming_data = Mock(side_effect=Exception("Test error"))
        manager.add_plot('plot_1', mock_widget)
        
        # Should not raise
        manager._on_frame_ready('series_1', {'value': 42})
    
    def test_on_sync_status_changed(self, qapp):
        """Test _on_sync_status_changed updates plots."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        manager = StreamingPlotManager(sync)
        
        mock_widget = Mock()
        mock_widget.set_sync_status = Mock()
        manager.add_plot('plot_1', mock_widget)
        
        manager._on_sync_status_changed(True)
        
        mock_widget.set_sync_status.assert_called_once_with(True)


# =============================================================================
# Integration Tests
# =============================================================================

class TestTemporalSyncIntegration:
    """Integration tests for temporal synchronization."""
    
    @pytest.fixture
    def qapp(self, qtbot):
        """Qt application fixture."""
        return qtbot
    
    def test_full_streaming_workflow(self, qapp):
        """Test complete streaming workflow."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )

        # Setup
        sync = TemporalSynchronizer('master', buffer_size=100)
        manager = StreamingPlotManager(sync)
        
        mock_widget = Mock()
        mock_widget.update_streaming_data = Mock()
        mock_widget.set_sync_status = Mock()
        manager.add_plot('plot_1', mock_widget)
        
        # Add series
        sync.add_series('master')
        sync.add_series('slave1')
        
        # Start streaming properly
        sync.start_streaming(fps=30.0)
        
        # Add some frames
        for i in range(10):
            sync.add_frame('master', float(i), {'value': i})
            sync.add_frame('slave1', float(i) + 0.01, {'value': i * 2})
        
        # Get statistics
        stats = sync.get_statistics()
        assert stats['is_streaming'] is True
        
        # Stop streaming properly
        sync.stop_streaming()
        
        assert sync.is_streaming is False
    
    def test_multiple_plot_managers(self, qapp):
        """Test multiple managers sharing synchronizer."""
        from platform_base.streaming.temporal_sync import (
            StreamingPlotManager,
            TemporalSynchronizer,
        )
        
        sync = TemporalSynchronizer('master')
        
        manager1 = StreamingPlotManager(sync)
        manager2 = StreamingPlotManager(sync)
        
        mock_widget1 = Mock()
        mock_widget2 = Mock()
        
        manager1.add_plot('plot_1', mock_widget1)
        manager2.add_plot('plot_2', mock_widget2)
        
        # Both managers should be connected to same synchronizer
        assert manager1.synchronizer is manager2.synchronizer
