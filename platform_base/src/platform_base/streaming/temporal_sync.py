"""
Temporal Synchronization for Streaming - Platform Base v2.0

Basic implementation for synchronized temporal streaming across multiple views.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Any

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from platform_base.utils.logging import get_logger


logger = get_logger(__name__)

@dataclass
class StreamFrame:
    """Represents a single frame of streaming data"""
    timestamp: float
    data: dict[str, Any]
    series_id: str
    frame_number: int

@dataclass
class SyncPoint:
    """Synchronization point for temporal alignment"""
    master_timestamp: float
    slave_offsets: dict[str, float]  # series_id -> offset in seconds

class TemporalSynchronizer(QObject):
    """
    Synchronizes temporal streaming across multiple data series.

    Features:
    - Master/slave synchronization
    - Temporal alignment with interpolation
    - Frame dropping for performance
    - Buffer management
    """

    # Signals for PyQt integration
    frame_ready = pyqtSignal(str, object)  # series_id, frame_data
    sync_status_changed = pyqtSignal(bool)  # is_synchronized
    buffer_status = pyqtSignal(str, int, int)  # series_id, current_size, max_size

    def __init__(self, master_series_id: str, buffer_size: int = 1000):
        super().__init__()

        self.master_series_id = master_series_id
        self.buffer_size = buffer_size

        # Streaming state
        self.is_streaming = False
        self.is_synchronized = False
        self._lock = Lock()

        # Data buffers for each series
        self._buffers: dict[str, list[StreamFrame]] = {}
        self._sync_points: list[SyncPoint] = []

        # Timing control
        self.target_fps = 30.0
        self.frame_interval = 1.0 / self.target_fps

        # PyQt timer for frame emission
        self._timer = QTimer()
        self._timer.timeout.connect(self._emit_synchronized_frames)

        # Performance tracking
        self._frames_emitted = 0
        self._frames_dropped = 0
        self._last_emit_time = 0.0

        logger.info("temporal_synchronizer_initialized",
                   master=master_series_id, buffer_size=buffer_size)

    def add_series(self, series_id: str, time_offset: float = 0.0):
        """Add a series to be synchronized"""
        with self._lock:
            if series_id not in self._buffers:
                self._buffers[series_id] = []
                logger.debug("series_added_to_sync", series_id=series_id, offset=time_offset)

    def remove_series(self, series_id: str):
        """Remove a series from synchronization"""
        with self._lock:
            if series_id in self._buffers:
                del self._buffers[series_id]
                logger.debug("series_removed_from_sync", series_id=series_id)

    def start_streaming(self, fps: float | None = None):
        """Start temporal streaming"""
        if fps:
            self.target_fps = fps
            self.frame_interval = 1.0 / fps

        self.is_streaming = True
        self._timer.start(int(self.frame_interval * 1000))  # Convert to milliseconds

        logger.info("temporal_streaming_started", fps=self.target_fps)

    def stop_streaming(self):
        """Stop temporal streaming"""
        self.is_streaming = False
        self._timer.stop()

        # Clear buffers
        with self._lock:
            for buffer in self._buffers.values():
                buffer.clear()

        logger.info("temporal_streaming_stopped")

    def add_frame(self, series_id: str, timestamp: float, data: Any):
        """Add a new frame to the streaming buffer"""
        if not self.is_streaming:
            return

        # Create frame
        frame = StreamFrame(
            timestamp=timestamp,
            data=data,
            series_id=series_id,
            frame_number=len(self._buffers.get(series_id, [])),
        )

        with self._lock:
            # Add to buffer - create buffer directly if not exists (avoid deadlock)
            if series_id not in self._buffers:
                self._buffers[series_id] = []
                logger.debug("series_added_to_sync", series_id=series_id, offset=0.0)

            buffer = self._buffers[series_id]
            buffer.append(frame)

            # Manage buffer size
            if len(buffer) > self.buffer_size:
                buffer.pop(0)  # Remove oldest frame

            # Emit buffer status
            self.buffer_status.emit(series_id, len(buffer), self.buffer_size)

        logger.debug("frame_added", series_id=series_id, timestamp=timestamp)

    def _emit_synchronized_frames(self):
        """Emit synchronized frames to all connected plots"""
        current_time = time.time()

        # Performance throttling
        if current_time - self._last_emit_time < self.frame_interval:
            return

        with self._lock:
            # Find master frame
            master_frames = self._buffers.get(self.master_series_id, [])
            if not master_frames:
                return

            # Get current master frame (most recent)
            master_frame = master_frames[-1]
            master_timestamp = master_frame.timestamp

            # Collect synchronized frames for all series
            synchronized_frames = {}

            for series_id, buffer in self._buffers.items():
                if not buffer:
                    continue

                # Find frame closest to master timestamp
                closest_frame = self._find_closest_frame(buffer, master_timestamp)
                if closest_frame:
                    synchronized_frames[series_id] = closest_frame

            # Emit frames if we have enough synchronized data
            if len(synchronized_frames) >= 2:  # At least master + 1 slave
                for series_id, frame in synchronized_frames.items():
                    self.frame_ready.emit(series_id, frame.data)

                self._frames_emitted += 1
                self.is_synchronized = True
                self.sync_status_changed.emit(True)
            else:
                self.is_synchronized = False
                self.sync_status_changed.emit(False)

        self._last_emit_time = current_time

        logger.debug("synchronized_frames_emitted",
                    count=len(synchronized_frames),
                    master_time=master_timestamp)

    def _find_closest_frame(self, buffer: list[StreamFrame], target_timestamp: float) -> StreamFrame | None:
        """Find frame closest to target timestamp"""
        if not buffer:
            return None

        # Simple linear search (could be optimized with binary search)
        closest_frame = None
        min_diff = float("inf")

        for frame in buffer:
            diff = abs(frame.timestamp - target_timestamp)
            if diff < min_diff:
                min_diff = diff
                closest_frame = frame

        return closest_frame

    def get_statistics(self) -> dict[str, Any]:
        """Get streaming statistics"""
        with self._lock:
            buffer_stats = {}
            for series_id, buffer in self._buffers.items():
                buffer_stats[series_id] = {
                    "buffer_size": len(buffer),
                    "latest_timestamp": buffer[-1].timestamp if buffer else None,
                }

        return {
            "is_streaming": self.is_streaming,
            "is_synchronized": self.is_synchronized,
            "target_fps": self.target_fps,
            "frames_emitted": self._frames_emitted,
            "frames_dropped": self._frames_dropped,
            "buffer_stats": buffer_stats,
        }

class StreamingPlotManager(QObject):
    """
    Manages streaming visualization for multiple plots
    """

    def __init__(self, synchronizer: TemporalSynchronizer):
        super().__init__()

        self.synchronizer = synchronizer
        self.plot_widgets: dict[str, Any] = {}  # plot_id -> widget

        # Connect to synchronizer signals
        synchronizer.frame_ready.connect(self._on_frame_ready)
        synchronizer.sync_status_changed.connect(self._on_sync_status_changed)

        logger.info("streaming_plot_manager_initialized")

    def add_plot(self, plot_id: str, plot_widget: Any):
        """Add a plot widget for streaming"""
        self.plot_widgets[plot_id] = plot_widget
        logger.debug("plot_added_to_streaming", plot_id=plot_id)

    def remove_plot(self, plot_id: str):
        """Remove a plot widget from streaming"""
        if plot_id in self.plot_widgets:
            del self.plot_widgets[plot_id]
            logger.debug("plot_removed_from_streaming", plot_id=plot_id)

    def _on_frame_ready(self, series_id: str, frame_data: Any):
        """Handle new synchronized frame"""
        # Update all plots that display this series
        for plot_id, plot_widget in self.plot_widgets.items():
            try:
                # Update plot with new data
                if hasattr(plot_widget, "update_streaming_data"):
                    plot_widget.update_streaming_data(series_id, frame_data)

            except Exception as e:
                logger.exception("streaming_plot_update_failed",
                           plot_id=plot_id, series_id=series_id, error=str(e))

    def _on_sync_status_changed(self, is_synchronized: bool):
        """Handle synchronization status change"""
        logger.debug("sync_status_changed", synchronized=is_synchronized)

        # Update UI indicators if needed
        for plot_widget in self.plot_widgets.values():
            if hasattr(plot_widget, "set_sync_status"):
                plot_widget.set_sync_status(is_synchronized)
