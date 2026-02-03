from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from platform_base.core.models import SeriesID, SessionID, ViewID
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


logger = get_logger(__name__)


class ValuePredicate(BaseModel):
    series_id: SeriesID
    operator: Literal[">", "<", ">=", "<=", "==", "!="]
    value: float

    def evaluate(self, values: np.ndarray) -> np.ndarray:
        """Evaluate predicate on array of values"""
        ops = {
            ">": np.greater,
            "<": np.less,
            ">=": np.greater_equal,
            "<=": np.less_equal,
            "==": np.equal,
            "!=": np.not_equal,
        }
        return ops[self.operator](values, self.value)


class SmoothConfig(BaseModel):
    method: Literal["savitzky_golay", "gaussian", "median", "lowpass"]
    window: int = 5
    sigma: float | None = None


class ScaleConfig(BaseModel):
    method: Literal["linear", "log", "normalized"]
    range: tuple[float, float] | None = None


class TimeInterval(BaseModel):
    start: float
    end: float

    def contains(self, t: float) -> bool:
        return self.start <= t <= self.end


class StreamFilters(BaseModel):
    """Filtros detalhados para streaming conforme PRD seção 11.2"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # 1) Filtros temporais
    time_include: list[TimeInterval] | None = None
    time_exclude: list[TimeInterval] | None = None

    # 2) Filtros de amostragem
    max_points_per_window: int = 5000
    downsample_method: Literal["lttb", "minmax", "adaptive"] = "lttb"

    # 3) Filtros de qualidade
    hide_interpolated: bool = False
    hide_nan: bool = True
    quality_threshold: float | None = None

    # 4) Filtros de valor
    value_predicates: dict[SeriesID, ValuePredicate] = Field(default_factory=dict)

    # 5) Filtros visuais (render-only)
    visual_smoothing: SmoothConfig | None = None
    hidden_series: list[SeriesID] = Field(default_factory=list)
    scale_override: ScaleConfig | None = None


class PlayState(BaseModel):
    is_playing: bool = False
    is_paused: bool = False
    is_stopped: bool = True


class StreamingState(BaseModel):
    """Estado de streaming por sessão (NÃO global)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    play_state: PlayState = Field(default_factory=PlayState)
    current_time_index: int = 0
    speed: float = 1.0
    window_size: timedelta = timedelta(seconds=60)
    loop: bool = False
    filters: StreamFilters = Field(default_factory=StreamFilters)


