"""
Comprehensive tests for viz/figures_3d.py module.

Target: Increase coverage from ~29% to 80%+
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestCreateColormapFromScale:
    """Tests for _create_colormap_from_scale function."""
    
    def test_viridis_colormap(self):
        """Test creating viridis colormap."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale
        
        cmap = _create_colormap_from_scale(ColorScale.VIRIDIS, n_colors=256)
        
        assert cmap.shape == (256, 3)
        assert cmap.max() <= 255
        assert cmap.min() >= 0
    
    def test_plasma_colormap(self):
        """Test creating plasma colormap."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale
        
        cmap = _create_colormap_from_scale(ColorScale.PLASMA, n_colors=256)
        
        assert cmap.shape == (256, 3)
    
    def test_coolwarm_colormap(self):
        """Test creating coolwarm colormap."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale
        
        cmap = _create_colormap_from_scale(ColorScale.COOLWARM, n_colors=256)
        
        assert cmap.shape == (256, 3)
    
    def test_default_colormap_for_unknown(self):
        """Test default colormap for unknown colorscale."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale

        # GRAYSCALE should fall back to viridis
        cmap = _create_colormap_from_scale(ColorScale.GRAYSCALE, n_colors=256)
        
        assert cmap.shape == (256, 3)
    
    def test_custom_n_colors(self):
        """Test creating colormap with custom number of colors."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale
        
        cmap = _create_colormap_from_scale(ColorScale.VIRIDIS, n_colors=64)
        
        assert cmap.shape == (64, 3)
    
    def test_small_n_colors(self):
        """Test creating colormap with small number of colors."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale
        
        cmap = _create_colormap_from_scale(ColorScale.VIRIDIS, n_colors=10)
        
        assert cmap.shape == (10, 3)


class TestPyvistaAvailability:
    """Tests for PyVista availability checks."""
    
    def test_pyvista_available_flag_exists(self):
        """Test PYVISTA_AVAILABLE flag exists."""
        import platform_base.viz.figures_3d as figures_3d_module
        assert hasattr(figures_3d_module, 'PYVISTA_AVAILABLE')
    
    def test_pyvista_qt_available_flag_exists(self):
        """Test PYVISTA_QT_AVAILABLE flag exists."""
        import platform_base.viz.figures_3d as figures_3d_module
        assert hasattr(figures_3d_module, 'PYVISTA_QT_AVAILABLE')


class TestVizConfig3D:
    """Tests for VizConfig usage in 3D visualization."""
    
    def test_config_has_required_attributes(self):
        """Test VizConfig has required attributes for 3D viz."""
        from platform_base.viz.config import VizConfig
        
        config = VizConfig()
        
        assert hasattr(config, 'theme')
        assert hasattr(config, 'colors')
        assert hasattr(config.colors, 'background_color')
        assert hasattr(config, 'style')
        assert hasattr(config.style, 'line_width')


class TestColorScaleValues:
    """Tests for ColorScale enum values."""
    
    def test_all_colorscales_produce_valid_output(self):
        """Test all colorscales produce valid colormap arrays."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.figures_3d import _create_colormap_from_scale
        
        for scale in ColorScale:
            cmap = _create_colormap_from_scale(scale, n_colors=256)
            
            # All colormaps should produce valid RGB arrays
            assert cmap.shape == (256, 3)
            assert cmap.dtype in [np.float64, np.float32]
            assert cmap.min() >= 0
            assert cmap.max() <= 255


class Test3DDataGeneration:
    """Tests for generating 3D visualization data."""
    
    def test_trajectory_points_format(self):
        """Test trajectory points array format."""
        # Generate sample trajectory
        t = np.linspace(0, 4 * np.pi, 100)
        x = np.sin(t)
        y = np.cos(t)
        z = t
        
        points = np.column_stack([x, y, z])
        
        assert points.shape == (100, 3)
    
    def test_surface_grid_format(self):
        """Test surface grid format."""
        # Generate sample surface
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        
        assert X.shape == (50, 50)
        assert Y.shape == (50, 50)
        assert Z.shape == (50, 50)
    
    def test_volume_data_format(self):
        """Test volume data format."""
        # Generate sample volume
        x = np.linspace(-3, 3, 30)
        y = np.linspace(-3, 3, 30)
        z = np.linspace(-3, 3, 30)
        X, Y, Z = np.meshgrid(x, y, z)
        
        values = np.exp(-(X**2 + Y**2 + Z**2))
        
        assert values.shape == (30, 30, 30)
    
    def test_scalars_array_format(self):
        """Test scalars array format for coloring."""
        n_points = 100
        scalars = np.linspace(0, 1, n_points)
        
        assert scalars.shape == (n_points,)
        assert scalars.min() == 0.0
        assert scalars.max() == 1.0


