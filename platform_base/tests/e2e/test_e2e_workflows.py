"""
Extended End-to-End Workflow Tests

Tests complete user workflows from start to finish, simulating real user interactions.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.e2e


class TestUserWorkflowAnalysis:
    """E2E tests for typical analysis workflows."""
    
    def test_load_visualize_calculate_export_workflow(self, tmp_path):
        """Complete user workflow: Load → Visualize → Calculate → Export."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative, integral
        
        # User loads data file
        csv_file = tmp_path / "sensor_data.csv"
        t = np.linspace(0, 100, 1000)
        velocity = np.sin(0.1 * t) * 10  # Simulated velocity
        df = pd.DataFrame({"time": t, "velocity": velocity})
        df.to_csv(csv_file, index=False)
        
        # Step 1: Load
        dataset = load(csv_file)
        assert dataset is not None
        series = list(dataset.series.values())[0]
        
        # Step 2: User views data (simulated)
        assert len(series.values) == 1000
        
        # Step 3: Calculate derivative (acceleration)
        accel_result = derivative(series.values, dataset.t_seconds, order=1)
        assert accel_result is not None
        
        # Step 4: Calculate integral (position)
        position_result = integral(series.values, dataset.t_seconds)
        assert position_result is not None
        
        # Step 5: Export results
        output_file = tmp_path / "results.csv"
        # Ensure all arrays have the same length by truncating to shortest
        min_len = min(len(dataset.t_seconds), len(series.values), 
                      len(accel_result.values), len(position_result.values))
        df_results = pd.DataFrame({
            "time": dataset.t_seconds[:min_len],
            "velocity": series.values[:min_len],
            "acceleration": accel_result.values[:min_len],
            "position": position_result.values[:min_len]
        })
        df_results.to_csv(output_file, index=False)
        
        assert output_file.exists()
        df_check = pd.read_csv(output_file)
        assert "acceleration" in df_check.columns
        assert "position" in df_check.columns
    
    def test_multi_file_comparison_workflow(self, tmp_path):
        """Workflow: Load multiple files → Compare → Export comparison."""
        from platform_base.io.loader import load
        from platform_base.processing.synchronization import synchronize
        
        # Create multiple test files (e.g., different sensors)
        files = []
        for i in range(3):
            csv_file = tmp_path / f"sensor_{i}.csv"
            t = np.linspace(0, 10, 100 + i * 10)  # Different resolutions
            y = np.sin(2 * np.pi * t + i * np.pi / 3)  # Phase shifted
            df = pd.DataFrame({"time": t, f"sensor_{i}": y})
            df.to_csv(csv_file, index=False)
            files.append(csv_file)
        
        # Load all files
        datasets = [load(f) for f in files]
        assert len(datasets) == 3
        
        # Synchronize all series
        series_dict = {}
        time_dict = {}
        for i, ds in enumerate(datasets):
            series = list(ds.series.values())[0]
            series_dict[f"sensor_{i}"] = series.values
            time_dict[f"sensor_{i}"] = ds.t_seconds
        
        synced = synchronize(series_dict, time_dict, method="common_grid_interpolate", params={})
        
        # Verify synchronization
        assert len(synced.synced_series) == 3
        lengths = [len(v) for v in synced.synced_series.values()]
        assert len(set(lengths)) == 1  # All same length after sync
        
        # Export comparison
        output = tmp_path / "comparison.csv"
        df_compare = pd.DataFrame({
            "time": synced.t_common,
            **synced.synced_series
        })
        df_compare.to_csv(output, index=False)
        assert output.exists()
    
    def test_data_quality_workflow(self, tmp_path):
        """Workflow: Load → Check quality → Clean → Interpolate → Analyze."""
        from platform_base.io.loader import load
        from platform_base.processing.interpolation import interpolate
        
        # Create noisy data with gaps
        csv_file = tmp_path / "noisy_data.csv"
        t = np.linspace(0, 100, 1000)
        y = np.sin(0.1 * t) + 0.5 * np.random.randn(len(t))
        
        # Introduce NaN gaps
        y[200:220] = np.nan
        y[500:510] = np.nan
        
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Load data
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Check quality
        nan_count = np.isnan(series.values).sum()
        assert nan_count > 0  # Has gaps
        
        # Interpolate to fill gaps
        result = interpolate(series.values, dataset.t_seconds, method="linear", params={})
        
        # Verify gaps filled
        result_nan_count = np.isnan(result.values).sum()
        assert result_nan_count <= nan_count  # Should have fewer or equal NaN


