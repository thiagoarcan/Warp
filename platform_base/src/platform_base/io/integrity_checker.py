"""
File Integrity Checker - Category 10.5

Validates file integrity before loading to prevent crashes and data corruption.

Features:
- Checksum verification
- Truncation detection
- Schema validation for CSV/Excel
- Encoding detection
- Data quality assessment
- Temporal consistency checks
- Repair suggestions
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


@dataclass
class IntegrityIssue:
    """Represents a file integrity issue."""
    severity: str  # "error", "warning", "info"
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    repairable: bool = False
    repair_action: str | None = None


@dataclass
class IntegrityReport:
    """Report of file integrity check."""
    file_path: Path
    file_size: int
    checksum: str
    is_valid: bool
    issues: list[IntegrityIssue] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def has_errors(self) -> bool:
        """Check if report has any errors."""
        return any(issue.severity == "error" for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if report has any warnings."""
        return any(issue.severity == "warning" for issue in self.issues)

    def get_repairable_issues(self) -> list[IntegrityIssue]:
        """Get list of repairable issues."""
        return [issue for issue in self.issues if issue.repairable]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'file_path': str(self.file_path),
            'file_size': self.file_size,
            'checksum': self.checksum,
            'is_valid': self.is_valid,
            'issues': [
                {
                    'severity': issue.severity,
                    'code': issue.code,
                    'message': issue.message,
                    'details': issue.details,
                    'repairable': issue.repairable,
                    'repair_action': issue.repair_action,
                }
                for issue in self.issues
            ],
            'data_quality': self.data_quality,
            'timestamp': self.timestamp.isoformat(),
        }


