# -*- coding: utf-8 -*-
"""
Test 12: Layouts
================

Tests:
- Test responsive layouts
- Verify proper resizing behavior
- Test widget alignment
- Verify layout margins and spacing
"""
from __future__ import annotations

import pytest


class TestLayoutTypes:
    """Test different layout types."""

    def test_vbox_layout(self, qapp):
        """Verify QVBoxLayout works correctly."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        layout.addWidget(QLabel("Item 1"))
        layout.addWidget(QLabel("Item 2"))
        layout.addWidget(QLabel("Item 3"))
        
        assert layout.count() == 3
        
        parent.deleteLater()
        qapp.processEvents()

    def test_hbox_layout(self, qapp):
        """Verify QHBoxLayout works correctly."""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
        
        parent = QWidget()
        layout = QHBoxLayout(parent)
        
        layout.addWidget(QLabel("Left"))
        layout.addWidget(QLabel("Center"))
        layout.addWidget(QLabel("Right"))
        
        assert layout.count() == 3
        
        parent.deleteLater()
        qapp.processEvents()

    def test_grid_layout(self, qapp):
        """Verify QGridLayout works correctly."""
        from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
        
        parent = QWidget()
        layout = QGridLayout(parent)
        
        layout.addWidget(QLabel("0,0"), 0, 0)
        layout.addWidget(QLabel("0,1"), 0, 1)
        layout.addWidget(QLabel("1,0"), 1, 0)
        layout.addWidget(QLabel("1,1"), 1, 1)
        
        assert layout.count() == 4
        assert layout.rowCount() == 2
        assert layout.columnCount() == 2
        
        parent.deleteLater()
        qapp.processEvents()

    def test_form_layout(self, qapp):
        """Verify QFormLayout works correctly."""
        from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit
        
        parent = QWidget()
        layout = QFormLayout(parent)
        
        layout.addRow("Name:", QLineEdit())
        layout.addRow("Email:", QLineEdit())
        layout.addRow("Phone:", QLineEdit())
        
        assert layout.rowCount() == 3
        
        parent.deleteLater()
        qapp.processEvents()

    def test_stacked_layout(self, qapp):
        """Verify QStackedLayout works correctly."""
        from PyQt6.QtWidgets import QWidget, QStackedLayout, QLabel
        
        parent = QWidget()
        layout = QStackedLayout(parent)
        
        page1 = QLabel("Page 1")
        page2 = QLabel("Page 2")
        
        layout.addWidget(page1)
        layout.addWidget(page2)
        
        layout.setCurrentIndex(0)
        assert layout.currentWidget() == page1
        
        layout.setCurrentIndex(1)
        assert layout.currentWidget() == page2
        
        parent.deleteLater()
        qapp.processEvents()


class TestResponsiveLayouts:
    """Test responsive layout behavior."""

    def test_stretch_factors(self, qapp):
        """Verify stretch factors work."""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
        
        parent = QWidget()
        layout = QHBoxLayout(parent)
        
        label1 = QLabel("Small")
        label2 = QLabel("Large")
        
        layout.addWidget(label1, stretch=1)
        layout.addWidget(label2, stretch=2)
        
        parent.resize(300, 100)
        parent.show()
        qapp.processEvents()
        
        # Label2 should be roughly twice as wide as label1
        # (exact sizes depend on content and margins)
        
        parent.deleteLater()
        qapp.processEvents()

    def test_size_policy(self, qapp):
        """Verify size policies work."""
        from PyQt6.QtWidgets import QWidget, QSizePolicy
        
        widget = QWidget()
        
        # Set expanding policy
        policy = QSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        widget.setSizePolicy(policy)
        
        assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
        assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Fixed
        
        widget.deleteLater()
        qapp.processEvents()

    def test_minimum_size(self, qapp):
        """Verify minimum size is respected."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        widget.setMinimumSize(100, 50)
        
        # Try to resize smaller
        widget.resize(50, 25)
        
        # Should not go below minimum
        assert widget.width() >= 100
        assert widget.height() >= 50
        
        widget.deleteLater()
        qapp.processEvents()

    def test_maximum_size(self, qapp):
        """Verify maximum size is respected."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        widget.setMaximumSize(200, 100)
        
        # Try to resize larger
        widget.resize(300, 200)
        
        # Should not exceed maximum
        assert widget.width() <= 200
        assert widget.height() <= 100
        
        widget.deleteLater()
        qapp.processEvents()

    def test_fixed_size(self, qapp):
        """Verify fixed size works."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        widget.setFixedSize(150, 75)
        
        widget.resize(200, 100)  # Try to resize
        
        assert widget.width() == 150
        assert widget.height() == 75
        
        widget.deleteLater()
        qapp.processEvents()