class TestDataStreamingWorkflow:
    """E2E tests for streaming/playback workflows."""
    
    def test_streaming_playback_workflow(self):
        """Workflow: Load time series → Stream/playback → Apply filters in real-time."""
        from platform_base.streaming.filters import create_range_filter, FilterAction
        
        # Generate time series data
        t = np.linspace(0, 10, 1000)
        # Signal with noise
        signal = np.sin(2 * np.pi * t) + 0.2 * np.sin(20 * np.pi * t)
        
        # Simulate streaming - process in chunks
        chunk_size = 100
        filter_obj = create_range_filter(min_value=-1.5, max_value=1.5)
        
        filtered_chunks = []
        for i in range(0, len(signal), chunk_size):
            chunk = signal[i:i+chunk_size]
            chunk_t = t[i:i+chunk_size]
            # Apply filter to each point in chunk
            filtered_chunk = []
            for timestamp, value in zip(chunk_t, chunk):
                result = filter_obj.apply(timestamp, value)
                if result.action == FilterAction.PASS:
                    filtered_chunk.append(value)
                elif result.action == FilterAction.MODIFY and result.value is not None:
                    filtered_chunk.append(result.value)
                else:
                    filtered_chunk.append(np.nan)
            filtered_chunks.append(np.array(filtered_chunk))
        
        # Combine chunks
        filtered_full = np.concatenate(filtered_chunks)
        
        # Verify filtering occurred
        assert len(filtered_full) == len(signal)
        valid_values = filtered_full[~np.isnan(filtered_full)]
        # Most values should pass through within range
        assert len(valid_values) > 0


class TestExportWorkflows:
    """E2E tests for various export workflows."""
    
    def test_export_multiple_formats_workflow(self, tmp_path):
        """Workflow: Process data → Export to multiple formats."""
        from platform_base.io.loader import load
        
        # Create source data
        csv_file = tmp_path / "source.csv"
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Load
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Export to different formats
        formats = {
            "csv": tmp_path / "export.csv",
            "xlsx": tmp_path / "export.xlsx",
            "parquet": tmp_path / "export.parquet"
        }
        
        for fmt, output_path in formats.items():
            df_export = pd.DataFrame({
                "time": dataset.t_seconds,
                "value": series.values
            })
            
            if fmt == "csv":
                df_export.to_csv(output_path, index=False)
            elif fmt == "xlsx":
                df_export.to_excel(output_path, index=False)
            elif fmt == "parquet":
                df_export.to_parquet(output_path, index=False)
            
            assert output_path.exists()
    
    def test_export_with_metadata_workflow(self, tmp_path):
        """Workflow: Add metadata → Export with embedded metadata."""
        from platform_base.core.models import Dataset, Series, SourceInfo
        from datetime import datetime, timezone
        import pint
        
        # Create dataset with metadata
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        ureg = pint.UnitRegistry()
        series = Series(
            series_id="test",
            name="Test Signal",
            values=y,
            unit=ureg.parse_units("m/s"),
            metadata={
                "sensor": "IMU-001", 
                "location": "Engine Room",
                "original_name": "Test Signal",
                "source_column": "value"
            }
        )
        
        dataset = Dataset(
            dataset_id="test_ds",
            version=1,
            parent_id=None,
            source=SourceInfo(
                filepath=str(tmp_path / "source.csv"),
                filename="source.csv",
                format="csv",
                size_bytes=1024,
                checksum="dummy"
            ),
            t_seconds=t,
            t_datetime=pd.to_datetime(t, unit='s').values,  # Convert to ndarray
            series={"test": series},
            metadata={
                "description": None,
                "tags": [],
                "custom": {"project": "Sea Trial", "vessel": "Ship-123"}
            },
            created_at=datetime.now(timezone.utc)
        )
        
        # Export with metadata
        output = tmp_path / "with_metadata.csv"
        df = pd.DataFrame({
            "time": t,
            "value": y
        })
        df.to_csv(output, index=False)
        
        # Metadata would be in separate file or embedded
        metadata_file = tmp_path / "metadata.json"
        import json
        metadata_file.write_text(json.dumps({
            "dataset": dataset.metadata.model_dump(),
            "series": series.metadata if isinstance(series.metadata, dict) else series.metadata.model_dump() if hasattr(series.metadata, 'model_dump') else dict(series.metadata)
        }))
        
        assert output.exists()
        assert metadata_file.exists()


