"""
Tests for viz/state_cube.py and viz/multipanel.py

Tests for 3D state cube visualization and multipanel exports.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestStateCube3D:
    """Tests for StateCube3D class"""

    def test_state_cube_creation(self):
        """Test creating StateCube3D"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig(title="Test Cube")
        cube = StateCube3D(config=config)
        
        assert cube.config.title == "Test Cube"

    def test_state_cube_render(self):
        """Test rendering StateCube3D"""
        import plotly.graph_objects as go

        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig(title="State Space")
        cube = StateCube3D(config=config)
        
        # Create test data - 3D states
        states = np.array([
            [0, 0, 0],
            [1, 1, 1],
            [2, 2, 2],
            [3, 3, 3]
        ])
        
        fig = cube.render(states)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "State Space"

    def test_state_cube_render_random_data(self):
        """Test rendering with random data"""
        import plotly.graph_objects as go

        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig()
        cube = StateCube3D(config=config)
        
        # Random 3D points
        states = np.random.randn(100, 3)
        
        fig = cube.render(states)
        
        assert isinstance(fig, go.Figure)
        # Should have one Scatter3d trace
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Scatter3d)

    def test_state_cube_render_single_point(self):
        """Test rendering with single point"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig()
        cube = StateCube3D(config=config)
        
        states = np.array([[1, 2, 3]])
        
        fig = cube.render(states)
        
        # Should still render
        assert len(fig.data[0].x) == 1

    def test_state_cube_render_marker_mode(self):
        """Test that render uses markers mode"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig()
        cube = StateCube3D(config=config)
        
        states = np.random.randn(10, 3)
        fig = cube.render(states)
        
        assert fig.data[0].mode == "markers"

    def test_state_cube_coordinates(self):
        """Test that coordinates are correctly assigned"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig()
        cube = StateCube3D(config=config)
        
        states = np.array([
            [1, 2, 3],
            [4, 5, 6]
        ])
        
        fig = cube.render(states)
        
        # Verify x, y, z from columns 0, 1, 2
        np.testing.assert_array_equal(fig.data[0].x, [1, 4])
        np.testing.assert_array_equal(fig.data[0].y, [2, 5])
        np.testing.assert_array_equal(fig.data[0].z, [3, 6])


class TestMultipanelExport:
    """Tests for multipanel module export"""

    def test_multipanel_export(self):
        """Test that MultipanelPlot is exported from multipanel module"""
        from platform_base.viz.multipanel import MultipanelPlot

        # Should be importable
        assert MultipanelPlot is not None

    def test_multipanel_all(self):
        """Test __all__ exports"""
        from platform_base.viz import multipanel
        
        assert hasattr(multipanel, "__all__")
        assert "MultipanelPlot" in multipanel.__all__


class TestStateCubeEdgeCases:
    """Edge case tests for StateCube3D"""

    def test_state_cube_large_dataset(self):
        """Test with large dataset"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig(title="Large Data")
        cube = StateCube3D(config=config)
        
        # 10000 points
        states = np.random.randn(10000, 3)
        
        fig = cube.render(states)
        
        assert len(fig.data[0].x) == 10000

    def test_state_cube_float32(self):
        """Test with float32 data"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig()
        cube = StateCube3D(config=config)
        
        states = np.array([[1, 2, 3]], dtype=np.float32)
        
        fig = cube.render(states)
        
        # Should handle float32
        assert len(fig.data) == 1

    def test_state_cube_integer_data(self):
        """Test with integer data"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig()
        cube = StateCube3D(config=config)
        
        states = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
        
        fig = cube.render(states)
        
        assert len(fig.data) == 1


class TestStateCubeInheritance:
    """Tests for StateCube3D inheritance"""

    def test_inherits_from_base_figure(self):
        """Test that StateCube3D inherits from BaseFigure"""
        from platform_base.viz.base import BaseFigure
        from platform_base.viz.state_cube import StateCube3D
        
        assert issubclass(StateCube3D, BaseFigure)

    def test_has_config_attribute(self):
        """Test that StateCube3D has config from BaseFigure"""
        from platform_base.viz.config import PlotConfig
        from platform_base.viz.state_cube import StateCube3D
        
        config = PlotConfig(title="Config Test")
        cube = StateCube3D(config=config)
        
        assert hasattr(cube, 'config')
        assert cube.config.title == "Config Test"
