"""
SignalHub - Central signal dispatcher for Platform Base v2.0

Implements centralized signal communication pattern to replace Dash callbacks.
This provides decoupled communication between UI components.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QObject, pyqtSignal

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from platform_base.core.models import DatasetID, SeriesID


logger = get_logger(__name__)


class SignalHub(QObject):
    """
    Central signal dispatcher for cross-component communication.

    Replaces Dash callback pattern with PyQt6 signals/slots.
    All components connect to this hub instead of directly to each other.
    """

    # Dataset management signals
    dataset_loaded = pyqtSignal(str)  # dataset_id
    dataset_removed = pyqtSignal(str)  # dataset_id
    dataset_selected = pyqtSignal(str)  # dataset_id

    # Series management signals
    series_added = pyqtSignal(str, str)  # dataset_id, series_id
    series_removed = pyqtSignal(str, str)  # dataset_id, series_id
    series_selected = pyqtSignal(str, str)  # dataset_id, series_id
    series_deselected = pyqtSignal(str, str)  # dataset_id, series_id

    # Visualization signals
    plot_created = pyqtSignal(str)  # view_id
    plot_updated = pyqtSignal(str)  # view_id
    plot_closed = pyqtSignal(str)  # view_id
    view_synchronized = pyqtSignal(list)  # list of view_ids

    # Selection signals
    time_selection_changed = pyqtSignal(float, float)  # start_time, end_time
    value_selection_changed = pyqtSignal(str, object)  # series_id, selection_data
    selection_cleared = pyqtSignal()

    # Processing signals
    operation_started = pyqtSignal(str, str)  # operation_type, operation_id
    operation_progress = pyqtSignal(str, int)  # operation_id, progress_percent
    operation_completed = pyqtSignal(str, object)  # operation_id, result
    operation_failed = pyqtSignal(str, str)  # operation_id, error_message
    operation_cancelled = pyqtSignal()  # Request to cancel current operation

    # Streaming signals
    streaming_started = pyqtSignal()
    streaming_stopped = pyqtSignal()
    streaming_paused = pyqtSignal()
    streaming_time_changed = pyqtSignal(float)  # current_time

    # UI state signals
    ui_mode_changed = pyqtSignal(str)  # mode: "explore", "stream", "analyze"
    theme_changed = pyqtSignal(str)  # theme: "light", "dark", "auto"
    layout_changed = pyqtSignal(str)  # layout configuration

    # Error/status signals
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    status_updated = pyqtSignal(str)  # status_message
    progress_updated = pyqtSignal(int)  # progress_percent

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._signal_counts = {}
        logger.info("signal_hub_initialized")

    def emit_dataset_loaded(self, dataset_id: DatasetID):
        """Emit dataset loaded signal"""
        self.dataset_loaded.emit(dataset_id)
        self._log_signal_emission("dataset_loaded", dataset_id=dataset_id)

    def emit_series_selected(self, dataset_id: DatasetID, series_id: SeriesID):
        """Emit series selected signal"""
        self.series_selected.emit(dataset_id, series_id)
        self._log_signal_emission("series_selected",
                                dataset_id=dataset_id, series_id=series_id)

    def emit_time_selection(self, start_time: float, end_time: float):
        """Emit time selection changed signal"""
        self.time_selection_changed.emit(start_time, end_time)
        self._log_signal_emission("time_selection_changed",
                                start_time=start_time, end_time=end_time)

    def emit_operation_started(self, operation_type: str, operation_id: str):
        """Emit operation started signal"""
        self.operation_started.emit(operation_type, operation_id)
        self._log_signal_emission("operation_started",
                                operation_type=operation_type, operation_id=operation_id)

    def emit_operation_progress(self, operation_id: str, progress: int):
        """Emit operation progress signal"""
        self.operation_progress.emit(operation_id, progress)
        # Don't log progress signals to avoid spam

    def emit_operation_completed(self, operation_id: str, result: Any):
        """Emit operation completed signal"""
        self.operation_completed.emit(operation_id, result)
        self._log_signal_emission("operation_completed", operation_id=operation_id)

    def emit_error(self, error_type: str, error_message: str):
        """Emit error signal"""
        self.error_occurred.emit(error_type, error_message)
        self._log_signal_emission("error_occurred",
                                error_type=error_type, error_message=error_message)

    def emit_status_update(self, message: str):
        """Emit status update signal"""
        self.status_updated.emit(message)
        # Don't log status updates to avoid spam

    def _log_signal_emission(self, signal_name: str, **kwargs):
        """Log signal emission for debugging"""
        self._signal_counts[signal_name] = self._signal_counts.get(signal_name, 0) + 1
        logger.debug("signal_emitted",
                    signal=signal_name,
                    count=self._signal_counts[signal_name],
                    **kwargs)

    def get_signal_stats(self) -> dict[str, int]:
        """Get statistics about signal emissions"""
        return self._signal_counts.copy()
