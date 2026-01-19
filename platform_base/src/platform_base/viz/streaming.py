from __future__ import annotations

from datetime import timedelta
from typing import Literal, Optional, Any, Iterator
from pathlib import Path
import numpy as np

from pydantic import BaseModel, ConfigDict, Field

from platform_base.core.models import SeriesID, ViewID, SessionID
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class ValuePredicate(BaseModel):
    series_id: SeriesID
    operator: Literal[">", "<", ">=", "<=", "==", "!="]
    value: float


class SmoothConfig(BaseModel):
    method: Literal["savitzky_golay", "gaussian", "median", "lowpass"]
    window: int = 5
    sigma: Optional[float] = None


class ScaleConfig(BaseModel):
    method: Literal["linear", "log", "normalized"]
    range: Optional[tuple[float, float]] = None


class TimeInterval(BaseModel):
    start: float
    end: float


class StreamFilters(BaseModel):
    """Filtros detalhados para streaming conforme PRD seção 11.2"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # 1) Filtros temporais
    time_include: Optional[list[TimeInterval]] = None
    time_exclude: Optional[list[TimeInterval]] = None
    
    # 2) Filtros de amostragem
    max_points_per_window: int = 5000
    downsample_method: Literal["lttb", "minmax", "adaptive"] = "lttb"
    
    # 3) Filtros de qualidade
    hide_interpolated: bool = False
    hide_nan: bool = True
    quality_threshold: Optional[float] = None
    
    # 4) Filtros de valor
    value_predicates: dict[SeriesID, ValuePredicate] = Field(default_factory=dict)
    
    # 5) Filtros visuais (render-only)
    visual_smoothing: Optional[SmoothConfig] = None
    hidden_series: list[SeriesID] = Field(default_factory=list)
    scale_override: Optional[ScaleConfig] = None


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
    window_data: dict[SeriesID, np.ndarray]
    reached_end: bool = False


class StreamingEngine:
    """Engine de streaming não global, instância por sessão"""
    
    def __init__(self, state: StreamingState):
        self.state = state
        self.total_points = 0
        self.time_points: np.ndarray = np.array([])
        self.eligible_indices: np.ndarray = np.array([])
        
    def setup_data(self, time_points: np.ndarray) -> None:
        """Configura dados temporais e aplica filtros de elegibilidade"""
        self.time_points = time_points
        self.total_points = len(time_points)
        self.eligible_indices = self._apply_eligibility_filters()
        logger.info("streaming_data_setup", 
                   total_points=self.total_points,
                   eligible_points=len(self.eligible_indices))
    
    def _apply_eligibility_filters(self) -> np.ndarray:
        """Aplica filtros temporais para determinar índices elegíveis"""
        indices = np.arange(len(self.time_points))
        
        # Filtro de inclusão temporal
        if self.state.filters.time_include:
            mask = np.zeros(len(self.time_points), dtype=bool)
            for interval in self.state.filters.time_include:
                mask |= (self.time_points >= interval.start) & (self.time_points <= interval.end)
            indices = indices[mask]
        
        # Filtro de exclusão temporal  
        if self.state.filters.time_exclude:
            mask = np.ones(len(self.time_points), dtype=bool)
            for interval in self.state.filters.time_exclude:
                mask &= ~((self.time_points >= interval.start) & (self.time_points <= interval.end))
            indices = indices[mask]
            
        return indices

    def tick(self) -> TickUpdate:
        """Avança um tick no streaming"""
        if not self.state.play_state.is_playing:
            return self._current_update()
            
        # Avança índice conforme velocidade
        self.state.current_time_index += int(self.state.speed)
        
        # Check bounds
        if self.state.current_time_index >= len(self.eligible_indices):
            if self.state.loop:
                self.state.current_time_index = 0
            else:
                self.state.play_state.is_playing = False
                self.state.current_time_index = len(self.eligible_indices) - 1
                return TickUpdate(
                    session_id="",  # será preenchido pelo chamador
                    current_time_index=self.state.current_time_index,
                    current_time_seconds=self._current_time(),
                    window_data={},
                    reached_end=True
                )
        
        return self._current_update()
    
    def _current_update(self) -> TickUpdate:
        """Gera update para o estado atual"""
        return TickUpdate(
            session_id="",  # será preenchido pelo chamador
            current_time_index=self.state.current_time_index,
            current_time_seconds=self._current_time(),
            window_data=self._get_window_data(),
            reached_end=False
        )
    
    def _current_time(self) -> float:
        """Retorna tempo atual em segundos"""
        if len(self.eligible_indices) == 0:
            return 0.0
        idx = min(self.state.current_time_index, len(self.eligible_indices) - 1)
        return self.time_points[self.eligible_indices[idx]]
    
    def _get_window_data(self) -> dict[SeriesID, np.ndarray]:
        """Obtém dados da janela deslizante atual"""
        # Implementação simplificada - seria expandida com dados reais
        return {}

    def play(self) -> None:
        """Inicia playback"""
        self.state.play_state.is_playing = True
        self.state.play_state.is_paused = False
        self.state.play_state.is_stopped = False
        logger.info("streaming_play", current_index=self.state.current_time_index)

    def pause(self) -> None:
        """Pausa playback"""
        self.state.play_state.is_playing = False
        self.state.play_state.is_paused = True
        self.state.play_state.is_stopped = False
        logger.info("streaming_pause", current_index=self.state.current_time_index)

    def stop(self) -> None:
        """Para playback e reseta"""
        self.state.play_state.is_playing = False
        self.state.play_state.is_paused = False
        self.state.play_state.is_stopped = True
        self.state.current_time_index = 0
        logger.info("streaming_stop")

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

    def sync_views(self, views: list[ViewID]) -> None:
        """Sincroniza múltiplas views"""
        logger.info("streaming_sync_views", view_count=len(views))


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
                      resolution: tuple[int, int]) -> None:
        """Exporta usando OpenCV"""
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("opencv-python not available for video export") from exc
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            str(output_path),
            fourcc, 
            fps,
            resolution
        )
        
        try:
            # Simula captura de frames (implementação real capturaria plots)
            total_frames = len(streaming_session.eligible_indices) if streaming_session.eligible_indices.size > 0 else 100
            
            for frame_idx in range(total_frames):
                # Placeholder: geraria frame real do plot
                frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)
                writer.write(frame)
                
        finally:
            writer.release()
    
    def _export_moviepy(self,
                       streaming_session: StreamingEngine,
                       output_path: Path,
                       fps: int,
                       resolution: tuple[int, int]) -> None:
        """Exporta usando MoviePy (placeholder)"""
        try:
            import moviepy
        except ImportError as exc:
            raise RuntimeError("moviepy not available for video export") from exc
            
        logger.info("moviepy_export_placeholder", 
                   message="MoviePy export would be implemented here")
        # Implementation would use moviepy.VideoClip