class FileIntegrityChecker:
    """
    Comprehensive file integrity checker.
    
    Validates files before loading to prevent crashes and ensure data quality.
    """

    def __init__(
        self,
        max_nan_percent: float = 20.0,
        max_duplicate_percent: float = 10.0,
        min_valid_rows: int = 10,
    ):
        self.max_nan_percent = max_nan_percent
        self.max_duplicate_percent = max_duplicate_percent
        self.min_valid_rows = min_valid_rows

    def check_file(self, file_path: str | Path) -> IntegrityReport:
        """
        Perform comprehensive file integrity check.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            IntegrityReport with all findings
        """
        file_path = Path(file_path)
        issues: list[IntegrityIssue] = []

        # Basic file checks
        if not file_path.exists():
            return IntegrityReport(
                file_path=file_path,
                file_size=0,
                checksum="",
                is_valid=False,
                issues=[IntegrityIssue(
                    severity="error",
                    code="FILE_NOT_FOUND",
                    message="File does not exist",
                )]
            )

        file_size = file_path.stat().st_size

        # Check if file is empty
        if file_size == 0:
            issues.append(IntegrityIssue(
                severity="error",
                code="EMPTY_FILE",
                message="File is empty",
            ))

        # Calculate checksum
        checksum = self._calculate_checksum(file_path)

        # Detect truncation
        if self._is_truncated(file_path):
            issues.append(IntegrityIssue(
                severity="error",
                code="FILE_TRUNCATED",
                message="File appears to be truncated (unexpected EOF)",
            ))

        # Check encoding
        encoding_result = self._check_encoding(file_path)
        if encoding_result['ambiguous']:
            issues.append(IntegrityIssue(
                severity="warning",
                code="AMBIGUOUS_ENCODING",
                message=f"Encoding detection ambiguous: {encoding_result['detected']}",
                details=encoding_result,
            ))

        # For CSV/Excel files, do deeper validation
        if file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
            try:
                data_issues, quality_metrics = self._check_data_quality(file_path)
                issues.extend(data_issues)
                data_quality = quality_metrics
            except Exception as e:
                issues.append(IntegrityIssue(
                    severity="error",
                    code="DATA_READ_ERROR",
                    message=f"Failed to read file for quality check: {str(e)}",
                ))
                data_quality = {}
        else:
            data_quality = {}

        # Determine if file is valid
        has_errors = any(issue.severity == "error" for issue in issues)
        is_valid = not has_errors

        logger.info("file_integrity_checked",
                   file=str(file_path),
                   valid=is_valid,
                   issues_count=len(issues))

        return IntegrityReport(
            file_path=file_path,
            file_size=file_size,
            checksum=checksum,
            is_valid=is_valid,
            issues=issues,
            data_quality=data_quality,
        )

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _is_truncated(self, file_path: Path) -> bool:
        """Check if file is truncated."""
        try:
            # For CSV files, check if last line is complete
            if file_path.suffix.lower() == '.csv':
                with open(file_path, 'rb') as f:
                    # Read last few bytes
                    f.seek(max(0, file_path.stat().st_size - 100))
                    last_bytes = f.read()
                    # Check if ends with newline
                    return not last_bytes.endswith(b'\n') and not last_bytes.endswith(b'\r\n')

            # For Excel, try to open it
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                pd.read_excel(file_path, nrows=1)
                return False

        except Exception:
            return True

        return False

    def _check_encoding(self, file_path: Path) -> dict[str, Any]:
        """Check file encoding."""
        try:
            import chardet

            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)

                return {
                    'detected': result['encoding'],
                    'confidence': result['confidence'],
                    'ambiguous': result['confidence'] < 0.9,
                }

        except ImportError:
            # chardet not available, assume UTF-8
            return {
                'detected': 'utf-8',
                'confidence': 0.0,
                'ambiguous': True,
            }

    def _check_data_quality(
        self, file_path: Path
    ) -> tuple[list[IntegrityIssue], dict[str, Any]]:
        """Check data quality."""
        issues: list[IntegrityIssue] = []

        # Try to read file
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, nrows=10000)  # Sample first 10K rows
            else:
                df = pd.read_excel(file_path, nrows=10000)
        except Exception as e:
            issues.append(IntegrityIssue(
                severity="error",
                code="PARSE_ERROR",
                message=f"Failed to parse file: {str(e)}",
            ))
            return issues, {}

        # Check if empty
        if len(df) == 0:
            issues.append(IntegrityIssue(
                severity="error",
                code="NO_DATA",
                message="File contains no data rows",
            ))
            return issues, {}

        # Check minimum rows
        if len(df) < self.min_valid_rows:
            issues.append(IntegrityIssue(
                severity="warning",
                code="INSUFFICIENT_DATA",
                message=f"File has only {len(df)} rows (minimum: {self.min_valid_rows})",
                details={'row_count': len(df)},
            ))

        # Calculate NaN percentage
        total_cells = df.size
        nan_cells = df.isna().sum().sum()
        nan_percent = (nan_cells / total_cells * 100) if total_cells > 0 else 0

        if nan_percent > self.max_nan_percent:
            issues.append(IntegrityIssue(
                severity="warning",
                code="HIGH_NAN_PERCENT",
                message=f"High percentage of missing values: {nan_percent:.1f}%",
                details={'nan_percent': nan_percent, 'threshold': self.max_nan_percent},
                repairable=True,
                repair_action="Remove rows/columns with excessive NaN values",
            ))

        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        duplicate_percent = (duplicate_count / len(df) * 100) if len(df) > 0 else 0

        if duplicate_percent > self.max_duplicate_percent:
            issues.append(IntegrityIssue(
                severity="warning",
                code="HIGH_DUPLICATE_PERCENT",
                message=f"High percentage of duplicate rows: {duplicate_percent:.1f}%",
                details={'duplicate_count': duplicate_count, 'duplicate_percent': duplicate_percent},
                repairable=True,
                repair_action="Remove duplicate rows",
            ))

        # Check for temporal consistency (if timestamp column exists)
        timestamp_cols = [col for col in df.columns if any(
            word in col.lower() for word in ['time', 'timestamp', 'date', 'datetime']
        )]

        if timestamp_cols:
            try:
                ts_col = timestamp_cols[0]
                df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')

                # Check for invalid timestamps
                invalid_ts = df[ts_col].isna().sum()
                if invalid_ts > 0:
                    issues.append(IntegrityIssue(
                        severity="warning",
                        code="INVALID_TIMESTAMPS",
                        message=f"Found {invalid_ts} invalid timestamp values",
                        details={'invalid_count': invalid_ts, 'column': ts_col},
                        repairable=True,
                        repair_action="Interpolate or remove rows with invalid timestamps",
                    ))

                # Check for non-monotonic timestamps
                if not df[ts_col].dropna().is_monotonic_increasing:
                    issues.append(IntegrityIssue(
                        severity="info",
                        code="NON_MONOTONIC_TIMESTAMPS",
                        message="Timestamps are not in chronological order",
                        details={'column': ts_col},
                        repairable=True,
                        repair_action="Sort data by timestamp",
                    ))

            except Exception as e:
                issues.append(IntegrityIssue(
                    severity="warning",
                    code="TIMESTAMP_CHECK_FAILED",
                    message=f"Could not validate timestamps: {str(e)}",
                ))

        # Calculate quality metrics
        quality_metrics = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'nan_percent': nan_percent,
            'duplicate_percent': duplicate_percent,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # Calculate value ranges for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            quality_metrics['numeric_ranges'] = {
                col: {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                }
                for col in numeric_cols[:5]  # First 5 numeric columns
            }

        return issues, quality_metrics

    def apply_repairs(
        self,
        file_path: str | Path,
        report: IntegrityReport,
        output_path: str | Path | None = None,
    ) -> Path:
        """
        Apply suggested repairs to file.
        
        Args:
            file_path: Original file path
            report: Integrity report with issues
            output_path: Output path for repaired file (default: add _repaired suffix)
            
        Returns:
            Path to repaired file
        """
        file_path = Path(file_path)

        if output_path is None:
            output_path = file_path.with_stem(f"{file_path.stem}_repaired")
        else:
            output_path = Path(output_path)

        # Read file
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        repairs_applied = []

        # Get repairable issues
        for issue in report.get_repairable_issues():
            if issue.code == "HIGH_NAN_PERCENT":
                # Remove rows with excessive NaN
                threshold = df.shape[1] * 0.5  # More than 50% NaN
                df = df.dropna(thresh=threshold)
                repairs_applied.append(issue.code)

            elif issue.code == "HIGH_DUPLICATE_PERCENT":
                # Remove duplicates
                df = df.drop_duplicates()
                repairs_applied.append(issue.code)

            elif issue.code == "INVALID_TIMESTAMPS":
                # Remove rows with invalid timestamps
                ts_col = issue.details.get('column')
                if ts_col:
                    df = df.dropna(subset=[ts_col])
                    repairs_applied.append(issue.code)

            elif issue.code == "NON_MONOTONIC_TIMESTAMPS":
                # Sort by timestamp
                ts_col = issue.details.get('column')
                if ts_col:
                    df = df.sort_values(by=ts_col)
                    repairs_applied.append(issue.code)

        # Save repaired file
        if file_path.suffix.lower() == '.csv':
            df.to_csv(output_path, index=False)
        else:
            df.to_excel(output_path, index=False)

        logger.info("file_repaired",
                   original=str(file_path),
                   repaired=str(output_path),
                   repairs=repairs_applied)

        return output_path


# Global instance
_integrity_checker: FileIntegrityChecker | None = None


def get_integrity_checker() -> FileIntegrityChecker:
    """Get global integrity checker instance."""
    global _integrity_checker
    if _integrity_checker is None:
        _integrity_checker = FileIntegrityChecker()
    return _integrity_checker


def check_file_integrity(file_path: str | Path) -> IntegrityReport:
    """Convenience function to check file integrity."""
    return get_integrity_checker().check_file(file_path)
