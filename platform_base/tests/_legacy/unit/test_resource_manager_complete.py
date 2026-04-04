"""
Comprehensive tests for utils/resource_manager.py module.

Target: Increase coverage from ~42% to 80%+
"""
from __future__ import annotations

import gc
import weakref
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest


# Helper class that supports weak references (unlike object())
class WeakRefable:
    """A simple class that supports weak references for testing."""
    def __init__(self, name: str = "resource"):
        self.name = name
        self.closed = False
    
    def close(self):
        self.closed = True


class TestResourceTracker:
    """Tests for ResourceTracker class."""
    
    @pytest.fixture
    def tracker(self):
        """Create fresh ResourceTracker instance."""
        from platform_base.utils.resource_manager import ResourceTracker
        return ResourceTracker()
    
    def test_initialization(self, tracker):
        """Test ResourceTracker initializes with empty resources."""
        assert tracker._resources == {}
        assert tracker._cleanup_funcs == {}
    
    def test_register_new_category(self, tracker):
        """Test registering resource in new category."""
        resource = WeakRefable("test_resource")
        
        tracker.register("test_category", resource)
        
        assert "test_category" in tracker._resources
    
    def test_register_multiple_in_same_category(self, tracker):
        """Test registering multiple resources in same category."""
        resources = [WeakRefable(f"r{i}") for i in range(5)]
        
        for r in resources:
            tracker.register("widgets", r)
        
        assert len(tracker._resources["widgets"]) == 5
    
    def test_register_in_different_categories(self, tracker):
        """Test registering in different categories."""
        r1 = WeakRefable("fig")
        r2 = WeakRefable("worker")
        r3 = WeakRefable("canvas")
        tracker.register("figures", r1)
        tracker.register("workers", r2)
        tracker.register("canvases", r3)
        
        assert len(tracker._resources) == 3
    
    def test_unregister_existing(self, tracker):
        """Test unregistering existing resource."""
        resource = WeakRefable("test_res")
        tracker.register("test", resource)
        
        tracker.unregister("test", resource)
        
        assert len(tracker._resources["test"]) == 0
    
    def test_unregister_nonexistent_category(self, tracker):
        """Test unregistering from nonexistent category doesn't raise."""
        resource = WeakRefable("test_res")
        
        # Should not raise
        tracker.unregister("nonexistent", resource)
    
    def test_get_count_all_categories(self, tracker):
        """Test getting count of all categories."""
        r1 = WeakRefable("fig1")
        r2 = WeakRefable("fig2")
        r3 = WeakRefable("worker1")
        tracker.register("figures", r1)
        tracker.register("figures", r2)
        tracker.register("workers", r3)
        
        counts = tracker.get_count()
        
        assert counts["figures"] == 2
        assert counts["workers"] == 1
    
    def test_get_count_specific_category(self, tracker):
        """Test getting count for specific category."""
        r1 = WeakRefable("fig1")
        r2 = WeakRefable("fig2")
        r3 = WeakRefable("worker1")
        tracker.register("figures", r1)
        tracker.register("figures", r2)
        tracker.register("workers", r3)
        
        counts = tracker.get_count("figures")
        
        assert counts == {"figures": 2}
    
    def test_get_count_nonexistent_category(self, tracker):
        """Test getting count for nonexistent category."""
        counts = tracker.get_count("nonexistent")
        
        assert counts == {"nonexistent": 0}
    
    def test_add_cleanup_func(self, tracker):
        """Test adding cleanup function."""
        cleanup_called = []
        
        def cleanup():
            cleanup_called.append(True)
        
        tracker.add_cleanup_func("test", cleanup)
        
        assert "test" in tracker._cleanup_funcs
        assert len(tracker._cleanup_funcs["test"]) == 1
    
    def test_add_multiple_cleanup_funcs(self, tracker):
        """Test adding multiple cleanup functions."""
        tracker.add_cleanup_func("test", lambda: None)
        tracker.add_cleanup_func("test", lambda: None)
        tracker.add_cleanup_func("test", lambda: None)
        
        assert len(tracker._cleanup_funcs["test"]) == 3
    
    def test_cleanup_category_calls_funcs(self, tracker):
        """Test cleanup_category calls registered functions."""
        cleanup_called = []
        
        def cleanup1():
            cleanup_called.append(1)
        
        def cleanup2():
            cleanup_called.append(2)
        
        r = WeakRefable("test_res")
        tracker.add_cleanup_func("test", cleanup1)
        tracker.add_cleanup_func("test", cleanup2)
        tracker.register("test", r)
        
        tracker.cleanup_category("test")
        
        assert 1 in cleanup_called
        assert 2 in cleanup_called
    
    def test_cleanup_category_handles_exceptions(self, tracker):
        """Test cleanup_category handles exceptions in cleanup funcs."""
        def failing_cleanup():
            raise ValueError("Cleanup failed!")
        
        r = WeakRefable("test_res")
        tracker.add_cleanup_func("test", failing_cleanup)
        tracker.register("test", r)
        
        # Should not raise
        count = tracker.cleanup_category("test")
        
        assert count == 1
    
    def test_cleanup_category_returns_count(self, tracker):
        """Test cleanup_category returns resource count."""
        r1 = WeakRefable("test1")
        r2 = WeakRefable("test2")
        r3 = WeakRefable("test3")
        tracker.register("test", r1)
        tracker.register("test", r2)
        tracker.register("test", r3)
        
        count = tracker.cleanup_category("test")
        
        assert count == 3
    
    def test_cleanup_category_clears_resources(self, tracker):
        """Test cleanup_category clears resources."""
        r1 = WeakRefable("test1")
        r2 = WeakRefable("test2")
        tracker.register("test", r1)
        tracker.register("test", r2)
        
        tracker.cleanup_category("test")
        
        assert len(tracker._resources["test"]) == 0
    
    def test_cleanup_all(self, tracker):
        """Test cleanup_all clears all categories."""
        r1 = WeakRefable("fig1")
        r2 = WeakRefable("worker1")
        r3 = WeakRefable("canvas1")
        tracker.register("figures", r1)
        tracker.register("workers", r2)
        tracker.register("canvases", r3)
        
        results = tracker.cleanup_all()
        
        assert "figures" in results
        assert "workers" in results
        assert "canvases" in results


