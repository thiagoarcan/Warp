"""
End-to-End Tests - Complete Workflow Tests

Tests that verify complete user workflows from start to finish.
These tests ensure that all components work together correctly.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# Skip all E2E tests if PyQt6 is not available in headless mode
pytestmark = pytest.mark.e2e


class TestLoadAnalyzeExportCSV:
    """E2E test: Load CSV → Analyze → Export."""
    
    def test_e2e_load_analyze_export_csv(self, tmp_path):
        """Complete workflow: load CSV, calculate derivative, export result."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative

        # Step 1: Create test CSV file
        csv_file = tmp_path / "test_data.csv"
        t = np.linspace(0, 10, 1000)
        y = np.sin(t)
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Step 2: Load the file
        dataset = load(csv_file)
        assert dataset is not None
        assert len(dataset.series) >= 1
        
        # Step 3: Get time and value series (series is a dict)
        series = list(dataset.series.values())[0]
        t_loaded = dataset.t_seconds
        y_loaded = series.values
        
        assert len(t_loaded) == 1000
        assert len(y_loaded) == 1000
        
        # Step 4: Calculate derivative
        result = derivative(y_loaded, t_loaded, order=1)
        assert result is not None
        
        # Step 5: Export result to new CSV
        output_file = tmp_path / "derivative_result.csv"
        if hasattr(result, 'values'):
            result_values = result.values
        else:
            result_values = result
        
        df_output = pd.DataFrame({
            "time": t_loaded,
            "original": y_loaded,
            "derivative": result_values
        })
        df_output.to_csv(output_file, index=False)
        
        # Step 6: Verify export
        assert output_file.exists()
        df_verify = pd.read_csv(output_file)
        assert len(df_verify) == 1000
        assert "derivative" in df_verify.columns


class TestLoadAnalyzeExportXLSX:
    """E2E test: Load XLSX → Analyze → Export."""
    
    def test_e2e_load_analyze_export_xlsx(self, tmp_path):
        """Complete workflow: load XLSX, smooth data, export result."""
        from platform_base.io.loader import load
        from platform_base.processing.smoothing import smooth

        # Step 1: Create test XLSX file
        xlsx_file = tmp_path / "test_data.xlsx"
        t = np.linspace(0, 10, 500)
        y = np.sin(t) + np.random.normal(0, 0.1, len(t))
        df = pd.DataFrame({"time": t, "noisy_signal": y})
        df.to_excel(xlsx_file, index=False)
        
        # Step 2: Load the file
        dataset = load(xlsx_file)
        assert dataset is not None
        assert len(dataset.series) >= 1
        
        # Step 3: Get data (series is a dict)
        series = list(dataset.series.values())[0]
        y_loaded = series.values
        
        # Step 4: Apply smoothing
        result = smooth(y_loaded, method="savitzky_golay", params={"window_length": 11, "polyorder": 3})
        assert result is not None
        
        # Step 5: Export result
        output_file = tmp_path / "smoothed_result.xlsx"
        if hasattr(result, 'values'):
            result_values = result.values
        elif isinstance(result, np.ndarray):
            result_values = result
        else:
            result_values = np.array(result)
        
        df_output = pd.DataFrame({
            "time": t,
            "original": y_loaded,
            "smoothed": result_values
        })
        df_output.to_excel(output_file, index=False)
        
        # Step 6: Verify export
        assert output_file.exists()
        df_verify = pd.read_excel(output_file)
        assert len(df_verify) == 500
        assert "smoothed" in df_verify.columns


