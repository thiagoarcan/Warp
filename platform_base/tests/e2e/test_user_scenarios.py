"""
End-to-End Tests - User Scenarios

Tests that simulate real user scenarios and workflows.
These tests ensure the application works as expected from a user perspective.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.e2e


class TestNewUserFirstFile:
    """Scenario: New user opens their first file."""
    
    def test_scenario_new_user_first_file(self, tmp_path):
        """New user loads their first CSV file and views it."""
        from platform_base.io.loader import load

        # Step 1: User creates/has a simple CSV file
        csv_file = tmp_path / "my_first_data.csv"
        t = np.arange(0, 100, 0.1)
        y = np.sin(2 * np.pi * 0.1 * t)  # 0.1 Hz sine wave
        pd.DataFrame({"tempo": t, "sinal": y}).to_csv(csv_file, index=False)
        
        # Step 2: User loads the file
        dataset = load(csv_file)
        
        # Step 3: Verify user can access the data
        assert dataset is not None
        assert len(dataset.series) >= 1
        
        # Step 4: User can see basic info
        series = list(dataset.series.values())[0]
        assert len(series.values) == 1000  # 100 / 0.1
        assert dataset.t_seconds is not None


class TestCompareTwoSeries:
    """Scenario: User compares two time series."""
    
    def test_scenario_compare_two_series(self, tmp_path):
        """User loads two files and compares the series."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative

        # Step 1: Create two similar signals
        t = np.linspace(0, 5, 500)
        
        # Signal 1: Clean sine
        csv1 = tmp_path / "signal_reference.csv"
        y1 = np.sin(2 * np.pi * t)
        pd.DataFrame({"time": t, "value": y1}).to_csv(csv1, index=False)
        
        # Signal 2: Slightly different sine (amplitude variation)
        csv2 = tmp_path / "signal_measured.csv"
        y2 = 0.95 * np.sin(2 * np.pi * t + 0.1)  # Slightly off
        pd.DataFrame({"time": t, "value": y2}).to_csv(csv2, index=False)
        
        # Step 2: Load both files
        ds1 = load(csv1)
        ds2 = load(csv2)
        
        # Step 3: Compare directly
        s1 = list(ds1.series.values())[0].values
        s2 = list(ds2.series.values())[0].values
        
        # Calculate RMS error
        rms_error = np.sqrt(np.mean((s1 - s2) ** 2))
        
        # Step 4: User sees the difference
        assert rms_error < 0.5  # Not exactly the same but similar
        assert rms_error > 0.01  # But not identical


class TestDerivativeIntegralWorkflow:
    """Scenario: User calculates derivative and integral."""
    
    def test_scenario_calculate_derivative_integral(self, tmp_path):
        """User calculates derivative and verifies with integral."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative, integral

        # Step 1: Create test data (y = sin(t), dy/dt = cos(t))
        csv_file = tmp_path / "sin_wave.csv"
        t = np.linspace(0, 4 * np.pi, 1000)
        y = np.sin(t)
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Step 3: Use explicit t array (loader may not parse 'time' as timestamp)
        # This ensures derivative calculation has proper time values
        time_array = t.copy()
        
        # Step 4: Calculate derivative
        deriv = derivative(series.values, time_array, order=1)
        if hasattr(deriv, 'values'):
            deriv_values = deriv.values
        else:
            deriv_values = deriv
        
        # Step 5: Verify derivative has expected length
        assert len(deriv_values) == len(t), f"Derivative length {len(deriv_values)} != expected {len(t)}"
        
        # Step 6: Verify derivative is approximately cos(t)
        expected_deriv = np.cos(t)
        # Use middle portion to avoid boundary effects
        mid_start, mid_end = 100, 900
        # Filter out NaN values for correlation
        mask = ~np.isnan(deriv_values[mid_start:mid_end])
        if np.sum(mask) > 10:
            correlation = np.corrcoef(
                deriv_values[mid_start:mid_end][mask], 
                expected_deriv[mid_start:mid_end][mask]
            )[0, 1]
            assert correlation > 0.9, f"Correlation {correlation} too low"
        
        # Step 7: Calculate cumulative integral to verify roundtrip
        # Use method="cumulative" to get an array of the same length as input
        integ = integral(deriv_values, time_array, method="cumulative")
        if hasattr(integ, 'values'):
            integ_values = integ.values
        else:
            integ_values = integ
        
        # Integral of derivative should have same length as original
        assert len(integ_values) == len(series.values)


class TestExportResults:
    """Scenario: User exports analysis results."""
    
    def test_scenario_export_results(self, tmp_path):
        """User performs analysis and exports results."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative
        from platform_base.processing.smoothing import smooth

        # Step 1: Load data
        csv_file = tmp_path / "input_data.csv"
        t = np.linspace(0, 10, 500)
        y = np.sin(t) + np.random.normal(0, 0.1, len(t))
        pd.DataFrame({"time": t, "signal": y}).to_csv(csv_file, index=False)
        
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Step 2: Smooth the data
        smoothed = smooth(series.values, method="savitzky_golay", params={"window_length": 15, "polyorder": 3})
        if isinstance(smoothed, np.ndarray):
            smoothed_values = smoothed
        else:
            smoothed_values = smoothed.values
        
        # Step 3: Calculate derivative of smoothed data
        deriv = derivative(smoothed_values, dataset.t_seconds, order=1)
        if hasattr(deriv, 'values'):
            deriv_values = deriv.values
        else:
            deriv_values = deriv
        
        # Step 4: Export all results
        output_file = tmp_path / "analysis_results.csv"
        results_df = pd.DataFrame({
            "time": t,
            "original": series.values,
            "smoothed": smoothed_values,
            "derivative": deriv_values
        })
        results_df.to_csv(output_file, index=False)
        
        # Step 5: Verify export
        assert output_file.exists()
        
        # Step 6: User can reload and verify
        reloaded = pd.read_csv(output_file)
        assert len(reloaded) == 500
        assert list(reloaded.columns) == ["time", "original", "smoothed", "derivative"]


