"""
VizConfig - Configurações de visualização conforme seção 10.1

Sistema de configuração para todos os tipos de visualização:
- Cores, estilos e temas
- Performance e rendering
- Interação e seleção
- Exportação e layout
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ThemeType(str, Enum):
    """Temas disponíveis"""
    LIGHT = "light"
    DARK = "dark"
    SCIENTIFIC = "scientific"
    HIGH_CONTRAST = "high_contrast"


class RenderMode(str, Enum):
    """Modos de renderização"""
    FAST = "fast"          # OpenGL básico
    QUALITY = "quality"    # Anti-aliasing ativado
    INTERACTIVE = "interactive"  # Otimizado para interação
    EXPORT = "export"      # Máxima qualidade para exportação


class ColorScale(str, Enum):
    """Escalas de cor disponíveis"""
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    COOLWARM = "coolwarm"
    RAINBOW = "rainbow"
    GRAYSCALE = "grayscale"


class ColorConfig(BaseModel):
    """Configuração de cores"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Paleta principal
    primary_colors: list[str] = Field(default_factory=lambda: [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ])

    # Background
    background_color: str = "#ffffff"
    grid_color: str = "#e0e0e0"
    axis_color: str = "#333333"

    # Seleção
    selection_color: str = "#ff6b6b"
    selection_alpha: float = 0.3

    # Highlighting
    highlight_color: str = "#ffa502"
    highlight_width: float = 3.0

    # NaN/Invalid data
    nan_color: str = "#cccccc"

    def get_color_cycle(self, n: int) -> list[str]:
        """Retorna ciclo de cores para n series"""
        if n <= len(self.primary_colors):
            return self.primary_colors[:n]

        # Repete cores se necessário
        cycle = []
        for i in range(n):
            cycle.append(self.primary_colors[i % len(self.primary_colors)])
        return cycle


class StyleConfig(BaseModel):
    """Configuração de estilo"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Line styles
    line_width: float = 1.5
    marker_size: float = 6.0
    marker_alpha: float = 0.8

    # Font settings
    font_family: str = "Arial"
    font_size: int = 10
    title_font_size: int = 14
    label_font_size: int = 12

    # Grid
    grid_enabled: bool = True
    grid_alpha: float = 0.3
    grid_line_width: float = 0.5

    # Axes
    axis_line_width: float = 1.0
    tick_length: float = 5.0

    # Margins
    margin_left: float = 80.0
    margin_right: float = 20.0
    margin_top: float = 20.0
    margin_bottom: float = 60.0


class PerformanceConfig(BaseModel):
    """Configuração de performance"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Downsampling
    max_points_2d: int = 100_000
    max_points_3d: int = 50_000
    downsample_method: str = "lttb"  # lttb, uniform, adaptive

    # Renderização
    render_mode: RenderMode = RenderMode.INTERACTIVE
    use_opengl: bool = True
    antialias: bool = True

    # Cache
    cache_plots: bool = True
    cache_size_mb: int = 500

    # Threading
    use_worker_threads: bool = True
    max_threads: int = 4

    # Memory
    max_memory_mb: int = 2048
    gc_threshold: float = 0.8  # Trigger GC at 80% memory usage


class InteractionConfig(BaseModel):
    """Configuração de interação"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Pan/Zoom
    pan_enabled: bool = True
    zoom_enabled: bool = True
    wheel_zoom_factor: float = 0.1

    # Seleção
    selection_enabled: bool = True
    brush_selection: bool = True
    lasso_selection: bool = False
    rect_selection: bool = True

    # Hover
    hover_enabled: bool = True
    hover_timeout_ms: int = 500
    show_coordinates: bool = True

    # Context menu
    context_menu_enabled: bool = True

    # Keyboard shortcuts
    keyboard_shortcuts: dict[str, str] = Field(default_factory=lambda: {
        "ctrl+z": "undo",
        "ctrl+y": "redo",
        "ctrl+a": "select_all",
        "ctrl+c": "copy",
        "delete": "delete_selection",
        "escape": "clear_selection",
    })


class Export2DConfig(BaseModel):
    """Configuração para export 2D"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Formatos suportados
    supported_formats: list[str] = Field(default_factory=lambda: [
        "png", "jpg", "svg", "pdf", "eps",
    ])

    # Resolução
    default_dpi: int = 300
    max_dpi: int = 600

    # Dimensões
    default_width: int = 1920
    default_height: int = 1080

    # Qualidade
    jpeg_quality: int = 95
    png_compression: int = 6

    # Incluir metadados
    include_metadata: bool = True


