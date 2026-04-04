"""
Testes completos para utils/errors.py - Platform Base v2.0

Cobertura de 100% das classes de erro e funções auxiliares.
"""

import pytest

from platform_base.utils.errors import (
    CacheError,
    CalculusError,
    ConfigError,
    DataLoadError,
    DownsampleError,
    ExportError,
    InterpolationError,
    PlatformError,
    PluginError,
    SchemaDetectionError,
    StreamingError,
    ValidationError,
    handle_error,
)


class TestPlatformError:
    """Testes para classe base PlatformError"""
    
    def test_create_with_message_only(self):
        """Testa criação com apenas mensagem"""
        error = PlatformError("Test error message")
        
        assert error.message == "Test error message"
        assert error.context == {}
        assert str(error) == "Test error message"
    
    def test_create_with_message_and_context(self):
        """Testa criação com mensagem e contexto"""
        context = {"key": "value", "count": 42}
        error = PlatformError("Error with context", context)
        
        assert error.message == "Error with context"
        assert error.context == context
        assert error.context["key"] == "value"
        assert error.context["count"] == 42
    
    def test_context_is_none_defaults_to_empty_dict(self):
        """Testa que contexto None vira dict vazio"""
        error = PlatformError("Test", None)
        
        assert error.context == {}
        assert isinstance(error.context, dict)
    
    def test_inheritance_from_exception(self):
        """Testa que PlatformError herda de Exception"""
        error = PlatformError("Test")
        
        assert isinstance(error, Exception)
    
    def test_raise_and_catch(self):
        """Testa raise e catch do erro"""
        with pytest.raises(PlatformError) as exc_info:
            raise PlatformError("Raised error", {"source": "test"})
        
        assert exc_info.value.message == "Raised error"
        assert exc_info.value.context["source"] == "test"


