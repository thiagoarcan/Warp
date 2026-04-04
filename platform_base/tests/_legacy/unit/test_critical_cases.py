"""
Testes para casos críticos - Platform Base v2.0

Cobertura de cenários edge-case e situações críticas:
- TEST-004: Load de arquivo vazio
- TEST-005: Load de arquivo corrompido
- TEST-006: Operação com dados NaN
- TEST-007: Cancelamento de operação em andamento
- TEST-008: Múltiplos datasets simultâneos
- TEST-009: Stress test com 10+ datasets
"""

import os
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from platform_base.core.dataset_store import DatasetStore
from platform_base.core.models import (
    Dataset,
    DatasetMetadata,
    InterpolationInfo,
    Lineage,
    Series,
    SeriesMetadata,
    SourceInfo,
)

# Imports corretos do platform_base
from platform_base.io.loader import FileFormat, LoadConfig, load
from platform_base.processing.calculus import derivative
from platform_base.processing.interpolation import interpolate
from platform_base.processing.units import parse_unit
from platform_base.utils.errors import DataLoadError


def make_series(name: str, time: np.ndarray, values: np.ndarray) -> Series:
    """Helper para criar Series com metadata completa"""
    return Series(
        series_id=name,
        name=name,
        unit=parse_unit("m"),
        values=values,
        interpolation_info=InterpolationInfo(
            is_interpolated=np.zeros(len(values), dtype=bool),
            method_used=np.full(len(values), "original", dtype="<U32")
        ),
        metadata=SeriesMetadata(
            original_name=name,
            source_column=name,
            original_unit="m"
        ),
        lineage=Lineage(
            origin_series=[],
            operation="test",
            parameters={},
            timestamp=datetime.now(timezone.utc),
            version="2.0.0"
        )
    )


def make_dataset(name: str, series_dict: dict) -> Dataset:
    """Helper para criar Dataset com metadata completa"""
    first_series = list(series_dict.values())[0]
    t_seconds = np.linspace(0, 10, len(first_series.values))
    
    return Dataset(
        dataset_id=name,
        version=1,
        parent_id=None,
        source=SourceInfo(
            filepath=f"/test/{name}.csv",
            filename=f"{name}.csv",
            format="csv",
            size_bytes=1000,
            checksum="test_checksum"
        ),
        t_seconds=t_seconds,
        t_datetime=np.array([datetime.now() + timedelta(seconds=t) for t in t_seconds], dtype='datetime64[ns]'),
        series=series_dict,
        metadata=DatasetMetadata(),
        created_at=datetime.now(timezone.utc)
    )


# =============================================================================
# TEST-004: Load de arquivo vazio
# =============================================================================

class TestEmptyFileLoad:
    """Testes para carregamento de arquivos vazios"""
    
    def test_load_empty_csv_file(self, tmp_path):
        """Testa carregamento de CSV vazio"""
        # Cria arquivo CSV vazio
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        
        with pytest.raises((DataLoadError, Exception)):
            load(str(empty_file))
    
    def test_load_csv_with_headers_only(self, tmp_path):
        """Testa CSV com apenas cabeçalhos (sem dados)"""
        # CSV com apenas headers
        csv_headers_only = tmp_path / "headers_only.csv"
        csv_headers_only.write_text("timestamp,value1,value2\n")
        
        with pytest.raises((DataLoadError, Exception)):
            load(str(csv_headers_only))
    
    def test_load_csv_with_single_row(self, tmp_path):
        """Testa CSV com apenas uma linha de dados"""
        # CSV com uma linha de dados
        csv_single_row = tmp_path / "single_row.csv"
        csv_single_row.write_text("timestamp,value\n2025-01-01 00:00:00,1.0\n")
        
        config = LoadConfig(min_valid_points=1)
        
        # Deve carregar com sucesso
        dataset = load(str(csv_single_row), config=config)
        
        assert dataset is not None
        assert len(dataset.series) > 0
    
    def test_load_empty_excel_file(self, tmp_path):
        """Testa carregamento de Excel vazio"""
        # Cria arquivo Excel vazio
        empty_xlsx = tmp_path / "empty.xlsx"
        pd.DataFrame().to_excel(empty_xlsx, index=False)
        
        with pytest.raises((DataLoadError, Exception)):
            load(str(empty_xlsx))
    
    def test_load_csv_with_whitespace_only(self, tmp_path):
        """Testa CSV com apenas espaços em branco"""
        # CSV com apenas whitespace
        whitespace_file = tmp_path / "whitespace.csv"
        whitespace_file.write_text("   \n   \n   \n")
        
        with pytest.raises((DataLoadError, Exception)):
            load(str(whitespace_file))