class TestResizingBehavior:
    """Test widget resizing behavior."""

    def test_window_resize(self, qapp):
        """Verify window resize works."""
        from PyQt6.QtWidgets import QMainWindow
        
        window = QMainWindow()
        window.resize(800, 600)
        window.show()
        
        assert window.width() == 800
        assert window.height() == 600
        
        window.resize(1024, 768)
        
        assert window.width() == 1024
        assert window.height() == 768
        
        window.close()
        window.deleteLater()
        qapp.processEvents()

    def test_layout_updates_on_resize(self, qapp):
        """Verify layout updates when parent resizes."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        button = QPushButton("Test")
        layout.addWidget(button)
        
        parent.resize(200, 200)
        parent.show()
        qapp.processEvents()
        
        initial_width = button.width()
        
        parent.resize(400, 200)
        qapp.processEvents()
        
        # Button should expand with parent
        assert button.width() >= initial_width
        
        parent.deleteLater()
        qapp.processEvents()

    def test_splitter_resize(self, qapp):
        """Verify splitter resize works."""
        from PyQt6.QtWidgets import QSplitter, QWidget
        from PyQt6.QtCore import Qt
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left = QWidget()
        right = QWidget()
        
        splitter.addWidget(left)
        splitter.addWidget(right)
        
        splitter.setSizes([200, 300])
        splitter.show()
        qapp.processEvents()
        
        sizes = splitter.sizes()
        
        # Verify that the splitter respects the ratio approximately
        # The exact sizes may vary due to handles and minimum sizes
        total_requested = 200 + 300
        total_actual = sum(sizes)
        
        # The ratio should be approximately preserved
        if total_actual > 0:
            ratio_requested = 200 / total_requested  # ~0.4
            ratio_actual = sizes[0] / total_actual if total_actual else 0
            
            # Allow 20% tolerance on ratio
            assert abs(ratio_actual - ratio_requested) < 0.2, \
                f"Ratio {ratio_actual:.2f} should be close to {ratio_requested:.2f}"
        
        splitter.deleteLater()
        qapp.processEvents()


class TestWidgetAlignment:
    """Test widget alignment."""

    def test_layout_alignment(self, qapp):
        """Verify layout alignment works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        label = QLabel("Centered")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Should be centered in layout
        parent.show()
        qapp.processEvents()
        
        parent.deleteLater()
        qapp.processEvents()

    def test_label_text_alignment(self, qapp):
        """Verify label text alignment works."""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt
        
        label = QLabel("Test")
        
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        assert label.alignment() == Qt.AlignmentFlag.AlignCenter
        
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        assert label.alignment() == Qt.AlignmentFlag.AlignRight
        
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        assert label.alignment() == Qt.AlignmentFlag.AlignLeft
        
        label.deleteLater()
        qapp.processEvents()

    def test_grid_cell_alignment(self, qapp):
        """Verify grid cell alignment works."""
        from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
        from PyQt6.QtCore import Qt
        
        parent = QWidget()
        layout = QGridLayout(parent)
        
        label = QLabel("Aligned")
        layout.addWidget(
            label, 0, 0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        
        assert layout.count() == 1
        
        parent.deleteLater()
        qapp.processEvents()


class TestMarginsAndSpacing:
    """Test layout margins and spacing."""

    def test_layout_margins(self, qapp):
        """Verify layout margins work."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        layout.setContentsMargins(10, 20, 30, 40)
        
        margins = layout.contentsMargins()
        assert margins.left() == 10
        assert margins.top() == 20
        assert margins.right() == 30
        assert margins.bottom() == 40
        
        parent.deleteLater()
        qapp.processEvents()

    def test_layout_spacing(self, qapp):
        """Verify layout spacing works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        layout.setSpacing(10)
        layout.addWidget(QPushButton("1"))
        layout.addWidget(QPushButton("2"))
        
        assert layout.spacing() == 10
        
        parent.deleteLater()
        qapp.processEvents()

    def test_zero_margins(self, qapp):
        """Verify zero margins work."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        layout.setContentsMargins(0, 0, 0, 0)
        
        margins = layout.contentsMargins()
        assert margins.left() == 0
        assert margins.right() == 0
        
        parent.deleteLater()
        qapp.processEvents()


class TestNestedLayouts:
    """Test nested layout structures."""

    def test_nested_vbox_hbox(self, qapp):
        """Verify nested VBox and HBox layouts work."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
        
        parent = QWidget()
        main_layout = QVBoxLayout(parent)
        
        # Add nested horizontal layouts
        for i in range(3):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Row {i} - Left"))
            row.addWidget(QLabel(f"Row {i} - Right"))
            main_layout.addLayout(row)
        
        assert main_layout.count() == 3
        
        parent.deleteLater()
        qapp.processEvents()

    def test_deeply_nested_layouts(self, qapp):
        """Verify deeply nested layouts work."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        widgets = []
        
        # Create nested structure
        root = QWidget()
        widgets.append(root)
        current_layout = QVBoxLayout(root)
        
        for i in range(5):
            container = QWidget()
            widgets.append(container)
            current_layout.addWidget(container)
            current_layout = QVBoxLayout(container)
            current_layout.addWidget(QLabel(f"Level {i}"))
        
        # Should work without issues
        root.show()
        qapp.processEvents()
        
        root.deleteLater()
        qapp.processEvents()


class TestLayoutItems:
    """Test layout item management."""

    def test_add_remove_widgets(self, qapp):
        """Verify adding and removing widgets works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        btn1 = QPushButton("1")
        btn2 = QPushButton("2")
        
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        
        assert layout.count() == 2
        
        layout.removeWidget(btn1)
        btn1.deleteLater()
        
        assert layout.count() == 1
        
        parent.deleteLater()
        qapp.processEvents()

    def test_insert_widget(self, qapp):
        """Verify inserting widgets works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        layout.addWidget(QLabel("First"))
        layout.addWidget(QLabel("Last"))
        
        # Insert in middle
        layout.insertWidget(1, QLabel("Middle"))
        
        assert layout.count() == 3
        
        parent.deleteLater()
        qapp.processEvents()

    def test_add_spacer(self, qapp):
        """Verify adding spacers works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        layout.addWidget(QPushButton("Top"))
        layout.addStretch(1)  # Spacer
        layout.addWidget(QPushButton("Bottom"))
        
        assert layout.count() == 3
        
        parent.deleteLater()
        qapp.processEvents()

    def test_replace_widget(self, qapp):
        """Verify replacing widgets works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        old_widget = QPushButton("Old")
        layout.addWidget(old_widget)
        
        new_widget = QLabel("New")
        layout.replaceWidget(old_widget, new_widget)
        
        old_widget.deleteLater()
        
        # New widget should be in layout
        assert layout.indexOf(new_widget) == 0
        
        parent.deleteLater()
        qapp.processEvents()