class TestDataLoadError:
    """Testes para DataLoadError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = DataLoadError("Load failed")
        
        assert isinstance(error, PlatformError)
        assert isinstance(error, Exception)
    
    def test_with_file_context(self):
        """Testa com contexto de arquivo"""
        error = DataLoadError(
            "Failed to load file",
            {"filepath": "/path/to/file.csv", "format": "csv", "size": 1024}
        )
        
        assert error.message == "Failed to load file"
        assert error.context["filepath"] == "/path/to/file.csv"
        assert error.context["format"] == "csv"
    
    def test_raise_and_catch_specific(self):
        """Testa catch específico de DataLoadError"""
        with pytest.raises(DataLoadError):
            raise DataLoadError("File not found", {"path": "/test"})


class TestSchemaDetectionError:
    """Testes para SchemaDetectionError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = SchemaDetectionError("Schema detection failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_schema_context(self):
        """Testa com contexto de schema"""
        error = SchemaDetectionError(
            "Cannot detect timestamp column",
            {"columns": ["col1", "col2", "col3"], "confidence": 0.3}
        )
        
        assert "columns" in error.context
        assert error.context["confidence"] == 0.3


class TestValidationError:
    """Testes para ValidationError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = ValidationError("Validation failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_validation_context(self):
        """Testa com contexto de validação"""
        error = ValidationError(
            "Invalid data format",
            {"field": "timestamp", "expected": "datetime", "got": "string"}
        )
        
        assert error.context["field"] == "timestamp"
        assert error.context["expected"] == "datetime"


class TestInterpolationError:
    """Testes para InterpolationError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = InterpolationError("Interpolation failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_method_context(self):
        """Testa com contexto de método de interpolação"""
        error = InterpolationError(
            "Insufficient points for spline",
            {"method": "spline_cubic", "n_points": 2, "min_required": 4}
        )
        
        assert error.context["method"] == "spline_cubic"
        assert error.context["n_points"] == 2


class TestCalculusError:
    """Testes para CalculusError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = CalculusError("Calculus operation failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_derivative_context(self):
        """Testa com contexto de derivada"""
        error = CalculusError(
            "Order must be between 1 and 3",
            {"order": 5, "operation": "derivative"}
        )
        
        assert error.context["order"] == 5
        assert error.context["operation"] == "derivative"


class TestPluginError:
    """Testes para PluginError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = PluginError("Plugin loading failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_plugin_context(self):
        """Testa com contexto de plugin"""
        error = PluginError(
            "Plugin not found",
            {"plugin_name": "dtw_plugin", "path": "/plugins/dtw"}
        )
        
        assert error.context["plugin_name"] == "dtw_plugin"


class TestExportError:
    """Testes para ExportError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = ExportError("Export failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_export_context(self):
        """Testa com contexto de exportação"""
        error = ExportError(
            "Cannot write to file",
            {"filepath": "/output/data.csv", "format": "csv", "reason": "permission denied"}
        )
        
        assert error.context["format"] == "csv"
        assert error.context["reason"] == "permission denied"


class TestCacheError:
    """Testes para CacheError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = CacheError("Cache operation failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_cache_context(self):
        """Testa com contexto de cache"""
        error = CacheError(
            "Cache key not found",
            {"key": "dataset_123", "cache_type": "memory"}
        )
        
        assert error.context["key"] == "dataset_123"
        assert error.context["cache_type"] == "memory"


class TestDownsampleError:
    """Testes para DownsampleError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = DownsampleError("Downsampling failed")
        
        assert isinstance(error, PlatformError)
    
    def test_with_downsample_context(self):
        """Testa com contexto de downsampling"""
        error = DownsampleError(
            "Invalid target points",
            {"method": "lttb", "n_points": 0, "original_size": 10000}
        )
        
        assert error.context["method"] == "lttb"
        assert error.context["n_points"] == 0


class TestConfigError:
    """Testes para ConfigError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = ConfigError("Configuration error")
        
        assert isinstance(error, PlatformError)
    
    def test_with_config_context(self):
        """Testa com contexto de configuração"""
        error = ConfigError(
            "Invalid configuration key",
            {"key": "invalid.path", "expected_type": "string"}
        )
        
        assert error.context["key"] == "invalid.path"


class TestStreamingError:
    """Testes para StreamingError"""
    
    def test_inheritance(self):
        """Testa herança de PlatformError"""
        error = StreamingError("Streaming error")
        
        assert isinstance(error, PlatformError)
    
    def test_with_streaming_context(self):
        """Testa com contexto de streaming"""
        error = StreamingError(
            "Buffer overflow",
            {"buffer_size": 10000, "incoming_rate": 15000}
        )
        
        assert error.context["buffer_size"] == 10000
        assert error.context["incoming_rate"] == 15000


class TestHandleError:
    """Testes para função handle_error"""
    
    def test_handle_platform_error(self):
        """Testa tratamento de PlatformError"""
        error = PlatformError("Test error", {"source": "unit_test"})
        
        # Não deve lançar exceção
        handle_error(error)
    
    def test_handle_dataload_error(self):
        """Testa tratamento de DataLoadError"""
        error = DataLoadError("Load failed", {"file": "test.csv"})
        
        handle_error(error)
    
    def test_handle_all_error_types(self):
        """Testa tratamento de todos os tipos de erro"""
        errors = [
            PlatformError("Platform error"),
            DataLoadError("Data load error"),
            SchemaDetectionError("Schema error"),
            ValidationError("Validation error"),
            InterpolationError("Interpolation error"),
            CalculusError("Calculus error"),
            PluginError("Plugin error"),
            ExportError("Export error"),
            CacheError("Cache error"),
            DownsampleError("Downsample error"),
            ConfigError("Config error"),
            StreamingError("Streaming error"),
        ]
        
        for error in errors:
            handle_error(error)


class TestErrorChaining:
    """Testes para encadeamento de erros"""
    
    def test_nested_try_except(self):
        """Testa captura aninhada de erros"""
        def inner_function():
            raise DataLoadError("Inner error", {"level": "inner"})
        
        def outer_function():
            try:
                inner_function()
            except DataLoadError as e:
                raise ValidationError("Outer error", {"original": e.message})
        
        with pytest.raises(ValidationError) as exc_info:
            outer_function()
        
        assert exc_info.value.context["original"] == "Inner error"
    
    def test_catch_as_base_class(self):
        """Testa captura como classe base"""
        errors_caught = []
        
        try:
            raise DataLoadError("Test")
        except PlatformError as e:
            errors_caught.append(type(e).__name__)
        
        try:
            raise CalculusError("Test")
        except PlatformError as e:
            errors_caught.append(type(e).__name__)
        
        assert "DataLoadError" in errors_caught
        assert "CalculusError" in errors_caught
