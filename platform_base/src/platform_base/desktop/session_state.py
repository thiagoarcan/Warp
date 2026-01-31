"""
SessionState - Centralized state management for Platform Base v2.0

Replaces Dash's client-side storage with centralized Python state management.
Provides signal-based state change notifications.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QObject, pyqtSignal

from platform_base.core.models import DatasetID, SeriesID, TimeWindow, ViewID
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from platform_base.core.dataset_store import DatasetStore


logger = get_logger(__name__)


@dataclass
class SelectionState:
    """Current selection state"""
    dataset_id: DatasetID | None = None
    series_ids: list[SeriesID] = field(default_factory=list)
    time_window: TimeWindow | None = None
    selected_points: dict[SeriesID, list[int]] = field(default_factory=dict)


@dataclass
class ViewState:
    """View configuration state"""
    active_views: dict[ViewID, dict] = field(default_factory=dict)
    synchronized_views: list[ViewID] = field(default_factory=list)
    plot_configs: dict[ViewID, dict] = field(default_factory=dict)


@dataclass
class ProcessingState:
    """Processing operation state"""
    active_operations: dict[str, dict] = field(default_factory=dict)
    operation_history: list[dict] = field(default_factory=list)
    last_results: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingState:
    """Streaming playback state"""
    is_active: bool = False
    is_paused: bool = False
    current_time: float = 0.0
    playback_speed: float = 1.0
    time_window: TimeWindow | None = None
    loop_enabled: bool = False


@dataclass
class UIState:
    """UI configuration state"""
    current_mode: str = "explore"  # explore, stream, analyze
    theme: str = "auto"  # light, dark, auto
    layout_config: dict[str, Any] = field(default_factory=dict)
    panel_visibility: dict[str, bool] = field(default_factory=lambda: {
        "data": True,
        "viz": True,
        "operations": True,
        "results": False,
    })


class SessionState(QObject):
    """
    Centralized session state management.

    Replaces Dash's dcc.Store with centralized Python state.
    Emits signals when state changes to notify UI components.
    """

    # State change signals
    selection_changed = pyqtSignal(object)  # SelectionState
    view_state_changed = pyqtSignal(object)  # ViewState
    processing_state_changed = pyqtSignal(object)  # ProcessingState
    streaming_state_changed = pyqtSignal(object)  # StreamingState
    ui_state_changed = pyqtSignal(object)  # UIState

    # Session signals
    session_loaded = pyqtSignal(str)  # session_path
    session_saved = pyqtSignal(str)  # session_path
    session_cleared = pyqtSignal()

    def __init__(self, dataset_store: DatasetStore, parent: QObject | None = None):
        super().__init__(parent)

        self.dataset_store = dataset_store

        # Initialize state objects
        self.selection = SelectionState()
        self.view = ViewState()
        self.processing = ProcessingState()
        self.streaming = StreamingState()
        self.ui = UIState()

        # Session metadata
        self.session_id = f"session_{datetime.now().isoformat()}"
        self.created_at = datetime.now()
        self.modified_at = datetime.now()

        logger.info("session_state_initialized", session_id=self.session_id)

    # Selection state management
    def set_current_dataset(self, dataset_id: DatasetID | None):
        """Set current dataset selection"""
        if self.selection.dataset_id != dataset_id:
            self.selection.dataset_id = dataset_id
            self.selection.series_ids.clear()  # Clear series selection
            self.selection.selected_points.clear()
            self._update_modified()
            self.selection_changed.emit(self.selection)
            logger.debug("current_dataset_changed", dataset_id=dataset_id)

    def add_series_selection(self, series_id: SeriesID):
        """Add series to selection"""
        if series_id not in self.selection.series_ids:
            self.selection.series_ids.append(series_id)
            self._update_modified()
            self.selection_changed.emit(self.selection)
            logger.debug("series_added_to_selection", series_id=series_id)

    def remove_series_selection(self, series_id: SeriesID):
        """Remove series from selection"""
        if series_id in self.selection.series_ids:
            self.selection.series_ids.remove(series_id)
            self.selection.selected_points.pop(series_id, None)
            self._update_modified()
            self.selection_changed.emit(self.selection)
            logger.debug("series_removed_from_selection", series_id=series_id)

    def set_time_window(self, time_window: TimeWindow | None):
        """Set time selection window"""
        self.selection.time_window = time_window
        self._update_modified()
        self.selection_changed.emit(self.selection)
        logger.debug("time_window_changed",
                    start=time_window.start if time_window else None,
                    end=time_window.end if time_window else None)

    def clear_selection(self):
        """Clear all selections"""
        self.selection = SelectionState()
        self._update_modified()
        self.selection_changed.emit(self.selection)
        logger.debug("selection_cleared")

    # View state management
    def add_view(self, view_id: ViewID, config: dict):
        """Add view configuration"""
        self.view.active_views[view_id] = config
        self._update_modified()
        self.view_state_changed.emit(self.view)
        logger.debug("view_added", view_id=view_id)

    def remove_view(self, view_id: ViewID):
        """Remove view"""
        self.view.active_views.pop(view_id, None)
        self.view.plot_configs.pop(view_id, None)
        if view_id in self.view.synchronized_views:
            self.view.synchronized_views.remove(view_id)
        self._update_modified()
        self.view_state_changed.emit(self.view)
        logger.debug("view_removed", view_id=view_id)

    def set_view_synchronization(self, view_ids: list[ViewID]):
        """Set synchronized views"""
        self.view.synchronized_views = view_ids.copy()
        self._update_modified()
        self.view_state_changed.emit(self.view)
        logger.debug("view_synchronization_changed", view_ids=view_ids)

    # Processing state management
    def start_operation(self, operation_id: str, operation_type: str, params: dict):
        """Start processing operation"""
        self.processing.active_operations[operation_id] = {
            "type": operation_type,
            "params": params,
            "started_at": datetime.now(),
            "progress": 0,
        }
        self._update_modified()
        self.processing_state_changed.emit(self.processing)
        logger.info("operation_started", operation_id=operation_id, type=operation_type)

    def update_operation_progress(self, operation_id: str, progress: int):
        """Update operation progress"""
        if operation_id in self.processing.active_operations:
            self.processing.active_operations[operation_id]["progress"] = progress
            # Don't emit signal for every progress update to avoid spam

    def complete_operation(self, operation_id: str, result: Any):
        """Complete processing operation"""
        if operation_id in self.processing.active_operations:
            op_info = self.processing.active_operations.pop(operation_id)
            op_info["completed_at"] = datetime.now()
            op_info["success"] = True

            self.processing.operation_history.append(op_info)
            self.processing.last_results[operation_id] = result

            self._update_modified()
            self.processing_state_changed.emit(self.processing)
            logger.info("operation_completed", operation_id=operation_id)

    def fail_operation(self, operation_id: str, error: str):
        """Mark operation as failed"""
        if operation_id in self.processing.active_operations:
            op_info = self.processing.active_operations.pop(operation_id)
            op_info["completed_at"] = datetime.now()
            op_info["success"] = False
            op_info["error"] = error

            self.processing.operation_history.append(op_info)

            self._update_modified()
            self.processing_state_changed.emit(self.processing)
            logger.error("operation_failed", operation_id=operation_id, error=error)

    # Streaming state management
    def start_streaming(self, time_window: TimeWindow, speed: float = 1.0):
        """Start streaming playback"""
        self.streaming.is_active = True
        self.streaming.is_paused = False
        self.streaming.current_time = time_window.start
        self.streaming.playback_speed = speed
        self.streaming.time_window = time_window

        self._update_modified()
        self.streaming_state_changed.emit(self.streaming)
        logger.info("streaming_started", start=time_window.start, end=time_window.end)

    def pause_streaming(self):
        """Pause streaming playback"""
        self.streaming.is_paused = True
        self._update_modified()
        self.streaming_state_changed.emit(self.streaming)
        logger.debug("streaming_paused")

    def resume_streaming(self):
        """Resume streaming playback"""
        self.streaming.is_paused = False
        self._update_modified()
        self.streaming_state_changed.emit(self.streaming)
        logger.debug("streaming_resumed")

    def stop_streaming(self):
        """Stop streaming playback"""
        self.streaming.is_active = False
        self.streaming.is_paused = False
        self._update_modified()
        self.streaming_state_changed.emit(self.streaming)
        logger.info("streaming_stopped")

    def update_streaming_time(self, current_time: float):
        """Update current streaming time"""
        self.streaming.current_time = current_time
        # Don't emit signal for every time update to avoid spam

    # UI state management
    def set_ui_mode(self, mode: str):
        """Set UI mode"""
        if mode in ["explore", "stream", "analyze"]:
            self.ui.current_mode = mode
            self._update_modified()
            self.ui_state_changed.emit(self.ui)
            logger.debug("ui_mode_changed", mode=mode)

    def set_theme(self, theme: str):
        """Set UI theme"""
        if theme in ["light", "dark", "auto"]:
            self.ui.theme = theme
            self._update_modified()
            self.ui_state_changed.emit(self.ui)
            logger.debug("theme_changed", theme=theme)

    def set_panel_visibility(self, panel: str, visible: bool):
        """Set panel visibility"""
        if panel in self.ui.panel_visibility:
            self.ui.panel_visibility[panel] = visible
            self._update_modified()
            self.ui_state_changed.emit(self.ui)
            logger.debug("panel_visibility_changed", panel=panel, visible=visible)

    # Session persistence
    def save_session(self, filepath: str) -> bool:
        """Save session to file"""
        try:
            session_data = {
                "session_id": self.session_id,
                "created_at": self.created_at.isoformat(),
                "modified_at": self.modified_at.isoformat(),
                "selection": {
                    "dataset_id": self.selection.dataset_id,
                    "series_ids": self.selection.series_ids,
                    "time_window": {
                        "start": self.selection.time_window.start,
                        "end": self.selection.time_window.end,
                    } if self.selection.time_window else None,
                },
                "ui": {
                    "current_mode": self.ui.current_mode,
                    "theme": self.ui.theme,
                    "panel_visibility": self.ui.panel_visibility,
                },
                "view": {
                    "synchronized_views": self.view.synchronized_views,
                },
            }

            Path(filepath).write_text(json.dumps(session_data, indent=2))
            self.session_saved.emit(filepath)
            logger.info("session_saved", filepath=filepath)
            return True

        except Exception as e:
            logger.exception("session_save_failed", filepath=filepath, error=str(e))
            return False

    def load_session(self, filepath: str) -> bool:
        """Load session from file"""
        try:
            session_data = json.loads(Path(filepath).read_text())

            # Restore selection state
            selection_data = session_data.get("selection", {})
            self.selection.dataset_id = selection_data.get("dataset_id")
            self.selection.series_ids = selection_data.get("series_ids", [])

            time_window_data = selection_data.get("time_window")
            if time_window_data:
                self.selection.time_window = TimeWindow(
                    start=time_window_data["start"],
                    end=time_window_data["end"],
                )

            # Restore UI state
            ui_data = session_data.get("ui", {})
            self.ui.current_mode = ui_data.get("current_mode", "explore")
            self.ui.theme = ui_data.get("theme", "auto")
            self.ui.panel_visibility.update(ui_data.get("panel_visibility", {}))

            # Restore view state
            view_data = session_data.get("view", {})
            self.view.synchronized_views = view_data.get("synchronized_views", [])

            # Update metadata
            self.session_id = session_data.get("session_id", self.session_id)
            self.created_at = datetime.fromisoformat(session_data.get("created_at", self.created_at.isoformat()))
            self.modified_at = datetime.now()

            # Emit all change signals
            self.selection_changed.emit(self.selection)
            self.ui_state_changed.emit(self.ui)
            self.view_state_changed.emit(self.view)

            self.session_loaded.emit(filepath)
            logger.info("session_loaded", filepath=filepath, session_id=self.session_id)
            return True

        except Exception as e:
            logger.exception("session_load_failed", filepath=filepath, error=str(e))
            return False

    def clear_session(self):
        """Clear current session"""
        self.__init__(self.dataset_store, self.parent())
        self.session_cleared.emit()
        logger.info("session_cleared")

    def _update_modified(self):
        """Update modification timestamp"""
        self.modified_at = datetime.now()

    def get_state_summary(self) -> dict:
        """Get summary of current state"""
        return {
            "session_id": self.session_id,
            "current_dataset": self.selection.dataset_id,
            "selected_series_count": len(self.selection.series_ids),
            "active_views": len(self.view.active_views),
            "active_operations": len(self.processing.active_operations),
            "streaming_active": self.streaming.is_active,
            "ui_mode": self.ui.current_mode,
            "theme": self.ui.theme,
        }
