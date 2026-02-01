"""
Comprehensive tests for ui/app.py

Target: 100% coverage for the PlatformApplication class.
"""

from __future__ import annotations

import signal
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Skip all tests if PyQt6 is not available or no display
pytestmark = pytest.mark.skipif(
    not pytest.importorskip("PyQt6", reason="PyQt6 required").QtWidgets,
    reason="PyQt6.QtWidgets not available"
)


class TestPlatformApplication:
    """Tests for the PlatformApplication class."""
    
    @pytest.fixture
    def mock_qapp(self):
        """Mock QApplication to avoid display requirements."""
        with patch("platform_base.ui.app.QApplication.__init__", return_value=None):
            with patch("platform_base.ui.app.QApplication.setApplicationName"):
                with patch("platform_base.ui.app.QApplication.setApplicationVersion"):
                    with patch("platform_base.ui.app.QApplication.setOrganizationName"):
                        with patch("platform_base.ui.app.QApplication.setOrganizationDomain"):
                            with patch("platform_base.ui.app.QApplication.setFont"):
                                with patch("platform_base.ui.app.QApplication.processEvents"):
                                    yield

    def test_platform_application_initialization(self, mock_qapp):
        """Test that PlatformApplication initializes correctly."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            
            # Check attributes initialized
            assert app._dataset_store is None
            assert app._session_state is None
            assert app._main_window is None
            assert app._splash is None
    
    def test_setup_signal_handlers(self, mock_qapp):
        """Test signal handlers are set up correctly."""
        from platform_base.ui.app import PlatformApplication
        
        with patch("signal.signal") as mock_signal:
            with patch("platform_base.ui.app.QTimer") as mock_timer:
                mock_timer_instance = MagicMock()
                mock_timer.return_value = mock_timer_instance
                
                app = PlatformApplication(["test"])
                
                # Verify signal.signal was called for SIGINT and SIGTERM
                calls = mock_signal.call_args_list
                signal_nums = [call[0][0] for call in calls]
                assert signal.SIGINT in signal_nums
                assert signal.SIGTERM in signal_nums
                
                # Verify timer started
                mock_timer_instance.start.assert_called_with(500)
    
    def test_signal_handler_emits_shutdown(self, mock_qapp):
        """Test that signal handler emits shutdown signal."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            
            # Mock the signal emission
            app.shutdown_requested = MagicMock()
            
            # Call signal handler
            app._signal_handler(signal.SIGINT, None)
            
            # Verify shutdown_requested was emitted
            app.shutdown_requested.emit.assert_called_once()
    
    def test_initialize_components_success(self, mock_qapp):
        """Test successful component initialization."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "_show_splash"):
                with patch.object(PlatformApplication, "_update_splash"):
                    with patch("platform_base.ui.app.DatasetStore") as mock_store:
                        with patch("platform_base.ui.app.SessionState") as mock_session:
                            app = PlatformApplication(["test"])
                            app.shutdown_requested = MagicMock()
                            
                            result = app.initialize_components()
                            
                            assert result is True
                            assert app._dataset_store is not None
                            assert app._session_state is not None
    
    def test_initialize_components_with_cache_config(self, mock_qapp):
        """Test component initialization with cache configuration."""
        from platform_base.ui.app import PlatformApplication
        
        cache_config = {"max_size": 1000, "ttl": 3600}
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "_show_splash"):
                with patch.object(PlatformApplication, "_update_splash"):
                    with patch("platform_base.ui.app.DatasetStore") as mock_store:
                        with patch("platform_base.ui.app.SessionState"):
                            app = PlatformApplication(["test"])
                            app.shutdown_requested = MagicMock()
                            
                            result = app.initialize_components(cache_config)
                            
                            # Verify DatasetStore was called with cache_config
                            mock_store.assert_called_once_with(cache_config)
    
    def test_initialize_components_failure(self, mock_qapp):
        """Test component initialization failure handling."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "_show_splash"):
                with patch.object(PlatformApplication, "_show_error") as mock_error:
                    with patch("platform_base.ui.app.DatasetStore", side_effect=Exception("Init failed")):
                        app = PlatformApplication(["test"])
                        
                        result = app.initialize_components()
                        
                        assert result is False
                        mock_error.assert_called_once()
    
    def test_show_splash(self, mock_qapp):
        """Test splash screen display."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch("platform_base.ui.app.QPixmap") as mock_pixmap:
                with patch("platform_base.ui.app.QSplashScreen") as mock_splash:
                    mock_pixmap_instance = MagicMock()
                    mock_pixmap.return_value = mock_pixmap_instance
                    
                    mock_splash_instance = MagicMock()
                    mock_splash.return_value = mock_splash_instance
                    
                    app = PlatformApplication(["test"])
                    app._show_splash()
                    
                    # Verify splash was created and shown
                    mock_pixmap.assert_called_once_with(400, 200)
                    mock_splash.assert_called_once()
                    mock_splash_instance.show.assert_called_once()
    
    def test_update_splash(self, mock_qapp):
        """Test splash screen message update."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            
            # Create mock splash
            mock_splash = MagicMock()
            app._splash = mock_splash
            
            app._update_splash("Loading...")
            
            mock_splash.showMessage.assert_called_once()
    
    def test_update_splash_no_splash(self, mock_qapp):
        """Test update splash when no splash exists."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            app._splash = None
            
            # Should not raise
            app._update_splash("Test message")
    
    def test_hide_splash(self, mock_qapp):
        """Test splash screen hiding."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            
            mock_splash = MagicMock()
            app._splash = mock_splash
            
            app._hide_splash()
            
            mock_splash.close.assert_called_once()
            assert app._splash is None
    
    def test_hide_splash_no_splash(self, mock_qapp):
        """Test hide splash when no splash exists."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            app._splash = None
            
            # Should not raise
            app._hide_splash()
    
    def test_create_main_window_no_session_state(self, mock_qapp):
        """Test main window creation fails without session state."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "_show_error") as mock_error:
                app = PlatformApplication(["test"])
                app._session_state = None
                
                result = app.create_main_window()
                
                assert result is False
                mock_error.assert_called_once()
    
    def test_create_main_window_success(self, mock_qapp):
        """Test successful main window creation."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "_update_splash"):
                with patch.object(PlatformApplication, "_hide_splash"):
                    with patch.object(PlatformApplication, "_get_app_icon"):
                        with patch("platform_base.ui.app.MainWindow") as mock_window:
                            mock_window_instance = MagicMock()
                            mock_window.return_value = mock_window_instance
                            
                            app = PlatformApplication(["test"])
                            app._session_state = MagicMock()
                            
                            result = app.create_main_window()
                            
                            assert result is True
                            mock_window_instance.show.assert_called_once()
    
    def test_create_main_window_failure(self, mock_qapp):
        """Test main window creation failure."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "_update_splash"):
                with patch.object(PlatformApplication, "_show_error") as mock_error:
                    with patch("platform_base.ui.app.MainWindow", side_effect=Exception("Window failed")):
                        app = PlatformApplication(["test"])
                        app._session_state = MagicMock()
                        
                        result = app.create_main_window()
                        
                        assert result is False
                        mock_error.assert_called_once()
    
    def test_get_app_icon_custom_exists(self, mock_qapp):
        """Test app icon retrieval when custom icon exists."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch("platform_base.ui.app.Path") as mock_path_cls:
                with patch("platform_base.ui.app.QIcon") as mock_icon:
                    mock_icon_path = MagicMock()
                    mock_icon_path.exists.return_value = True
                    mock_icon_path.__str__ = MagicMock(return_value="/path/to/icon.png")
                    
                    mock_path_cls.return_value.__truediv__ = MagicMock(return_value=mock_icon_path)
                    
                    app = PlatformApplication(["test"])
                    
                    # Need to reset the mock to test the method
                    with patch.object(Path, "exists", return_value=True):
                        icon = app._get_app_icon()
    
    def test_get_app_icon_default(self, mock_qapp):
        """Test app icon retrieval using default icon."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            
            # Mock style
            mock_style = MagicMock()
            app.style = MagicMock(return_value=mock_style)
            
            with patch.object(Path, "exists", return_value=False):
                icon = app._get_app_icon()
                
                mock_style.standardIcon.assert_called()
    
    def test_show_error(self, mock_qapp):
        """Test error dialog display."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch("platform_base.ui.app.QMessageBox") as mock_msgbox:
                mock_msgbox_instance = MagicMock()
                mock_msgbox.return_value = mock_msgbox_instance
                
                app = PlatformApplication(["test"])
                app._show_error("Test Title", "Test Message")
                
                mock_msgbox_instance.setWindowTitle.assert_called_with("Test Title")
                mock_msgbox_instance.setText.assert_called_with("Test Message")
                mock_msgbox_instance.exec.assert_called_once()
    
    def test_graceful_shutdown(self, mock_qapp):
        """Test graceful shutdown process."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            app.quit = MagicMock()
            
            mock_window = MagicMock()
            mock_store = MagicMock()
            app._main_window = mock_window
            app._dataset_store = mock_store
            
            app._graceful_shutdown()
            
            mock_window.save_session_on_exit.assert_called_once()
            mock_store.clear_cache.assert_called_once()
            app.quit.assert_called_once()
    
    def test_graceful_shutdown_exception(self, mock_qapp):
        """Test graceful shutdown handles exceptions."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            app.quit = MagicMock()
            
            mock_window = MagicMock()
            mock_window.save_session_on_exit.side_effect = Exception("Save failed")
            app._main_window = mock_window
            
            # Should not raise
            app._graceful_shutdown()
            
            # quit should still be called
            app.quit.assert_called_once()
    
    def test_graceful_shutdown_no_components(self, mock_qapp):
        """Test graceful shutdown with no components initialized."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            app = PlatformApplication(["test"])
            app.quit = MagicMock()
            app._main_window = None
            app._dataset_store = None
            
            # Should not raise
            app._graceful_shutdown()
            
            app.quit.assert_called_once()
    
    def test_run_success(self, mock_qapp):
        """Test successful application run."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "initialize_components", return_value=True):
                with patch.object(PlatformApplication, "create_main_window", return_value=True):
                    with patch.object(PlatformApplication, "exec", return_value=0):
                        app = PlatformApplication(["test"])
                        
                        result = app.run()
                        
                        assert result == 0
    
    def test_run_init_failure(self, mock_qapp):
        """Test run with initialization failure."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "initialize_components", return_value=False):
                app = PlatformApplication(["test"])
                
                result = app.run()
                
                assert result == 1
    
    def test_run_window_failure(self, mock_qapp):
        """Test run with main window creation failure."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "initialize_components", return_value=True):
                with patch.object(PlatformApplication, "create_main_window", return_value=False):
                    app = PlatformApplication(["test"])
                    
                    result = app.run()
                    
                    assert result == 1
    
    def test_run_exception(self, mock_qapp):
        """Test run with unhandled exception."""
        from platform_base.ui.app import PlatformApplication
        
        with patch.object(PlatformApplication, "_setup_signal_handlers"):
            with patch.object(PlatformApplication, "initialize_components", side_effect=Exception("Fatal")):
                with patch.object(PlatformApplication, "_show_error") as mock_error:
                    app = PlatformApplication(["test"])
                    
                    result = app.run()
                    
                    assert result == 1
                    mock_error.assert_called_once()


class TestCreateApplication:
    """Tests for create_application factory function."""
    
    def test_create_application_default_argv(self):
        """Test create_application with default argv."""
        with patch("platform_base.ui.app.PlatformApplication") as mock_app:
            with patch("platform_base.ui.app.Qt") as mock_qt:
                mock_app_instance = MagicMock()
                mock_app.return_value = mock_app_instance
                
                from platform_base.ui.app import create_application
                
                result = create_application()
                
                assert result is mock_app_instance
    
    def test_create_application_custom_argv(self):
        """Test create_application with custom argv."""
        with patch("platform_base.ui.app.PlatformApplication") as mock_app:
            with patch("platform_base.ui.app.Qt") as mock_qt:
                mock_app_instance = MagicMock()
                mock_app.return_value = mock_app_instance
                
                from platform_base.ui.app import create_application
                
                custom_argv = ["test_app", "--debug"]
                result = create_application(custom_argv)
                
                mock_app.assert_called_once_with(custom_argv)


class TestMain:
    """Tests for main entry point."""
    
    def test_main_success(self):
        """Test main function with successful run."""
        with patch("platform_base.ui.app.setup_logging"):
            with patch("platform_base.ui.app.create_application") as mock_create:
                mock_app = MagicMock()
                mock_app.run.return_value = 0
                mock_create.return_value = mock_app
                
                from platform_base.ui.app import main
                
                result = main(["test"])
                
                assert result == 0
                mock_app.run.assert_called_once()
    
    def test_main_failure(self):
        """Test main function with failed run."""
        with patch("platform_base.ui.app.setup_logging"):
            with patch("platform_base.ui.app.create_application") as mock_create:
                mock_app = MagicMock()
                mock_app.run.return_value = 1
                mock_create.return_value = mock_app
                
                from platform_base.ui.app import main
                
                result = main()
                
                assert result == 1


class TestRun:
    """Tests for run CLI entry point."""
    
    def test_run_exits_with_code(self):
        """Test run function exits with correct code."""
        with patch("platform_base.ui.app.main", return_value=0):
            with patch("sys.exit") as mock_exit:
                from platform_base.ui.app import run
                
                run()
                
                mock_exit.assert_called_once_with(0)
    
    def test_run_exits_with_error_code(self):
        """Test run function exits with error code."""
        with patch("platform_base.ui.app.main", return_value=1):
            with patch("sys.exit") as mock_exit:
                from platform_base.ui.app import run
                
                run()
                
                mock_exit.assert_called_once_with(1)
