"""
Tests for io/integrity_checker.py module.

Tests file integrity checking functionality including:
- IntegrityIssue dataclass
- IntegrityReport dataclass
- FileIntegrityChecker class
- check_file_integrity function
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def integrity_checker():
    """Create FileIntegrityChecker instance."""
    from platform_base.io.integrity_checker import FileIntegrityChecker
    return FileIntegrityChecker()


@pytest.fixture
def custom_checker():
    """Create FileIntegrityChecker with custom settings."""
    from platform_base.io.integrity_checker import FileIntegrityChecker
    return FileIntegrityChecker(
        max_nan_percent=10.0,
        max_duplicate_percent=5.0,
        min_valid_rows=5,
    )


@pytest.fixture
def valid_csv_file(tmp_path):
    """Create a valid CSV file for testing."""
    file_path = tmp_path / "valid_data.csv"
    df = pd.DataFrame({
        'time': np.arange(100),
        'value': np.random.randn(100),
        'label': ['A'] * 50 + ['B'] * 50,
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file(tmp_path):
    """Create an empty file."""
    file_path = tmp_path / "empty.csv"
    file_path.touch()
    return file_path


@pytest.fixture
def csv_with_nans(tmp_path):
    """Create CSV with many NaN values."""
    file_path = tmp_path / "nan_data.csv"
    df = pd.DataFrame({
        'time': np.arange(100),
        'value': [np.nan] * 50 + list(range(50)),
        'other': [np.nan] * 80 + list(range(20)),
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def csv_with_duplicates(tmp_path):
    """Create CSV with duplicate rows."""
    file_path = tmp_path / "dup_data.csv"
    df = pd.DataFrame({
        'time': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5] * 10,
        'value': list(range(10)) * 10,
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def small_csv_file(tmp_path):
    """Create CSV with few rows."""
    file_path = tmp_path / "small_data.csv"
    df = pd.DataFrame({
        'time': [1, 2, 3],
        'value': [10, 20, 30],
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def valid_xlsx_file(tmp_path):
    """Create a valid Excel file."""
    file_path = tmp_path / "valid_data.xlsx"
    df = pd.DataFrame({
        'time': np.arange(50),
        'value': np.random.randn(50),
    })
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# IntegrityIssue Tests
# =============================================================================

class TestIntegrityIssue:
    """Tests for IntegrityIssue dataclass."""
    
    def test_create_basic_issue(self):
        """Test creating basic integrity issue."""
        from platform_base.io.integrity_checker import IntegrityIssue
        
        issue = IntegrityIssue(
            severity="error",
            code="TEST_ERROR",
            message="Test error message",
        )
        
        assert issue.severity == "error"
        assert issue.code == "TEST_ERROR"
        assert issue.message == "Test error message"
        assert issue.details == {}
        assert issue.repairable is False
        assert issue.repair_action is None
    
    def test_create_repairable_issue(self):
        """Test creating repairable issue."""
        from platform_base.io.integrity_checker import IntegrityIssue
        
        issue = IntegrityIssue(
            severity="warning",
            code="NAN_VALUES",
            message="Too many NaN values",
            details={'nan_percent': 25.5},
            repairable=True,
            repair_action="Remove rows with NaN",
        )
        
        assert issue.repairable is True
        assert issue.repair_action == "Remove rows with NaN"
        assert issue.details['nan_percent'] == 25.5
    
    def test_issue_severity_types(self):
        """Test different severity types."""
        from platform_base.io.integrity_checker import IntegrityIssue
        
        for severity in ["error", "warning", "info"]:
            issue = IntegrityIssue(
                severity=severity,
                code="TEST",
                message="Test",
            )
            assert issue.severity == severity


# =============================================================================
# IntegrityReport Tests
# =============================================================================

class TestIntegrityReport:
    """Tests for IntegrityReport dataclass."""
    
    def test_create_valid_report(self, tmp_path):
        """Test creating valid report."""
        from platform_base.io.integrity_checker import IntegrityReport
        
        report = IntegrityReport(
            file_path=tmp_path / "test.csv",
            file_size=1024,
            checksum="abc123",
            is_valid=True,
        )
        
        assert report.is_valid is True
        assert report.file_size == 1024
        assert report.checksum == "abc123"
        assert report.issues == []
        assert report.data_quality == {}
        assert isinstance(report.timestamp, datetime)
    
    def test_has_errors(self, tmp_path):
        """Test has_errors method."""
        from platform_base.io.integrity_checker import IntegrityIssue, IntegrityReport

        # Report without errors
        report = IntegrityReport(
            file_path=tmp_path / "test.csv",
            file_size=1024,
            checksum="abc123",
            is_valid=True,
            issues=[
                IntegrityIssue(severity="warning", code="WARN", message="Warning"),
                IntegrityIssue(severity="info", code="INFO", message="Info"),
            ],
        )
        assert report.has_errors() is False
        
        # Report with errors
        report.issues.append(
            IntegrityIssue(severity="error", code="ERR", message="Error")
        )
        assert report.has_errors() is True
    
    def test_has_warnings(self, tmp_path):
        """Test has_warnings method."""
        from platform_base.io.integrity_checker import IntegrityIssue, IntegrityReport

        # Report without warnings
        report = IntegrityReport(
            file_path=tmp_path / "test.csv",
            file_size=1024,
            checksum="abc123",
            is_valid=True,
        )
        assert report.has_warnings() is False
        
        # Report with warnings
        report.issues.append(
            IntegrityIssue(severity="warning", code="WARN", message="Warning")
        )
        assert report.has_warnings() is True
    
    def test_get_repairable_issues(self, tmp_path):
        """Test get_repairable_issues method."""
        from platform_base.io.integrity_checker import IntegrityIssue, IntegrityReport
        
        report = IntegrityReport(
            file_path=tmp_path / "test.csv",
            file_size=1024,
            checksum="abc123",
            is_valid=False,
            issues=[
                IntegrityIssue(severity="error", code="ERR1", message="Error 1", repairable=True),
                IntegrityIssue(severity="error", code="ERR2", message="Error 2", repairable=False),
                IntegrityIssue(severity="warning", code="WARN", message="Warning", repairable=True),
            ],
        )
        
        repairable = report.get_repairable_issues()
        assert len(repairable) == 2
        assert all(issue.repairable for issue in repairable)
    
    def test_to_dict(self, tmp_path):
        """Test to_dict method."""
        from platform_base.io.integrity_checker import IntegrityIssue, IntegrityReport
        
        report = IntegrityReport(
            file_path=tmp_path / "test.csv",
            file_size=1024,
            checksum="abc123",
            is_valid=True,
            issues=[
                IntegrityIssue(severity="warning", code="WARN", message="Warning"),
            ],
            data_quality={'nan_percent': 5.0},
        )
        
        result = report.to_dict()
        
        assert isinstance(result, dict)
        assert result['file_size'] == 1024
        assert result['checksum'] == "abc123"
        assert result['is_valid'] is True
        assert len(result['issues']) == 1
        assert result['data_quality']['nan_percent'] == 5.0
        assert 'timestamp' in result


# =============================================================================
# FileIntegrityChecker Tests
# =============================================================================

class TestFileIntegrityChecker:
    """Tests for FileIntegrityChecker class."""
    
    def test_init_default_settings(self, integrity_checker):
        """Test initialization with default settings."""
        assert integrity_checker.max_nan_percent == 20.0
        assert integrity_checker.max_duplicate_percent == 10.0
        assert integrity_checker.min_valid_rows == 10
    
    def test_init_custom_settings(self, custom_checker):
        """Test initialization with custom settings."""
        assert custom_checker.max_nan_percent == 10.0
        assert custom_checker.max_duplicate_percent == 5.0
        assert custom_checker.min_valid_rows == 5
    
    def test_check_valid_csv(self, integrity_checker, valid_csv_file):
        """Test checking valid CSV file."""
        report = integrity_checker.check_file(valid_csv_file)
        
        assert report.is_valid is True
        assert report.file_size > 0
        assert len(report.checksum) == 64  # SHA256 hex length
        assert report.file_path == valid_csv_file
    
    def test_check_nonexistent_file(self, integrity_checker, tmp_path):
        """Test checking non-existent file."""
        report = integrity_checker.check_file(tmp_path / "nonexistent.csv")
        
        assert report.is_valid is False
        assert report.file_size == 0
        assert report.checksum == ""
        assert len(report.issues) == 1
        assert report.issues[0].code == "FILE_NOT_FOUND"
    
    def test_check_empty_file(self, integrity_checker, empty_file):
        """Test checking empty file."""
        report = integrity_checker.check_file(empty_file)
        
        assert report.is_valid is False
        assert report.has_errors() is True
        # Should have EMPTY_FILE error
        error_codes = [issue.code for issue in report.issues]
        assert "EMPTY_FILE" in error_codes
    
    def test_check_csv_with_nans(self, integrity_checker, csv_with_nans):
        """Test checking CSV with many NaN values."""
        report = integrity_checker.check_file(csv_with_nans)
        
        # Should have warning about NaN percentage
        assert report.data_quality.get('nan_percent', 0) > 0
    
    def test_check_small_csv(self, custom_checker, small_csv_file):
        """Test checking CSV with few rows."""
        report = custom_checker.check_file(small_csv_file)
        
        # With min_valid_rows=5 and file has 3 rows, should have warning
        warn_codes = [issue.code for issue in report.issues if issue.severity == "warning"]
        assert "INSUFFICIENT_DATA" in warn_codes
    
    def test_check_valid_xlsx(self, integrity_checker, valid_xlsx_file):
        """Test checking valid Excel file."""
        report = integrity_checker.check_file(valid_xlsx_file)
        
        assert report.file_size > 0
        assert len(report.checksum) == 64
    
    def test_check_file_with_string_path(self, integrity_checker, valid_csv_file):
        """Test check_file accepts string path."""
        report = integrity_checker.check_file(str(valid_csv_file))
        
        assert report.is_valid is True
        assert report.file_path == valid_csv_file
    
    def test_calculate_checksum_consistency(self, integrity_checker, valid_csv_file):
        """Test checksum is consistent for same file."""
        report1 = integrity_checker.check_file(valid_csv_file)
        report2 = integrity_checker.check_file(valid_csv_file)
        
        assert report1.checksum == report2.checksum
    
    def test_data_quality_metrics(self, integrity_checker, valid_csv_file):
        """Test data quality metrics are calculated."""
        report = integrity_checker.check_file(valid_csv_file)
        
        # Should have data quality dict populated
        assert isinstance(report.data_quality, dict)


class TestFileIntegrityCheckerPrivateMethods:
    """Tests for FileIntegrityChecker private methods."""
    
    def test_calculate_checksum(self, integrity_checker, valid_csv_file):
        """Test _calculate_checksum method."""
        checksum = integrity_checker._calculate_checksum(valid_csv_file)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex length
        # Checksum should be consistent
        assert checksum == integrity_checker._calculate_checksum(valid_csv_file)
    
    def test_is_truncated_valid_csv(self, integrity_checker, valid_csv_file):
        """Test _is_truncated with valid CSV."""
        is_truncated = integrity_checker._is_truncated(valid_csv_file)
        assert is_truncated is False
    
    def test_is_truncated_xlsx(self, integrity_checker, valid_xlsx_file):
        """Test _is_truncated with valid Excel."""
        is_truncated = integrity_checker._is_truncated(valid_xlsx_file)
        assert is_truncated is False
    
    def test_check_encoding(self, integrity_checker, valid_csv_file):
        """Test _check_encoding method."""
        result = integrity_checker._check_encoding(valid_csv_file)
        
        assert isinstance(result, dict)
        assert 'detected' in result
        assert 'confidence' in result
        assert 'ambiguous' in result


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""
    
    def test_check_file_integrity_function(self, valid_csv_file):
        """Test check_file_integrity convenience function."""
        from platform_base.io.integrity_checker import check_file_integrity
        
        report = check_file_integrity(valid_csv_file)
        
        assert report.is_valid is True
        assert report.file_size > 0
    
    def test_get_integrity_checker_function(self):
        """Test get_integrity_checker convenience function."""
        from platform_base.io.integrity_checker import (
            FileIntegrityChecker,
            get_integrity_checker,
        )
        
        checker = get_integrity_checker()
        
        assert isinstance(checker, FileIntegrityChecker)


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_binary_file(self, integrity_checker, tmp_path):
        """Test checking binary file."""
        file_path = tmp_path / "binary.bin"
        file_path.write_bytes(b'\x00\x01\x02\x03\x04\x05')
        
        report = integrity_checker.check_file(file_path)
        
        assert report.file_size == 6
        assert len(report.checksum) == 64
    
    def test_utf8_content(self, integrity_checker, tmp_path):
        """Test file with UTF-8 content."""
        file_path = tmp_path / "utf8.csv"
        df = pd.DataFrame({
            'nome': ['João', 'María', '日本語'],
            'valor': [1, 2, 3],
        })
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        report = integrity_checker.check_file(file_path)
        
        assert report.file_size > 0
    
    def test_large_file_simulation(self, integrity_checker, tmp_path):
        """Test with larger file (simulated)."""
        file_path = tmp_path / "large.csv"
        df = pd.DataFrame({
            'time': np.arange(10000),
            'value': np.random.randn(10000),
        })
        df.to_csv(file_path, index=False)
        
        report = integrity_checker.check_file(file_path)
        
        assert report.is_valid is True
        assert report.file_size > 100000  # Should be > 100KB
    
    def test_csv_missing_newline(self, integrity_checker, tmp_path):
        """Test CSV without trailing newline."""
        file_path = tmp_path / "no_newline.csv"
        # Write without newline at end
        with open(file_path, 'w') as f:
            f.write("a,b,c\n1,2,3")  # No newline at end
        
        report = integrity_checker.check_file(file_path)
        
        # Should be detected but might not be error
        assert report.file_size > 0
    
    def test_corrupted_excel(self, integrity_checker, tmp_path):
        """Test corrupted Excel file."""
        file_path = tmp_path / "corrupted.xlsx"
        # Write invalid Excel content
        file_path.write_bytes(b'This is not a valid Excel file')
        
        report = integrity_checker.check_file(file_path)
        
        # Should have error
        assert report.has_errors() is True


# =============================================================================
# Report Serialization Tests
# =============================================================================

class TestReportSerialization:
    """Tests for report serialization."""
    
    def test_report_to_json(self, integrity_checker, valid_csv_file):
        """Test converting report to JSON-serializable dict."""
        import json
        
        report = integrity_checker.check_file(valid_csv_file)
        report_dict = report.to_dict()
        
        # Should be JSON serializable
        json_str = json.dumps(report_dict)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        loaded = json.loads(json_str)
        assert loaded['is_valid'] == report.is_valid
    
    def test_report_timestamp_serialization(self, tmp_path):
        """Test timestamp serialization."""
        from platform_base.io.integrity_checker import IntegrityReport
        
        report = IntegrityReport(
            file_path=tmp_path / "test.csv",
            file_size=100,
            checksum="abc",
            is_valid=True,
        )
        
        report_dict = report.to_dict()
        
        # Timestamp should be ISO format string
        assert isinstance(report_dict['timestamp'], str)
        # Should be parseable
        datetime.fromisoformat(report_dict['timestamp'])