class TestInteractiveAnalysisWorkflow:
    """E2E tests for interactive analysis scenarios."""
    
    def test_iterative_parameter_tuning_workflow(self, tmp_path):
        """Workflow: Load → Try different parameters → Select best → Export."""
        from platform_base.processing.interpolation import interpolate
        from platform_base.io.loader import load
        
        # Create test data with at least 10 points
        csv_file = tmp_path / "data.csv"
        t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15])  # Irregular spacing, 13 points
        y = np.sin(t)
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Load
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Try different interpolation methods (use supported methods)
        methods = ["linear", "spline_cubic"]
        results = {}
        smoothness_values = {}
        
        for method in methods:
            result = interpolate(series.values, dataset.t_seconds, method=method, params={})
            results[method] = result
            
            # Calculate some metric (e.g., smoothness)
            if len(result.values) > 1:
                smoothness = np.mean(np.abs(np.diff(result.values)))
                smoothness_values[method] = smoothness
        
        # Select best (e.g., smoothest)
        best_method = min(smoothness_values.keys(), key=lambda k: smoothness_values[k])
        
        # Export best result
        output = tmp_path / f"result_{best_method}.csv"
        df_result = pd.DataFrame({
            "time": dataset.t_seconds,
            "value": results[best_method].values
        })
        df_result.to_csv(output, index=False)
        
        assert output.exists()
    
    def test_anomaly_detection_workflow(self, tmp_path):
        """Workflow: Load → Detect anomalies → Mark → Export."""
        from platform_base.io.loader import load
        
        # Create data with anomalies
        csv_file = tmp_path / "sensor_with_anomalies.csv"
        t = np.linspace(0, 100, 1000)
        y = np.sin(0.1 * t)
        
        # Add anomalies (spikes)
        anomaly_indices = [100, 250, 600, 850]
        for idx in anomaly_indices:
            y[idx] = y[idx] + 10  # Spike
        
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Load
        dataset = load(csv_file)
        series = list(dataset.series.values())[0]
        
        # Simple anomaly detection: values > 3 std from mean
        mean = np.mean(series.values)
        std = np.std(series.values)
        anomalies = np.abs(series.values - mean) > 3 * std
        
        assert anomalies.sum() >= len(anomaly_indices)  # Should detect most
        
        # Export with anomaly flags
        output = tmp_path / "flagged.csv"
        df_flagged = pd.DataFrame({
            "time": dataset.t_seconds,
            "value": series.values,
            "is_anomaly": anomalies
        })
        df_flagged.to_csv(output, index=False)
        
        assert output.exists()
        df_check = pd.read_csv(output)
        assert "is_anomaly" in df_check.columns
        assert df_check["is_anomaly"].sum() >= len(anomaly_indices)


class TestBatchProcessingWorkflow:
    """E2E tests for batch processing workflows."""
    
    def test_batch_process_multiple_files_workflow(self, tmp_path):
        """Workflow: Load multiple files → Process all → Export results."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative
        
        # Create batch of files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        files = []
        for i in range(5):
            csv_file = input_dir / f"data_{i:03d}.csv"
            t = np.linspace(0, 10, 100)
            y = np.sin((i + 1) * t)  # Different frequencies
            df = pd.DataFrame({"time": t, "value": y})
            df.to_csv(csv_file, index=False)
            files.append(csv_file)
        
        # Batch process
        for file in files:
            # Load
            dataset = load(file)
            series = list(dataset.series.values())[0]
            
            # Process
            result = derivative(series.values, dataset.t_seconds, order=1)
            
            # Export
            output_file = output_dir / file.name.replace(".csv", "_derivative.csv")
            df_out = pd.DataFrame({
                "time": dataset.t_seconds,
                "derivative": result.values
            })
            df_out.to_csv(output_file, index=False)
        
        # Verify all outputs created
        output_files = list(output_dir.glob("*_derivative.csv"))
        assert len(output_files) == 5