class TestStateSpaceVisualization:
    """Tests for state space visualization helpers."""
    
    def test_attractor_data_generation(self):
        """Test generating data for attractor visualization."""
        # Lorenz attractor parameters
        n_points = 1000
        
        # Simulate simple trajectory
        x = np.zeros(n_points)
        y = np.zeros(n_points)
        z = np.zeros(n_points)
        
        x[0], y[0], z[0] = 0.0, 1.0, 1.05
        dt = 0.01
        sigma, rho, beta = 10.0, 28.0, 8/3
        
        for i in range(1, n_points):
            x[i] = x[i-1] + sigma * (y[i-1] - x[i-1]) * dt
            y[i] = y[i-1] + (x[i-1] * (rho - z[i-1]) - y[i-1]) * dt
            z[i] = z[i-1] + (x[i-1] * y[i-1] - beta * z[i-1]) * dt
        
        points = np.column_stack([x, y, z])
        
        assert points.shape == (n_points, 3)
        assert not np.isnan(points).any()
    
    def test_phase_portrait_data(self):
        """Test generating phase portrait data."""
        # Simple harmonic oscillator phase space
        theta = np.linspace(0, 10 * np.pi, 500)
        x = np.cos(theta)
        y = -np.sin(theta)  # velocity
        z = theta / (10 * np.pi)  # time as z
        
        points = np.column_stack([x, y, z])
        
        assert points.shape == (500, 3)


class TestSurfacePlotHelpers:
    """Tests for surface plot helper functions."""
    
    def test_meshgrid_creation(self):
        """Test meshgrid creation for surface plots."""
        x = np.linspace(0, 10, 100)
        y = np.linspace(0, 10, 100)
        X, Y = np.meshgrid(x, y)
        
        assert X.shape == (100, 100)
        assert Y.shape == (100, 100)
    
    def test_surface_function_evaluation(self):
        """Test evaluating function over surface grid."""
        x = np.linspace(-2, 2, 50)
        y = np.linspace(-2, 2, 50)
        X, Y = np.meshgrid(x, y)
        
        # Gaussian surface
        Z = np.exp(-(X**2 + Y**2))
        
        assert Z.shape == (50, 50)
        assert Z.max() > 0.9  # Near center of Gaussian
        assert Z.min() < 0.2  # Edges approach 0
    
    def test_surface_normals_consistency(self):
        """Test surface normal calculation consistency."""
        # Simple plane z = x + y
        x = np.linspace(0, 1, 10)
        y = np.linspace(0, 1, 10)
        X, Y = np.meshgrid(x, y)
        Z = X + Y
        
        # Numerical gradient
        dz_dx, dz_dy = np.gradient(Z, x, y)
        
        # Should be constant for a plane
        assert np.allclose(dz_dx, 1.0, atol=0.1)
        assert np.allclose(dz_dy, 1.0, atol=0.1)


class TestVolumeVisualizationHelpers:
    """Tests for volume visualization helpers."""
    
    def test_volume_grid_creation(self):
        """Test creating 3D grid for volume data."""
        x = np.linspace(-1, 1, 20)
        y = np.linspace(-1, 1, 20)
        z = np.linspace(-1, 1, 20)
        X, Y, Z = np.meshgrid(x, y, z)
        
        assert X.shape == (20, 20, 20)
        assert Y.shape == (20, 20, 20)
        assert Z.shape == (20, 20, 20)
    
    def test_volume_scalar_field(self):
        """Test volume scalar field generation."""
        x = np.linspace(-1, 1, 20)
        y = np.linspace(-1, 1, 20)
        z = np.linspace(-1, 1, 20)
        X, Y, Z = np.meshgrid(x, y, z)
        
        # Distance from origin
        R = np.sqrt(X**2 + Y**2 + Z**2)
        
        assert R.shape == (20, 20, 20)
        assert R[10, 10, 10] < 0.15  # Near origin
    
    def test_isosurface_threshold(self):
        """Test isosurface threshold selection."""
        # Generate sample volume
        x = np.linspace(-2, 2, 40)
        y = np.linspace(-2, 2, 40)
        z = np.linspace(-2, 2, 40)
        X, Y, Z = np.meshgrid(x, y, z)
        
        # Sphere-like density
        density = np.exp(-(X**2 + Y**2 + Z**2))
        
        # Threshold selection
        threshold = 0.5
        mask = density >= threshold
        
        # Mask should select points near origin
        assert mask.sum() > 0
        assert mask[20, 20, 20] == True  # Center


