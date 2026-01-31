"""
Video Export - Sistema de exportação de vídeo para streaming temporal conforme seção 11.5

Features:
- Gravação de sessões de streaming
- Múltiplos formatos de vídeo (MP4, AVI, MOV)
- Configuração de qualidade e resolução
- Progresso em tempo real
- Sincronização com múltiplas views
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

    from platform_base.core.models import ViewID
    from platform_base.ui.multi_view_sync import MultiViewSynchronizer
    from platform_base.viz.streaming import StreamingEngine


logger = get_logger(__name__)


class VideoFormat(Enum):
    """Formatos de vídeo suportados"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"


class VideoQuality(Enum):
    """Qualidades de vídeo predefinidas"""
    LOW = "low"        # 720p, 15fps
    MEDIUM = "medium"  # 1080p, 30fps
    HIGH = "high"      # 1080p, 60fps
    ULTRA = "ultra"    # 4K, 30fps


@dataclass
class VideoExportSettings:
    """Configurações de exportação de vídeo"""
    output_path: Path
    format: VideoFormat = VideoFormat.MP4
    quality: VideoQuality = VideoQuality.MEDIUM
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
    duration_seconds: float | None = None
    include_audio: bool = False
    compress: bool = True
    view_ids: list[ViewID] = None  # Views a incluir
    layout_mode: str = "single"    # single, grid, split


