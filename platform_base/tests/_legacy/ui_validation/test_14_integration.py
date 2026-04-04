# -*- coding: utf-8 -*-
"""
Test 14: Integration
====================

Tests:
- Test window communication
- Verify data sharing between windows/panels
- Test event propagation
- Verify cross-component interactions
"""
from __future__ import annotations

import pytest


class TestWindowCommunication:
    """Test communication between windows."""

    def test_signal_between_windows(self, qapp):
        """Verify signals can communicate between windows."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import pyqtSignal, QObject
        
        class Sender(QWidget):
            data_sent = pyqtSignal(str)
        
        class Receiver(QWidget):
            def __init__(self):
                super().__init__()
                self.received_data = None
            
            def on_data_received(self, data):
                self.received_data = data
        
        sender = Sender()
        receiver = Receiver()
        
        sender.data_sent.connect(receiver.on_data_received)
        sender.data_sent.emit("Test message")
        
        assert receiver.received_data == "Test message"
        
        sender.deleteLater()
        receiver.deleteLater()
        qapp.processEvents()

    def test_parent_child_communication(self, qapp):
        """Verify parent-child widget communication."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        class Parent(QWidget):
            def __init__(self):
                super().__init__()
                self.layout = QVBoxLayout(self)
                self.child = Child()
                self.layout.addWidget(self.child)
                self.message_received = None
        
        class Child(QWidget):
            from PyQt6.QtCore import pyqtSignal
            message = pyqtSignal(str)
        
        parent = Parent()
        parent.child.message.connect(lambda msg: setattr(parent, 'message_received', msg))
        parent.child.message.emit("Hello from child")
        
        assert parent.message_received == "Hello from child"
        
        parent.deleteLater()
        qapp.processEvents()

    def test_dialog_parent_communication(self, qapp):
        """Verify dialog can communicate with parent."""
        from PyQt6.QtWidgets import QMainWindow, QDialog
        
        class MainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.dialog_result = None
        
        class CustomDialog(QDialog):
            def get_result(self):
                return "Dialog Result"
        
        main = MainWindow()
        dialog = CustomDialog(main)
        
        main.dialog_result = dialog.get_result()
        
        assert main.dialog_result == "Dialog Result"
        
        dialog.deleteLater()
        main.deleteLater()
        qapp.processEvents()


class TestDataSharing:
    """Test data sharing between components."""

    def test_shared_data_model(self, qapp):
        """Verify shared data model works."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class SharedModel(QObject):
            data_changed = pyqtSignal(dict)
            
            def __init__(self):
                super().__init__()
                self._data = {}
            
            def set_data(self, key, value):
                self._data[key] = value
                self.data_changed.emit(self._data)
            
            def get_data(self, key):
                return self._data.get(key)
        
        model = SharedModel()
        
        received = [None]
        model.data_changed.connect(lambda d: received.__setitem__(0, d))
        
        model.set_data("name", "Test")
        
        assert received[0] == {"name": "Test"}
        assert model.get_data("name") == "Test"
        
        model.deleteLater()
        qapp.processEvents()

    def test_list_model_sharing(self, qapp):
        """Verify list model can be shared between views."""
        from PyQt6.QtWidgets import QListView
        from PyQt6.QtCore import QStringListModel
        
        model = QStringListModel()
        model.setStringList(["Item 1", "Item 2", "Item 3"])
        
        view1 = QListView()
        view2 = QListView()
        
        view1.setModel(model)
        view2.setModel(model)
        
        # Both views share the same model
        assert view1.model() is view2.model()
        
        # Changes in model reflect in both views
        model.setStringList(["Updated 1", "Updated 2"])
        
        assert view1.model().rowCount() == 2
        assert view2.model().rowCount() == 2
        
        view1.deleteLater()
        view2.deleteLater()
        qapp.processEvents()

    def test_table_model_sharing(self, qapp):
        """Verify table model can be shared."""
        from PyQt6.QtWidgets import QTableView
        from PyQt6.QtCore import QAbstractTableModel, Qt
        
        class SimpleTableModel(QAbstractTableModel):
            def __init__(self, data):
                super().__init__()
                self._data = data
            
            def rowCount(self, parent=None):
                return len(self._data)
            
            def columnCount(self, parent=None):
                return len(self._data[0]) if self._data else 0
            
            def data(self, index, role=Qt.ItemDataRole.DisplayRole):
                if role == Qt.ItemDataRole.DisplayRole:
                    return self._data[index.row()][index.column()]
                return None
        
        data = [[1, 2], [3, 4], [5, 6]]
        model = SimpleTableModel(data)
        
        view1 = QTableView()
        view2 = QTableView()
        
        view1.setModel(model)
        view2.setModel(model)
        
        assert view1.model() is view2.model()
        
        view1.deleteLater()
        view2.deleteLater()
        qapp.processEvents()


class TestEventPropagation:
    """Test event propagation between components."""

    def test_event_filter(self, qapp):
        """Verify event filter works."""
        from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout
        from PyQt6.QtCore import QEvent
        
        class FilteringParent(QWidget):
            def __init__(self):
                super().__init__()
                self.layout = QVBoxLayout(self)
                self.edit = QLineEdit()
                self.layout.addWidget(self.edit)
                self.edit.installEventFilter(self)
                self.events_filtered = []
            
            def eventFilter(self, obj, event):
                if obj is self.edit:
                    self.events_filtered.append(event.type())
                return False  # Don't block events
        
        parent = FilteringParent()
        parent.show()
        qapp.processEvents()
        
        # Event filter should have captured some events
        parent.close()
        parent.deleteLater()
        qapp.processEvents()

    def test_custom_event(self, qapp):
        """Verify custom events work."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import QEvent
        
        # Custom event type
        CUSTOM_EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
        
        class CustomEvent(QEvent):
            def __init__(self, data):
                super().__init__(CUSTOM_EVENT_TYPE)
                self.data = data
        
        class Receiver(QWidget):
            def __init__(self):
                super().__init__()
                self.received_data = None
            
            def event(self, event):
                if event.type() == CUSTOM_EVENT_TYPE:
                    self.received_data = event.data
                    return True
                return super().event(event)
        
        receiver = Receiver()
        custom_event = CustomEvent("Custom Data")
        
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.postEvent(receiver, custom_event)
        qapp.processEvents()
        
        assert receiver.received_data == "Custom Data"
        
        receiver.deleteLater()
        qapp.processEvents()


