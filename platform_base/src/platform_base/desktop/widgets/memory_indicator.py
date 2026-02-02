"""
Memory Indicator Widget

Status bar widget showing real-time memory usage with color-coded levels.

Features:
- Real-time memory display (MB used / MB total)
- Color-coded levels (green, yellow, red)
- Tooltip with detailed information and suggestions
- Click to show detailed memory dialog
- Integration with MemoryManager
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMessageBox, QWidget

from platform_base.core.memory_manager import (
    MemoryLevel,
    MemoryManager,
    MemoryStatus,
    get_memory_manager,
)
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    pass


logger = get_logger(__name__)


class MemoryIndicator(QLabel):
    """
    Memory usage indicator for status bar.
    
    Displays current memory usage with color-coded warning levels.
    Click to show detailed information.
    """

    # Signals
    memory_critical = pyqtSignal()  # Emitted when memory reaches critical level

    # Colors for different levels
    COLORS = {
        MemoryLevel.NORMAL: "#2ecc71",      # Green
        MemoryLevel.WARNING: "#f39c12",     # Orange
        MemoryLevel.HIGH: "#e67e22",        # Dark orange
        MemoryLevel.CRITICAL: "#e74c3c",    # Red
    }

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._memory_manager = get_memory_manager()
        self._last_level = MemoryLevel.NORMAL

        # Setup UI
        self.setStyleSheet("""
            QLabel {
                padding: 2px 8px;
                border-radius: 3px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click for memory details")

        # Initial update
        self._update_display()

        # Setup periodic updates
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_display)
        self._update_timer.start(2000)  # Update every 2 seconds

        # Register callback with memory manager
        self._memory_manager.add_status_callback(self._on_memory_status)

    def _update_display(self) -> None:
        """Update the display with current memory info."""
        status = self._memory_manager.get_status()
        self._update_from_status(status)

    def _on_memory_status(self, status: MemoryStatus) -> None:
        """Callback for memory status updates."""
        self._update_from_status(status)

    def _update_from_status(self, status: MemoryStatus) -> None:
        """Update display from MemoryStatus."""
        # Format text
        text = f"RAM: {status.process_mb:.0f}/{status.total_mb:.0f} MB ({status.percent:.0f}%)"
        self.setText(text)

        # Update color based on level
        color = self.COLORS.get(status.level, self.COLORS[MemoryLevel.NORMAL])
        self.setStyleSheet(f"""
            QLabel {{
                padding: 2px 8px;
                border-radius: 3px;
                font-family: monospace;
                font-size: 11px;
                background-color: {color};
                color: white;
            }}
        """)

        # Update tooltip with suggestions
        tooltip = self._build_tooltip(status)
        self.setToolTip(tooltip)

        # Check for level changes
        if status.level != self._last_level:
            self._on_level_changed(status)
            self._last_level = status.level

    def _build_tooltip(self, status: MemoryStatus) -> str:
        """Build detailed tooltip."""
        lines = [
            f"<b>Memory Status: {status.level.name}</b>",
            "",
            f"Process: {status.process_mb:.1f} MB",
            f"System Total: {status.total_mb:.1f} MB",
            f"Available: {status.available_mb:.1f} MB",
            f"Usage: {status.percent:.1f}%",
        ]

        if status.suggestions:
            lines.append("")
            lines.append("<b>Suggestions:</b>")
            for suggestion in status.suggestions:
                lines.append(f"• {suggestion}")

        lines.append("")
        lines.append("<i>Click for detailed information</i>")

        return "<br>".join(lines)

    def _on_level_changed(self, status: MemoryStatus) -> None:
        """Handle memory level changes."""
        if status.level == MemoryLevel.CRITICAL:
            self.memory_critical.emit()
            self._show_critical_warning(status)

        elif status.level == MemoryLevel.HIGH:
            self._show_high_warning(status)

    def _show_critical_warning(self, status: MemoryStatus) -> None:
        """Show critical memory warning dialog."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Critical Memory Usage")
        msg.setText(f"<b>Memory usage is critical ({status.percent:.0f}%)</b>")

        details = [
            f"Available: {status.available_mb:.0f} MB",
            "",
            "Recommended actions:",
        ]
        details.extend(f"• {s}" for s in status.suggestions)

        msg.setDetailedText("\n".join(details))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _show_high_warning(self, status: MemoryStatus) -> None:
        """Show high memory warning (less intrusive)."""
        logger.warning(
            "High memory usage",
            extra={
                'percent': status.percent,
                'available_mb': status.available_mb,
                'suggestions': status.suggestions,
            }
        )

    def mousePressEvent(self, event) -> None:
        """Handle mouse click to show details."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._show_details_dialog()
        super().mousePressEvent(event)

    def _show_details_dialog(self) -> None:
        """Show detailed memory information dialog."""
        status = self._memory_manager.get_status()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Memory Information")
        msg.setText(f"<b>Memory Status: {status.level.name}</b>")

        details = [
            f"Process Memory: {status.process_mb:.1f} MB",
            f"System Total: {status.total_mb:.1f} MB",
            f"Available: {status.available_mb:.1f} MB",
            f"Usage: {status.percent:.1f}%",
            "",
            f"Low Memory Mode: {'Enabled' if self._memory_manager.is_low_memory_mode() else 'Disabled'}",
        ]

        if status.suggestions:
            details.append("")
            details.append("Suggestions:")
            details.extend(f"  • {s}" for s in status.suggestions)

        msg.setDetailedText("\n".join(details))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event) -> None:
        """Cleanup on close."""
        self._update_timer.stop()
        self._memory_manager.remove_status_callback(self._on_memory_status)
        super().closeEvent(event)