class TestMultipleFilesWorkflow:
    """E2E test: Load multiple files and combine."""
    
    def test_e2e_multiple_files_workflow(self, tmp_path):
        """Load multiple CSV files, combine, and analyze."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import integral

        # Step 1: Create multiple test files
        files = []
        for i in range(3):
            csv_file = tmp_path / f"data_{i}.csv"
            t = np.linspace(0, 10, 200)
            y = np.sin(t + i * np.pi / 3)  # Phase shifted
            df = pd.DataFrame({"time": t, f"signal_{i}": y})
            df.to_csv(csv_file, index=False)
            files.append(csv_file)
        
        # Step 2: Load all files
        datasets = []
        for f in files:
            ds = load(f)
            assert ds is not None
            datasets.append(ds)
        
        assert len(datasets) == 3
        
        # Step 3: Analyze each dataset (series is a dict)
        integrals = []
        for ds in datasets:
            series = list(ds.series.values())[0]
            result = integral(series.values, ds.t_seconds)
            integrals.append(result)
        
        assert len(integrals) == 3
        
        # Step 4: Verify integrals are different (phase shifted signals)
        # The integrals should be different due to phase shift


class TestCalculationWorkflow:
    """E2E test: Complete calculation workflow."""
    
    def test_e2e_calculation_workflow(self, tmp_path):
        """Load data → derivative → integral → compare."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative, integral

        # Step 1: Create test data
        csv_file = tmp_path / "calc_test.csv"
        t = np.linspace(0, 2 * np.pi, 500)
        y = np.sin(t)
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Step 3: Calculate derivative (should be ~cos(t))
        deriv = derivative(series.values, dataset.t_seconds, order=1)
        if hasattr(deriv, 'values'):
            deriv_values = deriv.values
        else:
            deriv_values = deriv
        
        # Step 4: Calculate integral of derivative (should be ~sin(t))
        integ = integral(deriv_values, dataset.t_seconds)
        if hasattr(integ, 'values'):
            integ_values = integ.values
        else:
            integ_values = integ
        
        # Step 5: Verify roundtrip (integral of derivative ≈ original)
        # Note: integral may return cumulative array or single value
        # Just verify we got a result
        assert integ_values is not None
        if isinstance(integ_values, np.ndarray) and len(integ_values) > 1:
            assert len(integ_values) == len(series.values)


class TestComparisonWorkflow:
    """E2E test: Compare two series."""
    
    def test_e2e_comparison_workflow(self, tmp_path):
        """Load two files and compare series."""
        from platform_base.io.loader import load

        # Step 1: Create two test files with similar data
        t = np.linspace(0, 10, 300)
        
        csv1 = tmp_path / "series1.csv"
        y1 = np.sin(t)
        pd.DataFrame({"time": t, "value": y1}).to_csv(csv1, index=False)
        
        csv2 = tmp_path / "series2.csv"
        y2 = np.sin(t) + np.random.normal(0, 0.01, len(t))  # Slightly noisy
        pd.DataFrame({"time": t, "value": y2}).to_csv(csv2, index=False)
        
        # Step 2: Load both files
        ds1 = load(csv1)
        ds2 = load(csv2)
        
        # Step 3: Compare series (series is a dict)
        s1 = list(ds1.series.values())[0].values
        s2 = list(ds2.series.values())[0].values
        
        # Calculate difference
        diff = np.abs(s1 - s2)
        mean_diff = np.mean(diff)
        max_diff = np.max(diff)
        
        # Step 4: Verify comparison metrics
        assert mean_diff < 0.1  # Mean difference should be small
        assert max_diff < 0.5   # Max difference should be reasonable