class TickUpdate(BaseModel):
    """Update retornado a cada tick"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: SessionID
    current_time_index: int
    current_time_seconds: float
    window_start: float
    window_end: float
    window_data: dict[SeriesID, np.ndarray]
    window_time: np.ndarray = Field(default_factory=lambda: np.array([]))
    reached_end: bool = False


@dataclass
class ViewSubscription:
    """Subscription for a view to receive streaming updates"""
    view_id: ViewID
    callback: Callable[[TickUpdate], None] | None = None
    series_filter: list[SeriesID] | None = None
    transform: Callable[[np.ndarray], np.ndarray] | None = None


class StreamingEngine:
    """
    Engine de streaming não global, instância por sessão.

    Implements PRD section 11 with:
    - Multi-view synchronization
    - Eligibility filters for playback
    - Window data extraction with downsampling
    - Subscriber notification system
    """

    def __init__(self, state: StreamingState, session_id: SessionID = ""):
        self.state = state
        self.session_id = session_id
        self.total_points = 0
        self.time_points: np.ndarray = np.array([])
        self.series_data: dict[SeriesID, np.ndarray] = {}
        self.eligible_indices: np.ndarray = np.array([])
        self.interpolation_masks: dict[SeriesID, np.ndarray] = {}

        # Multi-view subscription system
        self._subscribers: dict[ViewID, ViewSubscription] = {}
        self._sync_callbacks: list[Callable[[TickUpdate], None]] = []

    def setup_data(
        self,
        time_points: np.ndarray,
        series_data: dict[SeriesID, np.ndarray] | None = None,
        interpolation_masks: dict[SeriesID, np.ndarray] | None = None,
    ) -> None:
        """
        Configura dados temporais e de séries para streaming.

        Args:
            time_points: Array de timestamps em segundos
            series_data: Dict de séries com valores
            interpolation_masks: Dict de máscaras indicando pontos interpolados
        """
        self.time_points = time_points
        self.total_points = len(time_points)
        self.series_data = series_data or {}
        self.interpolation_masks = interpolation_masks or {}

        self.eligible_indices = self._apply_eligibility_filters()

        logger.info("streaming_data_setup",
                   session_id=self.session_id,
                   total_points=self.total_points,
                   eligible_points=len(self.eligible_indices),
                   n_series=len(self.series_data))

    def _apply_eligibility_filters(self) -> np.ndarray:
        """
        Aplica filtros temporais e de valor para determinar índices elegíveis.

        Returns:
            Array de índices elegíveis para playback
        """
        if len(self.time_points) == 0:
            return np.array([], dtype=int)

        indices = np.arange(len(self.time_points))
        mask = np.ones(len(self.time_points), dtype=bool)

        # 1) Filtro de inclusão temporal
        if self.state.filters.time_include:
            include_mask = np.zeros(len(self.time_points), dtype=bool)
            for interval in self.state.filters.time_include:
                include_mask |= (
                    (self.time_points >= interval.start) &
                    (self.time_points <= interval.end)
                )
            mask &= include_mask

        # 2) Filtro de exclusão temporal
        if self.state.filters.time_exclude:
            for interval in self.state.filters.time_exclude:
                mask &= ~(
                    (self.time_points >= interval.start) &
                    (self.time_points <= interval.end)
                )

        # 3) Filtro de qualidade - hide interpolated
        if self.state.filters.hide_interpolated and self.interpolation_masks:
            for series_id, interp_mask in self.interpolation_masks.items():
                if len(interp_mask) == len(self.time_points):
                    mask &= ~interp_mask

        # 4) Filtro de NaN
        if self.state.filters.hide_nan and self.series_data:
            for series_id, values in self.series_data.items():
                if len(values) == len(self.time_points):
                    mask &= np.isfinite(values)

        # 5) Filtros de valor
        if self.state.filters.value_predicates:
            for series_id, predicate in self.state.filters.value_predicates.items():
                if series_id in self.series_data:
                    values = self.series_data[series_id]
                    if len(values) == len(self.time_points):
                        pred_mask = predicate.evaluate(values)
                        mask &= pred_mask

        return indices[mask]

    def _get_window_indices(self) -> tuple[int, int]:
        """Get start and end indices for current window"""
        if len(self.eligible_indices) == 0:
            return 0, 0

        current_idx = min(self.state.current_time_index, len(self.eligible_indices) - 1)
        current_time = self.time_points[self.eligible_indices[current_idx]]

        window_seconds = self.state.window_size.total_seconds()
        window_start_time = current_time - window_seconds / 2
        window_end_time = current_time + window_seconds / 2

        # Find indices within window
        eligible_times = self.time_points[self.eligible_indices]
        in_window = (eligible_times >= window_start_time) & (eligible_times <= window_end_time)
        window_indices = np.where(in_window)[0]

        if len(window_indices) == 0:
            return current_idx, current_idx + 1

        return int(window_indices[0]), int(window_indices[-1]) + 1

    def _downsample_lttb(self, x: np.ndarray, y: np.ndarray, n_out: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Largest Triangle Three Buckets (LTTB) downsampling.

        Preserves visual appearance while reducing points.
        """
        if len(x) <= n_out:
            return x, y

        # Bucket size
        bucket_size = (len(x) - 2) / (n_out - 2)

        # Always include first point
        sampled_x = [x[0]]
        sampled_y = [y[0]]

        # Previous selected point
        prev_idx = 0

        for i in range(n_out - 2):
            # Current bucket bounds
            bucket_start = int((i + 1) * bucket_size) + 1
            bucket_end = int((i + 2) * bucket_size) + 1
            bucket_end = min(bucket_end, len(x) - 1)

            # Next bucket average (for triangle calculation)
            next_bucket_start = bucket_end
            next_bucket_end = int((i + 3) * bucket_size) + 1
            next_bucket_end = min(next_bucket_end, len(x))

            if next_bucket_start < next_bucket_end:
                avg_x = np.mean(x[next_bucket_start:next_bucket_end])
                avg_y = np.mean(y[next_bucket_start:next_bucket_end])
            else:
                avg_x = x[-1]
                avg_y = y[-1]

            # Find point with largest triangle area in bucket
            max_area = -1
            max_idx = bucket_start

            for j in range(bucket_start, bucket_end):
                # Triangle area
                area = abs(
                    (x[prev_idx] - avg_x) * (y[j] - y[prev_idx]) -
                    (x[prev_idx] - x[j]) * (avg_y - y[prev_idx]),
                )
                if area > max_area:
                    max_area = area
                    max_idx = j

            sampled_x.append(x[max_idx])
            sampled_y.append(y[max_idx])
            prev_idx = max_idx

        # Always include last point
        sampled_x.append(x[-1])
        sampled_y.append(y[-1])

        return np.array(sampled_x), np.array(sampled_y)

    def _get_window_data(self) -> tuple[dict[SeriesID, np.ndarray], np.ndarray]:
        """
        Obtém dados da janela deslizante atual com downsampling opcional.

        Returns:
            Tuple of (series_data_dict, time_array)
        """
        if len(self.eligible_indices) == 0 or len(self.series_data) == 0:
            return {}, np.array([])

        start_idx, end_idx = self._get_window_indices()

        if start_idx >= end_idx:
            return {}, np.array([])

        window_eligible = self.eligible_indices[start_idx:end_idx]
        window_time = self.time_points[window_eligible]

        window_data: dict[SeriesID, np.ndarray] = {}

        for series_id, values in self.series_data.items():
            # Skip hidden series
            if series_id in self.state.filters.hidden_series:
                continue

            series_values = values[window_eligible]

            # Apply downsampling if needed
            max_points = self.state.filters.max_points_per_window
            if len(series_values) > max_points:
                if self.state.filters.downsample_method == "lttb":
                    window_time_ds, series_values = self._downsample_lttb(
                        window_time, series_values, max_points,
                    )
                elif self.state.filters.downsample_method == "minmax":
                    # MinMax preserves peaks
                    step = len(series_values) // max_points
                    indices = []
                    for i in range(0, len(series_values) - step, step):
                        chunk = series_values[i:i+step]
                        indices.append(i + np.argmin(chunk))
                        indices.append(i + np.argmax(chunk))
                    indices = sorted(set(indices))
                    series_values = series_values[indices]
                    window_time = window_time[indices]
                else:  # adaptive
                    # Simple decimation
                    step = max(1, len(series_values) // max_points)
                    series_values = series_values[::step]

            # Apply visual smoothing if configured
            if self.state.filters.visual_smoothing:
                series_values = self._apply_visual_smoothing(series_values)

            window_data[series_id] = series_values

        return window_data, window_time

    def _apply_visual_smoothing(self, values: np.ndarray) -> np.ndarray:
        """Apply visual smoothing to values (render-only, doesn't modify source)"""
        config = self.state.filters.visual_smoothing
        if config is None or len(values) < config.window:
            return values

        if config.method == "gaussian":
            from scipy.ndimage import gaussian_filter1d
            sigma = config.sigma or config.window / 4
            return gaussian_filter1d(values, sigma)
        if config.method == "median":
            from scipy.ndimage import median_filter
            return median_filter(values, size=config.window)
        if config.method == "savitzky_golay":
            from scipy.signal import savgol_filter
            if len(values) > config.window:
                return savgol_filter(values, config.window, min(3, config.window - 1))

        return values

    def tick(self) -> TickUpdate:
        """
        Avança um tick no streaming e retorna update.

        Returns:
            TickUpdate com dados atuais da janela
        """
        if not self.state.play_state.is_playing:
            return self._current_update()

        # Avança índice conforme velocidade
        self.state.current_time_index += int(self.state.speed)

        # Check bounds
        if self.state.current_time_index >= len(self.eligible_indices):
            if self.state.loop:
                self.state.current_time_index = 0
                logger.debug("streaming_loop", session_id=self.session_id)
            else:
                self.state.play_state.is_playing = False
                self.state.current_time_index = len(self.eligible_indices) - 1

                update = self._current_update()
                update.reached_end = True

                # Notify subscribers of end
                self._notify_subscribers(update)

                return update

        update = self._current_update()

        # Notify all subscribers
        self._notify_subscribers(update)

        return update

    def _current_update(self) -> TickUpdate:
        """Gera update para o estado atual"""
        window_data, window_time = self._get_window_data()

        current_time = self._current_time()
        window_seconds = self.state.window_size.total_seconds()

        return TickUpdate(
            session_id=self.session_id,
            current_time_index=self.state.current_time_index,
            current_time_seconds=current_time,
            window_start=current_time - window_seconds / 2,
            window_end=current_time + window_seconds / 2,
            window_data=window_data,
            window_time=window_time,
            reached_end=False,
        )

    def _current_time(self) -> float:
        """Retorna tempo atual em segundos"""
        if len(self.eligible_indices) == 0:
            return 0.0
        idx = min(self.state.current_time_index, len(self.eligible_indices) - 1)
        return float(self.time_points[self.eligible_indices[idx]])

    # ========================================================================
    # Multi-view Synchronization
    # ========================================================================

    def subscribe(self, subscription: ViewSubscription) -> None:
        """
        Subscribe a view to receive streaming updates.

        Args:
            subscription: ViewSubscription with callback and optional filters
        """
        self._subscribers[subscription.view_id] = subscription
        logger.info("view_subscribed",
                   session_id=self.session_id,
                   view_id=subscription.view_id)

    def unsubscribe(self, view_id: ViewID) -> None:
        """Unsubscribe a view from streaming updates"""
        if view_id in self._subscribers:
            del self._subscribers[view_id]
            logger.info("view_unsubscribed",
                       session_id=self.session_id,
                       view_id=view_id)

    def add_sync_callback(self, callback: Callable[[TickUpdate], None]) -> None:
        """Add a global sync callback for all updates"""
        self._sync_callbacks.append(callback)

    def _notify_subscribers(self, update: TickUpdate) -> None:
        """Notify all subscribed views of update"""
        # Call global sync callbacks
        for callback in self._sync_callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.exception("sync_callback_failed", error=str(e))

        # Call individual subscriber callbacks
        for view_id, subscription in self._subscribers.items():
            if subscription.callback is None:
                continue

            try:
                # Filter series if specified
                if subscription.series_filter:
                    filtered_data = {
                        k: v for k, v in update.window_data.items()
                        if k in subscription.series_filter
                    }
                    filtered_update = TickUpdate(
                        session_id=update.session_id,
                        current_time_index=update.current_time_index,
                        current_time_seconds=update.current_time_seconds,
                        window_start=update.window_start,
                        window_end=update.window_end,
                        window_data=filtered_data,
                        window_time=update.window_time,
                        reached_end=update.reached_end,
                    )
                    subscription.callback(filtered_update)
                else:
                    subscription.callback(update)

            except Exception as e:
                logger.exception("subscriber_callback_failed",
                           view_id=view_id,
                           error=str(e))

    def sync_views(self, views: list[ViewID]) -> None:
        """
        Sincroniza múltiplas views com estado atual.

        Sends current update to specified views.
        """
        update = self._current_update()

        for view_id in views:
            if view_id in self._subscribers:
                subscription = self._subscribers[view_id]
                if subscription.callback:
                    try:
                        subscription.callback(update)
                    except Exception as e:
                        logger.exception("sync_view_failed",
                                   view_id=view_id,
                                   error=str(e))

        logger.info("streaming_sync_views",
                   session_id=self.session_id,
                   view_count=len(views))

    # ========================================================================
    # Playback Controls
    # ========================================================================

    def play(self) -> None:
        """Inicia playback"""
        self.state.play_state.is_playing = True
        self.state.play_state.is_paused = False
        self.state.play_state.is_stopped = False
        logger.info("streaming_play",
                   session_id=self.session_id,
                   current_index=self.state.current_time_index)

    def pause(self) -> None:
        """Pausa playback"""
        self.state.play_state.is_playing = False
        self.state.play_state.is_paused = True
        self.state.play_state.is_stopped = False
        logger.info("streaming_pause",
                   session_id=self.session_id,
                   current_index=self.state.current_time_index)

    def stop(self) -> None:
        """Para playback e reseta"""
        self.state.play_state.is_playing = False
        self.state.play_state.is_paused = False
        self.state.play_state.is_stopped = True
        self.state.current_time_index = 0
        logger.info("streaming_stop", session_id=self.session_id)

    def seek(self, time_seconds: float) -> None:
        """Pula para tempo específico"""
        # Encontra índice mais próximo
        if len(self.eligible_indices) > 0:
            eligible_times = self.time_points[self.eligible_indices]
            closest_idx = np.argmin(np.abs(eligible_times - time_seconds))
            self.state.current_time_index = closest_idx
            logger.info("streaming_seek",
                       target_time=time_seconds,
                       actual_time=eligible_times[closest_idx])

class VideoExporter:
    """Exportador de vídeo conforme PRD seção 11.4"""

    def __init__(self, library: Literal["opencv", "moviepy"] = "opencv"):
        self.library = library

    def export(self,
               streaming_session: StreamingEngine,
               output_path: Path,
               fps: int = 30,
               resolution: tuple[int, int] = (1920, 1080)) -> None:
        """
        Exporta sessão de streaming como vídeo

        Args:
            streaming_session: Sessão de streaming para exportar
            output_path: Caminho do arquivo de saída
            fps: Frames por segundo
            resolution: Resolução (width, height)
        """
        logger.info("video_export_start",
                   output_path=str(output_path),
                   fps=fps,
                   resolution=resolution)

        if self.library == "opencv":
            self._export_opencv(streaming_session, output_path, fps, resolution)
        else:
            self._export_moviepy(streaming_session, output_path, fps, resolution)

        logger.info("video_export_complete", output_path=str(output_path))

    def _export_opencv(self,
                      streaming_session: StreamingEngine,
                      output_path: Path,
                      fps: int,
                      resolution: tuple[int, int],
                      plot_widget: "QWidget | None" = None,
                      frame_callback: "Callable[[int], None] | None" = None) -> None:
        """Exporta vídeo usando OpenCV.
        
        Args:
            streaming_session: Engine de streaming com dados
            output_path: Caminho do arquivo de saída
            fps: Frames por segundo
            resolution: Tupla (width, height)
            plot_widget: Widget Qt opcional para captura de frames
            frame_callback: Callback para cada frame processado (progress)
        """
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("opencv-python not available for video export") from exc

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            resolution,
        )

        try:
            total_frames = len(streaming_session.eligible_indices) if streaming_session.eligible_indices.size > 0 else 100
            
            for frame_idx in range(total_frames):
                if plot_widget is not None:
                    # Capture real frame from Qt widget
                    try:
                        # Update streaming position
                        streaming_session.tick_forward()
                        
                        # Capture widget as image
                        pixmap = plot_widget.grab()
                        
                        # Scale to target resolution
                        scaled = pixmap.scaled(
                            resolution[0], resolution[1],
                            aspectRatioMode=1  # Qt.KeepAspectRatio
                        )
                        
                        # Convert QPixmap to numpy array for OpenCV
                        qimage = scaled.toImage()
                        width = qimage.width()
                        height = qimage.height()
                        
                        # Get raw bytes and convert to numpy
                        ptr = qimage.bits()
                        ptr.setsize(height * width * 4)  # 4 bytes per pixel (RGBA)
                        arr = np.array(ptr).reshape(height, width, 4)
                        
                        # Convert RGBA to BGR for OpenCV
                        frame = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                        
                        # Ensure correct resolution
                        if frame.shape[:2] != (resolution[1], resolution[0]):
                            frame = cv2.resize(frame, resolution)
                            
                    except Exception as e:
                        logger.warning(f"Frame capture failed at {frame_idx}: {e}")
                        # Fallback to black frame
                        frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)
                else:
                    # No widget provided - create placeholder frame with info text
                    frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)
                    # Add frame info text
                    cv2.putText(frame, f"Frame {frame_idx + 1}/{total_frames}",
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                writer.write(frame)
                
                # Progress callback
                if frame_callback is not None:
                    frame_callback(frame_idx)
                    
            logger.info("opencv_export_complete", 
                       total_frames=total_frames, 
                       output_path=str(output_path))

        finally:
            writer.release()

    def _export_moviepy(self,
                       streaming_session: StreamingEngine,
                       output_path: Path,
                       fps: int,
                       resolution: tuple[int, int]) -> None:
        """Exporta usando MoviePy com VideoClip e frame generator"""
        try:
            from moviepy import VideoClip
        except ImportError as exc:
            raise RuntimeError("moviepy not available for video export") from exc
        
        plot_widget = getattr(streaming_session, '_plot_widget', None)
        total_frames = len(streaming_session.eligible_indices) if streaming_session.eligible_indices.size > 0 else 100
        duration = total_frames / fps
        
        def make_frame(t: float) -> np.ndarray:
            """Generate frame at time t (seconds)"""
            frame_idx = int(t * fps)
            frame_idx = min(frame_idx, total_frames - 1)
            
            if plot_widget is not None:
                try:
                    # Update streaming position
                    streaming_session.state.current_time_index = frame_idx
                    streaming_session.tick()
                    
                    # Capture widget as image
                    pixmap = plot_widget.grab()
                    scaled = pixmap.scaled(resolution[0], resolution[1], aspectRatioMode=1)
                    
                    # Convert QPixmap to numpy array (RGB for moviepy)
                    qimage = scaled.toImage()
                    width = qimage.width()
                    height = qimage.height()
                    
                    ptr = qimage.bits()
                    ptr.setsize(height * width * 4)
                    arr = np.array(ptr).reshape(height, width, 4)
                    
                    # Convert RGBA to RGB (moviepy expects RGB)
                    frame = arr[:, :, :3]
                    
                    # Ensure correct resolution
                    if frame.shape[:2] != (resolution[1], resolution[0]):
                        import cv2
                        frame = cv2.resize(frame, resolution)
                    
                    return frame
                    
                except Exception as e:
                    logger.warning(f"MoviePy frame capture failed at {frame_idx}: {e}")
            
            # Fallback: create placeholder frame
            frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)
            return frame
        
        logger.info("moviepy_export_start", 
                   total_frames=total_frames,
                   duration=duration,
                   output_path=str(output_path))
        
        # Create video clip from frame generator
        clip = VideoClip(make_frame, duration=duration)
        
        # Write video file
        clip.write_videofile(
            str(output_path),
            fps=fps,
            codec='libx264',
            audio=False,
            logger=None  # Suppress moviepy's verbose logging
        )
        
        clip.close()
        
        logger.info("moviepy_export_complete",
                   output_path=str(output_path))
