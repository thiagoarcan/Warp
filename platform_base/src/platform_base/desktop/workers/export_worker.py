"""
ExportWorker - Data export worker for Platform Base v2.0

Handles data export operations in background threads.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from platform_base.desktop.workers.base_worker import BaseWorker
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class DataExportWorker(BaseWorker):
    """Worker for exporting dataset/series data"""

    def __init__(self, dataset_store, dataset_id: str, series_ids: list[str] | None,
                 output_path: str, format_type: str, export_config: dict[str, Any]):
        super().__init__()
        self.dataset_store = dataset_store
        self.dataset_id = dataset_id
        self.series_ids = series_ids
        self.output_path = output_path
        self.format_type = format_type
        self.export_config = export_config

    def run(self):
        """Execute data export operation"""
        try:
            self.emit_progress(0, "Preparing data for export...")

            # Get dataset
            dataset = self.dataset_store.get_dataset(self.dataset_id)

            self.emit_progress(20, "Collecting series data...")

            # Determine which series to export
            if self.series_ids:
                selected_series = {sid: dataset.series[sid] for sid in self.series_ids if sid in dataset.series}
            else:
                selected_series = dataset.series

            # Create DataFrame for export
            export_data = {"timestamp": dataset.t_datetime}

            for series in selected_series.values():
                export_data[series.name] = series.values

            df = pd.DataFrame(export_data)

            self.emit_progress(60, f"Exporting to {self.format_type} format...")

            # Export based on format
            output_path = Path(self.output_path)

            if self.format_type == "csv":
                df.to_csv(output_path, index=False,
                         sep=self.export_config.get("delimiter", ","),
                         encoding=self.export_config.get("encoding", "utf-8"))

            elif self.format_type == "xlsx":
                with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Data", index=False)

                    # Add metadata sheet if requested
                    if self.export_config.get("include_metadata", False):
                        metadata_df = self._create_metadata_df(dataset, selected_series)
                        metadata_df.to_excel(writer, sheet_name="Metadata", index=False)

            elif self.format_type == "parquet":
                df.to_parquet(output_path, index=False)

            elif self.format_type == "hdf5":
                df.to_hdf(output_path, key="data", mode="w", index=False)

            else:
                raise ValueError(f"Unsupported export format: {self.format_type}")

            if self.is_cancelled:
                return

            self.emit_progress(100, "Export completed successfully")

            # Emit completion
            self.finished.emit()
            logger.info("data_export_completed",
                       output_path=str(output_path), format=self.format_type)

        except Exception as e:
            self.emit_error(f"Export failed: {e!s}")

    def _create_metadata_df(self, dataset, selected_series) -> pd.DataFrame:
        """Create metadata DataFrame for export"""
        metadata_rows = []

        # Dataset metadata
        metadata_rows.append({
            "Type": "Dataset",
            "Name": dataset.dataset_id,
            "Source": dataset.source.filename,
            "Format": dataset.source.format,
            "Size_MB": dataset.source.size_bytes / 1024 / 1024,
            "Created": dataset.source.loaded_at,
            "Points": len(dataset.t_seconds),
            "Duration_s": dataset.t_seconds[-1] - dataset.t_seconds[0],
        })

        # Series metadata
        for series in selected_series.values():
            metadata_rows.append({
                "Type": "Series",
                "Name": series.name,
                "Original_Name": series.metadata.original_name,
                "Unit": str(series.unit),
                "Points": len(series.values),
                "Valid_Points": (~pd.isna(series.values)).sum(),
                "Min_Value": pd.Series(series.values).min(),
                "Max_Value": pd.Series(series.values).max(),
                "Mean_Value": pd.Series(series.values).mean(),
                "Is_Derived": series.lineage is not None,
            })

        return pd.DataFrame(metadata_rows)


class SessionExportWorker(BaseWorker):
    """Worker for exporting session data"""

    def __init__(self, session_state, output_path: str, export_config: dict[str, Any]):
        super().__init__()
        self.session_state = session_state
        self.output_path = output_path
        self.export_config = export_config

    def run(self):
        """Execute session export operation"""
        try:
            self.emit_progress(0, "Preparing session data...")

            # Save current session
            success = self.session_state.save_session(self.output_path)

            if not success:
                raise RuntimeError("Failed to save session")

            if self.is_cancelled:
                return

            self.emit_progress(100, "Session export completed")

            # Emit completion
            self.finished.emit()
            logger.info("session_export_completed", output_path=self.output_path)

        except Exception as e:
            self.emit_error(f"Session export failed: {e!s}")


class PlotExportWorker(BaseWorker):
    """Worker for exporting plot images"""

    def __init__(self, plot_widget, output_path: str, format_type: str,
                 export_config: dict[str, Any]):
        super().__init__()
        self.plot_widget = plot_widget
        self.output_path = output_path
        self.format_type = format_type
        self.export_config = export_config

    def run(self):
        """Execute plot export operation"""
        try:
            self.emit_progress(0, "Preparing plot for export...")

            # Get export parameters
            width = self.export_config.get("width", 1920)
            height = self.export_config.get("height", 1080)
            self.export_config.get("dpi", 300)

            self.emit_progress(50, f"Rendering plot as {self.format_type}...")

            # Export based on plot type
            if hasattr(self.plot_widget, "export"):
                # pyqtgraph PlotWidget
                self.plot_widget.export(self.output_path, width=width, height=height)

            elif hasattr(self.plot_widget, "plotter"):
                # PyVista plot
                self.plot_widget.plotter.screenshot(
                    self.output_path,
                    window_size=[width, height],
                    return_img=False,
                )

            else:
                raise ValueError(f"Unsupported plot widget type: {type(self.plot_widget)}")

            if self.is_cancelled:
                return

            self.emit_progress(100, "Plot export completed")

            # Emit completion
            self.finished.emit()
            logger.info("plot_export_completed",
                       output_path=self.output_path, format=self.format_type)

        except Exception as e:
            self.emit_error(f"Plot export failed: {e!s}")


class VideoExportWorker(BaseWorker):
    """Worker for exporting streaming animations as video"""

    def __init__(self, dataset_store, dataset_id: str, series_ids: list[str],
                 output_path: str, video_config: dict[str, Any]):
        super().__init__()
        self.dataset_store = dataset_store
        self.dataset_id = dataset_id
        self.series_ids = series_ids
        self.output_path = output_path
        self.video_config = video_config

    def run(self):
        """Execute video export operation"""
        try:
            # Check if video export dependencies are available
            try:
                import cv2
                import matplotlib.pyplot as plt
                from matplotlib.animation import FFMpegWriter
            except ImportError as e:
                self.emit_error(f"Video export requires additional packages: {e}")
                return

            self.emit_progress(0, "Preparing video export...")

            # Get dataset and series
            dataset = self.dataset_store.get_dataset(self.dataset_id)
            selected_series = {sid: dataset.series[sid] for sid in self.series_ids if sid in dataset.series}

            # Video parameters
            fps = self.video_config.get("fps", 30)
            duration = self.video_config.get("duration", 10)  # seconds
            width = self.video_config.get("width", 1920)
            height = self.video_config.get("height", 1080)

            # Calculate frame parameters
            n_frames = int(fps * duration)
            time_step = (dataset.t_seconds[-1] - dataset.t_seconds[0]) / n_frames

            self.emit_progress(20, "Setting up video writer...")

            # Setup matplotlib figure
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)

            # Setup video writer
            writer = FFMpegWriter(fps=fps, bitrate=self.video_config.get("bitrate", 2000))

            with writer.saving(fig, self.output_path, dpi=100):
                for frame in range(n_frames):
                    if self.is_cancelled:
                        break

                    # Calculate time window for this frame
                    current_time = dataset.t_seconds[0] + frame * time_step
                    window_size = self.video_config.get("window_size", 60)  # seconds

                    time_mask = (dataset.t_seconds >= current_time - window_size/2) & \
                               (dataset.t_seconds <= current_time + window_size/2)

                    # Clear and plot
                    ax.clear()

                    for series in selected_series.values():
                        ax.plot(dataset.t_seconds[time_mask], series.values[time_mask],
                               label=series.name, linewidth=2)

                    # Add current time indicator
                    ax.axvline(current_time, color="red", linestyle="--", alpha=0.7)

                    # Formatting
                    ax.set_xlabel("Time (s)")
                    ax.set_ylabel("Value")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"Time Series Animation - t = {current_time:.2f}s")

                    # Write frame
                    writer.grab_frame()

                    # Update progress
                    progress = 20 + int(75 * frame / n_frames)
                    self.emit_progress(progress, f"Rendering frame {frame+1}/{n_frames}")

            plt.close(fig)

            if not self.is_cancelled:
                self.emit_progress(100, "Video export completed")
                self.finished.emit()
                logger.info("video_export_completed",
                           output_path=self.output_path, frames=n_frames)

        except Exception as e:
            self.emit_error(f"Video export failed: {e!s}")


class ExportWorkerManager:
    """Manager for export workers"""

    def __init__(self, dataset_store, session_state, signal_hub):
        self.dataset_store = dataset_store
        self.session_state = session_state
        self.signal_hub = signal_hub
        self.active_workers: dict[str, BaseWorker] = {}

    def start_data_export(self, operation_id: str, dataset_id: str,
                         series_ids: list[str] | None, output_path: str,
                         format_type: str, export_config: dict[str, Any]):
        """Start data export worker"""
        worker = DataExportWorker(self.dataset_store, dataset_id, series_ids,
                                output_path, format_type, export_config)
        self._start_worker(operation_id, worker)

    def start_session_export(self, operation_id: str, output_path: str,
                           export_config: dict[str, Any]):
        """Start session export worker"""
        worker = SessionExportWorker(self.session_state, output_path, export_config)
        self._start_worker(operation_id, worker)

    def start_plot_export(self, operation_id: str, plot_widget, output_path: str,
                         format_type: str, export_config: dict[str, Any]):
        """Start plot export worker"""
        worker = PlotExportWorker(plot_widget, output_path, format_type, export_config)
        self._start_worker(operation_id, worker)

    def start_video_export(self, operation_id: str, dataset_id: str,
                          series_ids: list[str], output_path: str,
                          video_config: dict[str, Any]):
        """Start video export worker"""
        worker = VideoExportWorker(self.dataset_store, dataset_id, series_ids,
                                 output_path, video_config)
        self._start_worker(operation_id, worker)

    def _start_worker(self, operation_id: str, worker: BaseWorker):
        """Start worker and connect signals"""
        # Connect worker signals to signal hub
        worker.progress.connect(
            lambda p: self.signal_hub.emit_operation_progress(operation_id, p))
        worker.error.connect(
            lambda e: self.signal_hub.operation_failed.emit(operation_id, e))
        worker.finished.connect(
            lambda: self._on_worker_finished(operation_id))

        # Start worker
        self.active_workers[operation_id] = worker
        worker.start()

        logger.info("export_worker_started",
                   operation_id=operation_id, worker_type=type(worker).__name__)

    def _on_worker_finished(self, operation_id: str):
        """Handle worker completion"""
        if operation_id in self.active_workers:
            worker = self.active_workers.pop(operation_id)

            # If worker finished successfully, emit completion
            if not worker.is_cancelled:
                self.signal_hub.operation_completed.emit(operation_id, {
                    "operation_id": operation_id,
                    "operation_type": "export",
                    "success": True,
                })

            # Clean up worker
            worker.deleteLater()

            logger.debug("export_worker_finished", operation_id=operation_id)

    def cancel_operation(self, operation_id: str):
        """Cancel running operation"""
        if operation_id in self.active_workers:
            worker = self.active_workers[operation_id]
            worker.cancel()
            logger.info("export_worker_cancelled", operation_id=operation_id)
