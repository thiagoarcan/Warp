"""
AutoSave Status Indicator Widget

Status bar widget showing auto-save status and progress.

Features:
- Shows last save time
- Shows next save countdown
- Visual indicator during save operation
- Color-coded status (saved/unsaved/saving/error)
- Click to trigger manual save
- Tooltip with detailed information
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMessageBox, QWidget

from platform_base.core.auto_save import AutoSaveManager, AutoSaveStatus, get_auto_save_manager
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    pass


logger = get_logger(__name__)


class AutoSaveIndicator(QLabel):
    """
    Auto-save status indicator for status bar.
    
    Shows current auto-save status with last/next save times.
    Click to trigger manual save.
    """
    
    # Signals
    manual_save_requested = pyqtSignal()
    
    # Status icons (using unicode symbols)
    ICONS = {
        'saved': '✓',           # Checkmark
        'unsaved': '●',         # Dot
        'saving': '⟳',          # Circular arrow
        'error': '✗',           # X mark
        'disabled': '○',        # Empty circle
    }
    
    # Colors
    COLORS = {
        'saved': '#2ecc71',      # Green
        'unsaved': '#f39c12',    # Orange
        'saving': '#3498db',     # Blue
        'error': '#e74c3c',      # Red
        'disabled': '#95a5a6',   # Gray
    }
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        self._auto_save_manager = get_auto_save_manager()
        self._last_status: AutoSaveStatus | None = None
        
        # Setup UI
        self.setStyleSheet("""
            QLabel {
                padding: 2px 8px;
                font-size: 11px;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to save now")
        
        # Initial update
        self._update_display()
        
        # Setup periodic updates
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_display)
        self._update_timer.start(1000)  # Update every second
        
        # Register callback with auto-save manager
        self._auto_save_manager.set_status_callback(self._on_status_changed)
    
    def _update_display(self) -> None:
        """Update the display with current auto-save status."""
        status = self._auto_save_manager.status
        self._update_from_status(status)
    
    def _on_status_changed(self, status: AutoSaveStatus) -> None:
        """Callback for status updates."""
        self._update_from_status(status)
    
    def _update_from_status(self, status: AutoSaveStatus) -> None:
        """Update display from AutoSaveStatus."""
        self._last_status = status
        
        # Determine current state
        if not self._auto_save_manager.is_enabled:
            state = 'disabled'
            text = f"{self.ICONS['disabled']} Auto-save disabled"
        
        elif status.is_saving:
            state = 'saving'
            text = f"{self.ICONS['saving']} Saving..."
        
        elif status.last_error:
            state = 'error'
            text = f"{self.ICONS['error']} Save failed"
        
        elif status.unsaved_changes:
            state = 'unsaved'
            if status.next_save:
                seconds_until = (status.next_save - datetime.now()).total_seconds()
                if seconds_until > 0:
                    text = f"{self.ICONS['unsaved']} Save in {int(seconds_until)}s"
                else:
                    text = f"{self.ICONS['unsaved']} Saving soon..."
            else:
                text = f"{self.ICONS['unsaved']} Unsaved changes"
        
        else:
            state = 'saved'
            if status.last_save:
                elapsed = (datetime.now() - status.last_save).total_seconds()
                if elapsed < 60:
                    text = f"{self.ICONS['saved']} Saved just now"
                elif elapsed < 3600:
                    text = f"{self.ICONS['saved']} Saved {int(elapsed / 60)}m ago"
                else:
                    text = f"{self.ICONS['saved']} Saved {int(elapsed / 3600)}h ago"
            else:
                text = f"{self.ICONS['saved']} No changes"
        
        self.setText(text)
        
        # Update color
        color = self.COLORS[state]
        self.setStyleSheet(f"""
            QLabel {{
                padding: 2px 8px;
                font-size: 11px;
                color: {color};
            }}
        """)
        
        # Update tooltip
        tooltip = self._build_tooltip(status)
        self.setToolTip(tooltip)
    
    def _build_tooltip(self, status: AutoSaveStatus) -> str:
        """Build detailed tooltip."""
        lines = ["<b>Auto-Save Status</b>", ""]
        
        if not self._auto_save_manager.is_enabled:
            lines.append("Auto-save is disabled")
            lines.append("")
            lines.append("<i>Click to save manually</i>")
            return "<br>".join(lines)
        
        # Last save
        if status.last_save:
            last_save_str = status.last_save.strftime("%H:%M:%S")
            lines.append(f"Last save: {last_save_str}")
        else:
            lines.append("Last save: Never")
        
        # Next save
        if status.next_save and not status.is_saving:
            seconds_until = (status.next_save - datetime.now()).total_seconds()
            if seconds_until > 0:
                next_save_str = status.next_save.strftime("%H:%M:%S")
                lines.append(f"Next save: {next_save_str} ({int(seconds_until)}s)")
            else:
                lines.append("Next save: Soon...")
        
        # Status
        if status.is_saving:
            lines.append("")
            lines.append("Status: <b>Saving...</b>")
        elif status.unsaved_changes:
            lines.append("")
            lines.append("Status: <b>Unsaved changes</b>")
        else:
            lines.append("")
            lines.append("Status: All changes saved")
        
        # Error
        if status.last_error:
            lines.append("")
            lines.append(f"<font color='red'>Error: {status.last_error}</font>")
        
        lines.append("")
        lines.append("<i>Click to save now</i>")
        
        return "<br>".join(lines)
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse click to trigger manual save."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.manual_save_requested.emit()
            self._trigger_manual_save()
        super().mousePressEvent(event)
    
    def _trigger_manual_save(self) -> None:
        """Trigger manual save."""
        try:
            result = self._auto_save_manager.save_backup(
                description="Manual save",
                force=True,
            )
            
            if result:
                logger.info("Manual save successful")
                # Show brief confirmation (optional)
                # Could add a temporary "Saved!" message
            else:
                logger.warning("Manual save failed: no callback configured")
                
        except Exception as e:
            logger.error(f"Manual save failed: {e}")
            self._show_error_dialog(str(e))
    
    def _show_error_dialog(self, error: str) -> None:
        """Show error dialog."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Save Failed")
        msg.setText("<b>Failed to save</b>")
        msg.setInformativeText(f"Error: {error}")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def closeEvent(self, event) -> None:
        """Cleanup on close."""
        self._update_timer.stop()
        # Note: We don't clear the callback as manager is singleton
        # and may be used elsewhere
        super().closeEvent(event)
