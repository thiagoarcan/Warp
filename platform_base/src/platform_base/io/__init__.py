# IO package
"""
Platform Base IO Module

Módulo de entrada/saída de dados:
- Carregamento de arquivos (CSV, Excel, Parquet, HDF5)
- Detecção automática de schema
- Detecção automática de encoding
- Validação de dados
- Exportação
"""

from platform_base.io.encoding_detector import (
    detect_bom,
    detect_encoding,
    get_encoding_info,
)
from platform_base.io.loader import (
    FileFormat,
    LoadConfig,
    LoadStrategy,
    load,
    load_async,
)
from platform_base.io.schema_detector import SchemaRules, detect_schema

__all__ = [
    # Loader
    'FileFormat',
    'LoadConfig',
    'LoadStrategy',
    'load',
    'load_async',
    
    # Encoding
    'detect_encoding',
    'get_encoding_info',
    'detect_bom',
    
    # Schema
    'SchemaRules',
    'detect_schema',
]