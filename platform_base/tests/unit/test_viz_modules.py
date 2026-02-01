"""
Testes para módulos de visualização - viz/
Cobertura para base, config, datetime_axis
"""
from datetime import datetime, timedelta

import numpy as np
import pytest


class TestVizBase:
    """Testes para viz/base.py."""
    
    def test_import_base(self):
        """Testa importação do módulo base."""
        try:
            from platform_base.viz import base
            assert base is not None
        except ImportError:
            pytest.skip("viz.base não disponível")
    
    def test_series_visualization_data(self):
        """Testa SeriesVisualizationData."""
        try:
            from platform_base.viz.base import SeriesVisualizationData
            
            data = SeriesVisualizationData(
                series_id="test_series",
                dataset_id="test_dataset",
                t_seconds=np.array([0.0, 1.0, 2.0]),
                values=np.array([1.0, 2.0, 3.0]),
                name="Test Series"
            )
            
            assert data.series_id == "test_series"
            assert len(data.t_seconds) == 3
            assert len(data.values) == 3
        except ImportError:
            pytest.skip("SeriesVisualizationData não disponível")
    
    def test_series_visualization_data_n_points(self):
        """Testa propriedade n_points."""
        try:
            from platform_base.viz.base import SeriesVisualizationData
            
            data = SeriesVisualizationData(
                series_id="test",
                dataset_id="ds",
                t_seconds=np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
                values=np.array([1.0, 2.0, 3.0, 4.0, 5.0])
            )
            
            assert data.n_points == 5
        except ImportError:
            pytest.skip("SeriesVisualizationData não disponível")


class TestVizConfig:
    """Testes para viz/config.py."""
    
    def test_import_config(self):
        """Testa importação do módulo config."""
        from platform_base.viz.config import VizConfig
        assert VizConfig is not None
    
    def test_viz_config_creation(self):
        """Testa criação de VizConfig."""
        from platform_base.viz.config import VizConfig
        
        config = VizConfig()
        assert config is not None
    
    def test_viz_config_line_width(self):
        """Testa configuração de estilo."""
        from platform_base.viz.config import VizConfig
        
        config = VizConfig()
        # Deve ter configurações de estilo
        assert hasattr(config, 'style') or hasattr(config, 'plot_2d_config')
    
    def test_viz_config_colors(self):
        """Testa configuração de cores."""
        from platform_base.viz.config import VizConfig
        
        config = VizConfig()
        # Deve ter paleta de cores
        assert hasattr(config, 'colors') or hasattr(config, 'color_palette')


class TestDatetimeAxis:
    """Testes para viz/datetime_axis.py."""
    
    def test_import(self):
        """Testa importação."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        assert DateTimeAxisItem is not None
    
    @pytest.mark.skip(reason="Requer ambiente Qt completo")
    def test_axis_creation(self):
        """Testa criação do eixo."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        
        axis = DateTimeAxisItem()
        assert axis is not None
    
    @pytest.mark.skip(reason="Requer ambiente Qt completo")
    def test_tick_strings(self):
        """Testa geração de strings para ticks."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        
        axis = DateTimeAxisItem()
        
        # Valores em segundos desde epoch
        values = [0.0, 3600.0, 7200.0]  # 0h, 1h, 2h
        
        if hasattr(axis, 'tickStrings'):
            strings = axis.tickStrings(values, 1.0, 3)
            assert len(strings) == 3


class TestVizStreaming:
    """Testes para viz/streaming.py."""
    
    def test_import_streaming_engine(self):
        """Testa importação do StreamingEngine."""
        try:
            from platform_base.viz.streaming import StreamingEngine
            assert StreamingEngine is not None
        except ImportError:
            pytest.skip("StreamingEngine não disponível")
    
    def test_import_streaming_state(self):
        """Testa importação do StreamingState."""
        try:
            from platform_base.viz.streaming import StreamingState
            assert StreamingState is not None
        except ImportError:
            pytest.skip("StreamingState não disponível")
    
    def test_play_state_model(self):
        """Testa PlayState model."""
        try:
            from platform_base.viz.streaming import PlayState

            # PlayState é um Pydantic model
            state = PlayState()
            assert hasattr(state, 'is_playing')
            assert hasattr(state, 'is_paused')
            assert hasattr(state, 'is_stopped')
            # Default é stopped
            assert state.is_stopped == True
        except ImportError:
            pytest.skip("PlayState não disponível")


class TestVizImports:
    """Testa todas as importações do módulo viz."""
    
    def test_all_viz_imports(self):
        """Testa que todos os módulos podem ser importados."""
        from platform_base.viz import base
        from platform_base.viz.config import VizConfig
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        
        assert base is not None
        assert VizConfig is not None
        assert DateTimeAxisItem is not None