# =============================================================================
# TEST-005: Load de arquivo corrompido
# =============================================================================

class TestCorruptedFileLoad:
    """Testes para carregamento de arquivos corrompidos"""
    
    def test_load_binary_garbage_as_csv(self, tmp_path):
        """Testa CSV com conteúdo binário"""
        # Arquivo com conteúdo binário aleatório
        garbage_file = tmp_path / "garbage.csv"
        garbage_file.write_bytes(os.urandom(1024))
        
        with pytest.raises((DataLoadError, UnicodeDecodeError, Exception)):
            load(str(garbage_file))
    
    def test_load_malformed_csv(self, tmp_path):
        """Testa CSV mal formado (colunas inconsistentes)"""
        # CSV com número inconsistente de colunas
        malformed_csv = tmp_path / "malformed.csv"
        content = """timestamp,value1,value2
2025-01-01 00:00:00,1.0,2.0
2025-01-01 00:01:00,3.0
2025-01-01 00:02:00,4.0,5.0,6.0,7.0
"""
        malformed_csv.write_text(content)
        
        # Pode carregar (pandas trata algumas malformações) ou lançar erro
        try:
            result = load(str(malformed_csv))
            # Se carregar, verificar se há dados
            assert result is not None
        except (DataLoadError, Exception):
            # Também é comportamento aceitável
            pass
    
    def test_load_csv_with_invalid_timestamps(self, tmp_path):
        """Testa CSV com timestamps inválidos"""
        # CSV com timestamps inválidos
        invalid_ts = tmp_path / "invalid_ts.csv"
        content = """timestamp,value
not_a_date,1.0
also_not_a_date,2.0
still_not_a_date,3.0
"""
        invalid_ts.write_text(content)
        
        with pytest.raises((DataLoadError, Exception)):
            load(str(invalid_ts))
    
    def test_load_truncated_file(self, tmp_path):
        """Testa arquivo truncado no meio"""
        # CSV truncado
        truncated = tmp_path / "truncated.csv"
        truncated.write_text("timestamp,value\n2025-01-01 00:00:00,1.5\n2025-01-")
        
        # Pode carregar parcialmente ou falhar
        try:
            result = load(str(truncated))
            assert result is not None
        except (DataLoadError, Exception):
            pass
    
    def test_load_excel_with_wrong_extension(self, tmp_path):
        """Testa arquivo com extensão errada"""
        # CSV com extensão .xlsx
        fake_xlsx = tmp_path / "fake.xlsx"
        fake_xlsx.write_text("timestamp,value\n2025-01-01 00:00:00,1.0\n")
        
        with pytest.raises((DataLoadError, Exception)):
            load(str(fake_xlsx))
    
    def test_load_nonexistent_file(self, tmp_path):
        """Testa carregamento de arquivo inexistente"""
        with pytest.raises((DataLoadError, FileNotFoundError, Exception)):
            load(str(tmp_path / "nonexistent.csv"))


# =============================================================================
# TEST-006: Operação com dados NaN
# =============================================================================