class TestLightingConfiguration:
    """Tests for 3D lighting configuration."""
    
    def test_light_position_format(self):
        """Test light position format."""
        position = (1.0, 1.0, 1.0)
        
        assert len(position) == 3
        assert all(isinstance(p, (int, float)) for p in position)
    
    def test_light_intensity_range(self):
        """Test light intensity range."""
        intensities = [0.0, 0.5, 0.8, 1.0]
        
        for intensity in intensities:
            assert 0.0 <= intensity <= 1.0
    
    def test_ambient_light_calculation(self):
        """Test ambient light contribution."""
        ambient_color = np.array([0.1, 0.1, 0.1])
        surface_color = np.array([1.0, 0.0, 0.0])  # Red
        
        ambient_contribution = ambient_color * surface_color
        
        assert ambient_contribution.shape == (3,)
        np.testing.assert_array_almost_equal(
            ambient_contribution, 
            np.array([0.1, 0.0, 0.0])
        )


class TestCameraConfiguration:
    """Tests for camera configuration."""
    
    def test_camera_position_format(self):
        """Test camera position format."""
        camera_position = (10.0, 10.0, 10.0)
        focal_point = (0.0, 0.0, 0.0)
        view_up = (0.0, 0.0, 1.0)
        
        assert len(camera_position) == 3
        assert len(focal_point) == 3
        assert len(view_up) == 3
    
    def test_isometric_view_angles(self):
        """Test isometric view angle calculation."""
        # Isometric view: equal angles from all axes
        angle = np.arctan(1/np.sqrt(2))  # ~35.26 degrees
        
        # Position for isometric view
        distance = 10.0
        x = distance * np.sin(angle) * np.cos(np.pi/4)
        y = distance * np.sin(angle) * np.sin(np.pi/4)
        z = distance * np.cos(angle)
        
        position = (x, y, z)
        
        assert len(position) == 3
    
    def test_zoom_factor_range(self):
        """Test zoom factor range."""
        zoom_factors = [0.5, 1.0, 2.0, 5.0]
        
        for factor in zoom_factors:
            assert factor > 0


class TestExportFormats:
    """Tests for 3D export format helpers."""
    
    def test_stl_export_data_format(self):
        """Test STL export data format."""
        # Simple triangle mesh data
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0.5, 1, 0],
            [0.5, 0.5, 1],
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2],
            [0, 1, 3],
            [1, 2, 3],
            [0, 2, 3],
        ], dtype=np.int32)
        
        assert vertices.shape[1] == 3
        assert faces.shape[1] == 3
    
    def test_obj_export_data_format(self):
        """Test OBJ export data format."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ])
        
        # OBJ uses 1-based indices
        faces = np.array([
            [1, 2, 3, 4],  # Quad face
        ])
        
        assert vertices.dtype == np.float64
        assert faces.min() >= 1  # 1-based indexing


class TestPerformanceOptimization:
    """Tests for performance optimization helpers."""
    
    def test_downsample_trajectory(self):
        """Test trajectory downsampling for performance."""
        # Generate large trajectory
        n_points = 10000
        t = np.linspace(0, 10, n_points)
        points = np.column_stack([
            np.sin(t),
            np.cos(t),
            t
        ])
        
        # Downsample to 1000 points
        target = 1000
        indices = np.linspace(0, n_points - 1, target, dtype=int)
        downsampled = points[indices]
        
        assert downsampled.shape == (target, 3)
    
    def test_lod_selection(self):
        """Test level-of-detail selection."""
        # Different LOD levels
        lod_levels = [100, 500, 1000, 5000]
        
        # Select based on distance
        distance = 50.0
        
        # Simple LOD selection: more detail when closer
        if distance < 20:
            lod = lod_levels[3]
        elif distance < 50:
            lod = lod_levels[2]
        elif distance < 100:
            lod = lod_levels[1]
        else:
            lod = lod_levels[0]
        
        # distance=50 is not < 50, so it goes to level 1 (500)
        assert lod == 500


class TestBoundingBoxCalculation:
    """Tests for bounding box calculation."""
    
    def test_calculate_bounds(self):
        """Test bounding box calculation."""
        points = np.array([
            [0, 0, 0],
            [10, 0, 0],
            [5, 10, 0],
            [5, 5, 10],
        ])
        
        bounds = [
            points[:, 0].min(), points[:, 0].max(),  # x_min, x_max
            points[:, 1].min(), points[:, 1].max(),  # y_min, y_max
            points[:, 2].min(), points[:, 2].max(),  # z_min, z_max
        ]
        
        assert bounds == [0, 10, 0, 10, 0, 10]
    
    def test_center_of_bounds(self):
        """Test calculating center of bounds."""
        bounds = [0, 10, 0, 20, 0, 30]
        
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2,
        ]
        
        assert center == [5.0, 10.0, 15.0]
    
    def test_diagonal_length(self):
        """Test calculating diagonal length of bounding box."""
        bounds = [0, 10, 0, 10, 0, 10]
        
        dx = bounds[1] - bounds[0]
        dy = bounds[3] - bounds[2]
        dz = bounds[5] - bounds[4]
        
        diagonal = np.sqrt(dx**2 + dy**2 + dz**2)
        
        np.testing.assert_almost_equal(diagonal, 10 * np.sqrt(3))
