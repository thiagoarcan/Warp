from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StreamFilters(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    time_include: Optional[list[tuple[float, float]]] = None
    time_exclude: Optional[list[tuple[float, float]]] = None
    max_points_per_window: int = 5000
    downsample_method: str = "lttb"
    hide_interpolated: bool = False
    hide_nan: bool = True
    quality_threshold: Optional[float] = None
    value_predicates: dict[str, str] = Field(default_factory=dict)
    hidden_series: list[str] = Field(default_factory=list)


class StreamingState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    play_state: str = "stopped"
    current_time_index: int = 0
    speed: float = 1.0
    window_size: timedelta = timedelta(seconds=10)
    loop: bool = False
    filters: StreamFilters = Field(default_factory=StreamFilters)


@dataclass
class TickUpdate:
    index: int


class StreamingEngine:
    def __init__(self, state: StreamingState):
        self.state = state

    def tick(self) -> TickUpdate:
        if self.state.play_state != "playing":
            return TickUpdate(index=self.state.current_time_index)
        self.state.current_time_index += 1
        return TickUpdate(index=self.state.current_time_index)

    def sync_views(self, views: list[str]) -> None:
        _ = views


class VideoExporter:
    def __init__(self, library: str = "opencv"):
        self.library = library

    def export(self, streaming_session, output_path, fps: int, resolution: tuple[int, int]) -> None:
        if self.library == "opencv":
            try:
                import cv2  # noqa: F401
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError("opencv-python not available") from exc
        elif self.library == "moviepy":
            try:
                import moviepy  # noqa: F401
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError("moviepy not available") from exc
        else:
            raise ValueError(f"Unknown video library: {self.library}")
        _ = (streaming_session, output_path, fps, resolution)
