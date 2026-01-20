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

import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import time

try:
    import pyvista as pv
    import vtk
    from PyQt6.QtWidgets import QWidget, QVBoxLayout
    try:
        from pyvistaqt import QtInteractor
        PYVISTA_QT_AVAILABLE = True
    except ImportError:
        PYVISTA_QT_AVAILABLE = False
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    PYVISTA_QT_AVAILABLE = False

from platform_base.core.models import Dataset, Series
from platform_base.viz.base import BaseFigure
from platform_base.viz.config import VizConfig, ColorScale
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


if not PYVISTA_AVAILABLE:
    logger.error("pyvista_not_available", message="PyVista not available for 3D visualization")


def _create_colormap_from_scale(colorscale: ColorScale, n_colors: int = 256) -> np.ndarray:
    """Cria colormap NumPy compatível com PyVista"""
    if colorscale == ColorScale.VIRIDIS:
        from matplotlib.colors import LinearSegmentedColormap
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
    
    def __init__(self, config: VizConfig, parent: Optional[QWidget] = None):
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
    
    def add_trajectory(self, points: np.ndarray, scalars: Optional[np.ndarray] = None, 
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
            'line_width': self.config.style.line_width * 2,
            'render_lines_as_tubes': True,
            'name': name,
            **kwargs
        }
        
        if scalars is not None and len(scalars) == len(points):
            # Add scalars to spline
            spline[name + '_scalars'] = scalars
            plot_params['scalars'] = name + '_scalars'
            plot_params['cmap'] = 'viridis'
            plot_params['show_scalar_bar'] = True
        else:
            # Use solid color
            color = self.config.get_color_for_series(0)
            plot_params['color'] = color
        
        # Add to plotter
        actor = self.plotter.add_mesh(spline, **plot_params)
        
        # Add start/end markers
        start_sphere = pv.Sphere(center=points[0], radius=0.02)
        end_sphere = pv.Sphere(center=points[-1], radius=0.02)
        
        self.plotter.add_mesh(start_sphere, color='green', name=f"{name}_start")
        self.plotter.add_mesh(end_sphere, color='red', name=f"{name}_end")
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("trajectory_added", name=name, points=len(points), duration_ms=duration_ms)
        
        return actor
    
    def add_surface(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                   scalars: Optional[np.ndarray] = None, name: str = "surface", **kwargs):
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
            grid[name + '_scalars'] = scalars.ravel()
            scalar_name = name + '_scalars'
        else:
            scalar_name = None
        
        # Configure surface parameters
        surface_params = {
            'opacity': kwargs.get('opacity', 0.8),
            'show_edges': kwargs.get('show_edges', False),
            'cmap': kwargs.get('cmap', 'viridis'),
            'name': name,
            **kwargs
        }
        
        if scalar_name:
            surface_params['scalars'] = scalar_name
            surface_params['show_scalar_bar'] = True
        else:
            color = self.config.get_color_for_series(0)
            surface_params['color'] = color
        
        # Add surface to plotter
        actor = self.plotter.add_mesh(grid, **surface_params)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("surface_added", name=name, 
                   grid_shape=f"{x.shape[0]}x{x.shape[1]}", 
                   duration_ms=duration_ms)
        
        return actor
    
    def add_volume(self, volume_data: np.ndarray, spacing: Tuple[float, float, float] = (1, 1, 1),
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
            'scalars': name,
            'opacity': kwargs.get('opacity', [0, 0.2, 0.5, 0.8, 1.0]),
            'cmap': kwargs.get('cmap', 'viridis'),
            'show_scalar_bar': True,
            **kwargs
        }
        
        # Add volume to plotter
        actor = self.plotter.add_volume(grid, **volume_params)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("volume_added", name=name, 
                   shape=volume_data.shape, 
                   duration_ms=duration_ms)
        
        return actor
    
    def add_point_cloud(self, points: np.ndarray, scalars: Optional[np.ndarray] = None,
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
            cloud[name + '_scalars'] = scalars
            scalar_name = name + '_scalars'
        else:
            scalar_name = None
        
        # Point cloud parameters
        point_params = {
            'point_size': kwargs.get('point_size', self.config.style.marker_size),
            'render_points_as_spheres': kwargs.get('render_points_as_spheres', True),
            'name': name,
            **kwargs
        }
        
        if scalar_name:
            point_params['scalars'] = scalar_name
            point_params['cmap'] = kwargs.get('cmap', 'viridis')
            point_params['show_scalar_bar'] = True
        else:
            color = self.config.get_color_for_series(0)
            point_params['color'] = color
        
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
    
    def export_image(self, file_path: str, width: int = None, height: int = None):
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
            logger.error("plot3d_export_failed", file_path=file_path, error=str(e))
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
            logger.error("plot3d_model_export_failed", file_path=file_path, error=str(e))
            raise


class Trajectory3D(BaseFigure):
    """Wrapper para Plot3DWidget com interface para trajetórias 3D"""
    
    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Optional[Plot3DWidget] = None
    
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
            z_series.values[:min_len]
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
            name=f"{x_series.name}_{y_series.name}_{z_series.name}_trajectory"
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
        """Atualiza seleção visual"""
        # Placeholder implementation
        pass
    
    def export(self, file_path: str, format: str, **kwargs):
        """Exporta trajetória 3D"""
        if self._widget:
            if format in ['png', 'jpg']:
                self._widget.export_image(file_path, **kwargs)
            else:
                self._widget.export_3d_model(file_path, format)


class Surface3D(BaseFigure):
    """Visualização de superfície 3D"""
    
    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Optional[Plot3DWidget] = None
    
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
            name="multi_series_surface"
        )
        
        # Reset camera
        self._widget.reset_camera()
        
        logger.info("surface3d_rendered", 
                   n_series=n_series, 
                   n_time=n_time)
        
        return self._widget
    
    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual"""
        pass
    
    def export(self, file_path: str, format: str, **kwargs):
        """Exporta superfície 3D"""
        if self._widget:
            if format in ['png', 'jpg']:
                self._widget.export_image(file_path, **kwargs)
            else:
                self._widget.export_3d_model(file_path, format)


class VolumetricPlot(BaseFigure):
    """Visualização volumétrica"""
    
    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Optional[Plot3DWidget] = None
    
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
        X, Y, Z = np.meshgrid(x_centers, y_centers, z_centers, indexing='ij')
        
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
            cmap='hot'
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
        pass
    
    def export(self, file_path: str, format: str, **kwargs):
        """Exporta visualização volumétrica"""
        if self._widget:
            if format in ['png', 'jpg']:
                self._widget.export_image(file_path, **kwargs)
            else:
                self._widget.export_3d_model(file_path, format)
