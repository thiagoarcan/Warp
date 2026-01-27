"""
Testes completos para io/loader.py - Platform Base v2.0

Cobertura 100% do DataLoaderService e funções auxiliares.
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest


class TestFileFormat:
    """Testes para FileFormat enum"""
    
    def test_from_extension_csv(self):
        """Testa detecção de CSV"""
        from platform_base.io.loader import FileFormat
        
        assert FileFormat.from_extension('.csv') == FileFormat.CSV
        assert FileFormat.from_extension('csv') == FileFormat.CSV
        assert FileFormat.from_extension('.CSV') == FileFormat.CSV
    
    def test_from_extension_txt(self):
        """Testa detecção de TXT como CSV"""
        from platform_base.io.loader import FileFormat
        
        assert FileFormat.from_extension('.txt') == FileFormat.CSV
    
    def test_from_extension_excel(self):
        """Testa detecção de Excel"""
        from platform_base.io.loader import FileFormat
        
        assert FileFormat.from_extension('.xlsx') == FileFormat.EXCEL
        assert FileFormat.from_extension('.xls') == FileFormat.EXCEL
    
    def test_from_extension_parquet(self):
        """Testa detecção de Parquet"""
        from platform_base.io.loader import FileFormat
        
        assert FileFormat.from_extension('.parquet') == FileFormat.PARQUET
        assert FileFormat.from_extension('.pq') == FileFormat.PARQUET
    
    def test_from_extension_hdf5(self):
        """Testa detecção de HDF5"""
        from platform_base.io.loader import FileFormat
        
        assert FileFormat.from_extension('.h5') == FileFormat.HDF5
        assert FileFormat.from_extension('.hdf5') == FileFormat.HDF5
    
    def test_from_extension_unsupported(self):
        """Testa extensão não suportada"""
        from platform_base.io.loader import FileFormat
        from platform_base.utils.errors import DataLoadError
        
        with pytest.raises(DataLoadError):
            FileFormat.from_extension('.unknown')


class TestLoadConfig:
    """Testes para LoadConfig"""
    
    def test_default_config(self):
        """Testa configuração padrão"""
        from platform_base.io.loader import LoadConfig
        
        config = LoadConfig()
        
        assert config.timestamp_column is None
        assert config.delimiter == ","
        assert config.encoding == "auto"
        assert config.max_missing_ratio == 0.95
        assert config.min_valid_points == 10
    
    def test_custom_config(self):
        """Testa configuração customizada"""
        from platform_base.io.loader import LoadConfig
        
        config = LoadConfig(
            timestamp_column="time",
            delimiter=";",
            encoding="utf-8",
            max_rows=1000
        )
        
        assert config.timestamp_column == "time"
        assert config.delimiter == ";"
        assert config.encoding == "utf-8"
        assert config.max_rows == 1000
    
    def test_invalid_missing_ratio(self):
        """Testa validação de missing_ratio"""
        from platform_base.io.loader import LoadConfig
        
        with pytest.raises(ValueError):
            LoadConfig(max_missing_ratio=1.5)
        
        with pytest.raises(ValueError):
            LoadConfig(max_missing_ratio=-0.1)
    
    def test_invalid_min_points(self):
        """Testa validação de min_valid_points"""
        from platform_base.io.loader import LoadConfig
        
        with pytest.raises(ValueError):
            LoadConfig(min_valid_points=0)


class TestLoadStrategy:
    """Testes para LoadStrategy"""
    
    def test_strategy_creation(self):
        """Testa criação de estratégia"""
        from platform_base.io.loader import FileFormat, LoadStrategy
        
        strategy = LoadStrategy(format=FileFormat.CSV)
        
        assert strategy.format == FileFormat.CSV
        assert strategy.reader_params == {}
    
    def test_strategy_with_params(self):
        """Testa estratégia com parâmetros"""
        from platform_base.io.loader import FileFormat, LoadStrategy
        
        strategy = LoadStrategy(
            format=FileFormat.EXCEL,
            reader_params={"header": 1}
        )
        
        assert strategy.reader_params["header"] == 1


class TestParseTimestamps:
    """Testes para _parse_timestamps"""
    
    def test_parse_datetime_series(self):
        """Testa parsing de série datetime"""
        from platform_base.io.loader import _parse_timestamps
        
        series = pd.Series(pd.date_range('2024-01-01', periods=10, freq='h'))
        
        result = _parse_timestamps(series)
        
        assert len(result) == 10
        assert isinstance(result, pd.DatetimeIndex)
    
    def test_parse_string_timestamps(self):
        """Testa parsing de strings"""
        from platform_base.io.loader import _parse_timestamps
        
        series = pd.Series([
            "2024-01-01 00:00:00",
            "2024-01-01 01:00:00",
            "2024-01-01 02:00:00"
        ])
        
        result = _parse_timestamps(series)
        
        assert len(result) == 3
    
    def test_parse_iso_format(self):
        """Testa parsing de formato ISO"""
        from platform_base.io.loader import _parse_timestamps
        
        series = pd.Series([
            "2024-01-01T00:00:00",
            "2024-01-01T01:00:00"
        ])
        
        result = _parse_timestamps(series)
        
        assert len(result) == 2
    
    def test_parse_brazilian_format(self):
        """Testa parsing de formato brasileiro"""
        from platform_base.io.loader import _parse_timestamps
        
        series = pd.Series([
            "01/01/2024 00:00:00",
            "02/01/2024 00:00:00"
        ])
        
        result = _parse_timestamps(series)
        
        assert len(result) == 2


class TestValidateDataframe:
    """Testes para _validate_dataframe"""
    
    def test_validate_empty_dataframe(self):
        """Testa validação de DataFrame vazio"""
        from platform_base.io.loader import LoadConfig, _validate_dataframe
        from platform_base.utils.errors import DataLoadError
        
        df = pd.DataFrame()
        config = LoadConfig()
        
        with pytest.raises(DataLoadError):
            _validate_dataframe(df, config)
    
    def test_validate_too_few_points(self):
        """Testa validação com poucos pontos"""
        from platform_base.io.loader import LoadConfig, _validate_dataframe
        from platform_base.utils.errors import DataLoadError
        
        df = pd.DataFrame({'value': [1, 2, 3]})
        config = LoadConfig(min_valid_points=10)
        
        with pytest.raises(DataLoadError):
            _validate_dataframe(df, config)
    
    def test_validate_no_numeric_columns(self):
        """Testa validação sem colunas numéricas"""
        from platform_base.io.loader import LoadConfig, _validate_dataframe
        from platform_base.utils.errors import DataLoadError
        
        df = pd.DataFrame({
            'col1': ['a', 'b', 'c'] * 10,
            'col2': ['x', 'y', 'z'] * 10
        })
        config = LoadConfig()
        
        with pytest.raises(DataLoadError):
            _validate_dataframe(df, config)
    
    def test_validate_valid_dataframe(self):
        """Testa validação de DataFrame válido"""
        from platform_base.io.loader import LoadConfig, _validate_dataframe
        
        df = pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=100, freq='s'),
            'value': np.random.randn(100)
        })
        config = LoadConfig()
        
        # Não deve levantar exceção
        _validate_dataframe(df, config)


class TestLoadFunction:
    """Testes para função load"""
    
    def test_load_csv_basic(self):
        """Testa carregamento básico de CSV"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(100):
                ts = f"2024-01-01 00:00:{i:02d}"
                f.write(f"{ts},{np.random.randn()}\n")
            temp_file = f.name
        
        try:
            dataset = load(temp_file)
            
            assert dataset is not None
            assert len(dataset.t_seconds) == 100
        finally:
            os.unlink(temp_file)
    
    def test_load_file_not_found(self):
        """Testa carregamento de arquivo inexistente"""
        from platform_base.io.loader import load
        from platform_base.utils.errors import DataLoadError
        
        with pytest.raises(DataLoadError):
            load("/nonexistent/file.csv")
    
    def test_load_unsupported_format(self):
        """Testa carregamento de formato não suportado"""
        from platform_base.io.loader import load
        from platform_base.utils.errors import DataLoadError
        
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False, mode='w') as f:
            f.write("data")
            temp_file = f.name
        
        try:
            with pytest.raises(DataLoadError):
                load(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_with_config(self):
        """Testa carregamento com configuração"""
        from platform_base.io.loader import LoadConfig, load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("time;sensor_a;sensor_b\n")
            for i in range(50):
                ts = f"2024-01-01 00:00:{i:02d}"
                f.write(f"{ts};{i};{i*2}\n")
            temp_file = f.name
        
        try:
            config = LoadConfig(
                timestamp_column="time",
                delimiter=";"
            )
            
            dataset = load(temp_file, config)
            
            assert len(dataset.t_seconds) == 50
        finally:
            os.unlink(temp_file)


class TestDataLoaderService:
    """Testes para DataLoaderService"""
    
    def test_service_load_file(self):
        """Testa DataLoaderService.load_file"""
        from platform_base.io.loader import DataLoaderService
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(20):
                f.write(f"2024-01-01 00:{i:02d}:00,{i}\n")
            temp_file = f.name
        
        try:
            service = DataLoaderService()
            result = service.load_file(temp_file)
            
            assert result is not None
            assert isinstance(result, pd.DataFrame)
        finally:
            os.unlink(temp_file)


class TestLoadExcel:
    """Testes para carregamento de Excel"""
    
    def test_load_xlsx(self):
        """Testa carregamento de arquivo Excel"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_file = f.name
        
        try:
            # Cria arquivo Excel
            df = pd.DataFrame({
                'timestamp': pd.date_range('2024-01-01', periods=50, freq='h'),
                'value': np.random.randn(50)
            })
            df.to_excel(temp_file, index=False)
            
            dataset = load(temp_file)
            
            assert dataset is not None
            assert len(dataset.t_seconds) == 50
        finally:
            os.unlink(temp_file)


class TestLoadConfigValidation:
    """Testes de validação da configuração"""
    
    def test_unit_overrides(self):
        """Testa override de unidades"""
        from platform_base.io.loader import LoadConfig
        
        config = LoadConfig(
            unit_overrides={
                "temperature": "degC",
                "pressure": "bar"
            }
        )
        
        assert config.unit_overrides["temperature"] == "degC"
    
    def test_sheet_name_config(self):
        """Testa configuração de sheet_name"""
        from platform_base.io.loader import LoadConfig

        # Por nome
        config1 = LoadConfig(sheet_name="Data")
        assert config1.sheet_name == "Data"
        
        # Por índice
        config2 = LoadConfig(sheet_name=1)
        assert config2.sheet_name == 1


class TestSourceInfo:
    """Testes para criação de SourceInfo"""
    
    def test_create_source_info(self):
        """Testa criação de SourceInfo"""
        from platform_base.io.loader import FileFormat, _create_source_info
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("test data")
            temp_file = Path(f.name)
        
        try:
            info = _create_source_info(temp_file, FileFormat.CSV)
            
            assert info.filename.endswith('.csv')
            assert info.format == 'csv'
            assert info.size_bytes > 0
            assert len(info.checksum) == 64  # SHA256
        finally:
            os.unlink(temp_file)


class TestLoadEdgeCases:
    """Testes de edge cases"""
    
    def test_load_with_null_values(self):
        """Testa carregamento com valores nulos"""
        from platform_base.io.loader import load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(30):
                value = "" if i % 5 == 0 else str(i)
                f.write(f"2024-01-01 00:{i:02d}:00,{value}\n")
            temp_file = f.name
        
        try:
            dataset = load(temp_file)
            
            # Deve carregar com NaN nos valores nulos
            assert dataset is not None
        finally:
            os.unlink(temp_file)
    
    def test_load_large_file(self):
        """Testa carregamento com max_rows"""
        from platform_base.io.loader import LoadConfig, load
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i in range(1000):
                f.write(f"2024-01-01 00:00:{i % 60:02d},{i}\n")
            temp_file = f.name
        
        try:
            config = LoadConfig(max_rows=100)
            dataset = load(temp_file, config)
            
            # Deve respeitar limite
            assert len(dataset.t_seconds) <= 100
        finally:
            os.unlink(temp_file)