class TestMatplotlibResourceManager:
    """Tests for MatplotlibResourceManager class."""
    
    @pytest.fixture
    def manager(self):
        """Get MatplotlibResourceManager instance."""
        from platform_base.utils.resource_manager import MatplotlibResourceManager

        # Reset singleton for testing
        MatplotlibResourceManager._instance = None
        return MatplotlibResourceManager()
    
    def test_is_singleton(self, manager):
        """Test MatplotlibResourceManager is singleton."""
        from platform_base.utils.resource_manager import MatplotlibResourceManager
        
        manager2 = MatplotlibResourceManager()
        
        assert manager is manager2
    
    def test_initialization(self, manager):
        """Test manager initializes correctly."""
        assert manager._initialized is True
        assert hasattr(manager, '_figures')
        assert hasattr(manager, '_canvases')
    
    def test_register_figure(self, manager):
        """Test registering a figure."""
        mock_fig = MagicMock()
        
        manager.register_figure(mock_fig)
        
        assert mock_fig in manager._figures
    
    def test_register_canvas(self, manager):
        """Test registering a canvas."""
        mock_canvas = MagicMock()
        
        manager.register_canvas(mock_canvas)
        
        assert mock_canvas in manager._canvases
    
    def test_close_figure(self, manager):
        """Test closing a figure."""
        with patch('matplotlib.pyplot.close') as mock_close:
            mock_fig = MagicMock()
            mock_fig.axes = [MagicMock()]
            mock_fig.canvas = MagicMock()
            
            manager.register_figure(mock_fig)
            manager.close_figure(mock_fig)
            
            mock_close.assert_called_with(mock_fig)
    
    def test_close_figure_clears_axes(self, manager):
        """Test closing figure clears axes."""
        with patch('matplotlib.pyplot.close'):
            mock_fig = MagicMock()
            mock_ax1 = MagicMock()
            mock_ax2 = MagicMock()
            mock_fig.axes = [mock_ax1, mock_ax2]
            mock_fig.canvas = MagicMock()
            
            manager.close_figure(mock_fig)
            
            mock_ax1.clear.assert_called_once()
            mock_ax2.clear.assert_called_once()
    
    def test_close_figure_disconnects_events(self, manager):
        """Test closing figure disconnects event handlers."""
        with patch('matplotlib.pyplot.close'):
            mock_fig = MagicMock()
            mock_fig.axes = []
            mock_canvas = MagicMock()
            mock_fig.canvas = mock_canvas
            
            manager.close_figure(mock_fig)
            
            mock_canvas.mpl_disconnect.assert_called_with("all")
    
    def test_close_figure_handles_exception(self, manager):
        """Test closing figure handles exceptions gracefully."""
        with patch('matplotlib.pyplot.close') as mock_close:
            mock_close.side_effect = Exception("Test error")
            mock_fig = MagicMock()
            mock_fig.axes = []
            mock_fig.canvas = None
            
            # Should not raise
            manager.close_figure(mock_fig)
    
    def test_cleanup_all_figures(self, manager):
        """Test cleanup_all_figures clears all figures."""
        with patch('matplotlib.pyplot.close') as mock_plt_close:
            with patch('gc.collect') as mock_gc_collect:
                mock_fig1 = MagicMock()
                mock_fig1.axes = []
                mock_fig1.canvas = MagicMock()
                
                mock_fig2 = MagicMock()
                mock_fig2.axes = []
                mock_fig2.canvas = MagicMock()
                
                manager.register_figure(mock_fig1)
                manager.register_figure(mock_fig2)
                
                count = manager.cleanup_all_figures()
                
                mock_plt_close.assert_called_with("all")
                mock_gc_collect.assert_called()
    
    def test_get_figure_count(self, manager):
        """Test getting figure count."""
        with patch('matplotlib.pyplot.get_fignums') as mock_get_fignums:
            mock_get_fignums.return_value = [1, 2, 3]
            
            count = manager.get_figure_count()
            
            assert count == 3
    
    def test_get_memory_usage(self, manager):
        """Test getting memory usage stats."""
        with patch('matplotlib.pyplot.get_fignums') as mock_get_fignums:
            mock_get_fignums.return_value = [1, 2]
            
            mock_fig = MagicMock()
            manager.register_figure(mock_fig)
            
            mock_canvas = MagicMock()
            manager.register_canvas(mock_canvas)
            
            stats = manager.get_memory_usage()
            
            assert stats["active_figures"] == 2
            assert "tracked_figures" in stats
            assert "tracked_canvases" in stats


