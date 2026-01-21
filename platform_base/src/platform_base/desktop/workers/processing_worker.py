"""
ProcessingWorker - Data processing worker for Platform Base v2.0

Handles interpolation, calculus, and synchronization operations in background threads.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import numpy as np

from platform_base.desktop.workers.base_worker import BaseWorker
from platform_base.core.models import DatasetID, SeriesID, Series, Lineage
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class InterpolationWorker(BaseWorker):
    """Worker for interpolation operations"""
    
    def __init__(self, dataset_store, dataset_id: str, series_id: str, 
                 method: str, parameters: Dict[str, Any]):
        super().__init__()
        self.dataset_store = dataset_store
        self.dataset_id = dataset_id
        self.series_id = series_id
        self.method = method
        self.parameters = parameters
        
    def run(self):
        """Execute interpolation operation"""
        try:
            self.emit_progress(0, "Starting interpolation...")
            
            # Get source data
            dataset = self.dataset_store.get_dataset(self.dataset_id)
            source_series = dataset.series[self.series_id]
            
            self.emit_progress(20, "Loading interpolation module...")
            
            # Import interpolation module
            from platform_base.processing.interpolation import interpolate, InterpMethod, InterpParams
            
            # Convert parameters
            interp_method = InterpMethod(self.method)
            interp_params = InterpParams(**self.parameters)
            
            self.emit_progress(40, f"Applying {self.method} interpolation...")
            
            # Perform interpolation
            result = interpolate(source_series.values, dataset.t_seconds, 
                               interp_method, interp_params)
            
            if self.is_cancelled:
                return
                
            self.emit_progress(80, "Creating result series...")
            
            # Create new series with result
            new_series = Series(
                series_id=f"{self.series_id}_interp_{self.method}",
                name=f"{source_series.name} (interpolated)",
                unit=source_series.unit,
                values=result.values,
                interpolation_info=result.interpolation_info,
                metadata=source_series.metadata.copy(),
                lineage=Lineage(
                    origin_series=[self.series_id],
                    operation="interpolation",
                    parameters=self.parameters,
                    timestamp=datetime.now(),
                    version="2.0.0"
                )
            )
            
            # Add to dataset
            new_series_id = self.dataset_store.add_series(self.dataset_id, new_series)
            
            self.emit_progress(100, "Interpolation completed")
            
            # Emit result
            result_data = {
                "operation": "interpolation",
                "method": self.method,
                "series_id": new_series_id,
                "series_name": new_series.name,
                "n_points": len(result.values),
                "quality_score": 1.0 - np.isnan(result.values).mean(),
                "duration_ms": result.metadata.duration_ms,
                "parameters": self.parameters,
                "success": True,
                "timestamp": datetime.now()
            }
            
            self.finished.emit()
            logger.info("interpolation_completed", 
                       series_id=new_series_id, method=self.method)
            
        except Exception as e:
            self.emit_error(f"Interpolation failed: {str(e)}")


class CalculusWorker(BaseWorker):
    """Worker for calculus operations (derivatives, integrals)"""
    
    def __init__(self, dataset_store, dataset_id: str, series_id: str,
                 operation: str, parameters: Dict[str, Any]):
        super().__init__()
        self.dataset_store = dataset_store
        self.dataset_id = dataset_id  
        self.series_id = series_id
        self.operation = operation
        self.parameters = parameters
    
    def run(self):
        """Execute calculus operation"""
        try:
            self.emit_progress(0, f"Starting {self.operation}...")
            
            # Get source data
            dataset = self.dataset_store.get_dataset(self.dataset_id)
            source_series = dataset.series[self.series_id]
            
            self.emit_progress(20, "Loading calculus module...")
            
            # Import calculus module
            from platform_base.processing.calculus import calculate_derivative, calculate_integral
            
            self.emit_progress(40, f"Computing {self.operation}...")
            
            # Perform operation based on type
            if "derivative" in self.operation:
                order = int(self.operation.split("_")[1][0])  # derivative_1st -> 1
                result = calculate_derivative(
                    source_series.values, 
                    dataset.t_seconds, 
                    order=order,
                    method=self.parameters.get("derivative_method", "gradient"),
                    smooth_first=self.parameters.get("apply_smoothing", False),
                    smooth_window=self.parameters.get("smooth_window", 5)
                )
                operation_name = f"{order}st derivative" if order == 1 else f"{order}nd derivative" if order == 2 else f"{order}rd derivative"
                unit_suffix = f"/s^{order}"
                
            elif self.operation in ["integral", "area_under_curve"]:
                result = calculate_integral(
                    source_series.values,
                    dataset.t_seconds,
                    method=self.parameters.get("integration_method", "trapz")
                )
                operation_name = "integral"
                unit_suffix = "*s"
                
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            if self.is_cancelled:
                return
                
            self.emit_progress(80, "Creating result series...")
            
            # Create result series
            new_series = Series(
                series_id=f"{self.series_id}_{self.operation}",
                name=f"{source_series.name} ({operation_name})",
                unit=f"{source_series.unit}{unit_suffix}",
                values=result.values,
                metadata=source_series.metadata.copy(),
                lineage=Lineage(
                    origin_series=[self.series_id],
                    operation=self.operation,
                    parameters=self.parameters,
                    timestamp=datetime.now(),
                    version="2.0.0"
                )
            )
            
            # Add to dataset
            new_series_id = self.dataset_store.add_series(self.dataset_id, new_series)
            
            self.emit_progress(100, f"{operation_name} completed")
            
            # Emit result
            result_data = {
                "operation": self.operation,
                "series_id": new_series_id,
                "series_name": new_series.name,
                "n_points": len(result.values),
                "quality_score": 1.0 - np.isnan(result.values).mean(),
                "duration_ms": result.metadata.duration_ms,
                "parameters": self.parameters,
                "success": True,
                "timestamp": datetime.now()
            }
            
            self.finished.emit()
            logger.info("calculus_operation_completed", 
                       series_id=new_series_id, operation=self.operation)
            
        except Exception as e:
            self.emit_error(f"{self.operation} failed: {str(e)}")


class SynchronizationWorker(BaseWorker):
    """Worker for multi-series synchronization"""
    
    def __init__(self, dataset_store, dataset_id: str, series_ids: List[str],
                 method: str, parameters: Dict[str, Any]):
        super().__init__()
        self.dataset_store = dataset_store
        self.dataset_id = dataset_id
        self.series_ids = series_ids
        self.method = method
        self.parameters = parameters
    
    def run(self):
        """Execute synchronization operation"""
        try:
            self.emit_progress(0, f"Starting synchronization with {self.method}...")
            
            # Get source data
            dataset = self.dataset_store.get_dataset(self.dataset_id)
            source_series = [dataset.series[sid] for sid in self.series_ids]
            
            self.emit_progress(20, "Loading synchronization module...")
            
            # Import synchronization module
            from platform_base.processing.synchronization import synchronize_series, SyncMethod, SyncParams
            
            # Convert parameters
            sync_method = SyncMethod(self.method)
            sync_params = SyncParams(**self.parameters)
            
            self.emit_progress(40, f"Synchronizing {len(self.series_ids)} series...")
            
            # Perform synchronization
            sync_result = synchronize_series(
                [s.values for s in source_series],
                dataset.t_seconds,
                sync_method,
                sync_params
            )
            
            if self.is_cancelled:
                return
                
            self.emit_progress(80, "Creating synchronized series...")
            
            # Create new synchronized series
            new_series_ids = []
            for i, (series_id, values) in enumerate(zip(self.series_ids, sync_result.synced_series.values())):
                original_series = source_series[i]
                
                new_series = Series(
                    series_id=f"{series_id}_sync_{self.method}",
                    name=f"{original_series.name} (synchronized)",
                    unit=original_series.unit,
                    values=values,
                    metadata=original_series.metadata.copy(),
                    lineage=Lineage(
                        origin_series=self.series_ids,
                        operation="synchronization",
                        parameters=self.parameters,
                        timestamp=datetime.now(),
                        version="2.0.0"
                    )
                )
                
                new_series_id = self.dataset_store.add_series(self.dataset_id, new_series)
                new_series_ids.append(new_series_id)
            
            self.emit_progress(100, "Synchronization completed")
            
            # Emit result
            result_data = {
                "operation": "synchronization",
                "method": self.method,
                "series_ids": new_series_ids,
                "n_series": len(new_series_ids),
                "n_points": len(sync_result.t_common),
                "alignment_error": sync_result.alignment_error,
                "confidence": sync_result.confidence,
                "parameters": self.parameters,
                "success": True,
                "timestamp": datetime.now()
            }
            
            self.finished.emit()
            logger.info("synchronization_completed", 
                       method=self.method, n_series=len(new_series_ids))
            
        except Exception as e:
            self.emit_error(f"Synchronization failed: {str(e)}")


class ProcessingWorkerManager:
    """Manager for processing workers"""
    
    def __init__(self, dataset_store, signal_hub):
        self.dataset_store = dataset_store
        self.signal_hub = signal_hub
        self.active_workers: Dict[str, BaseWorker] = {}
    
    def start_interpolation(self, operation_id: str, dataset_id: str, 
                          series_id: str, method: str, parameters: Dict[str, Any]):
        """Start interpolation worker"""
        worker = InterpolationWorker(self.dataset_store, dataset_id, series_id, 
                                   method, parameters)
        self._start_worker(operation_id, worker)
    
    def start_calculus(self, operation_id: str, dataset_id: str, series_id: str,
                      operation: str, parameters: Dict[str, Any]):
        """Start calculus worker"""
        worker = CalculusWorker(self.dataset_store, dataset_id, series_id,
                              operation, parameters)
        self._start_worker(operation_id, worker)
    
    def start_synchronization(self, operation_id: str, dataset_id: str,
                            series_ids: List[str], method: str, 
                            parameters: Dict[str, Any]):
        """Start synchronization worker"""
        worker = SynchronizationWorker(self.dataset_store, dataset_id, 
                                     series_ids, method, parameters)
        self._start_worker(operation_id, worker)
    
    def _start_worker(self, operation_id: str, worker: BaseWorker):
        """Start worker and connect signals"""
        # Connect worker signals to signal hub
        worker.progress.connect(
            lambda p: self.signal_hub.emit_operation_progress(operation_id, p))
        worker.error.connect(
            lambda e: self.signal_hub.operation_failed.emit(operation_id, e))
        worker.finished.connect(
            lambda: self._on_worker_finished(operation_id))
        
        # Start worker
        self.active_workers[operation_id] = worker
        worker.start()
        
        logger.info("processing_worker_started", 
                   operation_id=operation_id, worker_type=type(worker).__name__)
    
    def _on_worker_finished(self, operation_id: str):
        """Handle worker completion"""
        if operation_id in self.active_workers:
            worker = self.active_workers.pop(operation_id)
            
            # If worker finished successfully, emit completion
            if not worker.is_cancelled:
                self.signal_hub.operation_completed.emit(operation_id, {
                    "operation_id": operation_id,
                    "success": True,
                    "timestamp": datetime.now()
                })
            
            # Clean up worker
            worker.deleteLater()
            
            logger.debug("processing_worker_finished", operation_id=operation_id)
    
    def cancel_operation(self, operation_id: str):
        """Cancel running operation"""
        if operation_id in self.active_workers:
            worker = self.active_workers[operation_id]
            worker.cancel()
            logger.info("processing_worker_cancelled", operation_id=operation_id)
    
    def cancel_all_operations(self):
        """Cancel all running operations"""
        for operation_id in list(self.active_workers.keys()):
            self.cancel_operation(operation_id)
    
    def get_active_operations(self) -> List[str]:
        """Get list of active operation IDs"""
        return list(self.active_workers.keys())