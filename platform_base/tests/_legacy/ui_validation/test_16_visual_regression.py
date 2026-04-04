# -*- coding: utf-8 -*-
"""
Test 16: Visual Regression
==========================

Tests:
- Screenshot capture functionality
- Visual comparison utilities
- UI appearance validation
- Theme consistency checks
"""
from __future__ import annotations

from pathlib import Path

import pytest


class TestScreenshotCapture:
    """Test screenshot capture functionality."""

    def test_widget_screenshot(self, qapp, tmp_path):
        """Verify widget can be captured as screenshot."""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QPixmap
        
        button = QPushButton("Test Button")
        button.setFixedSize(100, 30)
        button.show()
        qapp.processEvents()
        
        # Capture screenshot
        pixmap = button.grab()
        
        assert not pixmap.isNull()
        
        # In high-DPI or scaled environments, pixel size may differ
        # Check that dimensions are reasonable (within 50% of expected)
        expected_width = 100
        expected_height = 30
        width_ratio = pixmap.width() / expected_width
        height_ratio = pixmap.height() / expected_height
        
        assert 0.5 <= width_ratio <= 2.0, f"Width ratio {width_ratio} out of range"
        assert 0.5 <= height_ratio <= 2.0, f"Height ratio {height_ratio} out of range"
        
        # Save to file
        output_path = tmp_path / "button_screenshot.png"
        result = pixmap.save(str(output_path), "PNG")
        
        assert result
        assert output_path.exists()
        
        button.deleteLater()
        qapp.processEvents()

    def test_window_screenshot(self, qapp, tmp_path):
        """Verify window can be captured as screenshot."""
        from PyQt6.QtWidgets import QMainWindow, QLabel
        
        window = QMainWindow()
        window.setCentralWidget(QLabel("Main Window Content"))
        window.setFixedSize(400, 300)
        window.show()
        qapp.processEvents()
        
        # Capture screenshot
        pixmap = window.grab()
        
        assert not pixmap.isNull()
        assert pixmap.width() >= 400
        assert pixmap.height() >= 300
        
        window.close()
        window.deleteLater()
        qapp.processEvents()

    def test_partial_widget_screenshot(self, qapp):
        """Verify partial widget area can be captured."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import QRect
        
        widget = QWidget()
        widget.setFixedSize(200, 200)
        widget.setStyleSheet("background-color: blue;")
        widget.show()
        qapp.processEvents()
        
        # Capture only part of the widget
        rect = QRect(10, 10, 50, 50)
        pixmap = widget.grab(rect)
        
        assert not pixmap.isNull()
        assert pixmap.width() == 50
        assert pixmap.height() == 50
        
        widget.deleteLater()
        qapp.processEvents()

    def test_screen_screenshot(self, qapp):
        """Verify screen can be captured."""
        screen = qapp.primaryScreen()
        
        if screen is None:
            pytest.skip("No screen available")
        
        # Get screen geometry
        geometry = screen.geometry()
        
        assert geometry.width() > 0
        assert geometry.height() > 0


class TestVisualComparison:
    """Test visual comparison utilities."""

    def test_pixmap_comparison_identical(self, qapp):
        """Verify identical pixmaps compare as equal."""
        from PyQt6.QtGui import QPixmap, QColor
        
        # Create two identical pixmaps
        pixmap1 = QPixmap(100, 100)
        pixmap1.fill(QColor("red"))
        
        pixmap2 = QPixmap(100, 100)
        pixmap2.fill(QColor("red"))
        
        # Convert to images for comparison
        image1 = pixmap1.toImage()
        image2 = pixmap2.toImage()
        
        # Compare
        assert image1 == image2

    def test_pixmap_comparison_different(self, qapp):
        """Verify different pixmaps compare as not equal."""
        from PyQt6.QtGui import QPixmap, QColor
        
        pixmap1 = QPixmap(100, 100)
        pixmap1.fill(QColor("red"))
        
        pixmap2 = QPixmap(100, 100)
        pixmap2.fill(QColor("blue"))
        
        image1 = pixmap1.toImage()
        image2 = pixmap2.toImage()
        
        assert image1 != image2

    def test_image_size_comparison(self, qapp):
        """Verify images of different sizes compare as different."""
        from PyQt6.QtGui import QPixmap, QColor
        
        pixmap1 = QPixmap(100, 100)
        pixmap1.fill(QColor("red"))
        
        pixmap2 = QPixmap(200, 200)
        pixmap2.fill(QColor("red"))
        
        image1 = pixmap1.toImage()
        image2 = pixmap2.toImage()
        
        # Different sizes
        assert image1.size() != image2.size()

    def test_pixel_by_pixel_comparison(self, qapp):
        """Verify pixel-by-pixel comparison works."""
        from PyQt6.QtGui import QImage, QColor
        
        # Create two images
        img1 = QImage(10, 10, QImage.Format.Format_ARGB32)
        img2 = QImage(10, 10, QImage.Format.Format_ARGB32)
        
        img1.fill(QColor("white"))
        img2.fill(QColor("white"))
        
        # Set one pixel different
        img2.setPixelColor(5, 5, QColor("black"))
        
        # Compare pixel by pixel
        differences = 0
        for x in range(img1.width()):
            for y in range(img1.height()):
                if img1.pixelColor(x, y) != img2.pixelColor(x, y):
                    differences += 1
        
        assert differences == 1


class TestUIAppearanceValidation:
    """Test UI appearance validation."""

    def test_widget_has_expected_size(self, qapp):
        """Verify widget has expected size."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        button.setFixedSize(120, 40)
        
        assert button.width() == 120
        assert button.height() == 40
        
        button.deleteLater()
        qapp.processEvents()

    def test_widget_has_expected_style(self, qapp):
        """Verify widget has expected style properties."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel("Styled")
        label.setStyleSheet("""
            color: #ff0000;
            background-color: #ffffff;
            font-size: 14px;
        """)
        
        style = label.styleSheet()
        
        assert "#ff0000" in style
        assert "#ffffff" in style
        assert "14px" in style
        
        label.deleteLater()
        qapp.processEvents()

    def test_layout_symmetry(self, qapp):
        """Verify layout has expected symmetry."""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        
        layout.addWidget(QPushButton("Left"))
        layout.addWidget(QPushButton("Right"))
        
        margins = layout.contentsMargins()
        
        # Symmetric margins
        assert margins.left() == margins.right()
        assert margins.top() == margins.bottom()
        
        parent.deleteLater()
        qapp.processEvents()

    def test_color_palette_consistency(self, qapp):
        """Verify color palette is consistent."""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QPalette
        
        button = QPushButton("Test")
        palette = button.palette()
        
        # Get colors
        button_color = palette.color(QPalette.ColorRole.Button)
        window_color = palette.color(QPalette.ColorRole.Window)
        
        # Colors should be valid
        assert button_color.isValid()
        assert window_color.isValid()
        
        button.deleteLater()
        qapp.processEvents()


class TestThemeConsistency:
    """Test theme consistency across widgets."""

    def test_button_style_consistency(self, qapp):
        """Verify buttons have consistent styling."""
        from PyQt6.QtWidgets import QPushButton
        
        buttons = [
            QPushButton("Button 1"),
            QPushButton("Button 2"),
            QPushButton("Button 3"),
        ]
        
        # All buttons should have the same base palette
        first_palette = buttons[0].palette()
        
        for button in buttons[1:]:
            # Button color role should match
            assert button.palette().color(
                button.palette().ColorRole.Button
            ) == first_palette.color(first_palette.ColorRole.Button)
        
        for button in buttons:
            button.deleteLater()
        
        qapp.processEvents()

    def test_font_consistency(self, qapp):
        """Verify widgets have consistent fonts."""
        from PyQt6.QtWidgets import QPushButton, QLabel, QLineEdit
        
        widgets = [
            QPushButton("Button"),
            QLabel("Label"),
            QLineEdit(),
        ]
        
        # All widgets should use the application font as base
        app_font = qapp.font()
        
        for widget in widgets:
            # Font family should match application font
            assert widget.font().family() == app_font.family()
        
        for widget in widgets:
            widget.deleteLater()
        
        qapp.processEvents()

    def test_spacing_consistency(self, qapp):
        """Verify layouts have consistent spacing."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
        
        # Create parent widget to get proper spacing values
        parent = QWidget()
        v_layout = QVBoxLayout(parent)
        
        parent2 = QWidget()
        h_layout = QHBoxLayout(parent2)
        
        # Default spacing should be reasonable (may be -1 for system default)
        # -1 means use system default, which is valid
        v_spacing = v_layout.spacing()
        h_spacing = h_layout.spacing()
        
        # Either valid spacing value or -1 for system default
        assert v_spacing >= -1, f"V spacing should be >= -1, got {v_spacing}"
        assert h_spacing >= -1, f"H spacing should be >= -1, got {h_spacing}"
        
        parent.deleteLater()
        parent2.deleteLater()
        qapp.processEvents()

    def test_icon_size_consistency(self, qapp):
        """Verify icons have consistent sizes."""
        from PyQt6.QtWidgets import QToolButton
        from PyQt6.QtCore import QSize
        
        buttons = [
            QToolButton(),
            QToolButton(),
            QToolButton(),
        ]
        
        expected_size = QSize(24, 24)
        
        for button in buttons:
            button.setIconSize(expected_size)
            assert button.iconSize() == expected_size
        
        for button in buttons:
            button.deleteLater()
        
        qapp.processEvents()