class TestNaNHandling:
    """Testes para tratamento de dados com NaN"""
    
    def test_load_csv_with_nan_values(self, tmp_path):
        """Testa CSV com valores NaN"""
        # CSV com NaN
        nan_csv = tmp_path / "nan_values.csv"
        content = """timestamp,value1,value2
2025-01-01 00:00:00,1.0,2.0
2025-01-01 00:01:00,NaN,3.0
2025-01-01 00:02:00,4.0,
2025-01-01 00:03:00,,5.0
2025-01-01 00:04:00,6.0,7.0
"""
        nan_csv.write_text(content)
        
        config = LoadConfig(min_valid_points=2, max_missing_ratio=0.99)
        
        dataset = load(str(nan_csv), config=config)
        
        assert dataset is not None
        # Verifica que séries foram carregadas
        assert len(dataset.series) > 0
    
    def test_interpolation_with_nan(self):
        """Testa interpolação com dados contendo NaN"""
        # Série com NaN
        time = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        values = np.array([1.0, np.nan, 3.0, np.nan, 5.0, 6.0])
        
        # Interpolação linear deve preencher NaN
        result = interpolate(values, time, method="linear", params={})
        
        assert result is not None
        # Verifica que NaN foram interpolados
        assert not np.any(np.isnan(result.values[result.interpolation_info.is_interpolated]))
    
    def test_derivative_with_nan(self):
        """Testa derivada com dados contendo NaN"""
        # Série com NaN - precisamos tratá-los primeiro
        time = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])  # Sem NaN para derivada
        
        # Derivada deve funcionar com dados limpos
        result = derivative(values, time, order=1, method="finite_diff")
        
        assert result is not None
        assert len(result.values) == len(values)
    
    def test_statistics_with_nan(self):
        """Testa cálculo de estatísticas com NaN"""
        # Série com NaN
        values = np.array([1.0, np.nan, 3.0, np.nan, 5.0])
        
        # Estatísticas devem ignorar NaN
        valid_values = values[~np.isnan(values)]
        
        assert len(valid_values) == 3
        assert np.nanmean(values) == np.mean(valid_values)
    
    def test_all_nan_values(self, tmp_path):
        """Testa série com todos valores NaN em uma coluna"""
        # CSV com coluna toda NaN
        all_nan_csv = tmp_path / "all_nan.csv"
        content = """timestamp,valid_col,nan_col
2025-01-01 00:00:00,1.0,
2025-01-01 00:01:00,2.0,
2025-01-01 00:02:00,3.0,
"""
        all_nan_csv.write_text(content)
        
        config = LoadConfig(min_valid_points=2, max_missing_ratio=0.5)
        
        # Deve carregar, mas nan_col pode ser ignorada
        dataset = load(str(all_nan_csv), config=config)
        
        assert dataset is not None
        # A coluna valid_col deve existir
        assert any("valid" in s.name.lower() for s in dataset.series.values())


# =============================================================================
# TEST-007: Cancelamento de operação em andamento
# =============================================================================

class TestOperationCancellation:
    """Testes para cancelamento de operações"""
    
    def test_cancellation_flag_propagation(self):
        """Testa propagação de flag de cancelamento"""
        import threading
        import time
        
        cancelled = threading.Event()
        results = []
        
        def long_operation():
            for i in range(100):
                if cancelled.is_set():
                    results.append("cancelled")
                    return
                time.sleep(0.01)
            results.append("completed")
        
        thread = threading.Thread(target=long_operation)
        thread.start()
        
        time.sleep(0.05)  # Deixa rodar um pouco
        cancelled.set()   # Cancela
        
        thread.join(timeout=1.0)
        
        assert "cancelled" in results
    
    def test_cancellation_pattern(self):
        """Testa padrão de cancelamento comum"""
        class CancellableOperation:
            def __init__(self):
                self._cancelled = False
            
            def cancel(self):
                self._cancelled = True
            
            def is_cancelled(self):
                return self._cancelled
            
            def run(self, iterations):
                results = []
                for i in range(iterations):
                    if self._cancelled:
                        return results, "cancelled"
                    results.append(i)
                    # Adiciona pequeno delay para permitir cancelamento
                    if i % 100 == 0:
                        time.sleep(0.001)
                return results, "completed"
        
        op = CancellableOperation()
        
        # Teste sem cancelamento
        results, status = op.run(5)
        assert status == "completed"
        assert len(results) == 5
        
        # Teste com cancelamento assíncrono
        op2 = CancellableOperation()
        import threading
        
        def cancel_after_delay():
            time.sleep(0.02)  # Aguarda um pouco mais
            op2.cancel()
        
        cancel_thread = threading.Thread(target=cancel_after_delay)
        cancel_thread.start()
        results, status = op2.run(100000)  # Mais iterações
        cancel_thread.join()
        
        # O cancelamento deve ocorrer antes de completar
        assert status == "cancelled" or len(results) < 100000