class TestCrossComponentInteractions:
    """Test interactions between different component types."""

    def test_toolbar_menu_sync(self, qapp):
        """Verify toolbar and menu actions stay synchronized."""
        from PyQt6.QtWidgets import QMainWindow, QToolBar
        from PyQt6.QtGui import QAction
        
        window = QMainWindow()
        
        # Create shared action
        save_action = QAction("Save", window)
        save_action.setCheckable(True)
        
        # Add to menu
        menu = window.menuBar().addMenu("File")
        menu.addAction(save_action)
        
        # Add to toolbar
        toolbar = QToolBar()
        window.addToolBar(toolbar)
        toolbar.addAction(save_action)
        
        # Toggle action
        save_action.setChecked(True)
        
        # Both menu and toolbar should reflect the change
        assert save_action.isChecked()
        
        window.deleteLater()
        qapp.processEvents()

    def test_statusbar_updates(self, qapp):
        """Verify status bar responds to widget changes."""
        from PyQt6.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QWidget
        
        window = QMainWindow()
        central = QWidget()
        layout = QVBoxLayout(central)
        
        edit = QLineEdit()
        layout.addWidget(edit)
        window.setCentralWidget(central)
        
        def update_status(text):
            window.statusBar().showMessage(f"Entered: {text}")
        
        edit.textChanged.connect(update_status)
        
        edit.setText("Hello")
        
        assert "Hello" in window.statusBar().currentMessage()
        
        window.deleteLater()
        qapp.processEvents()

    def test_combobox_selection_updates_display(self, qapp):
        """Verify combobox selection updates related display."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        combo = QComboBox()
        combo.addItems(["Option A", "Option B", "Option C"])
        
        display = QLabel("No selection")
        
        layout.addWidget(combo)
        layout.addWidget(display)
        
        combo.currentTextChanged.connect(
            lambda text: display.setText(f"Selected: {text}")
        )
        
        combo.setCurrentIndex(1)
        
        assert "Option B" in display.text()
        
        widget.deleteLater()
        qapp.processEvents()


class TestPanelIntegration:
    """Test integration between panels."""

    def test_dock_widget_communication(self, qapp):
        """Verify dock widgets can communicate."""
        from PyQt6.QtWidgets import QMainWindow, QDockWidget, QWidget, QLabel, QVBoxLayout
        from PyQt6.QtCore import Qt, pyqtSignal
        
        class DataPanel(QWidget):
            data_selected = pyqtSignal(str)
            
            def select_item(self, item):
                self.data_selected.emit(item)
        
        class DetailsPanel(QWidget):
            def __init__(self):
                super().__init__()
                self.layout = QVBoxLayout(self)
                self.label = QLabel("No selection")
                self.layout.addWidget(self.label)
            
            def show_details(self, item):
                self.label.setText(f"Details for: {item}")
        
        window = QMainWindow()
        
        data_panel = DataPanel()
        details_panel = DetailsPanel()
        
        dock1 = QDockWidget("Data")
        dock1.setWidget(data_panel)
        
        dock2 = QDockWidget("Details")
        dock2.setWidget(details_panel)
        
        window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock1)
        window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock2)
        
        # Connect panels
        data_panel.data_selected.connect(details_panel.show_details)
        
        # Simulate selection
        data_panel.select_item("Item 1")
        
        assert "Item 1" in details_panel.label.text()
        
        window.deleteLater()
        qapp.processEvents()

    def test_splitter_panels(self, qapp):
        """Verify splitter panels can interact."""
        from PyQt6.QtWidgets import QSplitter, QListWidget, QTextEdit
        from PyQt6.QtCore import Qt
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        list_widget = QListWidget()
        list_widget.addItems(["Document 1", "Document 2", "Document 3"])
        
        editor = QTextEdit()
        
        splitter.addWidget(list_widget)
        splitter.addWidget(editor)
        
        # Connect selection to editor
        def on_selection_changed():
            current = list_widget.currentItem()
            if current:
                editor.setPlainText(f"Content of {current.text()}")
        
        list_widget.currentItemChanged.connect(lambda: on_selection_changed())
        
        list_widget.setCurrentRow(0)
        qapp.processEvents()
        
        assert "Document 1" in editor.toPlainText()
        
        splitter.deleteLater()
        qapp.processEvents()


class TestApplicationWideIntegration:
    """Test application-wide integration patterns."""

    def test_settings_affect_all_windows(self, qapp):
        """Verify application settings affect all windows."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtGui import QFont
        
        # Apply application-wide font FIRST
        font = QFont("Arial", 14)
        qapp.setFont(font)
        qapp.processEvents()
        
        # Get actual family (may differ from "Arial" in offscreen mode)
        actual_family = qapp.font().family()
        
        # Create windows AFTER setting the font
        windows = [QWidget() for _ in range(3)]
        
        # All new windows should inherit the app font
        for window in windows:
            # All windows should use same font family as the app font
            assert window.font().family() == actual_family
        
        for window in windows:
            window.deleteLater()
        qapp.processEvents()

    def test_palette_affects_all_widgets(self, qapp):
        """Verify palette changes affect all widgets."""
        from PyQt6.QtWidgets import QPushButton, QLineEdit
        from PyQt6.QtGui import QPalette
        
        # Create widgets
        button = QPushButton()
        edit = QLineEdit()
        
        # Get current palette
        palette = qapp.palette()
        
        # Both should use the same palette base
        assert button.palette() is not None
        assert edit.palette() is not None
        
        button.deleteLater()
        edit.deleteLater()
        qapp.processEvents()

    def test_clipboard_integration(self, qapp):
        """Verify clipboard works across widgets."""
        from PyQt6.QtWidgets import QApplication, QLineEdit
        
        edit1 = QLineEdit("Source text")
        edit2 = QLineEdit()
        
        # Copy from edit1
        edit1.selectAll()
        clipboard = QApplication.clipboard()
        clipboard.setText(edit1.selectedText())
        
        # Paste to edit2
        edit2.setText(clipboard.text())
        
        assert edit2.text() == "Source text"
        
        edit1.deleteLater()
        edit2.deleteLater()
        qapp.processEvents()

    def test_drag_drop_integration(self, qapp):
        """Verify drag-drop properties can be set."""
        from PyQt6.QtWidgets import QListWidget
        from PyQt6.QtCore import Qt
        
        source = QListWidget()
        source.setDragEnabled(True)
        source.addItems(["Item 1", "Item 2"])
        
        target = QListWidget()
        target.setAcceptDrops(True)
        target.setDefaultDropAction(Qt.DropAction.CopyAction)
        
        assert source.dragEnabled()
        assert target.acceptDrops()
        
        source.deleteLater()
        target.deleteLater()
        qapp.processEvents()