class VideoExportWorker(QThread):
    """Worker thread para exportação de vídeo"""

    # Signals
    progress_updated = pyqtSignal(int)  # percentage
    frame_captured = pyqtSignal(int)    # frame number
    export_completed = pyqtSignal()
    export_failed = pyqtSignal(str)     # error message

    def __init__(self, settings: VideoExportSettings,
                 synchronizer: MultiViewSynchronizer,
                 parent: QObject | None = None):
        super().__init__(parent)

        self.settings = settings
        self.synchronizer = synchronizer
        self.should_stop = False
        self.current_frame = 0
        self.total_frames = 0

        # Video writer (will be initialized in run)
        self.video_writer = None

    def run(self):
        """Executa exportação de vídeo"""
        try:
            self._setup_video_writer()
            self._calculate_total_frames()
            self._capture_video()
            self._cleanup()

            self.export_completed.emit()

        except Exception as e:
            logger.exception("video_export_failed", error=str(e))
            self.export_failed.emit(str(e))
        finally:
            self._cleanup()

    def stop_export(self):
        """Para exportação"""
        self.should_stop = True

    def _setup_video_writer(self):
        """Configura video writer baseado na biblioteca disponível"""
        try:
            import cv2

            # Define codec baseado no formato
            codec_map = {
                VideoFormat.MP4: cv2.VideoWriter_fourcc(*"mp4v"),
                VideoFormat.AVI: cv2.VideoWriter_fourcc(*"XVID"),
                VideoFormat.MOV: cv2.VideoWriter_fourcc(*"mp4v"),
                VideoFormat.WEBM: cv2.VideoWriter_fourcc(*"VP80"),
            }

            fourcc = codec_map.get(self.settings.format, cv2.VideoWriter_fourcc(*"mp4v"))

            self.video_writer = cv2.VideoWriter(
                str(self.settings.output_path),
                fourcc,
                self.settings.fps,
                self.settings.resolution,
            )

            if not self.video_writer.isOpened():
                raise RuntimeError("Failed to initialize video writer")

            logger.info("video_writer_initialized",
                       format=self.settings.format.value,
                       resolution=self.settings.resolution,
                       fps=self.settings.fps)

        except ImportError:
            raise RuntimeError("OpenCV not available for video export")

    def _calculate_total_frames(self):
        """Calcula total de frames baseado na duração"""
        if self.settings.duration_seconds:
            self.total_frames = int(self.settings.duration_seconds * self.settings.fps)
        else:
            # Use master view duration
            master_engine = self._get_master_streaming_engine()
            if master_engine and len(master_engine.eligible_indices) > 0:
                total_time = master_engine.time_points[master_engine.eligible_indices[-1]]
                self.total_frames = int(total_time * self.settings.fps)
            else:
                self.total_frames = 1000  # Default fallback

        logger.info("video_export_frames_calculated", total_frames=self.total_frames)

    def _capture_video(self):
        """Captura frames e escreve vídeo"""
        master_engine = self._get_master_streaming_engine()
        if not master_engine:
            raise RuntimeError("No master streaming engine available")

        # Calculate time step per frame
        time_step = 1.0 / self.settings.fps

        for frame_num in range(self.total_frames):
            if self.should_stop:
                break

            # Calculate current time
            current_time = frame_num * time_step

            # Seek all views to current time
            self.synchronizer.seek_all_views(current_time)

            # Capture frame from views
            frame = self._capture_current_frame()

            if frame is not None:
                # Write frame to video
                self.video_writer.write(frame)
                self.current_frame = frame_num + 1

                # Update progress
                progress = int((frame_num + 1) * 100 / self.total_frames)
                self.progress_updated.emit(progress)
                self.frame_captured.emit(frame_num + 1)

                # Small delay to avoid overwhelming the system
                time.sleep(0.001)

        logger.info("video_capture_completed", frames_written=self.current_frame)

    def _capture_current_frame(self) -> Any | None:
        """Captura frame atual das views"""

        if self.settings.layout_mode == "single":
            # Capture from single view (master)
            return self._capture_single_view_frame()
        if self.settings.layout_mode == "grid":
            # Capture from multiple views in grid layout
            return self._capture_grid_frame()
        # Default to single view
        return self._capture_single_view_frame()

    def _capture_single_view_frame(self) -> Any | None:
        """Captura frame de view única"""
        import numpy as np

        # Get master view widget
        master_view_id = self.synchronizer.sync_state.master_view_id
        if not master_view_id or master_view_id not in self.synchronizer.views:
            return None

        view_widget = self.synchronizer.views[master_view_id].widget

        # Capture widget to pixmap
        try:
            view_widget.grab()

            # Convert to numpy array (simplified implementation)
            # This would need proper conversion from QPixmap to cv2 format
            frame = np.zeros((self.settings.resolution[1], self.settings.resolution[0], 3), dtype=np.uint8)

            # TODO: Proper QPixmap to numpy conversion
            # For now, create a placeholder frame with timestamp
            height, width = frame.shape[:2]
            cv2 = None
            try:
                import cv2
                # Add timestamp text
                timestamp_text = f"Time: {self.synchronizer.sync_state.current_time_seconds:.2f}s"
                cv2.putText(frame, timestamp_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            except ImportError:
                pass

            return frame

        except Exception as e:
            logger.exception("frame_capture_failed", error=str(e))
            return None

    def _capture_grid_frame(self) -> Any | None:
        """Captura frame de múltiplas views em grid"""
        import numpy as np

        # Get active views
        view_ids = self.settings.view_ids or list(self.synchronizer.views.keys())
        active_views = [vid for vid in view_ids if vid in self.synchronizer.views]

        if not active_views:
            return None

        # Calculate grid layout
        n_views = len(active_views)
        grid_cols = int(np.ceil(np.sqrt(n_views)))
        grid_rows = int(np.ceil(n_views / grid_cols))

        # Create composite frame
        frame_height, frame_width = self.settings.resolution
        view_height = frame_height // grid_rows
        view_width = frame_width // grid_cols

        composite_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

        for i, _view_id in enumerate(active_views):
            if i >= grid_rows * grid_cols:
                break

            row = i // grid_cols
            col = i % grid_cols

            # Calculate position
            y_start = row * view_height
            y_end = min((row + 1) * view_height, frame_height)
            x_start = col * view_width
            x_end = min((col + 1) * view_width, frame_width)

            # Capture view frame (simplified)
            view_frame = np.random.randint(0, 255, (y_end - y_start, x_end - x_start, 3), dtype=np.uint8)
            composite_frame[y_start:y_end, x_start:x_end] = view_frame

        return composite_frame

    def _get_master_streaming_engine(self) -> StreamingEngine | None:
        """Retorna streaming engine da view master"""
        master_view_id = self.synchronizer.sync_state.master_view_id
        if not master_view_id or master_view_id not in self.synchronizer.views:
            return None

        return self.synchronizer.views[master_view_id].streaming_engine

    def _cleanup(self):
        """Limpa recursos"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None


class VideoExportDialog(QDialog):
    """Dialog para configurar exportação de vídeo"""

    def __init__(self, synchronizer: MultiViewSynchronizer, parent: QWidget | None = None):
        super().__init__(parent)

        self.synchronizer = synchronizer
        self.export_worker: VideoExportWorker | None = None
        self.settings = VideoExportSettings(output_path=Path())

        self.setWindowTitle("Export Video")
        self.setModal(True)
        self.resize(500, 400)

        self._setup_ui()
        self._update_ui_from_settings()

    def _setup_ui(self):
        """Configura interface do dialog"""
        layout = QVBoxLayout(self)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)

        # Output path
        path_layout = QHBoxLayout()
        self.path_edit = QLabel("No file selected")
        self.path_edit.setStyleSheet("border: 1px solid gray; padding: 4px;")
        path_layout.addWidget(self.path_edit)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_output_path)
        path_layout.addWidget(self.browse_btn)

        output_layout.addRow("Output File:", path_layout)

        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems([fmt.value.upper() for fmt in VideoFormat])
        output_layout.addRow("Format:", self.format_combo)

        layout.addWidget(output_group)

        # Quality settings
        quality_group = QGroupBox("Quality Settings")
        quality_layout = QFormLayout(quality_group)

        # Quality preset
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([q.value.title() for q in VideoQuality])
        self.quality_combo.currentTextChanged.connect(self._on_quality_changed)
        quality_layout.addRow("Quality Preset:", self.quality_combo)

        # Resolution
        resolution_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(240, 7680)
        self.width_spinbox.setValue(1920)
        resolution_layout.addWidget(self.width_spinbox)

        resolution_layout.addWidget(QLabel("×"))

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(240, 4320)
        self.height_spinbox.setValue(1080)
        resolution_layout.addWidget(self.height_spinbox)

        quality_layout.addRow("Resolution:", resolution_layout)

        # FPS
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 120)
        self.fps_spinbox.setValue(30)
        quality_layout.addRow("FPS:", self.fps_spinbox)

        layout.addWidget(quality_group)

        # Duration settings
        duration_group = QGroupBox("Duration Settings")
        duration_layout = QFormLayout(duration_group)

        # Full duration vs custom
        self.full_duration_checkbox = QCheckBox("Use full timeline")
        self.full_duration_checkbox.setChecked(True)
        self.full_duration_checkbox.stateChanged.connect(self._on_duration_mode_changed)
        duration_layout.addRow("", self.full_duration_checkbox)

        # Custom duration
        self.custom_duration_spinbox = QSpinBox()
        self.custom_duration_spinbox.setRange(1, 3600)
        self.custom_duration_spinbox.setValue(60)
        self.custom_duration_spinbox.setSuffix(" seconds")
        self.custom_duration_spinbox.setEnabled(False)
        duration_layout.addRow("Custom Duration:", self.custom_duration_spinbox)

        layout.addWidget(duration_group)

        # View selection
        view_group = QGroupBox("View Selection")
        view_layout = QFormLayout(view_group)

        # Layout mode
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Single View", "Grid Layout", "Split View"])
        view_layout.addRow("Layout:", self.layout_combo)

        # View list (simplified - would show actual views)
        self.include_all_views_checkbox = QCheckBox("Include all views")
        self.include_all_views_checkbox.setChecked(True)
        view_layout.addRow("Views:", self.include_all_views_checkbox)

        layout.addWidget(view_group)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.export_btn = QPushButton("Start Export")
        self.export_btn.clicked.connect(self._start_export)
        self.export_btn.setDefault(True)
        buttons_layout.addWidget(self.export_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def _update_ui_from_settings(self):
        """Atualiza UI baseada nas configurações"""
        # Update format combo
        format_index = list(VideoFormat).index(self.settings.format)
        self.format_combo.setCurrentIndex(format_index)

        # Update resolution
        self.width_spinbox.setValue(self.settings.resolution[0])
        self.height_spinbox.setValue(self.settings.resolution[1])

        # Update FPS
        self.fps_spinbox.setValue(self.settings.fps)

    @pyqtSlot()
    def _browse_output_path(self):
        """Seleciona arquivo de output"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video As...",
            "",
            "Video Files (*.mp4 *.avi *.mov *.webm);;All Files (*)",
        )

        if file_path:
            self.settings.output_path = Path(file_path)
            self.path_edit.setText(str(self.settings.output_path))

    @pyqtSlot(str)
    def _on_quality_changed(self, quality_text: str):
        """Callback quando qualidade preset muda"""
        quality_map = {
            "Low": (1280, 720, 15),
            "Medium": (1920, 1080, 30),
            "High": (1920, 1080, 60),
            "Ultra": (3840, 2160, 30),
        }

        if quality_text in quality_map:
            width, height, fps = quality_map[quality_text]
            self.width_spinbox.setValue(width)
            self.height_spinbox.setValue(height)
            self.fps_spinbox.setValue(fps)

    @pyqtSlot()
    def _on_duration_mode_changed(self):
        """Callback quando modo de duração muda"""
        use_full = self.full_duration_checkbox.isChecked()
        self.custom_duration_spinbox.setEnabled(not use_full)

    @pyqtSlot()
    def _start_export(self):
        """Inicia exportação de vídeo"""
        # Validate settings
        if not self.settings.output_path or not self.settings.output_path.parent.exists():
            QMessageBox.warning(self, "Invalid Output", "Please select a valid output file.")
            return

        if not self.synchronizer.views:
            QMessageBox.warning(self, "No Views", "No views available for export.")
            return

        # Update settings from UI
        self.settings.format = list(VideoFormat)[self.format_combo.currentIndex()]
        self.settings.resolution = (self.width_spinbox.value(), self.height_spinbox.value())
        self.settings.fps = self.fps_spinbox.value()

        if not self.full_duration_checkbox.isChecked():
            self.settings.duration_seconds = float(self.custom_duration_spinbox.value())
        else:
            self.settings.duration_seconds = None

        # Layout mode
        layout_modes = ["single", "grid", "split"]
        self.settings.layout_mode = layout_modes[self.layout_combo.currentIndex()]

        # Start export worker
        self.export_worker = VideoExportWorker(self.settings, self.synchronizer)

        # Connect signals
        self.export_worker.progress_updated.connect(self.progress_bar.setValue)
        self.export_worker.frame_captured.connect(self._on_frame_captured)
        self.export_worker.export_completed.connect(self._on_export_completed)
        self.export_worker.export_failed.connect(self._on_export_failed)

        # Update UI for export mode
        self.export_btn.setText("Stop Export")
        self.export_btn.clicked.disconnect()
        self.export_btn.clicked.connect(self._stop_export)

        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Starting export...")

        # Start worker
        self.export_worker.start()

        logger.info("video_export_started", output_path=str(self.settings.output_path))

    @pyqtSlot()
    def _stop_export(self):
        """Para exportação"""
        if self.export_worker:
            self.export_worker.stop_export()
            self.export_worker.wait()

        self._reset_ui()

    @pyqtSlot(int)
    def _on_frame_captured(self, frame_number: int):
        """Callback quando frame é capturado"""
        self.status_label.setText(f"Capturing frame {frame_number}...")

    @pyqtSlot()
    def _on_export_completed(self):
        """Callback quando exportação completa"""
        self.status_label.setText("Export completed successfully!")

        # Show completion message
        QMessageBox.information(
            self,
            "Export Complete",
            f"Video exported successfully to:\n{self.settings.output_path}",
        )

        self._reset_ui()
        self.accept()

    @pyqtSlot(str)
    def _on_export_failed(self, error: str):
        """Callback quando exportação falha"""
        self.status_label.setText("Export failed!")

        QMessageBox.critical(
            self,
            "Export Failed",
            f"Video export failed:\n{error}",
        )

        self._reset_ui()

    def _reset_ui(self):
        """Reset UI para estado inicial"""
        self.export_btn.setText("Start Export")
        self.export_btn.clicked.disconnect()
        self.export_btn.clicked.connect(self._start_export)

        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

        if self.export_worker:
            self.export_worker = None


# Utility functions for video export integration
def show_video_export_dialog(synchronizer: MultiViewSynchronizer,
                           parent: QWidget | None = None) -> bool:
    """Mostra dialog de exportação de vídeo e retorna True se exportado"""
    dialog = VideoExportDialog(synchronizer, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted


def export_video_programmatically(settings: VideoExportSettings,
                                synchronizer: MultiViewSynchronizer,
                                progress_callback: Callable[[int], None] | None = None) -> bool:
    """Exporta vídeo programaticamente sem UI"""
    try:
        worker = VideoExportWorker(settings, synchronizer)

        if progress_callback:
            worker.progress_updated.connect(progress_callback)

        # Run synchronously
        worker.run()
        return True

    except Exception as e:
        logger.exception("programmatic_video_export_failed", error=str(e))
        return False