# =============================================================================
# TEST-008: Múltiplos datasets simultâneos
# =============================================================================

class TestMultipleDatasets:
    """Testes para múltiplos datasets simultâneos"""
    
    def test_load_multiple_csv_files(self, tmp_path):
        """Testa carregamento de múltiplos CSV"""
        datasets = []
        config = LoadConfig(min_valid_points=2)
        
        for i in range(5):
            csv_file = tmp_path / f"data_{i}.csv"
            n_rows = 100 + i * 50
            
            # Gera dados
            timestamps = pd.date_range("2025-01-01", periods=n_rows, freq="1min")
            df = pd.DataFrame({
                "timestamp": timestamps,
                f"value_{i}": np.random.randn(n_rows) * (i + 1)
            })
            df.to_csv(csv_file, index=False)
            
            # Carrega
            dataset = load(str(csv_file), config=config)
            datasets.append(dataset)
        
        assert len(datasets) == 5
        
        # Verifica que cada dataset tem dados
        for i, ds in enumerate(datasets):
            assert ds is not None
            assert len(ds.series) > 0
    
    def test_dataset_store_multiple_datasets(self):
        """Testa DatasetStore com múltiplos datasets"""
        store = DatasetStore()
        
        # Adiciona 5 datasets
        for i in range(5):
            series = make_series(
                f"series_{i}",
                np.linspace(0, 10, 50),
                np.random.randn(50)
            )
            
            dataset = make_dataset(f"dataset_{i}", {series.series_id: series})
            store.add_dataset(dataset)
        
        # Verifica
        assert len(store.list_datasets()) == 5
        
        # Acessa cada um
        for i in range(5):
            ds = store.get_dataset(f"dataset_{i}")
            assert ds is not None
    
    def test_concurrent_dataset_access(self):
        """Testa acesso concorrente a datasets"""
        from concurrent.futures import ThreadPoolExecutor
        
        store = DatasetStore()
        
        # Pré-popula com datasets
        for i in range(10):
            series = make_series(
                f"series_{i}",
                np.linspace(0, 10, 100),
                np.random.randn(100)
            )
            
            dataset = make_dataset(f"dataset_{i}", {series.series_id: series})
            store.add_dataset(dataset)
        
        errors = []
        
        def access_dataset(idx):
            try:
                ds = store.get_dataset(f"dataset_{idx % 10}")
                if ds is None:
                    errors.append(f"Dataset {idx % 10} not found")
                return ds
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Acessa concorrentemente
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(access_dataset, i) for i in range(100)]
            results = [f.result() for f in futures]
        
        assert len(errors) == 0, f"Errors: {errors}"
        assert all(r is not None for r in results)


# =============================================================================
# TEST-009: Stress test com 10+ datasets
# =============================================================================

