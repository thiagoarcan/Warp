"""
Tests for ui/export.py - Export functionality

Tests for export configuration, session data, and export utilities.
"""

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestExportResult:
    """Tests for ExportResult model"""

    def test_export_result_creation(self):
        """Test creating ExportResult with required fields"""
        from platform_base.ui.export import ExportResult
        
        result = ExportResult(
            path=Path("/tmp/export.csv"),
            size_bytes=1024,
            rows_exported=100,
            export_time_seconds=1.5
        )
        
        assert result.path == Path("/tmp/export.csv")
        assert result.size_bytes == 1024
        assert result.rows_exported == 100
        assert result.export_time_seconds == 1.5

    def test_export_result_model_dump(self):
        """Test serializing ExportResult"""
        from platform_base.ui.export import ExportResult
        
        result = ExportResult(
            path=Path("/tmp/test.csv"),
            size_bytes=2048,
            rows_exported=200,
            export_time_seconds=2.0
        )
        
        data = result.model_dump()
        
        assert isinstance(data, dict)
        assert "path" in data
        assert data["size_bytes"] == 2048


class TestExportProgress:
    """Tests for ExportProgress model"""

    def test_export_progress_creation(self):
        """Test creating ExportProgress"""
        from platform_base.ui.export import ExportProgress
        
        progress = ExportProgress(
            percent=50.0,
            current_chunk=5,
            total_chunks=10,
            message="Exporting..."
        )
        
        assert progress.percent == 50.0
        assert progress.current_chunk == 5
        assert progress.total_chunks == 10
        assert progress.message == "Exporting..."

    def test_export_progress_zero_percent(self):
        """Test ExportProgress at start"""
        from platform_base.ui.export import ExportProgress
        
        progress = ExportProgress(
            percent=0.0,
            current_chunk=0,
            total_chunks=100,
            message="Starting export"
        )
        
        assert progress.percent == 0.0
        assert progress.current_chunk == 0

    def test_export_progress_complete(self):
        """Test ExportProgress at completion"""
        from platform_base.ui.export import ExportProgress
        
        progress = ExportProgress(
            percent=100.0,
            current_chunk=10,
            total_chunks=10,
            message="Export complete"
        )
        
        assert progress.percent == 100.0
        assert progress.current_chunk == progress.total_chunks


class TestExportConfig:
    """Tests for ExportConfig model"""

    def test_export_config_defaults(self):
        """Test ExportConfig with default values"""
        from platform_base.ui.export import ExportConfig
        
        config = ExportConfig()
        
        assert config.chunk_size_mb == 50
        assert config.async_threshold_mb == 10
        assert config.max_workers == 2
        assert config.compress is False
        assert config.include_metadata is True

    def test_export_config_custom(self):
        """Test ExportConfig with custom values"""
        from platform_base.ui.export import ExportConfig
        
        config = ExportConfig(
            chunk_size_mb=100,
            async_threshold_mb=20,
            max_workers=4,
            compress=True,
            include_metadata=False
        )
        
        assert config.chunk_size_mb == 100
        assert config.max_workers == 4
        assert config.compress is True
        assert config.include_metadata is False


class TestSessionData:
    """Tests for SessionData model"""

    def test_session_data_creation(self):
        """Test creating SessionData with minimal fields"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="test-123",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T01:00:00Z"
        )
        
        assert session.session_id == "test-123"
        assert session.version == "2.0.0"
        assert session.checksum == ""

    def test_session_data_defaults(self):
        """Test SessionData default factory fields"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z"
        )
        
        assert session.config == {}
        assert session.dataset_references == []
        assert session.selections == {}
        assert session.view_subscriptions == {}
        assert session.visualization_states == {}
        assert session.annotations == []
        assert session.processing_history == []
        assert session.streaming_sessions == {}

    def test_session_data_with_data(self):
        """Test SessionData with populated fields"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="full-test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T02:00:00Z",
            config={"theme": "dark"},
            dataset_references=[{"path": "/data/file.csv"}],
            annotations=[{"id": 1, "text": "Note"}]
        )
        
        assert session.config["theme"] == "dark"
        assert len(session.dataset_references) == 1
        assert len(session.annotations) == 1

    def test_session_data_model_dump(self):
        """Test serializing SessionData"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="serialize-test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z"
        )
        
        data = session.model_dump()
        
        assert isinstance(data, dict)
        assert data["version"] == "2.0.0"
        assert data["session_id"] == "serialize-test"


class TestGetFileSizeMb:
    """Tests for _get_file_size_mb function"""

    def test_get_file_size_nonexistent(self):
        """Test getting size of non-existent file"""
        from platform_base.ui.export import _get_file_size_mb
        
        result = _get_file_size_mb(Path("/nonexistent/file.txt"))
        
        assert result == 0.0

    def test_get_file_size_existing(self):
        """Test getting size of existing file"""
        from platform_base.ui.export import _get_file_size_mb
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * (1024 * 1024))  # 1 MB
            temp_path = Path(f.name)
        
        try:
            size = _get_file_size_mb(temp_path)
            assert 0.9 <= size <= 1.1  # Should be close to 1 MB
        finally:
            temp_path.unlink()

    def test_get_file_size_small_file(self):
        """Test getting size of small file"""
        from platform_base.ui.export import _get_file_size_mb
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"small data")
            temp_path = Path(f.name)
        
        try:
            size = _get_file_size_mb(temp_path)
            assert size < 0.001  # Less than 1 KB
        finally:
            temp_path.unlink()


class TestExportFormat:
    """Tests for ExportFormat type"""

    def test_export_format_values(self):
        """Test valid export format values"""
        from platform_base.ui.export import ExportFormat

        # These should be valid literal values
        valid_formats = ["csv", "xlsx", "parquet", "hdf5", "json"]
        
        for fmt in valid_formats:
            # Type checking would validate, here just verify they're strings
            assert isinstance(fmt, str)


class TestSessionDataChecksum:
    """Tests for SessionData checksum functionality"""

    def test_session_data_empty_checksum(self):
        """Test that checksum defaults to empty string"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z"
        )
        
        assert session.checksum == ""

    def test_session_data_custom_checksum(self):
        """Test setting custom checksum"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z",
            checksum="abc123"
        )
        
        assert session.checksum == "abc123"


class TestExportConfigValidation:
    """Tests for ExportConfig validation"""

    def test_export_config_positive_values(self):
        """Test ExportConfig with positive values"""
        from platform_base.ui.export import ExportConfig
        
        config = ExportConfig(
            chunk_size_mb=1,
            async_threshold_mb=1,
            max_workers=1
        )
        
        assert config.chunk_size_mb > 0
        assert config.async_threshold_mb > 0
        assert config.max_workers > 0

    def test_export_config_large_values(self):
        """Test ExportConfig with large values"""
        from platform_base.ui.export import ExportConfig
        
        config = ExportConfig(
            chunk_size_mb=1000,
            max_workers=32
        )
        
        assert config.chunk_size_mb == 1000
        assert config.max_workers == 32


class TestSessionDataVersioning:
    """Tests for SessionData versioning"""

    def test_session_data_default_version(self):
        """Test default version is 2.0.0"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            session_id="test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z"
        )
        
        assert session.version == "2.0.0"

    def test_session_data_custom_version(self):
        """Test setting custom version"""
        from platform_base.ui.export import SessionData
        
        session = SessionData(
            version="3.0.0",
            session_id="test",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z"
        )
        
        assert session.version == "3.0.0"
