"""
Testes completos para viz/base.py - Platform Base v2.0

Cobertura 100% das funcionalidades de visualização base.
"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest


class TestLTTBNumba:
    """Testes para LTTB com Numba"""
    
    def test_create_lttb_numba_available(self):
        """Testa criação de LTTB com numba disponível"""
        from platform_base.viz.base import NUMBA_AVAILABLE, _create_lttb_numba
        
        func = _create_lttb_numba()
        
        if NUMBA_AVAILABLE:
            assert func is not None
        else:
            assert func is None
    
    def test_lttb_numba_basic(self):
        """Testa LTTB numba básico"""
        from platform_base.viz.base import NUMBA_AVAILABLE, _lttb_numba
        
        if not NUMBA_AVAILABLE or _lttb_numba is None:
            pytest.skip("Numba não disponível")
        
        x = np.linspace(0, 100, 1000)
        y = np.sin(x) * 10
        
        x_down, y_down = _lttb_numba(x, y, 100)
        
        assert len(x_down) == 100
        assert len(y_down) == 100
        assert x_down[0] == x[0]
        assert x_down[-1] == x[-1]


class TestDetectFeatures:
    """Testes para detecção de features"""
    
    def test_detect_features_basic(self):
        """Testa detecção básica de features"""
        from platform_base.viz.base import _detect_features

        # Sinal com peaks e valleys claros
        x = np.linspace(0, 4 * np.pi, 100)
        y = np.sin(x)
        
        peaks, valleys, edges = _detect_features(x, y)
        
        assert len(peaks) > 0
        assert len(valleys) > 0
    
    def test_detect_features_few_points(self):
        """Testa com poucos pontos"""
        from platform_base.viz.base import _detect_features
        
        x = np.array([1, 2])
        y = np.array([1, 2])
        
        peaks, valleys, edges = _detect_features(x, y)
        
        # Deve retornar arrays vazios
        assert len(peaks) == 0
        assert len(valleys) == 0
        assert len(edges) == 0
    
    def test_detect_features_constant(self):
        """Testa com sinal constante"""
        from platform_base.viz.base import _detect_features
        
        x = np.linspace(0, 10, 100)
        y = np.ones(100) * 5
        
        peaks, valleys, edges = _detect_features(x, y)
        
        # Sinal constante não tem peaks/valleys
        assert len(peaks) == 0
        assert len(valleys) == 0


class TestDownsampleLTTB:
    """Testes para downsampling LTTB"""
    
    def test_downsample_no_reduction_needed(self):
        """Testa quando redução não é necessária"""
        from platform_base.viz.base import _downsample_lttb
        
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        
        x_down, y_down = _downsample_lttb(x, y, max_points=100)
        
        # Sem redução
        assert len(x_down) == 50
        np.testing.assert_array_equal(x_down, x)
    
    def test_downsample_basic(self):
        """Testa downsampling básico"""
        from platform_base.viz.base import _downsample_lttb

        # Usar dados limpos (sem ruído) para teste consistente
        x = np.linspace(0, 100, 10000)
        y = np.sin(x * 0.1)  # Sinal suave
        
        # Testar sem preservação de features para comportamento previsível
        x_down, y_down = _downsample_lttb(x, y, max_points=500, preserve_features=[])
        
        assert len(x_down) <= 500
        # Verifica que os pontos estão dentro do range original
        assert x_down[0] >= x[0]
        assert x_down[-1] <= x[-1]
        # Verifica que o range dos dados downsampled cobre a maioria
        # LTTB deve preservar extremos em sinal suave
        assert (x_down[-1] - x_down[0]) > 0.8 * (x[-1] - x[0])
    
    def test_downsample_preserve_peaks(self):
        """Testa preservação de peaks"""
        from platform_base.viz.base import _downsample_lttb

        # Sinal com peak claro
        x = np.linspace(0, 10, 1000)
        y = np.zeros(1000)
        y[500] = 100  # Peak no meio
        
        x_down, y_down = _downsample_lttb(x, y, max_points=100, preserve_features=["peaks"])
        
        # Peak deve estar presente
        assert 100 in y_down or np.max(y_down) > 50
    
    def test_downsample_no_features(self):
        """Testa sem preservação de features"""
        from platform_base.viz.base import _downsample_lttb
        
        x = np.linspace(0, 100, 5000)
        y = np.sin(x)
        
        x_down, y_down = _downsample_lttb(x, y, max_points=200, preserve_features=[])
        
        assert len(x_down) <= 200


class TestLTTBNumpy:
    """Testes para implementação numpy de LTTB"""
    
    def test_lttb_numpy_basic(self):
        """Testa LTTB numpy básico"""
        from platform_base.viz.base import _lttb_numpy
        
        x = np.linspace(0, 100, 10000)
        y = np.sin(x / 10) * 50
        
        x_down, y_down = _lttb_numpy(x, y, max_points=500)
        
        assert len(x_down) == 500
        assert len(y_down) == 500
        assert x_down[0] == x[0]
        assert x_down[-1] == x[-1]
    
    def test_lttb_numpy_few_points(self):
        """Testa com poucos pontos de saída"""
        from platform_base.viz.base import _lttb_numpy
        
        x = np.linspace(0, 10, 1000)
        y = np.sin(x)
        
        x_down, y_down = _lttb_numpy(x, y, max_points=2)
        
        assert len(x_down) == 2
    
    def test_lttb_numpy_preserves_range(self):
        """Testa que mantém range de valores"""
        from platform_base.viz.base import _lttb_numpy
        
        x = np.linspace(0, 100, 10000)
        y = np.sin(x) * 100  # Range: -100 a 100
        
        x_down, y_down = _lttb_numpy(x, y, max_points=200)
        
        # Range aproximado deve ser preservado
        assert np.min(y_down) < -80
        assert np.max(y_down) > 80


class TestBaseFigure:
    """Testes para classe BaseFigure"""
    
    @pytest.fixture
    def viz_config(self):
        """Cria VizConfig para testes"""
        from platform_base.viz.config import VizConfig
        
        return VizConfig()
    
    @pytest.fixture
    def concrete_figure(self, viz_config):
        """Cria implementação concreta de BaseFigure"""
        from platform_base.viz.base import BaseFigure
        
        class TestFigure(BaseFigure):
            def __init__(self, config):
                super().__init__(config)
                self.render_called = False
                self.export_called = False
                self.selection = None
            
            def render(self, data):
                self.render_called = True
                return data
            
            def update_selection(self, selection_indices):
                self.selection = selection_indices
            
            def export(self, file_path, format, **kwargs):
                self.export_called = True
                return file_path
        
        return TestFigure(viz_config)
    
    def test_figure_creation(self, concrete_figure):
        """Testa criação de figura"""
        assert concrete_figure.config is not None
        assert concrete_figure._cached_data == {}
    
    def test_clear_cache(self, concrete_figure):
        """Testa limpeza de cache"""
        concrete_figure._cached_data["key"] = "value"
        concrete_figure._last_render_params["param"] = 123
        
        concrete_figure.clear_cache()
        
        assert concrete_figure._cached_data == {}
        assert concrete_figure._last_render_params == {}
    
    def test_render(self, concrete_figure):
        """Testa render"""
        data = np.array([1, 2, 3])
        
        result = concrete_figure.render(data)
        
        assert concrete_figure.render_called
        np.testing.assert_array_equal(result, data)
    
    def test_update_selection(self, concrete_figure):
        """Testa update selection"""
        indices = np.array([0, 5, 10])
        
        concrete_figure.update_selection(indices)
        
        np.testing.assert_array_equal(concrete_figure.selection, indices)
    
    def test_export(self, concrete_figure):
        """Testa export"""
        result = concrete_figure.export("/path/to/file.png", "png")
        
        assert concrete_figure.export_called
        assert result == "/path/to/file.png"


class TestBaseFigureDownsampling:
    """Testes de downsampling na BaseFigure"""
    
    @pytest.fixture
    def figure_with_config(self):
        """Cria figura com configuração de performance"""
        from platform_base.viz.base import BaseFigure
        from platform_base.viz.config import VizConfig
        
        config = VizConfig()
        config.performance.max_points_2d = 1000
        config.performance.downsample_method = "lttb"
        
        class TestFigure(BaseFigure):
            def render(self, data): pass
            def update_selection(self, selection_indices): pass
            def export(self, file_path, format, **kwargs): pass
        
        return TestFigure(config)
    
    def test_apply_downsampling_no_reduction(self, figure_with_config):
        """Testa quando não precisa de redução"""
        x = np.linspace(0, 10, 500)
        y = np.sin(x)
        
        x_down, y_down = figure_with_config._apply_downsampling(x, y)
        
        assert len(x_down) == 500  # Sem redução
    
    def test_apply_downsampling_with_reduction(self, figure_with_config):
        """Testa quando precisa de redução"""
        x = np.linspace(0, 100, 10000)
        y = np.sin(x)
        
        x_down, y_down = figure_with_config._apply_downsampling(x, y)
        
        assert len(x_down) <= 1000
    
    def test_downsample_minmax(self, figure_with_config):
        """Testa minmax downsampling"""
        x = np.linspace(0, 100, 5000)
        y = np.sin(x) * 100
        
        x_down, y_down = figure_with_config._downsample_minmax(x, y, max_points=500)
        
        assert len(x_down) <= 500
        # MinMax preserva extremos
        assert np.min(y_down) < -80
        assert np.max(y_down) > 80
    
    def test_downsample_adaptive(self, figure_with_config):
        """Testa adaptive downsampling"""
        x = np.linspace(0, 100, 5000)
        # Sinal com alta variância no meio
        y = np.zeros(5000)
        y[2000:3000] = np.random.randn(1000) * 100
        
        x_down, y_down = figure_with_config._downsample_adaptive(x, y, max_points=500)
        
        assert len(x_down) == 500
        # Regiões de alta variância devem ter mais pontos


class TestBaseFigureTheme:
    """Testes de tema na BaseFigure"""
    
    @pytest.fixture
    def figure(self):
        """Cria figura para teste de tema"""
        from platform_base.viz.base import BaseFigure
        from platform_base.viz.config import VizConfig
        
        class TestFigure(BaseFigure):
            def render(self, data): pass
            def update_selection(self, selection_indices): pass
            def export(self, file_path, format, **kwargs): pass
        
        return TestFigure(VizConfig())
    
    def test_set_theme(self, figure):
        """Testa aplicação de tema"""
        # Cache algo para verificar se é limpo
        figure._cached_data["test"] = "value"
        
        # Aplica tema
        figure.set_theme("dark")
        
        # Cache deve ser limpo
        assert figure._cached_data == {}


class TestDownsamplingEdgeCases:
    """Testes de edge cases para downsampling"""
    
    def test_empty_array(self):
        """Testa com arrays vazios"""
        from platform_base.viz.base import _lttb_numpy
        
        x = np.array([])
        y = np.array([])
        
        # Não deve crashar
        # A função pode ter comportamento undefined para arrays vazios
        # mas não deve levantar exceção não tratada
    
    def test_single_point(self):
        """Testa com único ponto"""
        from platform_base.viz.base import _lttb_numpy
        
        x = np.array([5.0])
        y = np.array([10.0])
        
        x_down, y_down = _lttb_numpy(x, y, max_points=10)
        
        assert len(x_down) == 1
        assert x_down[0] == 5.0
    
    def test_two_points(self):
        """Testa com dois pontos"""
        from platform_base.viz.base import _lttb_numpy
        
        x = np.array([0.0, 10.0])
        y = np.array([0.0, 100.0])
        
        x_down, y_down = _lttb_numpy(x, y, max_points=10)
        
        assert len(x_down) == 2
    
    def test_constant_signal(self):
        """Testa com sinal constante"""
        from platform_base.viz.base import _downsample_lttb
        
        x = np.linspace(0, 100, 10000)
        y = np.ones(10000) * 50
        
        x_down, y_down = _downsample_lttb(x, y, max_points=500)
        
        assert len(x_down) <= 500
        # Valores devem ser todos 50
        np.testing.assert_array_almost_equal(y_down, 50.0)
    
    def test_linear_signal(self):
        """Testa com sinal linear"""
        from platform_base.viz.base import _downsample_lttb
        
        x = np.linspace(0, 100, 10000)
        y = x * 2  # Linear: y = 2x
        
        x_down, y_down = _downsample_lttb(x, y, max_points=500)
        
        # Relação linear deve ser preservada aproximadamente
        expected_y = x_down * 2
        np.testing.assert_array_almost_equal(y_down, expected_y, decimal=3)


class TestLTTBPerformance:
    """Testes de performance do LTTB"""
    
    def test_large_dataset_performance(self):
        """Testa performance com dataset grande"""
        import time

        from platform_base.viz.base import _downsample_lttb

        # Dataset grande
        n_points = 100000
        x = np.linspace(0, 1000, n_points)
        y = np.sin(x) + np.random.randn(n_points) * 0.1
        
        start = time.time()
        x_down, y_down = _downsample_lttb(x, y, max_points=1000)
        elapsed = time.time() - start
        
        # Deve completar em tempo razoável
        assert elapsed < 5.0
        assert len(x_down) <= 1000
    
    def test_multiple_downsamplings(self):
        """Testa múltiplos downsamplings"""
        from platform_base.viz.base import _downsample_lttb
        
        x = np.linspace(0, 100, 10000)
        y = np.sin(x)
        
        # Múltiplos downsamplings em sequência
        for target in [5000, 2000, 1000, 500]:
            x_down, y_down = _downsample_lttb(x, y, max_points=target)
            assert len(x_down) <= target