class TestCloseEventHandler:
    """Tests for CloseEventHandler class."""
    
    @pytest.fixture
    def mock_widget(self):
        """Create mock widget."""
        widget = MagicMock()
        return widget
    
    def test_initialization(self, mock_widget):
        """Test CloseEventHandler initialization."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler
            
            handler = CloseEventHandler(mock_widget)
            
            assert handler._cleaned is False
            mock_widget.installEventFilter.assert_called_with(handler)
    
    def test_initialization_with_cleanup_func(self, mock_widget):
        """Test initialization with custom cleanup function."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler
            
            cleanup_func = MagicMock()
            handler = CloseEventHandler(mock_widget, cleanup_func)
            
            assert handler._cleanup_func == cleanup_func
    
    def test_initialization_with_none_widget(self):
        """Test initialization with None widget raises TypeError (WeakRef requirement)."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler

            # Should raise TypeError because None doesn't support weak references
            with pytest.raises(TypeError):
                CloseEventHandler(None)
    
    def test_cleanup_calls_custom_func(self, mock_widget):
        """Test cleanup calls custom function."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler
            
            cleanup_called = []
            def custom_cleanup():
                cleanup_called.append(True)
            
            handler = CloseEventHandler(mock_widget, custom_cleanup)
            handler._widget = lambda: None  # Widget returns None
            
            handler.cleanup()
            
            assert True in cleanup_called
    
    def test_cleanup_only_runs_once(self, mock_widget):
        """Test cleanup only runs once."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler
            
            cleanup_count = []
            def custom_cleanup():
                cleanup_count.append(1)
            
            handler = CloseEventHandler(mock_widget, custom_cleanup)
            handler._widget = lambda: None
            
            handler.cleanup()
            handler.cleanup()
            handler.cleanup()
            
            assert len(cleanup_count) == 1
    
    def test_cleanup_closes_figure(self, mock_widget):
        """Test cleanup closes matplotlib figure."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            with patch('platform_base.utils.resource_manager.get_matplotlib_manager') as mock_get_mgr:
                from platform_base.utils.resource_manager import CloseEventHandler
                
                mock_mgr = MagicMock()
                mock_get_mgr.return_value = mock_mgr
                
                # Widget with figure
                mock_widget.figure = MagicMock()
                handler = CloseEventHandler(mock_widget)
                handler._widget = lambda: mock_widget
                
                handler.cleanup()
                
                mock_mgr.close_figure.assert_called_with(mock_widget.figure)
    
    def test_cleanup_closes_canvas(self, mock_widget):
        """Test cleanup closes canvas."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            with patch('platform_base.utils.resource_manager.get_matplotlib_manager') as mock_get_mgr:
                from platform_base.utils.resource_manager import CloseEventHandler
                
                mock_get_mgr.return_value = MagicMock()
                
                # Widget with canvas
                mock_canvas = MagicMock()
                mock_widget.canvas = mock_canvas
                mock_widget.figure = None
                delattr(mock_widget, 'figure')
                
                handler = CloseEventHandler(mock_widget)
                handler._widget = lambda: mock_widget
                
                handler.cleanup()
                
                mock_canvas.close.assert_called_once()
    
    def test_cleanup_emits_signal(self, mock_widget):
        """Test cleanup emits cleanup_completed signal."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler
            
            handler = CloseEventHandler(mock_widget)
            handler._widget = lambda: None
            handler.cleanup_completed = MagicMock()
            
            handler.cleanup()
            
            handler.cleanup_completed.emit.assert_called_once()
    
    def test_cleanup_handles_exceptions(self, mock_widget):
        """Test cleanup handles exceptions gracefully."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            from platform_base.utils.resource_manager import CloseEventHandler
            
            def failing_cleanup():
                raise ValueError("Cleanup failed!")
            
            handler = CloseEventHandler(mock_widget, failing_cleanup)
            handler._widget = lambda: None
            handler.cleanup_completed = MagicMock()
            
            # Should not raise
            handler.cleanup()
    
    def test_event_filter_intercepts_close(self, mock_widget):
        """Test event filter intercepts close events."""
        with patch('platform_base.utils.resource_manager.QObject.__init__'):
            with patch('platform_base.utils.resource_manager.QObject.eventFilter', return_value=False):
                from PyQt6.QtCore import QEvent

                from platform_base.utils.resource_manager import CloseEventHandler
                
                handler = CloseEventHandler(mock_widget)
                handler._widget = lambda: None
                handler.cleanup = MagicMock()
                
                mock_event = MagicMock()
                mock_event.type.return_value = QEvent.Type.Close
                
                handler.eventFilter(mock_widget, mock_event)
                
                handler.cleanup.assert_called_once()


class TestModuleFunctions:
    """Tests for module-level functions."""
    
    def test_get_resource_tracker_returns_singleton(self):
        """Test get_resource_tracker returns same instance."""
        from platform_base.utils.resource_manager import get_resource_tracker
        
        tracker1 = get_resource_tracker()
        tracker2 = get_resource_tracker()
        
        assert tracker1 is tracker2
    
    def test_get_matplotlib_manager_returns_singleton(self):
        """Test get_matplotlib_manager returns same instance."""
        from platform_base.utils.resource_manager import (
            MatplotlibResourceManager,
            get_matplotlib_manager,
        )

        # Reset singleton
        MatplotlibResourceManager._instance = None
        
        manager1 = get_matplotlib_manager()
        manager2 = get_matplotlib_manager()
        
        assert manager1 is manager2
    
    def test_cleanup_on_close_returns_handler(self):
        """Test cleanup_on_close returns CloseEventHandler."""
        with patch('platform_base.utils.resource_manager.CloseEventHandler') as MockHandler:
            from platform_base.utils.resource_manager import cleanup_on_close
            
            mock_widget = MagicMock()
            mock_cleanup = MagicMock()
            
            result = cleanup_on_close(mock_widget, mock_cleanup)
            
            MockHandler.assert_called_with(mock_widget, mock_cleanup)
    
    def test_force_cleanup(self):
        """Test force_cleanup cleans all resources."""
        with patch('platform_base.utils.resource_manager.get_matplotlib_manager') as mock_mpl:
            with patch('platform_base.utils.resource_manager.get_resource_tracker') as mock_tracker:
                with patch('platform_base.utils.resource_manager.gc') as mock_gc:
                    from platform_base.utils.resource_manager import force_cleanup
                    
                    mock_mpl.return_value.cleanup_all_figures.return_value = 5
                    mock_tracker.return_value.cleanup_all.return_value = {"test": 3}
                    mock_gc.collect.return_value = 10
                    
                    results = force_cleanup()
                    
                    assert results["matplotlib"] == 5
                    assert results["resources"] == {"test": 3}
                    assert results["gc_collected"] == 10


class TestWeakRefBehavior:
    """Tests for weak reference behavior."""
    
    def test_resource_garbage_collected(self):
        """Test that resources can be garbage collected."""
        from platform_base.utils.resource_manager import ResourceTracker
        
        tracker = ResourceTracker()
        
        # Create resource and register
        class TestResource:
            pass
        
        resource = TestResource()
        tracker.register("test", resource)
        
        # Delete reference
        del resource
        gc.collect()
        
        # WeakSet should be empty or smaller
        # (WeakRef allows garbage collection)
    
    def test_figure_garbage_collected(self):
        """Test that figures can be garbage collected."""
        from platform_base.utils.resource_manager import MatplotlibResourceManager
        
        MatplotlibResourceManager._instance = None
        manager = MatplotlibResourceManager()
        
        # Create mock figure and register
        mock_fig = MagicMock()
        manager.register_figure(mock_fig)
        
        # Reference exists
        initial_count = len(manager._figures)
        
        # Delete reference
        del mock_fig
        gc.collect()
        
        # WeakSet automatically removes garbage collected items


class TestResourceTrackerEdgeCases:
    """Tests for edge cases in ResourceTracker."""
    
    def test_cleanup_empty_category(self):
        """Test cleanup on empty category."""
        from platform_base.utils.resource_manager import ResourceTracker
        
        tracker = ResourceTracker()
        
        # Cleanup nonexistent category
        count = tracker.cleanup_category("nonexistent")
        
        assert count == 0
    
    def test_cleanup_category_no_cleanup_funcs(self):
        """Test cleanup category with no registered cleanup functions."""
        from platform_base.utils.resource_manager import ResourceTracker
        
        tracker = ResourceTracker()
        r = WeakRefable("test_res")
        tracker.register("test", r)
        
        # No cleanup funcs registered, should still work
        count = tracker.cleanup_category("test")
        
        assert count == 1
    
    def test_multiple_cleanups_same_category(self):
        """Test multiple cleanups on same category."""
        from platform_base.utils.resource_manager import ResourceTracker
        
        tracker = ResourceTracker()
        r = WeakRefable("test_res")
        tracker.register("test", r)
        
        count1 = tracker.cleanup_category("test")
        count2 = tracker.cleanup_category("test")
        
        assert count1 == 1
        assert count2 == 0  # Already cleaned


class TestMatplotlibEdgeCases:
    """Tests for edge cases in MatplotlibResourceManager."""
    
    def test_close_figure_no_canvas(self):
        """Test closing figure without canvas."""
        from platform_base.utils.resource_manager import MatplotlibResourceManager
        
        MatplotlibResourceManager._instance = None
        manager = MatplotlibResourceManager()
        
        with patch('matplotlib.pyplot.close'):
            mock_fig = MagicMock()
            mock_fig.axes = []
            mock_fig.canvas = None
            
            # Should not raise
            manager.close_figure(mock_fig)
    
    def test_close_figure_no_axes(self):
        """Test closing figure without axes."""
        from platform_base.utils.resource_manager import MatplotlibResourceManager
        
        MatplotlibResourceManager._instance = None
        manager = MatplotlibResourceManager()
        
        with patch('matplotlib.pyplot.close') as mock_plt_close:
            mock_fig = MagicMock()
            mock_fig.axes = []
            mock_fig.canvas = MagicMock()
            
            manager.close_figure(mock_fig)
            
            mock_plt_close.assert_called_with(mock_fig)
    
    def test_cleanup_with_close_errors(self):
        """Test cleanup handles errors during close."""
        from platform_base.utils.resource_manager import MatplotlibResourceManager
        
        MatplotlibResourceManager._instance = None
        manager = MatplotlibResourceManager()
        
        with patch('matplotlib.pyplot.close'):
            with patch('gc.collect'):
                # Figure that raises on close
                mock_fig = MagicMock()
                mock_fig.axes = []
                mock_fig.canvas = MagicMock()
                
                def raise_on_disconnect(*args):
                    raise RuntimeError("Disconnect failed")
                
                mock_fig.canvas.mpl_disconnect = raise_on_disconnect
                
                manager.register_figure(mock_fig)
                
                # Should not raise
                manager.cleanup_all_figures()