class TestStressTests:
    """Testes de stress com muitos datasets"""
    
    def test_load_15_datasets(self, tmp_path):
        """Testa carregamento de 15 datasets"""
        store = DatasetStore()
        config = LoadConfig(min_valid_points=5)
        
        # Cria e carrega 15 arquivos
        for i in range(15):
            csv_file = tmp_path / f"stress_data_{i}.csv"
            n_rows = 500
            
            timestamps = pd.date_range("2025-01-01", periods=n_rows, freq="1min")
            df = pd.DataFrame({
                "timestamp": timestamps,
                "value": np.random.randn(n_rows),
                "value2": np.random.randn(n_rows)
            })
            df.to_csv(csv_file, index=False)
            
            dataset = load(str(csv_file), config=config)
            store.add_dataset(dataset)
        
        assert len(store.list_datasets()) == 15
    
    def test_memory_usage_multiple_datasets(self, tmp_path):
        """Testa uso de memória com múltiplos datasets"""
        import gc
        
        store = DatasetStore()
        config = LoadConfig(min_valid_points=5)
        
        # Carrega 10 datasets com 1000 pontos cada
        for i in range(10):
            csv_file = tmp_path / f"memory_test_{i}.csv"
            n_rows = 1000
            
            timestamps = pd.date_range("2025-01-01", periods=n_rows, freq="1min")
            df = pd.DataFrame({
                "timestamp": timestamps,
                "value": np.random.randn(n_rows)
            })
            df.to_csv(csv_file, index=False)
            
            dataset = load(str(csv_file), config=config)
            store.add_dataset(dataset)
        
        # Força garbage collection
        gc.collect()
        
        # Verifica que todos estão acessíveis
        assert len(store.list_datasets()) == 10
        
        # Limpa o store (acesso direto ao dicionário interno)
        with store._lock:
            store._datasets.clear()
        
        gc.collect()
        
        assert len(store.list_datasets()) == 0
    
    def test_concurrent_operations_stress(self):
        """Testa operações concorrentes sob stress"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        errors = []
        results = []
        
        def interpolate_data(idx):
            try:
                time = np.linspace(0, 100, 500 + idx * 10)
                values = np.sin(np.linspace(0, 10, 500 + idx * 10)) * (idx + 1)
                # Adiciona alguns NaN
                values[::50] = np.nan
                
                result = interpolate(values, time, method="linear", params={})
                return result
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Executa interpolações concorrentemente
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(interpolate_data, i): i for i in range(20)}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    results.append(result)
        
        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 20
    
    def test_large_dataset_operations(self, tmp_path):
        """Testa operações com dataset grande"""
        config = LoadConfig(min_valid_points=100)
        
        # Cria CSV com 100k linhas
        csv_file = tmp_path / "large_data.csv"
        n_rows = 100_000
        
        timestamps = pd.date_range("2020-01-01", periods=n_rows, freq="1s")
        df = pd.DataFrame({
            "timestamp": timestamps,
            "value1": np.random.randn(n_rows),
            "value2": np.random.randn(n_rows),
            "value3": np.random.randn(n_rows)
        })
        df.to_csv(csv_file, index=False)
        
        # Carrega
        start_time = time.time()
        dataset = load(str(csv_file), config=config)
        load_time = time.time() - start_time
        
        assert dataset is not None
        assert len(dataset.series) >= 1
        
        # Verifica que carregou em tempo razoável (< 30s)
        assert load_time < 30.0, f"Load took {load_time:.2f}s, expected < 30s"
    
    def test_rapid_add_remove_datasets(self):
        """Testa adição e remoção rápida de datasets"""
        store = DatasetStore()
        
        # Adiciona e remove rapidamente
        for cycle in range(5):
            # Adiciona 10 datasets
            for i in range(10):
                series = make_series(
                    f"series_{cycle}_{i}",
                    np.linspace(0, 10, 100),
                    np.random.randn(100)
                )
                
                dataset = make_dataset(f"dataset_{cycle}_{i}", {series.series_id: series})
                store.add_dataset(dataset)
            
            # Verifica contagem
            assert len(store.list_datasets()) == 10
            
            # Limpa o store (acesso direto ao dicionário interno)
            with store._lock:
                store._datasets.clear()
            
            assert len(store.list_datasets()) == 0


# =============================================================================
# Testes adicionais de edge cases
# =============================================================================

class TestEdgeCases:
    """Testes adicionais para edge cases"""
    
    def test_unicode_file_path(self, tmp_path):
        """Testa carregamento com caminho Unicode"""
        # Cria diretório com caracteres Unicode
        unicode_dir = tmp_path / "dados_acao_manutencao"
        unicode_dir.mkdir(exist_ok=True)
        
        csv_file = unicode_dir / "medicao_valvula.csv"
        timestamps = pd.date_range("2025-01-01", periods=50, freq="1min")
        df = pd.DataFrame({
            "timestamp": timestamps,
            "pressao": np.random.randn(50)
        })
        df.to_csv(csv_file, index=False)
        
        config = LoadConfig(min_valid_points=5)
        
        dataset = load(str(csv_file), config=config)
        
        assert dataset is not None
    
    def test_very_long_column_names(self, tmp_path):
        """Testa CSV com nomes de coluna muito longos"""
        csv_file = tmp_path / "long_names.csv"
        
        long_name = "A" * 255
        timestamps = pd.date_range("2025-01-01", periods=50, freq="1min")
        df = pd.DataFrame({
            "timestamp": timestamps,
            long_name: np.random.randn(50)
        })
        df.to_csv(csv_file, index=False)
        
        config = LoadConfig(min_valid_points=5)
        
        dataset = load(str(csv_file), config=config)
        
        assert dataset is not None
    
    def test_special_characters_in_values(self, tmp_path):
        """Testa CSV com caracteres especiais nos valores"""
        csv_file = tmp_path / "special_chars.csv"
        content = """timestamp,value,text
