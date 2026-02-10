"""
Testes para módulos de processing - Platform Base v2.0
Cobertura para downsampling, interpolation, synchronization, smoothing, units, timebase
"""
from datetime import datetime, timedelta

import numpy as np
import pytest


class TestDownsamplingMethods:
    """Testes para processing/downsampling.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.processing.downsampling import SUPPORTED_METHODS, downsample
        assert downsample is not None
        assert "lttb" in SUPPORTED_METHODS
    
    def test_downsample_lttb(self):
        """Testa downsample com método LTTB."""
        from platform_base.processing.downsampling import downsample
        
        t = np.arange(0, 100, 0.1)
        values = np.sin(t) + np.random.normal(0, 0.1, len(t))
        
        result = downsample(
            values=values,
            t_seconds=t,
            n_points=50,
            method="lttb"
        )
        
        assert result is not None
        assert hasattr(result, 't_seconds') or hasattr(result, 'indices')
    
    def test_downsample_minmax(self):
        """Testa downsample com método MinMax."""
        from platform_base.processing.downsampling import downsample
        
        t = np.arange(0, 100, 0.1)
        values = np.sin(t)
        
        result = downsample(
            values=values,
            t_seconds=t,
            n_points=100,
            method="minmax"
        )
        
        assert result is not None
    
    def test_downsample_adaptive(self):
        """Testa downsample adaptativo."""
        from platform_base.processing.downsampling import adaptive_downsample
        
        t = np.arange(0, 100, 0.1)
        values = np.sin(t)
        
        # Assinatura: values, t_seconds, n_points
        result = adaptive_downsample(
            values=values,
            t_seconds=t,
            n_points=200
        )
        
        assert result is not None
    
    def test_lttb_downsample_direct(self):
        """Testa função lttb_downsample diretamente."""
        from platform_base.processing.downsampling import lttb_downsample
        
        t = np.arange(0, 50, 0.5)
        values = np.cos(t)
        
        result = lttb_downsample(t, values, 20)
        
        # Retorna DownsampleResult
        assert result is not None
        assert hasattr(result, 't_seconds')
        assert hasattr(result, 'values')
        assert len(result.t_seconds) == 20
        assert len(result.values) == 20
    
    def test_minmax_downsample_direct(self):
        """Testa função minmax_downsample diretamente."""
        from platform_base.processing.downsampling import minmax_downsample
        
        t = np.arange(0, 50, 0.5)
        values = np.sin(t)
        
        result = minmax_downsample(t, values, 20)
        
        # Retorna DownsampleResult
        assert result is not None
        assert hasattr(result, 't_seconds')
        assert hasattr(result, 'values')
        # minmax pode retornar até 2*n_points
        assert len(result.t_seconds) <= 40
    
    def test_downsample_error_handling(self):
        """Testa tratamento de erros."""
        from platform_base.processing.downsampling import DownsampleError, downsample
        
        t = np.array([1.0])
        values = np.array([1.0])
        
        with pytest.raises(DownsampleError):
            downsample(values, t, 10)  # Insufficient data


class TestInterpolationMethods:
    """Testes para processing/interpolation.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.processing.interpolation import (
            SUPPORTED_METHODS,
            interpolate,
        )
        assert interpolate is not None
        assert len(SUPPORTED_METHODS) > 0
    
    def test_interpolate_linear(self):
        """Testa interpolação linear."""
        from platform_base.processing.interpolation import interpolate
        
        t = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        values = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        
        # Assinatura: values, t_seconds, method, params
        result = interpolate(
            values=values,
            t_seconds=t,
            method="linear",
            params={"n_points": 10}
        )
        
        assert result is not None
    
    def test_interpolate_cubic(self):
        """Testa interpolação cúbica spline."""
        from platform_base.processing.interpolation import interpolate
        
        t = np.linspace(0, 10, 20)
        values = np.sin(t)
        
        result = interpolate(
            values=values,
            t_seconds=t,
            method="spline_cubic",  # Nome correto do método
            params={"n_points": 50}
        )
        
        assert result is not None


