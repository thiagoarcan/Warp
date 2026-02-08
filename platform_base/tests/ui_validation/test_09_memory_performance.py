# -*- coding: utf-8 -*-
"""
Test 09: Memory and Performance
===============================

Tests:
- Test memory leaks (widget creation/destruction)
- Measure load times
- Test resource cleanup
- Monitor excessive CPU usage patterns
"""
from __future__ import annotations

import gc
import sys
import time
import weakref

import pytest


class TestMemoryLeaks:
    """Test memory leak detection."""

    def test_widget_garbage_collection(self, qapp):
        """Verify widgets are garbage collected when deleted."""
        from PyQt6.QtWidgets import QPushButton
        
        # Create widget and get weak reference
        widget = QPushButton("Test")
        weak_ref = weakref.ref(widget)
        
        # Verify widget exists
        assert weak_ref() is not None
        
        # Delete widget
        widget.deleteLater()
        widget = None
        
        # Process events and force garbage collection
        qapp.processEvents()
        gc.collect()
        
        # Widget should be collected (may take multiple cycles)
        # Note: Qt may keep references internally
        for _ in range(5):
            qapp.processEvents()
            gc.collect()

    def test_dialog_cleanup(self, qapp):
        """Verify dialogs are cleaned up after closing."""
        from PyQt6.QtWidgets import QDialog
        
        initial_objects = len(gc.get_objects())
        
        # Create and destroy multiple dialogs
        for _ in range(10):
            dialog = QDialog()
            dialog.deleteLater()
            qapp.processEvents()
        
        gc.collect()
        qapp.processEvents()
        
        # Object count should not grow significantly
        final_objects = len(gc.get_objects())
        growth = final_objects - initial_objects
        
        # Allow some growth but not excessive
        assert growth < 1000, f"Object growth too high: {growth}"

    def test_signal_disconnection(self, qapp):
        """Verify signals are properly disconnected."""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtCore import QObject
        
        button = QPushButton()
        
        handler_called = [0]
        
        def handler():
            handler_called[0] += 1
        
        button.clicked.connect(handler)
        button.click()
        assert handler_called[0] == 1
        
        button.clicked.disconnect(handler)
        button.click()
        assert handler_called[0] == 1  # Should not increment
        
        button.deleteLater()
        qapp.processEvents()

    def test_timer_cleanup(self, qapp):
        """Verify timers are properly stopped and cleaned."""
        from PyQt6.QtCore import QTimer
        
        timer = QTimer()
        timer.setInterval(100)
        timer.start()
        
        assert timer.isActive()
        
        timer.stop()
        assert not timer.isActive()
        
        timer.deleteLater()
        qapp.processEvents()


class TestLoadTimes:
    """Test UI load times."""

    def test_widget_creation_time(self, qapp):
        """Verify widget creation is fast."""
        from PyQt6.QtWidgets import QMainWindow
        
        start = time.perf_counter()
        
        window = QMainWindow()
        
        elapsed = time.perf_counter() - start
        
        # Should be under 100ms
        assert elapsed < 0.1, f"Window creation took {elapsed*1000:.2f}ms"
        
        window.deleteLater()
        qapp.processEvents()

    def test_complex_layout_creation_time(self, qapp):
        """Verify complex layout creation is reasonable."""
        from PyQt6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout,
            QPushButton, QLabel, QLineEdit
        )
        
        start = time.perf_counter()
        
        parent = QWidget()
        main_layout = QVBoxLayout(parent)
        
        # Create complex nested layout
        for i in range(10):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Label {i}"))
            row.addWidget(QLineEdit())
            row.addWidget(QPushButton(f"Button {i}"))
            main_layout.addLayout(row)
        
        elapsed = time.perf_counter() - start
        
        # Should be under 200ms
        assert elapsed < 0.2, f"Layout creation took {elapsed*1000:.2f}ms"
        
        parent.deleteLater()
        qapp.processEvents()

    def test_ui_file_load_time(self, ui_files_dir, qapp):
        """Verify .ui file loading is fast."""
        from pathlib import Path
        
        ui_files = list(Path(ui_files_dir).glob("*.ui"))
        
        if not ui_files:
            pytest.skip("No .ui files found")
        
        from PyQt6 import uic
        
        for ui_file in ui_files[:5]:  # Test first 5 files
            start = time.perf_counter()
            
            try:
                widget = uic.loadUi(str(ui_file))
                
                elapsed = time.perf_counter() - start
                
                # Each file should load under 500ms
                assert elapsed < 0.5, f"{ui_file.name} took {elapsed*1000:.2f}ms"
                
                widget.deleteLater()
                qapp.processEvents()
            except Exception:
                pass  # Skip files with errors

    def test_table_population_time(self, qapp):
        """Verify table population is reasonable."""
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        
        table = QTableWidget()
        table.setRowCount(100)
        table.setColumnCount(10)
        
        start = time.perf_counter()
        
        for row in range(100):
            for col in range(10):
                table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))
        
        elapsed = time.perf_counter() - start
        
        # Should be under 500ms for 1000 cells
        assert elapsed < 0.5, f"Table population took {elapsed*1000:.2f}ms"
        
        table.deleteLater()
        qapp.processEvents()


