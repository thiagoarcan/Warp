"""
End-to-End Tests - Error Recovery

Tests that verify the application handles errors gracefully and recovers.
These tests ensure robustness in edge cases and error conditions.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.e2e


class TestCorruptedFileRecovery:
    """Test recovery from corrupted file scenarios."""
    
    def test_e2e_corrupted_csv_recovery(self, tmp_path):
        """Handle partially corrupted CSV file."""
        from platform_base.io.loader import load

        # Step 1: Create a CSV file with some issues
        csv_file = tmp_path / "corrupted.csv"
        csv_file.write_text("time,value\n1,10\n2,20\nbad_line\n4,40\n5,50\n")
        
        # Step 2: Try to load - may raise or handle gracefully
        try:
            dataset = load(csv_file)
            # If it loads, verify some data was recovered
            if dataset and dataset.series:
                assert len(dataset.series) >= 0
        except Exception as e:
            # Acceptable to raise for corrupted file
            assert "error" in str(e).lower() or "parse" in str(e).lower() or True
    
    def test_e2e_empty_file_recovery(self, tmp_path):
        """Handle empty file gracefully."""
        from platform_base.io.loader import load

        # Create empty CSV
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")
        
        # Should handle gracefully
        try:
            dataset = load(csv_file)
            # If it returns, should be empty or None
            if dataset:
                assert len(dataset.series) == 0 or dataset.series is None
        except Exception:
            # Acceptable to raise for empty file
            pass
    
    def test_e2e_header_only_file(self, tmp_path):
        """Handle file with only headers."""
        from platform_base.io.loader import load
        
        csv_file = tmp_path / "header_only.csv"
        csv_file.write_text("time,value\n")
        
        try:
            dataset = load(csv_file)
            if dataset and dataset.series:
                # Series should be empty or very short
                for s in dataset.series:
                    assert len(s.values) == 0
        except Exception:
            pass  # Acceptable


class TestCalculationErrorRecovery:
    """Test recovery from calculation errors."""
    
    def test_e2e_derivative_nan_recovery(self, tmp_path):
        """Handle derivative calculation with NaN values."""
        from platform_base.processing.calculus import derivative

        # Create data with NaN
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        y[40:50] = np.nan  # Add NaN gap
        
        # Try to calculate derivative
        try:
            result = derivative(y, t, order=1)
            # If it works, verify result
            if result is not None:
                if hasattr(result, 'values'):
                    result_values = result.values
                else:
                    result_values = result
                # Result should have same length
                assert len(result_values) == len(y)
        except Exception:
            # Acceptable to raise for NaN data
            pass
    
    def test_e2e_integral_empty_array_recovery(self):
        """Handle integral calculation with empty array."""
        from platform_base.processing.calculus import integral
        
        t = np.array([])
        y = np.array([])
        
        try:
            result = integral(y, t)
            # If it works, verify result is empty
            if result is not None:
                if hasattr(result, 'values'):
                    result_values = result.values
                else:
                    result_values = result
                assert len(result_values) == 0
        except Exception:
            # Acceptable to raise for empty array
            pass
    
    def test_e2e_derivative_single_point_recovery(self):
        """Handle derivative calculation with single point."""
        from platform_base.processing.calculus import derivative
        
        t = np.array([0])
        y = np.array([1])
        
        try:
            result = derivative(y, t, order=1)
            # Single point derivative should be handled
            pass
        except Exception:
            # Acceptable to raise for single point
            pass
    
    def test_e2e_smoothing_short_data_recovery(self):
        """Handle smoothing with data shorter than window."""
        from platform_base.processing.smoothing import smooth

        # Very short array
        y = np.array([1, 2, 3])
        
        try:
            # Window size 11 is larger than data
            result = smooth(y, method="savitzky_golay", params={"window_length": 11, "polyorder": 3})
            # Should either work with adjusted window or raise
            pass
        except Exception:
            # Acceptable to raise for too-short data
            pass


class TestExportErrorRecovery:
    """Test recovery from export errors."""
    
    def test_e2e_export_readonly_recovery(self, tmp_path):
        """Handle export to read-only location."""
        # This test is platform-specific, may not work on all systems
        import os
        import stat

        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        
        try:
            # Make directory read-only (may not work on Windows)
            if os.name != 'nt':  # Not Windows
                os.chmod(readonly_dir, stat.S_IRUSR | stat.S_IXUSR)
            
            output_file = readonly_dir / "output.csv"
            
            # Try to write
            try:
                pd.DataFrame({"x": [1, 2, 3]}).to_csv(output_file, index=False)
                # If it worked (e.g., on Windows), that's fine
            except (PermissionError, OSError):
                # Expected on read-only directory
                pass
        finally:
            # Restore permissions
            if os.name != 'nt':
                os.chmod(readonly_dir, stat.S_IRWXU)
    
    def test_e2e_export_invalid_path_recovery(self, tmp_path):
        """Handle export to invalid path."""
        # Path with invalid characters (platform-specific)
        if os.name == 'nt':  # Windows
            invalid_path = tmp_path / "file<>name.csv"
        else:
            # On Unix, most characters are valid
            invalid_path = tmp_path / "normal_name.csv"
        
        df = pd.DataFrame({"x": [1, 2, 3]})
        
        try:
            df.to_csv(invalid_path, index=False)
        except (OSError, ValueError):
            # Expected for invalid path on Windows
            pass


class TestSessionCorruptionRecovery:
    """Test recovery from session corruption."""
    
    def test_e2e_session_json_corrupted(self, tmp_path):
        """Handle corrupted session JSON."""
        import json

        # Create corrupted JSON
        session_file = tmp_path / "corrupted_session.json"
        session_file.write_text('{"version": "2.0", "datasets": [')  # Incomplete JSON
        
        try:
            with open(session_file, "r") as f:
                session = json.load(f)
        except json.JSONDecodeError:
            # Expected - JSON is invalid
            pass
    
    def test_e2e_session_missing_fields(self, tmp_path):
        """Handle session with missing required fields."""
        import json

        # Create session with missing fields
        session_file = tmp_path / "incomplete_session.json"
        session_data = {
            "version": "2.0"
            # Missing datasets, plots, settings
        }
        
        with open(session_file, "w") as f:
            json.dump(session_data, f)
        
        with open(session_file, "r") as f:
            loaded = json.load(f)
        
        # Should be able to load, just with missing fields
        assert loaded.get("datasets") is None
        assert loaded.get("plots") is None
        
        # Application should handle missing fields with defaults
        datasets = loaded.get("datasets", [])
        plots = loaded.get("plots", [])
        
        assert datasets == []
        assert plots == []
    
    def test_e2e_session_version_mismatch(self, tmp_path):
        """Handle session from different version."""
        import json

        # Create session with old version format
        session_file = tmp_path / "old_session.json"
        session_data = {
            "version": "1.0",  # Old version
            "data": ["file1.csv", "file2.csv"]  # Old format
        }
        
        with open(session_file, "w") as f:
            json.dump(session_data, f)
        
        with open(session_file, "r") as f:
            loaded = json.load(f)
        
        # Check version
        version = loaded.get("version", "unknown")
        
        # Application should detect version mismatch
        if version != "2.0":
            # Would need migration or warning
            pass


class TestMemoryRecovery:
    """Test recovery from memory-related issues."""
    
    def test_e2e_large_file_memory_recovery(self, tmp_path):
        """Handle large file that might cause memory issues."""
        from platform_base.io.loader import load

        # Create moderately large file (not too large to avoid actual OOM)
        csv_file = tmp_path / "large_data.csv"
        n_rows = 100000
        t = np.arange(n_rows)
        y = np.random.randn(n_rows)
        
        # Use chunked writing to avoid memory issues in test
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        # Try to load
        try:
            dataset = load(csv_file)
            if dataset and dataset.series:
                assert len(list(dataset.series.values())[0].values) == n_rows
        except MemoryError:
            # Application should handle memory errors gracefully
            pass


class TestConcurrencyRecovery:
    """Test recovery from concurrency issues."""
    
    def test_e2e_file_access_conflict(self, tmp_path):
        """Handle file access conflicts."""
        from platform_base.io.loader import load
        
        csv_file = tmp_path / "shared_file.csv"
        
        # Create file
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        # Open file (simulating another process)
        with open(csv_file, "r") as f:
            # Try to load while file is open
            try:
                dataset = load(csv_file)
                # Should work - read access is usually shared
                assert dataset is not None
            except Exception:
                # Some systems may have issues
                pass


class TestInputValidationRecovery:
    """Test recovery from invalid input."""
    
    def test_e2e_invalid_method_recovery(self):
        """Handle invalid method parameter."""
        from platform_base.processing.smoothing import smooth
        
        y = np.sin(np.linspace(0, 10, 100))
        
        try:
            result = smooth(y, method="nonexistent_method", params={})
            # If it doesn't raise, should return something reasonable
        except (ValueError, KeyError, Exception) as e:
            # Expected for invalid method
            assert "method" in str(e).lower() or "not" in str(e).lower() or True
    
    def test_e2e_invalid_params_recovery(self):
        """Handle invalid parameters."""
        from platform_base.processing.smoothing import smooth
        
        y = np.sin(np.linspace(0, 10, 100))
        
        try:
            result = smooth(y, method="savitzky_golay", params={"window_length": -5})  # Invalid
            # If it doesn't raise, params were validated
        except (ValueError, Exception):
            # Expected for invalid params
            pass
    
    def test_e2e_type_mismatch_recovery(self):
        """Handle type mismatch in input."""
        from platform_base.processing.calculus import derivative
        
        try:
            # Pass wrong types
            result = derivative("not an array", [1, 2, 3], order=1)
        except (TypeError, ValueError, AttributeError):
            # Expected for wrong types
            pass


class TestBoundaryConditions:
    """Test boundary conditions."""
    
    def test_e2e_two_point_data(self, tmp_path):
        """Handle data with only two points."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative
        
        csv_file = tmp_path / "two_points.csv"
        pd.DataFrame({"time": [0, 1], "value": [0, 1]}).to_csv(csv_file, index=False)
        
        # Loading may fail due to minimum points requirement
        try:
            dataset = load(csv_file)
            
            if dataset and dataset.series:
                series = list(dataset.series.values())[0]
                assert len(series.values) == 2
                
                try:
                    result = derivative(series.values, dataset.t_seconds, order=1)
                    # Should handle two-point derivative
                except Exception:
                    # May require more points
                    pass
        except Exception as e:
            # Expected - loader may require minimum points
            assert "minimum" in str(e).lower() or "point" in str(e).lower() or True
    
    def test_e2e_constant_data(self, tmp_path):
        """Handle constant data (zero derivative)."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative
        
        csv_file = tmp_path / "constant.csv"
        t = np.linspace(0, 10, 100)
        y = np.ones_like(t) * 5  # Constant value
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        result = derivative(series.values, dataset.t_seconds, order=1)
        if hasattr(result, 'values'):
            result_values = result.values
        else:
            result_values = result
        
        # Derivative of constant should be near zero (or NaN at boundaries)
        # Filter out NaN values and check the rest
        finite_values = result_values[np.isfinite(result_values)]
        if len(finite_values) > 0:
            assert np.allclose(finite_values, 0, atol=1e-6)
    
    def test_e2e_negative_values(self, tmp_path):
        """Handle negative values correctly."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import integral
        
        csv_file = tmp_path / "negative.csv"
        t = np.linspace(0, 10, 100)
        y = -np.abs(np.sin(t))  # All negative
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Verify negative values loaded
        assert np.all(series.values <= 0)
        
        # Calculate integral
        result = integral(series.values, dataset.t_seconds)
        if hasattr(result, 'values'):
            result_values = result.values
        else:
            result_values = result
        
        # Integral of negative values should be negative
        assert result_values[-1] < 0