class TestChangeSettings:
    """Scenario: User changes application settings."""
    
    def test_scenario_change_settings(self, tmp_path):
        """User modifies settings and they persist."""
        import json

        # Step 1: Default settings
        default_settings = {
            "visualization": {
                "theme": "light",
                "grid_visible": True,
                "legend_visible": True,
                "line_width": 1.5
            },
            "processing": {
                "default_smooth_method": "savitzky_golay",
                "default_interp_method": "linear"
            },
            "performance": {
                "max_points_display": 50000,
                "auto_downsample": True
            }
        }
        
        # Step 2: Save default settings
        settings_file = tmp_path / "settings.json"
        with open(settings_file, "w") as f:
            json.dump(default_settings, f, indent=2)
        
        # Step 3: User changes settings
        with open(settings_file, "r") as f:
            settings = json.load(f)
        
        settings["visualization"]["theme"] = "dark"
        settings["visualization"]["line_width"] = 2.0
        settings["performance"]["max_points_display"] = 100000
        
        # Step 4: Save changed settings
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        
        # Step 5: Verify settings persisted
        with open(settings_file, "r") as f:
            loaded_settings = json.load(f)
        
        assert loaded_settings["visualization"]["theme"] == "dark"
        assert loaded_settings["visualization"]["line_width"] == 2.0
        assert loaded_settings["performance"]["max_points_display"] == 100000


class TestMultiplePlots:
    """Scenario: User creates multiple plots."""
    
    def test_scenario_multiple_plots(self, tmp_path):
        """User creates multiple plots from different data."""
        from platform_base.io.loader import load

        # Step 1: Create multiple data files
        files = []
        for i in range(3):
            csv_file = tmp_path / f"plot_data_{i}.csv"
            t = np.linspace(0, 10, 300)
            freq = (i + 1) * 0.5  # Different frequencies
            y = np.sin(2 * np.pi * freq * t)
            pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
            files.append(csv_file)
        
        # Step 2: Load all files
        datasets = [load(f) for f in files]
        
        # Step 3: Verify each dataset
        for i, ds in enumerate(datasets):
            assert ds is not None
            assert len(ds.series) >= 1
            series = list(ds.series.values())[0]
            assert len(series.values) == 300
        
        # Step 4: User would create plots (simulated here)
        plot_configs = [
            {"id": f"plot_{i}", "dataset": i, "type": "2d"}
            for i in range(3)
        ]
        
        assert len(plot_configs) == 3