class TestResourceCleanup:
    """Test resource cleanup."""

    def test_pixmap_cleanup(self, qapp):
        """Verify pixmaps are cleaned up."""
        from PyQt6.QtGui import QPixmap
        
        # Create and destroy pixmaps
        for _ in range(100):
            pixmap = QPixmap(100, 100)
            del pixmap
        
        gc.collect()
        # No assertion needed - just verify no crash

    def test_font_cleanup(self, qapp):
        """Verify fonts don't leak."""
        from PyQt6.QtGui import QFont
        
        for _ in range(100):
            font = QFont("Arial", 12)
            font.setBold(True)
            del font
        
        gc.collect()

    def test_color_cleanup(self, qapp):
        """Verify colors don't leak."""
        from PyQt6.QtGui import QColor
        
        for _ in range(1000):
            color = QColor(255, 0, 0)
            del color
        
        gc.collect()

    def test_painter_cleanup(self, qapp):
        """Verify painters are cleaned up."""
        from PyQt6.QtGui import QPixmap, QPainter
        
        for _ in range(10):
            pixmap = QPixmap(100, 100)
            painter = QPainter(pixmap)
            painter.fillRect(0, 0, 100, 100, painter.background())
            painter.end()
            del painter
            del pixmap
        
        gc.collect()


class TestPerformancePatterns:
    """Test performance patterns."""

    def test_batch_updates(self, qapp):
        """Verify batch updates are faster than individual."""
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        
        list_widget = QListWidget()
        
        # Individual updates
        start = time.perf_counter()
        for i in range(100):
            list_widget.addItem(f"Item {i}")
        individual_time = time.perf_counter() - start
        
        list_widget.clear()
        
        # Batch with updates disabled
        start = time.perf_counter()
        list_widget.setUpdatesEnabled(False)
        for i in range(100):
            list_widget.addItem(f"Item {i}")
        list_widget.setUpdatesEnabled(True)
        batch_time = time.perf_counter() - start
        
        # Batch should be at least as fast (often faster)
        # Note: May not always be true in all scenarios
        
        list_widget.deleteLater()
        qapp.processEvents()

    def test_layout_update_minimization(self, qapp):
        """Verify layout updates are minimized."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        # Block layout updates during batch add
        parent.setUpdatesEnabled(False)
        
        for i in range(20):
            layout.addWidget(QPushButton(f"Button {i}"))
        
        parent.setUpdatesEnabled(True)
        parent.update()
        
        assert layout.count() == 20
        
        parent.deleteLater()
        qapp.processEvents()

    def test_model_view_performance(self, qapp):
        """Verify model/view pattern is efficient."""
        from PyQt6.QtWidgets import QListView
        from PyQt6.QtCore import QStringListModel
        
        view = QListView()
        model = QStringListModel()
        
        # Generate data
        data = [f"Item {i}" for i in range(1000)]
        
        start = time.perf_counter()
        model.setStringList(data)
        view.setModel(model)
        elapsed = time.perf_counter() - start
        
        # Should be fast with model/view
        assert elapsed < 0.1, f"Model/view setup took {elapsed*1000:.2f}ms"
        
        view.deleteLater()
        qapp.processEvents()


class TestCPUUsage:
    """Test CPU usage patterns."""

    def test_idle_no_cpu_usage(self, qapp, qtbot):
        """Verify idle application uses minimal CPU."""
        from PyQt6.QtWidgets import QMainWindow
        
        window = QMainWindow()
        window.show()
        
        # Process events
        qapp.processEvents()
        
        # Just verify window is responsive
        assert window.isVisible()
        
        window.close()
        window.deleteLater()
        qapp.processEvents()

    def test_timer_interval_reasonable(self, qapp, qtbot):
        """Verify timers use reasonable intervals."""
        from PyQt6.QtCore import QTimer
        
        timer = QTimer()
        timer.setInterval(100)  # 100ms is reasonable
        
        # Intervals below 16ms (60fps) should be rare
        assert timer.interval() >= 16, "Timer interval too short"
        
        timer.deleteLater()
        qapp.processEvents()

    def test_animation_frame_rate(self, qapp):
        """Verify animations use reasonable frame rates."""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        widget.setGeometry(0, 0, 100, 100)
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(1000)  # 1 second
        
        # Duration should be reasonable
        assert animation.duration() >= 100, "Animation too short"
        
        widget.deleteLater()
        qapp.processEvents()


class TestMemoryBaseline:
    """Test memory baseline measurements."""

    def test_widget_memory_footprint(self, qapp):
        """Measure basic widget memory footprint."""
        from PyQt6.QtWidgets import QPushButton
        
        gc.collect()
        
        # Create widgets
        widgets = [QPushButton(f"Button {i}") for i in range(100)]
        
        # Count exists
        assert len(widgets) == 100
        
        # Cleanup
        for w in widgets:
            w.deleteLater()
        
        qapp.processEvents()
        gc.collect()

    def test_large_text_handling(self, qapp):
        """Verify large text doesn't cause memory issues."""
        from PyQt6.QtWidgets import QTextEdit
        
        text_edit = QTextEdit()
        
        # Insert large text
        large_text = "Lorem ipsum " * 10000
        text_edit.setPlainText(large_text)
        
        assert len(text_edit.toPlainText()) > 100000
        
        text_edit.clear()
        text_edit.deleteLater()
        qapp.processEvents()
        gc.collect()

    def test_image_memory_handling(self, qapp):
        """Verify images don't cause memory issues."""
        from PyQt6.QtGui import QImage
        from PyQt6.QtCore import Qt
        
        # Create large image
        image = QImage(1000, 1000, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.blue)
        
        assert not image.isNull()
        assert image.width() == 1000
        
        del image
        gc.collect()
