"""
Figures 3D - Sistema de visualização 3D com PyVista conforme seção 10.4

Features:
- Surface plots e volume rendering
- Trajetórias 3D interativas
- Visualização volumétrica
- State space plots
- Performance otimizada com VTK
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np

try:
    import pyvista as pv
    import vtk
    from PyQt6.QtWidgets import QVBoxLayout, QWidget
    try:
        from pyvistaqt import QtInteractor
        PYVISTA_QT_AVAILABLE = True
    except ImportError:
        PYVISTA_QT_AVAILABLE = False
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    PYVISTA_QT_AVAILABLE = False

from platform_base.utils.logging import get_logger
from platform_base.viz.base import BaseFigure
from platform_base.viz.config import ColorScale, VizConfig

if TYPE_CHECKING:
    from platform_base.core.models import Dataset, Series


logger = get_logger(__name__)


if not PYVISTA_AVAILABLE:
    logger.error("pyvista_not_available", message="PyVista not available for 3D visualization")


def _create_colormap_from_scale(colorscale: ColorScale, n_colors: int = 256) -> np.ndarray:
    """Cria colormap NumPy compatível com PyVista"""
    if colorscale == ColorScale.VIRIDIS:
        import matplotlib.pyplot as plt
        cmap = plt.cm.viridis
    elif colorscale == ColorScale.PLASMA:
        import matplotlib.pyplot as plt
        cmap = plt.cm.plasma
    elif colorscale == ColorScale.COOLWARM:
        import matplotlib.pyplot as plt
        cmap = plt.cm.coolwarm
    else:
        import matplotlib.pyplot as plt
        cmap = plt.cm.viridis  # Default

    # Convert to RGB array
    return cmap(np.linspace(0, 1, n_colors))[:, :3] * 255


class Plot3DWidget(QWidget):
    """
    Widget PyVista para visualização 3D conforme seção 10.4

    Features:
    - Surface plots com lighting realístico
    - Volume rendering para dados densos
    - Trajetórias 3D com colormap temporal
    - Interatividade completa (rotate, zoom, pan)
    - Export para formatos 3D
    """

    def __init__(self, config: VizConfig, parent: QWidget | None = None):
        super().__init__(parent)

        if not PYVISTA_AVAILABLE:
            raise ImportError("PyVista not available")

        if not PYVISTA_QT_AVAILABLE:
            raise ImportError("PyVistaQt not available - cannot create Qt widget")

        self.config = config
        self._setup_ui()

        logger.debug("plot3d_widget_initialized")

    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create PyVista plotter
        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor)

        # Apply theme configuration
        self._apply_theme()

        # Set default view
        self.plotter.view_isometric()

    def _apply_theme(self):
        """Aplica tema à visualização 3D"""
        bg_color = self.config.colors.background_color
        self.plotter.set_background(bg_color)

        # Configure lighting based on theme
        if self.config.theme.value == "dark":
            self.plotter.add_light(pv.Light(position=(1, 1, 1), intensity=0.8))
        else:
            self.plotter.add_light(pv.Light(position=(1, 1, 1), intensity=1.0))

    def add_trajectory(self, points: np.ndarray, scalars: np.ndarray | None = None,
                      name: str = "trajectory", **kwargs):
        """
        Adiciona trajetória 3D ao plot

        Args:
            points: Array Nx3 com coordenadas [x, y, z]
            scalars: Valores escalares para colorir (opcional)
            name: Nome da trajetória
            **kwargs: Argumentos adicionais para o plot
        """
        start_time = time.perf_counter()

        # Create spline from points
        spline = pv.Spline(points, n_points=len(points))

        # Configure plot parameters
        plot_params = {
            "line_width": self.config.style.line_width * 2,
            "render_lines_as_tubes": True,
            "name": name,
            **kwargs,
        }

        if scalars is not None and len(scalars) == len(points):
            # Add scalars to spline
            spline[name + "_scalars"] = scalars
            plot_params["scalars"] = name + "_scalars"
            plot_params["cmap"] = "viridis"
            plot_params["show_scalar_bar"] = True
        else:
            # Use solid color
            color = self.config.get_color_for_series(0)
            plot_params["color"] = color

        # Add to plotter
        actor = self.plotter.add_mesh(spline, **plot_params)

        # Add start/end markers
        start_sphere = pv.Sphere(center=points[0], radius=0.02)
        end_sphere = pv.Sphere(center=points[-1], radius=0.02)

        self.plotter.add_mesh(start_sphere, color="green", name=f"{name}_start")
        self.plotter.add_mesh(end_sphere, color="red", name=f"{name}_end")

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("trajectory_added", name=name, points=len(points), duration_ms=duration_ms)

        return actor

    def add_surface(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                   scalars: np.ndarray | None = None, name: str = "surface", **kwargs):
        """
        Adiciona superfície 3D ao plot

        Args:
            x, y, z: Arrays 2D com coordenadas da grade
            scalars: Valores escalares para colorir (opcional)
            name: Nome da superfície
            **kwargs: Argumentos adicionais
        """
        start_time = time.perf_counter()

        # Create structured grid
        grid = pv.StructuredGrid(x, y, z)

        if scalars is not None:
            grid[name + "_scalars"] = scalars.ravel()
            scalar_name = name + "_scalars"
        else:
            scalar_name = None

        # Configure surface parameters
        surface_params = {
            "opacity": kwargs.get("opacity", 0.8),
            "show_edges": kwargs.get("show_edges", False),
            "cmap": kwargs.get("cmap", "viridis"),
            "name": name,
            **kwargs,
        }

        if scalar_name:
            surface_params["scalars"] = scalar_name
            surface_params["show_scalar_bar"] = True
        else:
            color = self.config.get_color_for_series(0)
            surface_params["color"] = color

        # Add surface to plotter
        actor = self.plotter.add_mesh(grid, **surface_params)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("surface_added", name=name,
                   grid_shape=f"{x.shape[0]}x{x.shape[1]}",
                   duration_ms=duration_ms)

        return actor

    def add_volume(self, volume_data: np.ndarray, spacing: tuple[float, float, float] = (1, 1, 1),
                   name: str = "volume", **kwargs):
        """
        Adiciona volume rendering

        Args:
            volume_data: Array 3D com dados volumétricos
            spacing: Espaçamento entre voxels
            name: Nome do volume
            **kwargs: Argumentos adicionais
        """
        start_time = time.perf_counter()

        # Create uniform grid
        grid = pv.UniformGrid(dimensions=volume_data.shape, spacing=spacing)
        grid[name] = volume_data.ravel()

        # Volume rendering parameters
        volume_params = {
            "scalars": name,
            "opacity": kwargs.get("opacity", [0, 0.2, 0.5, 0.8, 1.0]),
            "cmap": kwargs.get("cmap", "viridis"),
            "show_scalar_bar": True,
            **kwargs,
        }

        # Add volume to plotter
        actor = self.plotter.add_volume(grid, **volume_params)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("volume_added", name=name,
                   shape=volume_data.shape,
                   duration_ms=duration_ms)

        return actor

    def add_point_cloud(self, points: np.ndarray, scalars: np.ndarray | None = None,
                       name: str = "points", **kwargs):
        """
        Adiciona nuvem de pontos

        Args:
            points: Array Nx3 com coordenadas
            scalars: Valores escalares para colorir (opcional)
            name: Nome da nuvem
            **kwargs: Argumentos adicionais
        """
        start_time = time.perf_counter()

        # Create point cloud
        cloud = pv.PolyData(points)

        if scalars is not None and len(scalars) == len(points):
            cloud[name + "_scalars"] = scalars
            scalar_name = name + "_scalars"
        else:
            scalar_name = None

        # Point cloud parameters
        point_params = {
            "point_size": kwargs.get("point_size", self.config.style.marker_size),
            "render_points_as_spheres": kwargs.get("render_points_as_spheres", True),
            "name": name,
            **kwargs,
        }

        if scalar_name:
            point_params["scalars"] = scalar_name
            point_params["cmap"] = kwargs.get("cmap", "viridis")
            point_params["show_scalar_bar"] = True
        else:
            color = self.config.get_color_for_series(0)
            point_params["color"] = color

        # Add to plotter
        actor = self.plotter.add_mesh(cloud, **point_params)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("point_cloud_added", name=name, points=len(points), duration_ms=duration_ms)

        return actor

    def clear(self):
        """Limpa todos os objetos do plot"""
        self.plotter.clear()
        logger.debug("plot3d_cleared")

    def reset_camera(self):
        """Reseta câmera para view padrão"""
        self.plotter.reset_camera()
        self.plotter.view_isometric()

    def export_image(self, file_path: str, width: int | None = None, height: int | None = None):
        """Exporta imagem do plot 3D"""
        try:
            if width is None:
                width = self.config.export_3d.render_resolution[0]
            if height is None:
                height = self.config.export_3d.render_resolution[1]

            # Screenshot with specified resolution
            self.plotter.screenshot(file_path, window_size=(width, height))

            logger.info("plot3d_exported", file_path=file_path, width=width, height=height)

        except Exception as e:
            logger.exception("plot3d_export_failed", file_path=file_path, error=str(e))
            raise

    def export_3d_model(self, file_path: str, format: str = "obj"):
        """Exporta modelo 3D para arquivo"""
        try:
            # Export all meshes
            if format.lower() == "obj":
                # PyVista doesn't directly support multi-mesh OBJ export
                # We'll export the first mesh for now
                meshes = list(self.plotter.renderer.actors.keys())
                if meshes:
                    first_mesh = meshes[0]
                    first_mesh.save(file_path)

            logger.info("plot3d_model_exported", file_path=file_path, format=format)

        except Exception as e:
            logger.exception("plot3d_model_export_failed", file_path=file_path, error=str(e))
            raise


class Trajectory3D(BaseFigure):
    """Wrapper para Plot3DWidget com interface para trajetórias 3D"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Plot3DWidget | None = None

    def render(self, x_series: Series, y_series: Series, z_series: Series,
               color_by_time: bool = True) -> Plot3DWidget:
        """
        Renderiza trajetória 3D de três séries temporais

        Args:
            x_series, y_series, z_series: Séries das três dimensões
            color_by_time: Se deve colorir por tempo
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = Plot3DWidget(self.config)

        # Clear existing data
        self._widget.clear()

        # Ensure same length
        min_len = min(len(x_series.values), len(y_series.values), len(z_series.values))

        # Create trajectory points
        points = np.column_stack([
            x_series.values[:min_len],
            y_series.values[:min_len],
            z_series.values[:min_len],
        ])

        # Apply downsampling if needed
        max_points = self.config.performance.max_points_3d
        if len(points) > max_points:
            indices = np.linspace(0, len(points)-1, max_points, dtype=int)
            points = points[indices]

        # Add trajectory
        scalars = None
        if color_by_time:
            scalars = np.linspace(0, 1, len(points))

        self._widget.add_trajectory(
            points=points,
            scalars=scalars,
            name=f"{x_series.name}_{y_series.name}_{z_series.name}_trajectory",
        )

        # Reset camera
        self._widget.reset_camera()

        logger.info("trajectory3d_rendered",
                   x_series=x_series.name,
                   y_series=y_series.name,
                   z_series=z_series.name,
                   n_points=len(points))

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual na trajetória 3D
        
        Destaca pontos selecionados usando esferas de marcação.
        
        Args:
            selection_indices: Índices dos pontos a destacar
        """
        if self._widget is None or self._widget.plotter is None:
            return
        
        # Remove previous selection markers
        try:
            self._widget.plotter.remove_actor("selection_markers")
        except Exception:
            pass
        
        if len(selection_indices) == 0:
            return
        
        # Get trajectory mesh to access points
        meshes = self._widget.plotter.mesh.values() if hasattr(self._widget.plotter, 'mesh') else []
        
        for mesh in meshes:
            if hasattr(mesh, 'points') and len(mesh.points) > 0:
                # Get selected points
                valid_indices = selection_indices[selection_indices < len(mesh.points)]
                if len(valid_indices) == 0:
                    continue
                    
                selected_points = mesh.points[valid_indices]
                
                # Create point cloud for selection
                selection_cloud = pv.PolyData(selected_points)
                
                # Add highlighted markers
                self._widget.plotter.add_mesh(
                    selection_cloud,
                    color="orange",
                    point_size=12,
                    render_points_as_spheres=True,
                    name="selection_markers"
                )
                
                logger.debug("trajectory3d_selection_updated",
                           n_selected=len(valid_indices))
                break

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta trajetória 3D"""
        if self._widget:
            if format in ["png", "jpg"]:
                self._widget.export_image(file_path, **kwargs)
            else:
                self._widget.export_3d_model(file_path, format)


class Surface3D(BaseFigure):
    """Visualização de superfície 3D"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Plot3DWidget | None = None

    def render(self, dataset: Dataset, time_axis: bool = True) -> Plot3DWidget:
        """
        Cria superfície 3D com tempo e múltiplas séries

        Args:
            dataset: Dataset com múltiplas séries
            time_axis: Se usar tempo como eixo X
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = Plot3DWidget(self.config)

        # Clear existing data
        self._widget.clear()

        series_list = list(dataset.series.values())
        if len(series_list) < 2:
            raise ValueError("Need at least 2 series for surface plot")

        # Create mesh grid
        n_time = len(dataset.t_seconds)
        n_series = len(series_list)

        if time_axis:
            # X = time, Y = series index, Z = values
            X, Y = np.meshgrid(dataset.t_seconds, range(n_series))
            Z = np.array([series.values for series in series_list])
        else:
            # More experimental configuration
            X, Y = np.meshgrid(range(n_series), dataset.t_seconds)
            Z = np.array([series.values for series in series_list]).T

        # Add surface
        self._widget.add_surface(
            x=X, y=Y, z=Z,
            scalars=Z,
            name="multi_series_surface",
        )

        # Reset camera
        self._widget.reset_camera()

        logger.info("surface3d_rendered",
                   n_series=n_series,
                   n_time=n_time)

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual na superfície 3D
        
        Destaca células/regiões selecionadas da superfície.
        
        Args:
            selection_indices: Índices dos pontos/células a destacar
        """
        if self._widget is None or self._widget.plotter is None:
            return
        
        # Remove previous selection overlay
        try:
            self._widget.plotter.remove_actor("surface_selection")
        except Exception:
            pass
        
        if len(selection_indices) == 0:
            return
        
        # Get surface mesh
        meshes = list(self._widget.plotter.mesh.values()) if hasattr(self._widget.plotter, 'mesh') else []
        
        for mesh in meshes:
            if hasattr(mesh, 'points') and len(mesh.points) > 0:
                # Get selected points from the surface
                valid_indices = selection_indices[selection_indices < len(mesh.points)]
                if len(valid_indices) == 0:
                    continue
                
                # Create extraction of selected region
                selected_points = mesh.points[valid_indices]
                
                # Create highlighted point cloud
                selection_cloud = pv.PolyData(selected_points)
                
                # Add selection overlay with distinct color
                self._widget.plotter.add_mesh(
                    selection_cloud,
                    color="orange",
                    point_size=8,
                    render_points_as_spheres=True,
                    opacity=0.9,
                    name="surface_selection"
                )
                
                logger.debug("surface3d_selection_updated",
                           n_selected=len(valid_indices))
                break

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta superfície 3D"""
        if self._widget:
            if format in ["png", "jpg"]:
                self._widget.export_image(file_path, **kwargs)
            else:
                self._widget.export_3d_model(file_path, format)


class VolumetricPlot(BaseFigure):
    """Visualização volumétrica"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Plot3DWidget | None = None

    def render(self, x_series: Series, y_series: Series, z_series: Series,
               bins: int = 20) -> Plot3DWidget:
        """
        Cria visualização volumétrica com densidade de pontos

        Args:
            x_series, y_series, z_series: Séries das três dimensões
            bins: Resolução da grade volumétrica
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = Plot3DWidget(self.config)

        # Clear existing data
        self._widget.clear()

        # Sync data
        min_len = min(len(x_series.values), len(y_series.values), len(z_series.values))
        x_data = x_series.values[:min_len]
        y_data = y_series.values[:min_len]
        z_data = z_series.values[:min_len]

        # Create 3D histogram
        hist, edges = np.histogramdd([x_data, y_data, z_data], bins=bins)

        # Get bin centers
        x_centers = (edges[0][:-1] + edges[0][1:]) / 2
        y_centers = (edges[1][:-1] + edges[1][1:]) / 2
        z_centers = (edges[2][:-1] + edges[2][1:]) / 2

        # Create meshgrid
        X, Y, Z = np.meshgrid(x_centers, y_centers, z_centers, indexing="ij")

        # Flatten and filter non-zero density
        points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
        densities = hist.ravel()

        mask = densities > 0
        points_filtered = points[mask]
        densities_filtered = densities[mask]

        # Add point cloud with density coloring
        self._widget.add_point_cloud(
            points=points_filtered,
            scalars=densities_filtered,
            name="density_cloud",
            point_size=8,
            cmap="hot",
        )

        # Reset camera
        self._widget.reset_camera()

        logger.info("volumetric_plot_rendered",
                   original_points=min_len,
                   density_points=len(points_filtered),
                   bins=bins)

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual"""

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta visualização volumétrica"""
        if self._widget:
            if format in ["png", "jpg"]:
                self._widget.export_image(file_path, **kwargs)
            else:
                self._widget.export_3d_model(file_path, format)


# =============================================================================
# Standalone functions and Figure3D class for test compatibility
# =============================================================================

class Figure3D:
    """
    High-level 3D figure class for visualization.
    
    This class provides a simple interface for creating 3D visualizations
    without requiring a VizConfig.
    """

    def __init__(self, title: str = "3D Figure", background: str = "white"):
        """
        Initialize a 3D figure.
        
        Args:
            title: Title for the figure
            background: Background color
        """
        self.title = title
        self.background = background
        self._plotter = None
        self._meshes = []

        if PYVISTA_AVAILABLE:
            try:
                self._plotter = pv.Plotter(off_screen=True)
                self._plotter.set_background(background)
            except Exception as e:
                logger.warning(f"Could not create plotter: {e}")

    def add_trajectory(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                       colormap: str = "viridis", color_values: np.ndarray = None,
                       line_width: float = 2.0, **kwargs):
        """Add a 3D trajectory to the figure."""
        if not PYVISTA_AVAILABLE or self._plotter is None:
            return None

        points = np.column_stack([x, y, z])
        spline = pv.Spline(points, n_points=len(points))

        if color_values is not None:
            spline["scalars"] = color_values
            self._plotter.add_mesh(spline, scalars="scalars", cmap=colormap,
                                   line_width=line_width, render_lines_as_tubes=True)
        else:
            self._plotter.add_mesh(spline, cmap=colormap, line_width=line_width,
                                   render_lines_as_tubes=True)

        self._meshes.append(spline)
        return spline

    def add_scatter(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                    point_size: float = 5.0, color: str = "blue",
                    colormap: str = None, scalars: np.ndarray = None, **kwargs):
        """Add a 3D scatter plot."""
        if not PYVISTA_AVAILABLE or self._plotter is None:
            return None

        points = np.column_stack([x, y, z])
        cloud = pv.PolyData(points)

        if scalars is not None and colormap:
            cloud["scalars"] = scalars
            self._plotter.add_mesh(cloud, scalars="scalars", cmap=colormap,
                                   point_size=point_size, render_points_as_spheres=True)
        else:
            self._plotter.add_mesh(cloud, color=color, point_size=point_size,
                                   render_points_as_spheres=True)

        self._meshes.append(cloud)
        return cloud

    def add_surface(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                    colormap: str = "viridis", opacity: float = 0.8, **kwargs):
        """Add a 3D surface."""
        if not PYVISTA_AVAILABLE or self._plotter is None:
            return None

        grid = pv.StructuredGrid(x, y, z)
        self._plotter.add_mesh(grid, cmap=colormap, opacity=opacity)
        self._meshes.append(grid)
        return grid

    def add_mesh(self, vertices: np.ndarray, faces: np.ndarray,
                 color: str = "gray", opacity: float = 1.0, **kwargs):
        """Add a 3D mesh."""
        if not PYVISTA_AVAILABLE or self._plotter is None:
            return None

        # Convert faces to VTK format
        n_faces = len(faces)
        vtk_faces = np.zeros(n_faces * 4, dtype=np.int64)
        for i, face in enumerate(faces):
            vtk_faces[i*4] = 3
            vtk_faces[i*4+1:i*4+4] = face

        mesh = pv.PolyData(vertices, vtk_faces)
        self._plotter.add_mesh(mesh, color=color, opacity=opacity)
        self._meshes.append(mesh)
        return mesh

    def set_camera_position(self, position: tuple, focal_point: tuple = None, up: tuple = None):
        """Set camera position."""
        if self._plotter is not None:
            self._plotter.camera_position = position

    def show_axes(self, show: bool = True):
        """Show/hide axes."""
        if self._plotter is not None:
            if show:
                self._plotter.add_axes()

    def show_grid(self, show: bool = True):
        """Show/hide grid."""
        if self._plotter is not None:
            if show:
                self._plotter.show_grid()

    def show_bounding_box(self, show: bool = True):
        """Show/hide bounding box."""
        if self._plotter is not None and self._meshes:
            if show:
                self._plotter.add_bounding_box()

    def set_lighting(self, ambient: float = 0.3, diffuse: float = 0.7, specular: float = 0.2):
        """Set lighting parameters."""
        if self._plotter is not None:
            pass  # PyVista handles lighting differently

    def export_image(self, filepath: str, resolution: tuple = (1920, 1080)):
        """Export to image file."""
        if self._plotter is not None:
            self._plotter.screenshot(filepath, window_size=resolution)

    def export_stl(self, filepath: str):
        """Export to STL format."""
        if self._meshes:
            combined = self._meshes[0]
            for mesh in self._meshes[1:]:
                combined = combined.merge(mesh)
            combined.save(filepath)

    def export_obj(self, filepath: str):
        """Export to OBJ format."""
        if self._meshes:
            combined = self._meshes[0]
            for mesh in self._meshes[1:]:
                combined = combined.merge(mesh)
            combined.save(filepath)

    def animate_rotation(self, filepath: str, n_frames: int = 60, fps: int = 30):
        """Create rotation animation."""
        if self._plotter is None:
            return

        # This would need moviepy or similar for actual animation
        logger.info(f"Animation export requested: {filepath}, {n_frames} frames at {fps} fps")

    def clear(self):
        """Clear all meshes."""
        self._meshes.clear()
        if self._plotter is not None:
            self._plotter.clear()

    def close(self):
        """Close the figure."""
        if self._plotter is not None:
            self._plotter.close()


def plot_trajectory_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                       colormap: str = "viridis", color_values: np.ndarray = None,
                       title: str = "3D Trajectory", **kwargs):
    """
    Create a 3D trajectory plot.
    
    Args:
        x, y, z: Coordinate arrays
        colormap: Colormap name
        color_values: Optional values for coloring
        title: Plot title
        **kwargs: Additional arguments
        
    Returns:
        Figure3D instance or None
    """
    fig = Figure3D(title=title)
    fig.add_trajectory(x, y, z, colormap=colormap, color_values=color_values, **kwargs)
    return fig


def scatter3d(x: np.ndarray, y: np.ndarray, z: np.ndarray,
              point_size: float = 5.0, color: str = "blue",
              colormap: str = None, scalars: np.ndarray = None,
              title: str = "3D Scatter", **kwargs):
    """
    Create a 3D scatter plot.
    
    Args:
        x, y, z: Coordinate arrays
        point_size: Size of points
        color: Point color
        colormap: Optional colormap
        scalars: Optional scalar values for coloring
        title: Plot title
        
    Returns:
        Figure3D instance or None
    """
    fig = Figure3D(title=title)
    fig.add_scatter(x, y, z, point_size=point_size, color=color,
                    colormap=colormap, scalars=scalars, **kwargs)
    return fig


def surface3d(x: np.ndarray, y: np.ndarray, z: np.ndarray,
              colormap: str = "viridis", opacity: float = 0.8,
              title: str = "3D Surface", **kwargs):
    """
    Create a 3D surface plot.
    
    Args:
        x, y, z: 2D coordinate arrays
        colormap: Colormap name
        opacity: Surface opacity
        title: Plot title
        
    Returns:
        Figure3D instance or None
    """
    fig = Figure3D(title=title)
    fig.add_surface(x, y, z, colormap=colormap, opacity=opacity, **kwargs)
    return fig


def mesh3d(vertices: np.ndarray, faces: np.ndarray,
           color: str = "gray", opacity: float = 1.0,
           title: str = "3D Mesh", **kwargs):
    """
    Create a 3D mesh plot.
    
    Args:
        vertices: Vertex coordinates (Nx3)
        faces: Face indices (Mx3)
        color: Mesh color
        opacity: Mesh opacity
        title: Plot title
        
    Returns:
        Figure3D instance or None
    """
    fig = Figure3D(title=title)
    fig.add_mesh(vertices, faces, color=color, opacity=opacity, **kwargs)
    return fig


# =============================================================================
# Utility functions
# =============================================================================

def get_available_colormaps() -> list:
    """Get list of available colormaps."""
    return [
        "viridis", "plasma", "inferno", "magma", "cividis",
        "hot", "cool", "coolwarm", "jet", "rainbow",
        "gray", "bone", "copper", "spring", "summer",
        "autumn", "winter", "spectral", "RdYlBu", "RdYlGn"
    ]


def create_mesh(vertices: np.ndarray, faces: np.ndarray) -> "pv.PolyData":
    """
    Create a PyVista mesh from vertices and faces.
    
    Args:
        vertices: Vertex coordinates (Nx3)
        faces: Face indices in VTK format (e.g., [3, v0, v1, v2] for triangles)
        
    Returns:
        PyVista PolyData mesh
    """
    if not PYVISTA_AVAILABLE:
        raise ImportError("PyVista not available")
    
    # Create the mesh
    mesh = pv.PolyData(vertices, faces)
    return mesh


def apply_colormap(values: np.ndarray, colormap: str = "viridis", 
                   vmin: float = None, vmax: float = None) -> np.ndarray:
    """
    Apply a colormap to scalar values.
    
    Args:
        values: Scalar values to color
        colormap: Name of the colormap
        vmin: Minimum value for normalization (default: min of values)
        vmax: Maximum value for normalization (default: max of values)
        
    Returns:
        RGBA color array (Nx4)
    """
    import matplotlib.pyplot as plt

    # Get the colormap
    cmap = plt.get_cmap(colormap)
    
    # Normalize values
    if vmin is None:
        vmin = np.min(values)
    if vmax is None:
        vmax = np.max(values)
    
    if vmax == vmin:
        normalized = np.zeros_like(values)
    else:
        normalized = (values - vmin) / (vmax - vmin)
    
    # Apply colormap
    colors = cmap(normalized)
    return colors


def export_stl(figure: Figure3D, filepath: str):
    """Export figure to STL format."""
    figure.export_stl(filepath)


def export_obj(figure: Figure3D, filepath: str):
    """Export figure to OBJ format."""
    figure.export_obj(filepath)
