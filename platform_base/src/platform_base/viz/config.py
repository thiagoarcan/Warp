from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AxisConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = ""
    scale: str = "linear"
    range: Optional[list[float]] = None


class ColorScheme(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    palette: list[str] = Field(
        default_factory=lambda: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    )


class DownsampleStrategy(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str = "lttb"
    max_points: int = 5000
    preserve_features: list[str] = Field(default_factory=list)


class InteractivityConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    show_legend: bool = True
    hover_mode: str = "x unified"


class PlotConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = ""
    axes: AxisConfig = Field(default_factory=AxisConfig)
    colors: ColorScheme = Field(default_factory=ColorScheme)
    downsample: DownsampleStrategy = Field(default_factory=DownsampleStrategy)
    interactive: InteractivityConfig = Field(default_factory=InteractivityConfig)