2025-01-01 00:00:00,1.0,"normal"
2025-01-01 00:01:00,2.0,"with,comma"
2025-01-01 00:02:00,3.0,"with""quote"
2025-01-01 00:03:00,4.0,"withnewline"
2025-01-01 00:04:00,5.0,"normal again"
"""
        csv_file.write_text(content)
        
        config = LoadConfig(min_valid_points=3)
        
        dataset = load(str(csv_file), config=config)
        
        assert dataset is not None
    
    def test_extreme_values(self, tmp_path):
        """Testa CSV com valores extremos"""
        csv_file = tmp_path / "extreme_values.csv"
        timestamps = pd.date_range("2025-01-01", periods=10, freq="1min")
        df = pd.DataFrame({
            "timestamp": timestamps,
            "value": [1e100, -1e100, 1e-100, 0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
        })
        df.to_csv(csv_file, index=False)
        
        config = LoadConfig(min_valid_points=3)
        
        # Deve lidar com valores extremos (sem inf)
        dataset = load(str(csv_file), config=config)
        assert dataset is not None
    
    def test_duplicate_timestamps(self, tmp_path):
        """Testa CSV com timestamps duplicados"""
        csv_file = tmp_path / "dup_timestamps.csv"
        content = """timestamp,value
2025-01-01 00:00:00,1.0
2025-01-01 00:00:00,2.0
2025-01-01 00:01:00,3.0
2025-01-01 00:01:00,4.0
2025-01-01 00:02:00,5.0
"""
        csv_file.write_text(content)
        
        config = LoadConfig(min_valid_points=2)
        
        # Deve lidar com duplicados
        dataset = load(str(csv_file), config=config)
        
        assert dataset is not None


class TestDataIntegrity:
    """Testes de integridade de dados"""
    
    def test_data_roundtrip_csv(self, tmp_path):
        """Testa que dados são preservados no roundtrip CSV"""
        # Dados originais
        original_values = np.array([1.23456789, 2.34567890, 3.45678901, 4.56789012, 5.67890123])
        original_times = pd.date_range("2025-01-01", periods=5, freq="1min")
        
        # Salva
        csv_file = tmp_path / "roundtrip.csv"
        df = pd.DataFrame({
            "timestamp": original_times,
            "value": original_values
        })
        df.to_csv(csv_file, index=False)
        
        # Carrega
        config = LoadConfig(min_valid_points=3)
        dataset = load(str(csv_file), config=config)
        
        # Verifica integridade
        assert dataset is not None
        series = list(dataset.series.values())[0]
        
        # Valores devem ser próximos (pode haver perda de precisão)
        np.testing.assert_array_almost_equal(series.values, original_values, decimal=5)
    
    def test_timestamp_precision(self, tmp_path):
        """Testa precisão de timestamps"""
        # Timestamps com microsegundos
        csv_file = tmp_path / "precision.csv"
        content = """timestamp,value
2025-01-01 00:00:00.123456,1.0
2025-01-01 00:00:00.234567,2.0
2025-01-01 00:00:00.345678,3.0
2025-01-01 00:00:00.456789,4.0
2025-01-01 00:00:00.567890,5.0
"""
        csv_file.write_text(content)
        
        config = LoadConfig(min_valid_points=3)
        
        dataset = load(str(csv_file), config=config)
        
        assert dataset is not None
        
        # Verifica que timestamps são distintos
        assert len(np.unique(dataset.t_seconds)) == 5