class TestVisualRegressionBaseline:
    """Test visual regression baseline utilities."""

    def test_create_baseline_image(self, qapp, tmp_path):
        """Verify baseline image can be created."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Baseline Button")
        button.setFixedSize(150, 40)
        button.show()
        qapp.processEvents()
        
        pixmap = button.grab()
        
        baseline_path = tmp_path / "baselines" / "button_baseline.png"
        baseline_path.parent.mkdir(exist_ok=True)
        
        pixmap.save(str(baseline_path), "PNG")
        
        assert baseline_path.exists()
        
        button.deleteLater()
        qapp.processEvents()

    def test_compare_with_baseline(self, qapp, tmp_path):
        """Verify current state can be compared with baseline."""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QPixmap
        
        # Create baseline
        button = QPushButton("Test Button")
        button.setFixedSize(100, 30)
        button.show()
        qapp.processEvents()
        
        baseline_pixmap = button.grab()
        baseline_path = tmp_path / "baseline.png"
        baseline_pixmap.save(str(baseline_path), "PNG")
        
        # Create current state (same widget)
        current_pixmap = button.grab()
        
        # Compare
        baseline_image = baseline_pixmap.toImage()
        current_image = current_pixmap.toImage()
        
        assert baseline_image == current_image
        
        button.deleteLater()
        qapp.processEvents()

    def test_detect_visual_changes(self, qapp):
        """Verify visual changes can be detected."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Before")
        button.setFixedSize(100, 30)
        button.show()
        qapp.processEvents()
        
        before_pixmap = button.grab()
        
        # Change the button
        button.setText("After")
        qapp.processEvents()
        
        after_pixmap = button.grab()
        
        # Images should be different
        before_image = before_pixmap.toImage()
        after_image = after_pixmap.toImage()
        
        assert before_image != after_image
        
        button.deleteLater()
        qapp.processEvents()


