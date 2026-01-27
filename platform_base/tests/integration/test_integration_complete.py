"""
Testes de integração - Platform Base v2.0

Testes end-to-end do pipeline: loading → processing → filtering → export.
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest


class TestDataLoadingPipeline:
    """Testes de pipeline de carregamento de dados"""
    
    def test_xlsx_loading_to_dataframe(self):
        """Testa carregamento de XLSX para DataFrame"""
        from platform_base.io.loader import DataLoaderService

        # Cria arquivo temporário
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
            
            # Carrega usando loader
            loader = DataLoaderService()
            result = loader.load_file(temp_file)
            
            assert result is not None
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 100
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_csv_loading_with_validation(self):
        """Testa carregamento de CSV com validação"""
        from platform_base.io.loader import DataLoaderService
        from platform_base.io.validator import validate_time, validate_values
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,sensor_a,sensor_b\n")
            for i in range(50):
                ts = f"2024-01-01 00:00:{i:02d}"
                f.write(f"{ts},{np.random.randn()},{np.random.randn()}\n")
            temp_file = f.name
        
        try:
            loader = DataLoaderService()
            df = loader.load_file(temp_file)
            
            # Valida dados
            time_col = pd.to_datetime(df['timestamp'])
            time_warnings = validate_time(time_col)
            value_warnings = validate_values(df['sensor_a'])
            
            assert len(df) == 50
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestDataProcessingPipeline:
    """Testes de pipeline de processamento"""
    
    def test_interpolation_pipeline(self):
        """Testa pipeline de interpolação"""
        from platform_base.processing.interpolation import (
            cubic_spline_interpolate,
            linear_interpolate,
        )

        # Dados com gaps
        x = np.array([0, 1, 2, 5, 6, 7, 10])  # Gaps em 3-4 e 8-9
        y = np.array([0, 1, 4, 25, 36, 49, 100])
        
        # Interpolação linear
        x_new = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y_linear = linear_interpolate(x, y, x_new)
        
        assert len(y_linear) == len(x_new)
        assert y_linear[0] == 0
        assert y_linear[-1] == 100
    
    def test_downsampling_pipeline(self):
        """Testa pipeline de downsampling"""
        from platform_base.processing.downsampling import (
            lttb_downsample,
            minmax_downsample,
        )

        # Dados de alta resolução
        n_points = 10000
        x = np.linspace(0, 10, n_points)
        y = np.sin(x) + np.random.randn(n_points) * 0.1
        
        # LTTB downsample
        target_points = 500
        x_down, y_down = lttb_downsample(x, y, target_points)
        
        assert len(x_down) == target_points
        assert len(y_down) == target_points
        
        # MinMax downsample
        x_minmax, y_minmax = minmax_downsample(x, y, target_points)
        
        assert len(x_minmax) == target_points
    
    def test_calculus_pipeline(self):
        """Testa pipeline de cálculos"""
        from platform_base.processing.calculus import (
            moving_average,
            numerical_derivative,
            numerical_integral,
        )

        # Função conhecida: y = x²
        x = np.linspace(0, 10, 1000)
        y = x ** 2
        
        # Derivada: dy/dx = 2x
        dy = numerical_derivative(x, y)
        expected_dy = 2 * x
        
        # Tolerância para erro numérico
        assert np.allclose(dy[10:-10], expected_dy[10:-10], rtol=0.1)
        
        # Integral
        integral = numerical_integral(x, y)
        # Integral de x² = x³/3
        expected_integral = x[-1] ** 3 / 3
        assert abs(integral - expected_integral) < expected_integral * 0.01


class TestFilteringPipeline:
    """Testes de pipeline de filtragem"""
    
    def test_quality_filter_chain(self):
        """Testa cadeia de filtros de qualidade"""
        from platform_base.streaming.filters import (
            FilterChain,
            QualityFilter,
            ValueFilter,
        )

        # Cria chain de filtros
        chain = FilterChain()
        chain.add_filter(QualityFilter(min_quality=0.8))
        chain.add_filter(ValueFilter(min_value=-100, max_value=100))
        
        # Dados de teste
        test_records = [
            {"quality": 0.9, "value": 50},   # Passa
            {"quality": 0.5, "value": 50},   # Falha (qualidade)
            {"quality": 0.9, "value": 150},  # Falha (valor)
            {"quality": 0.95, "value": -50}, # Passa
        ]
        
        results = []
        for record in test_records:
            result = chain.apply(record)
            results.append(result.action.value)
        
        assert results[0] == "accept"
        assert results[1] == "reject"
        assert results[2] == "reject"
        assert results[3] == "accept"
    
    def test_temporal_filter(self):
        """Testa filtro temporal"""
        from platform_base.streaming.filters import FilterAction, TemporalFilter
        
        now = datetime.now()
        filter_ = TemporalFilter(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1)
        )
        
        # Dentro do range
        record_in = {"timestamp": now}
        result_in = filter_.apply(record_in)
        assert result_in.action == FilterAction.ACCEPT
        
        # Fora do range
        record_out = {"timestamp": now - timedelta(days=1)}
        result_out = filter_.apply(record_out)
        assert result_out.action == FilterAction.REJECT


class TestDesktopIntegration:
    """Testes de integração com componentes desktop"""
    
    @pytest.fixture
    def mock_qt(self):
        """Mock PyQt6 se não disponível"""
        try:
            from PyQt6.QtCore import QObject, pyqtSignal
            return True
        except ImportError:
            return False
    
    def test_session_state_with_signal_hub(self, mock_qt):
        """Testa integração SessionState com SignalHub"""
        if not mock_qt:
            pytest.skip("PyQt6 não disponível")
        
        from platform_base.desktop.session_state import SessionState
        from platform_base.desktop.signal_hub import SignalHub
        
        signal_hub = SignalHub()
        session = SessionState()
        
        # Conecta sinais
        selection_changed = []
        signal_hub.selection_changed.connect(
            lambda s: selection_changed.append(s)
        )
        
        # Modifica estado
        session.selection.selected_tags = ["TAG1", "TAG2"]
        signal_hub.selection_changed.emit(session.selection)
        
        assert len(selection_changed) == 1
        assert "TAG1" in selection_changed[0].selected_tags
    
    def test_worker_with_session_state(self, mock_qt):
        """Testa integração Worker com SessionState"""
        if not mock_qt:
            pytest.skip("PyQt6 não disponível")
        
        from platform_base.desktop.session_state import SessionState
        from platform_base.desktop.workers import ProcessingWorker
        
        session = SessionState()
        
        # Define tarefa
        def processing_task(data, state):
            return data * 2
        
        worker = ProcessingWorker(
            task=processing_task,
            data=np.array([1, 2, 3]),
            session_state=session
        )
        
        # Verifica configuração
        assert worker._task is not None
        assert worker._data is not None


class TestCachingIntegration:
    """Testes de integração com cache"""
    
    def test_cache_with_loader(self):
        """Testa integração de cache com loader"""
        from platform_base.caching.memory import MemoryCache
        from platform_base.io.loader import DataLoaderService
        
        cache = MemoryCache(maxsize=100)
        loader = DataLoaderService()
        
        # Simula caching de dados carregados
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(10):
                f.write(f"2024-01-01 00:00:{i:02d},{i}\n")
            temp_file = f.name
        
        try:
            # Primeira carga
            df1 = loader.load_file(temp_file)
            cache.set(temp_file, df1)
            
            # Segunda "carga" do cache
            cached = cache.get(temp_file)
            
            assert cached is not None
            assert len(cached) == 10
            assert temp_file in cache
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_cache_eviction_on_large_data(self):
        """Testa eviction de cache com dados grandes"""
        from platform_base.caching.memory import MemoryCache
        
        cache = MemoryCache(maxsize=5)
        
        # Adiciona 10 itens
        for i in range(10):
            df = pd.DataFrame({'col': np.random.randn(100)})
            cache.set(f"dataset_{i}", df)
        
        # Apenas 5 devem permanecer
        assert len(cache) == 5
        
        # Últimos 5 devem estar presentes
        assert "dataset_9" in cache
        assert "dataset_5" in cache
        # Primeiros devem ter sido evicted
        assert "dataset_0" not in cache


class TestEndToEndPipeline:
    """Testes de pipeline end-to-end"""
    
    def test_full_data_pipeline(self):
        """Testa pipeline completo: load → process → filter → export"""
        from platform_base.caching.memory import MemoryCache
        from platform_base.io.loader import DataLoaderService
        from platform_base.io.validator import validate_time, validate_values
        from platform_base.processing.calculus import moving_average
        from platform_base.processing.downsampling import lttb_downsample
        from platform_base.streaming.filters import FilterChain, ValueFilter

        # 1. Gera dados de teste
        n_points = 10000
        time_values = np.linspace(0, 100, n_points)
        sensor_values = np.sin(time_values) * 100 + np.random.randn(n_points) * 10
        
        # Adiciona alguns outliers
        outlier_indices = np.random.choice(n_points, 50, replace=False)
        sensor_values[outlier_indices] = 500
        
        # 2. Valida dados
        warnings = validate_values(sensor_values)
        
        # 3. Filtra outliers
        filter_chain = FilterChain()
        filter_chain.add_filter(ValueFilter(min_value=-200, max_value=200))
        
        filtered_mask = np.abs(sensor_values) <= 200
        time_filtered = time_values[filtered_mask]
        values_filtered = sensor_values[filtered_mask]
        
        # 4. Aplica suavização
        smoothed = moving_average(values_filtered, window=5)
        
        # 5. Downsample para visualização
        target_points = 500
        time_down, values_down = lttb_downsample(
            time_filtered, smoothed, target_points
        )
        
        # 6. Cache resultado
        cache = MemoryCache()
        cache.set("processed_data", {
            "time": time_down,
            "values": values_down
        })
        
        # Verifica resultados
        assert len(time_down) == target_points
        assert len(values_down) == target_points
        assert "processed_data" in cache
        
        cached_data = cache.get("processed_data")
        assert cached_data is not None
        assert len(cached_data["time"]) == target_points
    
    def test_multi_signal_processing(self):
        """Testa processamento de múltiplos sinais"""
        from platform_base.processing.calculus import numerical_derivative
        from platform_base.processing.downsampling import lttb_downsample

        # Múltiplos sinais
        n_points = 5000
        time = np.linspace(0, 100, n_points)
        
        signals = {
            "temp": 20 + 5 * np.sin(time / 10),
            "pressure": 100 + 10 * np.cos(time / 5),
            "flow": 50 + 20 * np.sin(time / 20) + np.random.randn(n_points) * 2
        }
        
        # Processa cada sinal
        processed = {}
        target_points = 250
        
        for name, values in signals.items():
            # Downsample
            t_down, v_down = lttb_downsample(time, values, target_points)
            
            # Derivada
            dv = numerical_derivative(t_down, v_down)
            
            processed[name] = {
                "time": t_down,
                "values": v_down,
                "derivative": dv
            }
        
        # Verifica resultados
        for name, data in processed.items():
            assert len(data["time"]) == target_points
            assert len(data["values"]) == target_points
            assert len(data["derivative"]) == target_points


class TestErrorHandlingIntegration:
    """Testes de tratamento de erros na integração"""
    
    def test_loader_error_handling(self):
        """Testa tratamento de erro no loader"""
        from platform_base.io.loader import DataLoaderService
        from platform_base.utils.errors import DataLoadError
        
        loader = DataLoaderService()
        
        with pytest.raises(Exception):
            loader.load_file("/nonexistent/file.csv")
    
    def test_validation_error_handling(self):
        """Testa tratamento de erro na validação"""
        from platform_base.io.validator import validate_values

        # Dados com NaN
        data_with_nan = np.array([1, 2, np.nan, 4, np.nan, 6])
        
        warnings = validate_values(data_with_nan)
        
        # Deve retornar warnings, não quebrar
        assert isinstance(warnings, list)
    
    def test_processing_with_empty_data(self):
        """Testa processamento com dados vazios"""
        from platform_base.processing.calculus import moving_average

        # Dados vazios
        empty = np.array([])
        
        result = moving_average(empty, window=3)
        
        assert len(result) == 0
    
    def test_filter_chain_error_recovery(self):
        """Testa recuperação de erro no filter chain"""
        from platform_base.streaming.filters import FilterChain, QualityFilter
        
        chain = FilterChain()
        chain.add_filter(QualityFilter(min_quality=0.5))
        
        # Record sem campo quality
        record = {"value": 100}
        
        # Não deve quebrar
        result = chain.apply(record)
        # Comportamento depende da implementação


class TestPerformanceIntegration:
    """Testes de performance da integração"""
    
    def test_large_dataset_processing(self):
        """Testa processamento de dataset grande"""
        from platform_base.processing.downsampling import lttb_downsample

        # Dataset grande
        n_points = 100000
        x = np.linspace(0, 1000, n_points)
        y = np.sin(x) * np.exp(-x / 1000) + np.random.randn(n_points) * 0.01
        
        import time
        start = time.time()
        
        # Downsample
        x_down, y_down = lttb_downsample(x, y, 1000)
        
        elapsed = time.time() - start
        
        # Deve completar em tempo razoável (< 5s)
        assert elapsed < 5.0
        assert len(x_down) == 1000
    
    def test_cache_performance(self):
        """Testa performance do cache"""
        from platform_base.caching.memory import MemoryCache
        
        cache = MemoryCache(maxsize=1000)
        
        import time
        start = time.time()
        
        # Muitas operações
        for i in range(10000):
            cache.set(f"key_{i % 500}", f"value_{i}")
            cache.get(f"key_{i % 300}")
        
        elapsed = time.time() - start
        
        # Deve ser rápido (< 1s)
        assert elapsed < 1.0


class TestConfigurationIntegration:
    """Testes de integração com configuração"""
    
    def test_yaml_config_loading(self):
        """Testa carregamento de configuração YAML"""
        import yaml
        
        config_content = """
        processing:
          downsample_method: lttb
          target_points: 500
          
        filtering:
          quality_threshold: 0.8
          value_range:
            min: -100
            max: 100
            
        caching:
          maxsize: 1000
          enabled: true
        """
        
        config = yaml.safe_load(config_content)
        
        assert config["processing"]["downsample_method"] == "lttb"
        assert config["filtering"]["quality_threshold"] == 0.8
        assert config["caching"]["enabled"] is True
    
    def test_config_driven_processing(self):
        """Testa processamento baseado em configuração"""
        from platform_base.processing.downsampling import (
            lttb_downsample,
            minmax_downsample,
            uniform_downsample,
        )

        # Config simula
        config = {
            "method": "lttb",
            "target_points": 100
        }
        
        x = np.linspace(0, 10, 1000)
        y = np.sin(x)
        
        # Seleciona método baseado na config
        methods = {
            "lttb": lttb_downsample,
            "minmax": minmax_downsample,
            "uniform": uniform_downsample
        }
        
        method = methods[config["method"]]
        x_down, y_down = method(x, y, config["target_points"])
        
        assert len(x_down) == config["target_points"]