class Export3DConfig(BaseModel):
    """Configuração para export 3D"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Formatos 3D
    supported_formats: list[str] = Field(default_factory=lambda: [
        "png", "jpg", "obj", "ply", "stl", "vtk", "x3d",
    ])

    # Renderização
    render_resolution: tuple[int, int] = (1920, 1080)
    samples_per_pixel: int = 8

    # Lighting
    ambient_coefficient: float = 0.3
    diffuse_coefficient: float = 0.7
    specular_coefficient: float = 0.3

    # Camera
    default_camera_position: tuple[float, float, float] = (1.0, 1.0, 1.0)
    default_focal_point: tuple[float, float, float] = (0.0, 0.0, 0.0)


# Legacy compatibility classes (kept for backward compatibility)
class AxisConfig(BaseModel):
    """Legacy axis configuration"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = ""
    scale: str = "linear"
    range: list[float] | None = None


class ColorScheme(BaseModel):
    """Legacy color scheme"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    palette: list[str] = Field(
        default_factory=lambda: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
    )


class DownsampleStrategy(BaseModel):
    """Legacy downsampling strategy"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str = "lttb"
    max_points: int = 5000
    preserve_features: list[str] = Field(default_factory=list)


class InteractivityConfig(BaseModel):
    """Legacy interactivity config"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    show_legend: bool = True
    hover_mode: str = "x unified"


class PlotConfig(BaseModel):
    """Legacy plot configuration"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = ""
    axes: AxisConfig = Field(default_factory=AxisConfig)
    colors: ColorScheme = Field(default_factory=ColorScheme)
    downsample: DownsampleStrategy = Field(default_factory=DownsampleStrategy)
    interactive: InteractivityConfig = Field(default_factory=InteractivityConfig)


class VizConfig(BaseModel):
    """
    Configuração principal do sistema de visualização
    Conforme especificação seção 10.1
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Tema atual
    theme: ThemeType = ThemeType.LIGHT

    # Subconfigs
    colors: ColorConfig = Field(default_factory=ColorConfig)
    style: StyleConfig = Field(default_factory=StyleConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    interaction: InteractionConfig = Field(default_factory=InteractionConfig)
    export_2d: Export2DConfig = Field(default_factory=Export2DConfig)
    export_3d: Export3DConfig = Field(default_factory=Export3DConfig)

    # Configurações específicas por tipo
    plot_2d_config: dict[str, Any] = Field(default_factory=dict)
    plot_3d_config: dict[str, Any] = Field(default_factory=dict)
    heatmap_config: dict[str, Any] = Field(default_factory=dict)

    def apply_theme(self, theme: ThemeType):
        """Aplica tema pré-definido"""
        self.theme = theme

        if theme == ThemeType.DARK:
            self.colors.background_color = "#2d2d2d"
            self.colors.grid_color = "#404040"
            self.colors.axis_color = "#cccccc"
        elif theme == ThemeType.LIGHT:
            self.colors.background_color = "#ffffff"
            self.colors.grid_color = "#e0e0e0"
            self.colors.axis_color = "#333333"
        elif theme == ThemeType.SCIENTIFIC:
            self.colors.background_color = "#f8f8f8"
            self.colors.grid_color = "#d0d0d0"
            self.colors.axis_color = "#222222"
            self.style.grid_enabled = True
            self.style.font_family = "DejaVu Sans"
        elif theme == ThemeType.HIGH_CONTRAST:
            self.colors.background_color = "#000000"
            self.colors.grid_color = "#808080"
            self.colors.axis_color = "#ffffff"
            self.colors.primary_colors = ["#ffffff", "#ffff00", "#00ffff", "#ff00ff"]

    def get_color_for_series(self, series_index: int) -> str:
        """Retorna cor para série específica"""
        colors = self.colors.primary_colors
        return colors[series_index % len(colors)]

    def get_colormap_colors(self, colormap: ColorScale, n_colors: int) -> list[str]:
        """Retorna cores do colormap especificado"""
        # Simplified implementation - in practice would use actual colormap libraries
        if colormap == ColorScale.VIRIDIS:
            # Sample viridis colors
            return ["#440154", "#3b528b", "#21908c", "#5dc863", "#fde725"][:n_colors]
        if colormap == ColorScale.PLASMA:
            return ["#0d0887", "#6a00a8", "#b12a90", "#e16462", "#fca636"][:n_colors]
        # Add more colormaps as needed
        return self.colors.primary_colors[:n_colors]


# Configurações pré-definidas
def get_default_config() -> VizConfig:
    """Retorna configuração padrão"""
    return VizConfig()


def get_dark_config() -> VizConfig:
    """Retorna configuração dark theme"""
    config = VizConfig()
    config.apply_theme(ThemeType.DARK)
    return config


def get_scientific_config() -> VizConfig:
    """Retorna configuração científica"""
    config = VizConfig()
    config.apply_theme(ThemeType.SCIENTIFIC)
    return config


def get_high_contrast_config() -> VizConfig:
    """Retorna configuração alto contraste"""
    config = VizConfig()
    config.apply_theme(ThemeType.HIGH_CONTRAST)
    return config