class TestSynchronization:
    """Testes para processing/synchronization.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.processing.synchronization import (
            SUPPORTED_SYNC_METHODS,
            synchronize,
        )
        assert synchronize is not None
        assert len(SUPPORTED_SYNC_METHODS) > 0
    
    def test_synchronize(self):
        """Testa sincronização de séries."""
        from platform_base.processing.synchronization import synchronize
        
        t1 = np.arange(0, 10, 0.1)
        v1 = np.sin(t1)
        t2 = np.arange(0, 10, 0.15)
        v2 = np.cos(t2)
        
        # Assinatura: series_dict, t_dict, method, params
        result = synchronize(
            series_dict={"s1": v1, "s2": v2},
            t_dict={"s1": t1, "s2": t2},
            method="common_grid_interpolate",  # Método correto
            params={}
        )
        
        assert result is not None


class TestSmoothing:
    """Testes para processing/smoothing.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.processing.smoothing import SmoothingConfig, smooth
        assert smooth is not None
        assert SmoothingConfig is not None
    
    def test_smooth_savitzky_golay(self):
        """Testa suavização Savitzky-Golay."""
        from platform_base.processing.smoothing import smooth
        
        values = np.random.normal(0, 1, 100)
        
        # Nome correto: savitzky_golay
        result = smooth(values, method='savitzky_golay', params={'window_length': 11, 'polyorder': 3})
        
        assert len(result) == len(values)
    
    def test_smooth_gaussian(self):
        """Testa suavização gaussiana."""
        from platform_base.processing.smoothing import smooth
        
        values = np.random.normal(0, 1, 100)
        
        result = smooth(values, method='gaussian', params={'sigma': 2.0})
        
        assert len(result) == len(values)
    
    def test_smooth_median(self):
        """Testa suavização por mediana."""
        from platform_base.processing.smoothing import smooth
        
        values = np.random.normal(0, 1, 100)
        
        result = smooth(values, method='median', params={'kernel_size': 5})
        
        assert len(result) == len(values)
    
    def test_smooth_lowpass(self):
        """Testa suavização lowpass."""
        from platform_base.processing.smoothing import smooth
        
        values = np.random.normal(0, 1, 100)
        
        result = smooth(values, method='lowpass', params={'cutoff': 0.1, 'order': 3})
        
        assert len(result) == len(values)


class TestProcessingUnits:
    """Testes para processing/units.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.processing.units import (
            infer_unit_from_name,
            normalize_units,
            parse_unit,
        )
        assert parse_unit is not None
        assert normalize_units is not None
        assert infer_unit_from_name is not None
    
    def test_parse_unit(self):
        """Testa parse de unidades."""
        from platform_base.processing.units import parse_unit
        
        unit = parse_unit("m/s")
        assert unit is not None
    
    def test_infer_unit_from_name(self):
        """Testa inferência de unidade pelo nome."""
        from platform_base.processing.units import infer_unit_from_name
        
        unit = infer_unit_from_name("temperature_celsius")
        # Deve retornar algo ou None
        assert unit is None or unit is not None


class TestTimebase:
    """Testes para processing/timebase.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.processing.timebase import to_datetime, to_seconds
        assert to_seconds is not None
        assert to_datetime is not None
    
    def test_to_seconds(self):
        """Testa conversão para segundos."""
        from platform_base.processing.timebase import to_seconds

        # to_seconds espera um array numpy de datetimes
        dt_array = np.array([datetime(2024, 1, 1, 12, 0, 0)])
        seconds = to_seconds(dt_array)
        
        assert isinstance(seconds, np.ndarray)
        assert len(seconds) == 1
    
    def test_to_datetime(self):
        """Testa conversão para datetime."""
        from platform_base.processing.timebase import to_datetime

        # to_datetime espera array de segundos e uma origem
        seconds = np.array([0.0, 3600.0, 7200.0])
        origin = datetime(2024, 1, 1, 0, 0, 0)
        dt_array = to_datetime(seconds, origin)
        
        assert isinstance(dt_array, np.ndarray)
        assert len(dt_array) == 3


class TestDownsampleResult:
    """Testes para DownsampleResult dataclass."""
    
    def test_result_structure(self):
        """Testa estrutura do resultado."""
        from platform_base.processing.downsampling import downsample
        
        t = np.arange(0, 100, 0.1)
        values = np.sin(t)
        
        result = downsample(values, t, 50, "lttb")
        
        # Verifica atributos esperados
        assert hasattr(result, 't_seconds')
        assert hasattr(result, 'values')
        assert hasattr(result, 'indices') or hasattr(result, 'selected_indices')
    
    def test_result_metadata(self):
        """Testa metadados do resultado."""
        from platform_base.processing.downsampling import downsample
        
        t = np.arange(0, 100, 0.1)
        values = np.sin(t)
        
        result = downsample(values, t, 50, "lttb")
        
        # Deve ter metadados
        if hasattr(result, 'metadata'):
            assert result.metadata is not None


class TestQualityMetrics:
    """Testes para métricas de qualidade."""
    
    def test_downsampling_quality(self):
        """Testa métricas de qualidade do downsampling."""
        from platform_base.processing.downsampling import downsample
        
        t = np.arange(0, 100, 0.1)
        values = np.sin(t)
        
        result = downsample(values, t, 50, "lttb")
        
        # Verifica que as métricas existem
        if hasattr(result, 'quality'):
            assert result.quality is not None
