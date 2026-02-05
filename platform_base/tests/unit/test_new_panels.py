"""
Unit tests for new UI panels
"""

import pytest
from PyQt6.QtWidgets import QApplication
from platform_base.ui.panels.detached_manager import DetachedManager
from platform_base.ui.panels.resource_monitor_panel import ResourceMonitorPanel
from platform_base.ui.panels.activity_log_panel import ActivityLogPanel
from platform_base.ui.panels.data_tables_panel import DataTablesPanel
import pandas as pd


@pytest.fixture
def qapp():
    """Fixture for QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp, qtbot):
    """Fixture for a mock main window"""
    from PyQt6.QtWidgets import QMainWindow
    window = QMainWindow()
    qtbot.addWidget(window)
    return window


class TestDetachedManager:
    """Tests for DetachedManager"""
    
    def test_init(self, main_window):
        """Test DetachedManager initialization"""
        manager = DetachedManager(main_window)
        assert manager.main_window == main_window
        assert manager.get_detached_count() == 0
    
    def test_register_dock(self, main_window, qtbot):
        """Test dock registration"""
        from PyQt6.QtWidgets import QDockWidget
        
        manager = DetachedManager(main_window)
        dock = QDockWidget("Test", main_window)
        qtbot.addWidget(dock)
        
        manager.register_dock(dock)
        assert manager.get_detached_count() == 0  # Not floating yet
    
    def test_detect_floating_dock(self, main_window, qtbot):
        """Test detection of floating docks"""
        from PyQt6.QtWidgets import QDockWidget
        
        manager = DetachedManager(main_window)
        dock = QDockWidget("Test", main_window)
        qtbot.addWidget(dock)
        
        manager.register_dock(dock)
        
        # Make dock floating
        dock.setFloating(True)
        
        # Manager should detect it
        assert manager.get_detached_count() == 1
        assert dock in manager.get_detached_docks()
    
    def test_redock_all(self, main_window, qtbot):
        """Test re-docking all floating panels"""
        from PyQt6.QtWidgets import QDockWidget
        from PyQt6.QtCore import Qt
        
        manager = DetachedManager(main_window)
        
        # Create and register multiple docks
        docks = []
        for i in range(3):
            dock = QDockWidget(f"Test {i}", main_window)
            qtbot.addWidget(dock)
            main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            manager.register_dock(dock)
            dock.setFloating(True)
            docks.append(dock)
        
        assert manager.get_detached_count() == 3
        
        # Re-dock all
        manager.redock_all()
        
        assert manager.get_detached_count() == 0


class TestResourceMonitorPanel:
    """Tests for ResourceMonitorPanel"""
    
    def test_init(self, qapp, qtbot):
        """Test ResourceMonitorPanel initialization"""
        panel = ResourceMonitorPanel()
        qtbot.addWidget(panel)
        
        assert panel.cpu_label is not None
        assert panel.mem_label is not None
        assert panel.tasks_table is not None
    
    def test_add_task(self, qapp, qtbot):
        """Test adding a task to monitor"""
        panel = ResourceMonitorPanel()
        qtbot.addWidget(panel)
        
        initial_count = panel.tasks_table.rowCount()
        
        panel.add_task("Test Task", "task_001")
        
        assert panel.tasks_table.rowCount() == initial_count + 1
    
    def test_update_task(self, qapp, qtbot):
        """Test updating task information"""
        panel = ResourceMonitorPanel()
        qtbot.addWidget(panel)
        
        panel.add_task("Test Task", "task_001")
        panel.update_task("task_001", 50.0, 100.0, "Running")
        
        # Check if task was updated
        assert panel.tasks_table.rowCount() > 0
    
    def test_remove_task(self, qapp, qtbot):
        """Test removing a task"""
        panel = ResourceMonitorPanel()
        qtbot.addWidget(panel)
        
        panel.add_task("Test Task", "task_001")
        initial_count = panel.tasks_table.rowCount()
        
        panel.remove_task("task_001")
        
        assert panel.tasks_table.rowCount() == initial_count - 1
    
    def test_clear_tasks(self, qapp, qtbot):
        """Test clearing all tasks"""
        panel = ResourceMonitorPanel()
        qtbot.addWidget(panel)
        
        panel.add_task("Task 1", "task_001")
        panel.add_task("Task 2", "task_002")
        
        panel.clear_tasks()
        
        assert panel.tasks_table.rowCount() == 0


class TestActivityLogPanel:
    """Tests for ActivityLogPanel"""
    
    def test_init(self, qapp, qtbot):
        """Test ActivityLogPanel initialization"""
        panel = ActivityLogPanel()
        qtbot.addWidget(panel)
        
        assert panel.log_text is not None
        assert panel.clear_btn is not None
        assert panel.export_btn is not None
    
    def test_log_message(self, qapp, qtbot):
        """Test logging a message"""
        panel = ActivityLogPanel()
        qtbot.addWidget(panel)
        
        panel.log_message("Test message", "INFO")
        
        content = panel.log_text.toPlainText()
        assert "Test message" in content
        assert "INFO" in content
    
    def test_log_levels(self, qapp, qtbot):
        """Test different log levels"""
        panel = ActivityLogPanel()
        qtbot.addWidget(panel)
        
        panel.log_info("Info message")
        panel.log_warning("Warning message")
        panel.log_error("Error message")
        panel.log_success("Success message")
        
        content = panel.log_text.toPlainText()
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content
        assert "Success message" in content
    
    def test_add_operation_progress(self, qapp, qtbot):
        """Test adding an operation with progress bar"""
        panel = ActivityLogPanel()
        qtbot.addWidget(panel)
        
        panel.add_operation_progress("op_001", "Test Operation")
        
        assert "op_001" in panel._operation_progress
    
    def test_update_operation_progress(self, qapp, qtbot):
        """Test updating operation progress"""
        panel = ActivityLogPanel()
        qtbot.addWidget(panel)
        
        panel.add_operation_progress("op_001", "Test Operation")
        panel.update_operation_progress("op_001", 50, "Processing...")
        
        # Check if progress bar was updated
        assert panel._operation_progress["op_001"]["progress"].value() == 50
    
    def test_complete_operation(self, qapp, qtbot):
        """Test completing an operation"""
        panel = ActivityLogPanel()
        qtbot.addWidget(panel)
        
        panel.add_operation_progress("op_001", "Test Operation")
        panel.complete_operation("op_001", success=True)
        
        assert "op_001" not in panel._operation_progress


class TestDataTablesPanel:
    """Tests for DataTablesPanel"""
    
    def test_init(self, qapp, qtbot):
        """Test DataTablesPanel initialization"""
        panel = DataTablesPanel()
        qtbot.addWidget(panel)
        
        assert panel.tabs is not None
        # Use the constant from the class
        assert len(panel._views) == DataTablesPanel.EXPECTED_TAB_COUNT
    
    def test_set_raw_data(self, qapp, qtbot):
        """Test setting raw data"""
        panel = DataTablesPanel()
        qtbot.addWidget(panel)
        
        data = pd.DataFrame({
            'time': [0, 1, 2, 3],
            'value': [10, 20, 30, 40]
        })
        
        panel.set_raw_data(data)
        
        # Check if data was set
        raw_view = panel._views["raw"]
        assert raw_view.get_data() is not None
        assert len(raw_view.get_data()) == 4
    
    def test_set_multiple_data_types(self, qapp, qtbot):
        """Test setting different data types"""
        panel = DataTablesPanel()
        qtbot.addWidget(panel)
        
        data1 = pd.DataFrame({'a': [1, 2, 3]})
        data2 = pd.DataFrame({'b': [4, 5, 6]})
        data3 = pd.DataFrame({'c': [7, 8, 9]})
        
        panel.set_raw_data(data1)
        panel.set_interpolated_data(data2)
        panel.set_calculated_data(data3)
        
        assert panel._views["raw"].get_data() is not None
        assert panel._views["interpolated"].get_data() is not None
        assert panel._views["calculated"].get_data() is not None
    
    def test_clear_all(self, qapp, qtbot):
        """Test clearing all tables"""
        panel = DataTablesPanel()
        qtbot.addWidget(panel)
        
        data = pd.DataFrame({'a': [1, 2, 3]})
        panel.set_raw_data(data)
        
        panel.clear_all()
        
        # All views should be empty
        for view in panel._views.values():
            assert view.get_data() is None or view.get_data().empty


@pytest.mark.smoke
class TestPanelsIntegration:
    """Smoke tests for panel integration"""
    
    def test_all_panels_can_be_created(self, qapp, qtbot):
        """Test that all new panels can be instantiated"""
        panels = [
            ResourceMonitorPanel(),
            ActivityLogPanel(),
            DataTablesPanel(),
        ]
        
        for panel in panels:
            qtbot.addWidget(panel)
            assert panel is not None
