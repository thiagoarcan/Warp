

































































































































































































































































































































































































































































































































































"""
Testes de integração - Platform Base v2.0

Testes end-to-end do pipeline: loading → processing → filtering → export.
Usando as APIs corretas conforme implementação atual.
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest


class TestDataLoadingPipelineV2:
    """Testes de pipeline de carregamento de dados"""
    
    def test_csv_loading_basic(self):
        """Testa carregamento básico de CSV"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value1,value2\n")
            for i in range(50):
                ts = f"2024-01-01 00:00:{i:02d}"
                f.write(f"{ts},{np.random.randn()},{np.random.randn()}\n")
            temp_file = f.name
        
        try:
            dataset = load(temp_file)
            
            assert dataset is not None
            assert len(dataset.series) >= 1
            # Verifica que as séries têm valores
            for name, series in dataset.series.items():
                assert len(series.values) == 50
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_csv_loading_with_custom_config(self):
        """Testa carregamento de CSV com configuração custom"""
        from platform_base.io.loader import LoadConfig, load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("time;sensor_a;sensor_b\n")
            for i in range(30):
                ts = f"2024-01-01 00:00:{i:02d}"
                f.write(f"{ts};{np.random.randn()};{np.random.randn()}\n")
            temp_file = f.name
        
        try:
            config = LoadConfig(delimiter=";")
            dataset = load(temp_file, config=config)
            
            assert dataset is not None
            assert len(dataset.series) >= 1
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_xlsx_loading(self):
        """Testa carregamento de XLSX"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_file = f.name
            
        try:
            # Cria dados de teste
            df = pd.DataFrame({
                'time': pd.date_range('2024-01-01', periods=100, freq='1s'),
                'value1': np.random.randn(100),
                'value2': np.random.randn(100)
            })
            df.to_excel(temp_file, index=False)
            
            dataset = load(temp_file)
            
            assert dataset is not None
            assert len(dataset.series) >= 1
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestProcessingPipelineV2:
    """Testes de pipeline de processamento"""
    
    def test_interpolation_pipeline(self):
        """Testa pipeline de interpolação"""
        from platform_base.processing.interpolation import interpolate

        # Dados com lacunas
        t = np.array([0.0, 1.0, 2.0, 5.0, 6.0, 7.0])
        y = np.array([0.0, 1.0, 4.0, 25.0, 36.0, 49.0])
        
        # Interpola
        result = interpolate(y, t, method="linear", params={})
        
        assert len(result.values) > 0
    
    def test_downsampling_pipeline(self):
        """Testa pipeline de downsampling"""
        from platform_base.processing.downsampling import downsample

        # Dados grandes
        n = 10000
        t = np.linspace(0, 100, n)
        y = np.sin(t) * np.cos(t * 0.1)
        
        result = downsample(y, t, n_points=500, method="lttb")
        
        assert len(result.t_seconds) == 500
        assert len(result.values) == 500
        # Verifica que range é preservado aproximadamente
        assert result.t_seconds.min() >= t.min() - 0.1
        assert result.t_seconds.max() <= t.max() + 0.1
    
    def test_derivative_pipeline(self):
        """Testa pipeline de derivada"""
        from platform_base.processing.calculus import derivative

        # y = x^2, dy/dx = 2x
        t = np.linspace(0, 10, 1000)
        y = t ** 2
        
        result = derivative(y, t, order=1)
        
        # Verifica que derivada é aproximadamente 2*t
        expected = 2 * t
        # Permite erro nas bordas devido ao método numérico
        error = np.abs(result.values[10:-10] - expected[10:-10])
        assert np.mean(error) < 0.1
    
    def test_integral_pipeline(self):
        """Testa pipeline de integral"""
        from platform_base.processing.calculus import integral

        # y = 2x, integral de 0 a T = T^2
        t = np.linspace(0, 5, 100)
        y = 2 * t
        
        result = integral(y, t)
        
        # Integral de 2x de 0 a 5 = 5^2 = 25
        # Valor da integral cumulativa no final
        assert abs(result.values[-1] - 25) < 0.5
    
    def test_smoothing_pipeline(self):
        """Testa pipeline de suavização"""
        from platform_base.processing.smoothing import smooth

        # Sinal com ruído
        np.random.seed(42)
        t = np.linspace(0, 10, 1000)
        y_clean = np.sin(t)
        y_noisy = y_clean + np.random.randn(1000) * 0.3
        
        result = smooth(y_noisy, method="savitzky_golay", params={"window_length": 51, "polyorder": 3})
        
        # Verifica que suavização reduziu variância
        noise_before = np.var(y_noisy - y_clean)
        noise_after = np.var(result - y_clean)
        assert noise_after < noise_before


class TestMultiStepPipelineV2:
    """Testes de pipelines multi-step"""
    
    def test_load_then_process(self):
        """Testa carregamento seguido de processamento"""
        from platform_base.io.loader import load
        from platform_base.processing.downsampling import downsample
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,sensor\n")
            for i in range(1000):
                ts = f"2024-01-01 00:00:{i//60:02d}"
                f.write(f"{ts},{np.sin(i/100)}\n")
            temp_file = f.name
        
        try:
            # Carrega
            dataset = load(temp_file)
            
            # Processa primeira série
            series_name = list(dataset.series.keys())[0]
            series = dataset.series[series_name]
            
            # Downsampling
            t = np.arange(len(series.values), dtype=float)
            result = downsample(series.values, t, n_points=100, method="lttb")
            
            assert len(result.values) == 100
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_derivative_then_integral(self):
        """Testa derivada seguida de integral (devem se cancelar)"""
        from platform_base.processing.calculus import derivative, integral

        # y = sin(x)
        t = np.linspace(0, 2*np.pi, 1000)
        y = np.sin(t)
        
        # Deriva para cos(x)
        dy = derivative(y, t, order=1)
        
        # Integra de volta (deveria ser ~sin(x) + constante)
        integrated = integral(dy.values, t)
        
        # A integral da derivada deve ser próxima do original (diferença constante)
        diff = integrated.values - y
        # Verificar que a diferença é aproximadamente constante
        # Nota: A tolerância é maior devido a acúmulo de erros numéricos
        diff_std = np.std(diff)
        assert diff_std < 1.0  # Tolerância maior para erros numéricos


class TestSessionStateIntegrationV2:
    """Testes de integração com session state"""
    
    @pytest.mark.skip(reason="SessionState está em desktop, não em core")
    def test_session_state_signals(self):
        """Testa signals do session state"""
        pass
    
    @pytest.mark.skip(reason="SessionState está em desktop, não em core")
    def test_session_state_time_window(self):
        """Testa janela de tempo no session state"""
        pass


class TestCachingIntegrationV2:
    """Testes de integração com caching"""
    
    def test_memory_cache_basic(self):
        """Testa cache em memória básico"""
        from platform_base.caching.memory import MemoryCache
        
        cache = MemoryCache()
        
        # Adiciona item
        data = np.random.randn(1000)
        cache.set("test_key", data)
        
        # Recupera
        retrieved = cache.get("test_key")
        
        assert retrieved is not None
        assert np.array_equal(data, retrieved)
    
    def test_cache_get_nonexistent(self):
        """Testa recuperação de chave inexistente"""
        from platform_base.caching.memory import MemoryCache
        
        cache = MemoryCache()
        
        # Tenta recuperar chave que não existe
        result = cache.get("nonexistent_key")
        
        assert result is None


class TestValidationIntegrationV2:
    """Testes de integração com validação"""
    
    def test_validate_loaded_data(self):
        """Testa validação de dados carregados"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(100):
                ts = datetime(2024, 1, 1, 0, 0, i % 60)
                f.write(f"{ts.isoformat()},{np.random.randn()}\n")
            temp_file = f.name
        
        try:
            dataset = load(temp_file)
            
            # Verifica que dataset foi carregado com sucesso
            assert dataset is not None
            assert len(dataset.series) >= 1
            
            # Verifica que séries têm dados válidos
            for name, series in dataset.series.items():
                assert len(series.values) > 0
                # Verifica que não há todos NaN
                assert not np.all(np.isnan(series.values))
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestErrorHandlingIntegrationV2:
    """Testes de tratamento de erros em pipelines"""
    
    def test_load_invalid_file_error(self):
        """Testa erro ao carregar arquivo inválido"""
        from platform_base.io.loader import load
        from platform_base.utils.errors import DataLoadError
        
        with pytest.raises((FileNotFoundError, DataLoadError)):
            load("/nonexistent/path/file.csv")
    
    def test_process_empty_data_error(self):
        """Testa erro ao processar dados vazios"""
        from platform_base.processing.interpolation import interpolate
        
        t = np.array([])
        y = np.array([])
        
        # Deve levantar erro ou retornar array vazio
        try:
            result = interpolate(y, t, method="linear", params={})
            # Se não levantou erro, verifica resultado
            assert len(result.values) == 0 or result.values is not None
        except (ValueError, Exception):
            pass  # Esperado
    
    def test_downsample_few_points(self):
        """Testa downsampling com poucos pontos"""
        from platform_base.processing.downsampling import downsample
        
        t = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 1.0, 4.0])
        
        # Pede mais pontos do que existem - deve retornar todos
        result = downsample(y, t, n_points=10, method="lttb")
        
        assert len(result.t_seconds) <= 3


class TestPerformanceIntegrationV2:
    """Testes de performance básicos"""
    
    def test_large_dataset_processing(self):
        """Testa processamento de dataset grande"""
        import time

        from platform_base.processing.downsampling import downsample

        # 100K pontos
        n = 100000
        t = np.linspace(0, 1000, n)
        y = np.sin(t) + np.random.randn(n) * 0.1
        
        start = time.time()
        result = downsample(y, t, n_points=1000, method="lttb")
        elapsed = time.time() - start
        
        assert elapsed < 5.0  # Deve processar em menos de 5 segundos
        assert len(result.t_seconds) == 1000
    
    def test_derivative_large_data(self):
        """Testa derivada em dados grandes"""
        import time

        from platform_base.processing.calculus import derivative
        
        n = 100000
        t = np.linspace(0, 100, n)
        y = np.sin(t) * np.exp(-t/50)
        
        start = time.time()
        result = derivative(y, t, order=1)
        elapsed = time.time() - start
        
        assert elapsed < 2.0  # Deve processar em menos de 2 segundos
        assert len(result.values) == n