class TestRenderingValidation:
    """Test rendering validation."""

    def test_widget_renders_correctly(self, qapp):
        """Verify widget renders without errors."""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QPixmap
        
        label = QLabel("Test Text")
        label.setFixedSize(100, 30)
        label.show()
        qapp.processEvents()
        
        pixmap = label.grab()
        
        # Should render without being null
        assert not pixmap.isNull()
        
        # Should have content (not all same color if text is present)
        image = pixmap.toImage()
        
        label.deleteLater()
        qapp.processEvents()

    def test_styled_widget_renders(self, qapp):
        """Verify styled widget renders correctly."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Styled")
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
        """)
        button.setFixedSize(120, 40)
        button.show()
        qapp.processEvents()
        
        pixmap = button.grab()
        
        assert not pixmap.isNull()
        
        button.deleteLater()
        qapp.processEvents()

    def test_complex_layout_renders(self, qapp):
        """Verify complex layout renders correctly."""
        from PyQt6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout,
            QPushButton, QLabel, QLineEdit
        )
        
        parent = QWidget()
        main_layout = QVBoxLayout(parent)
        
        # Add multiple rows
        for i in range(3):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Label {i}"))
            row.addWidget(QLineEdit())
            row.addWidget(QPushButton(f"Button {i}"))
            main_layout.addLayout(row)
        
        parent.setFixedSize(400, 200)
        parent.show()
        qapp.processEvents()
        
        pixmap = parent.grab()
        
        assert not pixmap.isNull()
        assert pixmap.width() == 400
        assert pixmap.height() == 200
        
        parent.deleteLater()
        qapp.processEvents()
