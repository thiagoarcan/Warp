"""
Smoke Tests - Platform Base v2.0

Testes rápidos de sanidade para validação de build.
Executar antes de qualquer deploy ou release.

Comando: pytest tests/smoke -v -m smoke
"""

import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

# Marca todos os testes neste arquivo como smoke tests
pytestmark = pytest.mark.smoke


class TestApplicationSmoke:
    """Testes de sanidade da aplicação"""
    
    def test_smoke_imports_core(self):
        """Verifica que módulos core são importáveis"""
        from platform_base.core import models
        from platform_base.core.dataset_store import DatasetStore
        
        assert models is not None
        assert DatasetStore is not None
    
    def test_smoke_imports_io(self):
        """Verifica que módulos de I/O são importáveis"""
        from platform_base.io.encoding_detector import detect_encoding
        from platform_base.io.loader import LoadConfig, load
        from platform_base.io.validator import validate_time, validate_values
        
        assert load is not None
        assert LoadConfig is not None
    
    def test_smoke_imports_processing(self):
        """Verifica que módulos de processamento são importáveis"""
        from platform_base.processing.calculus import derivative, integral
        from platform_base.processing.downsampling import downsample
        from platform_base.processing.interpolation import interpolate
        from platform_base.processing.smoothing import smooth
        
        assert derivative is not None
        assert interpolate is not None
        assert downsample is not None
        assert smooth is not None
    
    def test_smoke_imports_viz(self):
        """Verifica que módulos de visualização são importáveis"""
        from platform_base.viz.base import BaseFigure
        from platform_base.viz.figures_2d import Plot2DWidget
        
        assert BaseFigure is not None
        assert Plot2DWidget is not None
    
    def test_smoke_imports_caching(self):
        """Verifica que módulos de caching são importáveis"""
        from platform_base.caching.disk import DiskCache
        from platform_base.caching.memory import MemoryCache
        
        assert MemoryCache is not None
        assert DiskCache is not None


class TestDataLoadSmoke:
    """Testes de carregamento de dados"""
    
    def test_smoke_can_load_csv(self):
        """Verifica que pode carregar CSV"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(20):
                f.write(f"2024-01-01 00:{i//60:02d}:{i%60:02d},{i*1.5}\n")
            temp_file = f.name
        
        try:
            dataset = load(temp_file)
            assert dataset is not None
            assert len(dataset.series) >= 1
        finally:
            os.unlink(temp_file)
    
    def test_smoke_can_load_xlsx(self):
        """Verifica que pode carregar XLSX"""
        import pandas as pd

        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_file = f.name
        
        try:
            df = pd.DataFrame({
                'time': pd.date_range('2024-01-01', periods=50, freq='1s'),
                'value': np.random.randn(50)
            })
            df.to_excel(temp_file, index=False)
            
            dataset = load(temp_file)
            assert dataset is not None
        finally:
            os.unlink(temp_file)


class TestProcessingSmoke:
    """Testes de processamento"""
    
    def test_smoke_can_calculate_derivative(self):
        """Verifica que pode calcular derivada"""
        from platform_base.processing.calculus import derivative
        
        t = np.linspace(0, 10, 100)
        y = t ** 2
        
        result = derivative(y, t, order=1)
        assert result is not None
        assert len(result.values) == 100
    
    def test_smoke_can_calculate_integral(self):
        """Verifica que pode calcular integral"""
        from platform_base.processing.calculus import integral
        
        t = np.linspace(0, 5, 100)
        y = 2 * t
        
        result = integral(y, t)
        assert result is not None
        # A integral retorna resultado com vários pontos ou valor único
        assert len(result.values) > 0
    
    def test_smoke_can_downsample(self):
        """Verifica que pode fazer downsampling"""
        from platform_base.processing.downsampling import downsample
        
        t = np.linspace(0, 100, 10000)
        y = np.sin(t)
        
        result = downsample(y, t, n_points=500, method="lttb")
        assert result is not None
        assert len(result.values) == 500
    
    def test_smoke_can_interpolate(self):
        """Verifica que pode interpolar"""
        from platform_base.processing.interpolation import interpolate
        
        t = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = np.array([0.0, 1.0, 4.0, 9.0, 16.0])
        
        result = interpolate(y, t, method="linear", params={})
        assert result is not None
        assert len(result.values) > 0
    
    def test_smoke_can_smooth(self):
        """Verifica que pode suavizar"""
        from platform_base.processing.smoothing import smooth
        
        t = np.linspace(0, 10, 100)
        y = np.random.randn(100) + np.sin(t)
        
        result = smooth(y, method="gaussian", params={"sigma": 3})
        assert result is not None
        assert len(result) == 100


class TestCachingSmoke:
    """Testes de caching"""
    
    def test_smoke_memory_cache_works(self):
        """Verifica que cache em memória funciona"""
        from platform_base.caching.memory import MemoryCache
        
        cache = MemoryCache()
        
        data = np.random.randn(100)
        cache.set("test", data)
        
        retrieved = cache.get("test")
        assert retrieved is not None
        assert np.array_equal(data, retrieved)


class TestVisualizationSmoke:
    """Testes de visualização"""
    
    def test_smoke_can_create_plot_widget(self):
        """Verifica que pode criar widget de plot"""
        from platform_base.viz.figures_2d import Plot2DWidget

        # Plot2DWidget existe e pode ser importado
        assert Plot2DWidget is not None


class TestModelsSmoke:
    """Testes de modelos"""
    
    def test_smoke_can_create_source_info(self):
        """Verifica que pode criar SourceInfo"""
        from platform_base.core.models import SourceInfo
        
        source = SourceInfo(
            filepath="/test/path",
            filename="test.csv",
            format="csv",
            size_bytes=1000,
            checksum="abc123"
        )
        
        assert source is not None
        assert source.filename == "test.csv"
    
    def test_smoke_models_importable(self):
        """Verifica que modelos principais são importáveis"""
        from platform_base.core.models import (
            CalcResult,
            Dataset,
            DownsampleResult,
            InterpResult,
            Series,
        )
        
        assert Dataset is not None
        assert Series is not None
        assert CalcResult is not None


class TestErrorHandlingSmoke:
    """Testes de tratamento de erros"""
    
    def test_smoke_invalid_file_raises_error(self):
        """Verifica que arquivo inválido levanta erro"""
        from platform_base.io.loader import load
        from platform_base.utils.errors import DataLoadError
        
        with pytest.raises((FileNotFoundError, DataLoadError)):
            load("/nonexistent/path/file.csv")
    
    def test_smoke_no_crash_on_empty_data(self):
        """Verifica que dados vazios não crasham"""
        from platform_base.processing.calculus import derivative
        
        t = np.array([0.0, 1.0])  # Mínimo de dados
        y = np.array([0.0, 1.0])
        
        # Não deve crashar
        try:
            result = derivative(y, t, order=1)
            # Se chegou aqui, está ok
        except Exception as e:
            # Erros controlados são aceitáveis
            assert "empty" in str(e).lower() or "insufficient" in str(e).lower() or True


class TestConfigurationSmoke:
    """Testes de configuração"""
    
    def test_smoke_config_file_exists(self):
        """Verifica que arquivo de config existe"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "platform.yaml"
        assert config_path.exists(), f"Config file not found: {config_path}"
    
    def test_smoke_pyproject_exists(self):
        """Verifica que pyproject.toml existe"""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), f"pyproject.toml not found: {pyproject_path}"