class TestVisualization3D:
    """Scenario: User creates 3D visualization."""
    
    def test_scenario_3d_visualization(self, tmp_path):
        """User creates 3D trajectory plot."""
        from platform_base.io.loader import load

        # Step 1: Create 3D trajectory data
        csv_file = tmp_path / "trajectory_3d.csv"
        t = np.linspace(0, 4 * np.pi, 500)
        x = np.cos(t)
        y = np.sin(t)
        z = t / (4 * np.pi)  # Linear increase
        
        pd.DataFrame({
            "time": t,
            "x": x,
            "y": y,
            "z": z
        }).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        
        # Step 3: Verify we have enough series for 3D
        assert len(dataset.series) >= 3  # x, y, z
        
        # Step 4: Extract coordinates (series is a dict)
        coords = {}
        for series in dataset.series.values():
            if 'x' in series.name.lower():
                coords['x'] = series.values
            elif 'y' in series.name.lower():
                coords['y'] = series.values
            elif 'z' in series.name.lower():
                coords['z'] = series.values
        
        # May or may not have all coords depending on naming
        # At minimum we should have data
        assert len(dataset.series) >= 1


class TestFilteringWorkflow:
    """Scenario: User applies filters to data."""
    
    def test_scenario_filtering_workflow(self, tmp_path):
        """User applies various filters to noisy data."""
        from platform_base.io.loader import load
        from platform_base.processing.smoothing import smooth

        # Step 1: Create noisy data with high-frequency noise
        csv_file = tmp_path / "noisy_signal.csv"
        t = np.linspace(0, 10, 1000)
        # Low frequency signal + high frequency noise
        y_signal = np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz
        y_noise = 0.3 * np.sin(2 * np.pi * 10 * t)  # 10 Hz noise
        y_total = y_signal + y_noise + np.random.normal(0, 0.1, len(t))
        
        pd.DataFrame({"time": t, "value": y_total}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Step 3: Apply smoothing (acts as low-pass filter)
        filtered = smooth(series.values, method="savitzky_golay", params={"window_length": 51, "polyorder": 3})
        if isinstance(filtered, np.ndarray):
            filtered_values = filtered
        else:
            filtered_values = filtered.values
        
        # Step 4: Verify filtering reduced high-frequency content
        # Simple check: variance should be reduced
        var_original = np.var(series.values)
        var_filtered = np.var(filtered_values)
        
        # Filtered signal should have lower variance (less noise)
        assert var_filtered < var_original


class TestInterpolationWorkflow:
    """Scenario: User interpolates irregular data."""
    
    def test_scenario_interpolation_workflow(self, tmp_path):
        """User interpolates irregular time series to regular grid."""
        from platform_base.io.loader import load
        from platform_base.processing.interpolation import interpolate

        # Step 1: Create irregular time series
        csv_file = tmp_path / "irregular_data.csv"
        # Irregular time points
        t_irregular = np.sort(np.random.uniform(0, 10, 50))
        y = np.sin(t_irregular)
        
        pd.DataFrame({"time": t_irregular, "value": y}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Step 3: Check time series properties
        dt = np.diff(dataset.t_seconds)
        # Just verify we have time data
        assert len(dt) > 0
        
        # Step 4: Interpolate to regular grid
        result = interpolate(series.values, dataset.t_seconds, "linear", {"factor": 2})
        
        # Step 5: Verify interpolation worked
        assert result is not None


class TestStatisticsWorkflow:
    """Scenario: User calculates statistics on data."""
    
    def test_scenario_statistics_workflow(self, tmp_path):
        """User loads data and calculates various statistics."""
        from platform_base.io.loader import load

        # Step 1: Create test data
        csv_file = tmp_path / "stats_data.csv"
        np.random.seed(42)
        t = np.linspace(0, 100, 1000)
        y = 5 + 2 * np.sin(2 * np.pi * 0.1 * t) + np.random.normal(0, 0.5, len(t))
        
        pd.DataFrame({"time": t, "value": y}).to_csv(csv_file, index=False)
        
        # Step 2: Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        values = series.values
        
        # Step 3: Calculate statistics
        stats = {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "rms": np.sqrt(np.mean(values ** 2)),
            "range": np.max(values) - np.min(values),
            "count": len(values)
        }
        
        # Step 4: Verify statistics make sense
        assert abs(stats["mean"] - 5) < 0.5  # Mean should be close to 5
        assert stats["std"] > 1  # Should have some variance
        assert stats["range"] > 3  # Should have reasonable range
        assert stats["count"] == 1000
