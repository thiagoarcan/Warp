"""
Testes para módulos de I/O - Platform Base v2.0
Cobertura para encoding_detector, schema_detector, loader, validator
"""
import os
import tempfile
from pathlib import Path

import numpy as np
import pytest


class TestEncodingDetector:
    """Testes para io/encoding_detector.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.io import detect_bom, detect_encoding, get_encoding_info
        assert detect_encoding is not None
        assert detect_bom is not None
        assert get_encoding_info is not None
    
    def test_detect_encoding_utf8(self):
        """Testa detecção de UTF-8."""
        from platform_base.io import detect_encoding
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("nome,valor\n")
            f.write("teste,123\n")
            f.write("açúcar,456\n")
            temp_path = f.name
        
        try:
            encoding = detect_encoding(temp_path)
            assert encoding is not None
            # Normaliza para comparação (utf_8 -> utf-8)
            encoding_norm = encoding.lower().replace('_', '-')
            assert encoding_norm in ['utf-8', 'utf-8-sig', 'ascii']
        finally:
            os.unlink(temp_path)
    
    def test_detect_encoding_latin1(self):
        """Testa detecção de Latin-1."""
        from platform_base.io import detect_encoding
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write("nome,valor\n".encode('latin-1'))
            f.write("café,789\n".encode('latin-1'))
            temp_path = f.name
        
        try:
            encoding = detect_encoding(temp_path)
            assert encoding is not None
        finally:
            os.unlink(temp_path)
    
    def test_get_encoding_info(self):
        """Testa obtenção de informações de encoding."""
        from platform_base.io import get_encoding_info
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("col1,col2\n1,2\n3,4\n")
            temp_path = f.name
        
        try:
            info = get_encoding_info(temp_path)
            assert info is not None
        finally:
            os.unlink(temp_path)


class TestSchemaDetector:
    """Testes para io/schema_detector.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.io import SchemaRules, detect_schema
        assert detect_schema is not None
        assert SchemaRules is not None
    
    def test_schema_rules(self):
        """Testa SchemaRules."""
        from platform_base.io import SchemaRules
        
        rules = SchemaRules()
        assert rules is not None


class TestLoader:
    """Testes para io/loader.py."""
    
    def test_import(self):
        """Testa importação do módulo."""
        from platform_base.io import FileFormat, LoadConfig, load
        assert load is not None
        assert LoadConfig is not None
        assert FileFormat is not None
    
    def test_load_csv(self):
        """Testa carregamento de CSV."""
        from platform_base.io import load
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("time,value1,value2\n")
            for i in range(100):
                f.write(f"{i*0.1},{np.sin(i*0.1)},{np.cos(i*0.1)}\n")
            temp_path = f.name
        
        try:
            result = load(temp_path)
            assert result is not None
        finally:
            os.unlink(temp_path)
    
    def test_load_with_config(self):
        """Testa carregamento com configuração."""
        from platform_base.io import LoadConfig, load
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("t,x,y\n")
            for i in range(50):
                f.write(f"{i},{i*2},{i*3}\n")
            temp_path = f.name
        
        try:
            config = LoadConfig(
                timestamp_column="t",
                encoding="utf-8"
            )
            result = load(temp_path, config=config)
            assert result is not None
        finally:
            os.unlink(temp_path)
    
    def test_file_format_enum(self):
        """Testa FileFormat enum."""
        from platform_base.io import FileFormat
        
        assert hasattr(FileFormat, 'CSV') or 'csv' in str(FileFormat).lower()


class TestLoadConfig:
    """Testes para LoadConfig."""
    
    def test_default_config(self):
        """Testa configuração padrão."""
        from platform_base.io import LoadConfig
        
        config = LoadConfig()
        assert config is not None
    
    def test_config_attributes(self):
        """Testa atributos da configuração."""
        from platform_base.io import LoadConfig
        
        config = LoadConfig(
            timestamp_column="timestamp",
            encoding="utf-8"
        )
        
        assert config.timestamp_column == "timestamp"
        assert config.encoding == "utf-8"


class TestLoadStrategy:
    """Testes para estratégias de carregamento."""
    
    def test_import(self):
        """Testa importação."""
        from platform_base.io import LoadStrategy
        assert LoadStrategy is not None


class TestEdgeCases:
    """Testes para casos extremos."""
    
    def test_empty_file(self):
        """Testa arquivo vazio."""
        from platform_base.io import load
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            # Pode levantar exceção ou retornar None
            try:
                result = load(temp_path)
            except Exception:
                pass  # Esperado para arquivo vazio
        finally:
            os.unlink(temp_path)
    
    def test_header_only(self):
        """Testa arquivo apenas com header."""
        from platform_base.io import load
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("col1,col2,col3\n")
            temp_path = f.name
        
        try:
            try:
                result = load(temp_path)
            except Exception:
                pass  # Pode falhar se não houver dados
        finally:
            os.unlink(temp_path)
    
    def test_large_file_simulation(self):
        """Testa simulação de arquivo grande."""
        from platform_base.io import load
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("time,value\n")
            for i in range(1000):  # 1000 linhas
                f.write(f"{i*0.001},{np.sin(i*0.01)}\n")
            temp_path = f.name
        
        try:
            result = load(temp_path)
            assert result is not None
        finally:
            os.unlink(temp_path)