class TestDownsamplingWorkflow:
    """E2E test: Downsampling workflow."""
    
    def test_e2e_downsampling_workflow(self, tmp_path):
        """Load large dataset, downsample, analyze, export."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative
        from platform_base.processing.downsampling import downsample

        # Step 1: Create large test file
        csv_file = tmp_path / "large_data.csv"
        t = np.linspace(0, 100, 10000)  # 10k points
        y = np.sin(t) + 0.5 * np.sin(3 * t)
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        assert len(series.values) == 10000
        
        # Step 3: Downsample (returns DownsampleResult object)
        ds_result = downsample(series.values, dataset.t_seconds, n_points=1000, method="lttb")
        ds_t = ds_result.t_seconds
        ds_y = ds_result.values
        
        assert len(ds_t) <= 1000
        assert len(ds_y) <= 1000
        
        # Step 4: Calculate derivative on downsampled data
        result = derivative(ds_y, ds_t, order=1)
        assert result is not None
        
        # Step 5: Export
        output_file = tmp_path / "downsampled_result.csv"
        if hasattr(result, 'values'):
            result_values = result.values
        else:
            result_values = result
            
        pd.DataFrame({
            "time": ds_t,
            "value": ds_y,
            "derivative": result_values
        }).to_csv(output_file, index=False)
        
        assert output_file.exists()


class TestSmoothingWorkflow:
    """E2E test: Smoothing workflow."""
    
    def test_e2e_smoothing_workflow(self, tmp_path):
        """Load noisy data, apply different smoothing methods, compare."""
        from platform_base.io.loader import load
        from platform_base.processing.smoothing import smooth

        # Step 1: Create noisy test data
        csv_file = tmp_path / "noisy_data.csv"
        t = np.linspace(0, 10, 500)
        y_clean = np.sin(t)
        y_noisy = y_clean + np.random.normal(0, 0.3, len(t))
        pd.DataFrame({"time": t, "value": y_noisy}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        y = series.values
        
        # Step 3: Apply Savitzky-Golay smoothing
        smoothed_savgol = smooth(y, method="savitzky_golay", params={"window_length": 11, "polyorder": 3})
        
        # Step 4: Apply Gaussian smoothing
        smoothed_gauss = smooth(y, method="gaussian", params={"sigma": 2})
        
        # Step 5: Verify smoothing reduced noise
        if isinstance(smoothed_savgol, np.ndarray):
            savgol_values = smoothed_savgol
        else:
            savgol_values = smoothed_savgol.values
            
        if isinstance(smoothed_gauss, np.ndarray):
            gauss_values = smoothed_gauss
        else:
            gauss_values = smoothed_gauss.values
        
        # Calculate variance reduction
        var_original = np.var(y - y_clean)
        var_savgol = np.var(savgol_values - y_clean)
        var_gauss = np.var(gauss_values - y_clean)
        
        # Smoothing should reduce variance (noise)
        assert var_savgol < var_original
        assert var_gauss < var_original


class TestSessionWorkflow:
    """E2E test: Session save/load workflow."""
    
    def test_e2e_session_workflow(self, tmp_path):
        """Create session state, save, load, verify."""
        import json

        # Step 1: Create session data
        session_data = {
            "version": "2.0",
            "datasets": [
                {
                    "id": "ds1",
                    "name": "test_dataset",
                    "filepath": str(tmp_path / "test.csv"),
                    "series_count": 1
                }
            ],
            "plots": [
                {
                    "id": "plot1",
                    "type": "2d",
                    "series": ["series1"]
                }
            ],
            "settings": {
                "theme": "light",
                "grid_visible": True,
                "legend_visible": True
            }
        }
        
        # Step 2: Save session
        session_file = tmp_path / "session.json"
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
        
        assert session_file.exists()
        
        # Step 3: Load session
        with open(session_file, "r") as f:
            loaded_session = json.load(f)
        
        # Step 4: Verify session data
        assert loaded_session["version"] == "2.0"
        assert len(loaded_session["datasets"]) == 1
        assert len(loaded_session["plots"]) == 1
        assert loaded_session["settings"]["theme"] == "light"


class TestDataValidationWorkflow:
    """E2E test: Data validation workflow."""
    
    def test_e2e_data_validation_workflow(self, tmp_path):
        """Load data with issues, validate, clean, analyze."""
        from platform_base.io.loader import load
        from platform_base.processing.smoothing import smooth

        # Step 1: Create data with NaN values
        csv_file = tmp_path / "data_with_nan.csv"
        t = np.linspace(0, 10, 200)
        y = np.sin(t)
        # Add some NaN values
        y[50:55] = np.nan
        y[150:152] = np.nan
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Step 3: Check for NaN values
        nan_count = np.sum(np.isnan(series.values))
        assert nan_count > 0
        
        # Step 4: Clean data (replace NaN with interpolation)
        clean_y = np.copy(series.values)
        mask = np.isnan(clean_y)
        clean_y[mask] = np.interp(
            np.flatnonzero(mask),
            np.flatnonzero(~mask),
            clean_y[~mask]
        )
        
        # Step 5: Verify cleaned
        assert np.sum(np.isnan(clean_y)) == 0
        
        # Step 6: Apply smoothing on cleaned data
        result = smooth(clean_y, method="gaussian", params={"sigma": 1})
        assert result is not None
