"""
Operation Workers - Workers thread para operações matemáticas

Implementa execução assíncrona com progress feedback para:
- Cálculos (derivadas, integrais, área entre curvas)
- Interpolação
- Filtragem
- Suavização
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class BaseOperationWorker(QObject):
    """
    Worker base para operações matemáticas
    
    Emite sinais de progresso e resultado
    """
    
    # Signals
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(object)    # result object
    error = pyqtSignal(str)          # error message
    
    def __init__(self, operation_name: str = "operation"):
        super().__init__()
        self.operation_name = operation_name
        self._cancelled = False
    
    def cancel(self):
        """Cancela operação"""
        self._cancelled = True
    
    def _emit_progress(self, percent: int, message: str):
        """Emite progresso de forma thread-safe"""
        self.progress.emit(percent, message)
        if QApplication.instance():
            QApplication.processEvents()
    
    def _check_cancelled(self) -> bool:
        """Verifica se operação foi cancelada"""
        if self._cancelled:
            self.error.emit("Operação cancelada pelo usuário")
            return True
        return False


class CalculusWorker(BaseOperationWorker):
    """
    Worker para operações de cálculo (derivadas, integrais, áreas)
    """
    
    def __init__(self, 
                 values: np.ndarray, 
                 t: np.ndarray,
                 operation: str,
                 params: Optional[Dict[str, Any]] = None):
        super().__init__("calculus")
        
        self.values = values
        self.t = t
        self.operation = operation
        self.params = params or {}
    
    def execute(self):
        """Executa operação de cálculo"""
        try:
            start_time = time.perf_counter()
            
            self._emit_progress(10, f"Iniciando {self.operation}...")
            
            if self._check_cancelled():
                return
            
            # Import calculus module
            from platform_base.processing.calculus import (
                area_between,
                area_between_with_crossings,
                derivative,
                integral,
            )
            
            result = None
            
            if self.operation == "derivative":
                self._emit_progress(30, "Calculando derivada...")
                
                order = self.params.get('order', 1)
                method = self.params.get('method', 'finite_diff')
                
                result = derivative(
                    self.values, 
                    self.t, 
                    order=order,
                    method=method,
                    params=self.params
                )
                
            elif self.operation == "integral":
                self._emit_progress(30, "Calculando integral...")
                
                method = self.params.get('method', 'trapezoid')
                
                result = integral(
                    self.values, 
                    self.t, 
                    method=method,
                    params=self.params
                )
                
            elif self.operation == "area_between":
                self._emit_progress(30, "Calculando área entre curvas...")
                
                values_lower = self.params.get('values_lower')
                if values_lower is None:
                    raise ValueError("values_lower is required for area_between")
                
                with_crossings = self.params.get('with_crossings', False)
                method = self.params.get('method', 'trapezoid')
                
                if with_crossings:
                    result = area_between_with_crossings(
                        self.values,
                        values_lower,
                        self.t,
                        method=method
                    )
                else:
                    result = area_between(
                        self.values,
                        values_lower,
                        self.t,
                        method=method
                    )
            else:
                raise ValueError(f"Operação desconhecida: {self.operation}")
            
            if self._check_cancelled():
                return
            
            self._emit_progress(90, "Finalizando...")
            
            duration = time.perf_counter() - start_time
            
            logger.info(f"calculus_worker_completed: {self.operation} in {duration * 1000:.1f}ms")
            
            self._emit_progress(100, f"{self.operation} concluído!")
            self.finished.emit(result)
            
        except Exception as e:
            logger.exception(f"calculus_worker_failed: {self.operation}")
            self.error.emit(str(e))


class InterpolationWorker(BaseOperationWorker):
    """
    Worker para operações de interpolação
    """
    
    def __init__(self, 
                 values: np.ndarray, 
                 t: np.ndarray,
                 method: str,
                 params: Optional[Dict[str, Any]] = None):
        super().__init__("interpolation")
        
        self.values = values
        self.t = t
        self.method = method
        self.params = params or {}
    
    def execute(self):
        """Executa interpolação"""
        try:
            start_time = time.perf_counter()
            
            self._emit_progress(10, f"Iniciando interpolação ({self.method})...")
            
            if self._check_cancelled():
                return
            
            # Import interpolation module
            from platform_base.processing.interpolation import (
                gpr,
                linear,
                lomb_scargle,
                mls,
                smoothing_spline,
                spline_cubic,
            )

            # Determina novos pontos de avaliação
            target_points = self.params.get('target_points', len(self.t) * 2)
            t_new = np.linspace(self.t[0], self.t[-1], target_points)
            
            self._emit_progress(30, f"Interpolando {target_points} pontos...")
            
            if self._check_cancelled():
                return
            
            # Executa interpolação baseada no método
            if self.method == "linear":
                result = linear(self.values, self.t, t_new)
            elif self.method == "spline_cubic":
                result = spline_cubic(self.values, self.t, t_new)
            elif self.method == "smoothing_spline":
                s = self.params.get('s', None)
                result = smoothing_spline(self.values, self.t, t_new, s=s)
            elif self.method == "mls":
                bandwidth = self.params.get('bandwidth', 0.1)
                result = mls(self.values, self.t, t_new, bandwidth=bandwidth)
            elif self.method == "gpr":
                kernel = self.params.get('kernel', 'rbf')
                result = gpr(self.values, self.t, t_new, kernel=kernel)
            elif self.method == "lomb_scargle":
                result = lomb_scargle(self.values, self.t, t_new)
            else:
                raise ValueError(f"Método de interpolação desconhecido: {self.method}")
            
            if self._check_cancelled():
                return
            
            self._emit_progress(90, "Finalizando...")
            
            duration = time.perf_counter() - start_time
            
            # Prepara resultado
            output = {
                't_new': t_new,
                'values_new': result.values if hasattr(result, 'values') else result,
                'method': self.method,
                'original_points': len(self.t),
                'new_points': len(t_new),
                'duration_ms': duration * 1000
            }
            
            if hasattr(result, 'quality_metrics'):
                output['quality_metrics'] = result.quality_metrics
            
            logger.info(f"interpolation_worker_completed: {self.method}, {len(self.t)} -> {len(t_new)} pts in {duration * 1000:.1f}ms")
            
            self._emit_progress(100, f"Interpolação ({self.method}) concluída!")
            self.finished.emit(output)
            
        except Exception as e:
            logger.exception(f"interpolation_worker_failed: {self.method}")
            self.error.emit(str(e))


class FilterWorker(BaseOperationWorker):
    """
    Worker para operações de filtragem
    """
    
    def __init__(self, 
                 values: np.ndarray, 
                 filter_type: str,
                 params: Optional[Dict[str, Any]] = None):
        super().__init__("filter")
        
        self.values = values
        self.filter_type = filter_type
        self.params = params or {}
    
    def execute(self):
        """Executa filtragem"""
        try:
            start_time = time.perf_counter()
            
            self._emit_progress(10, f"Aplicando filtro {self.filter_type}...")
            
            if self._check_cancelled():
                return
            
            from scipy import signal
            from scipy.ndimage import gaussian_filter1d, median_filter
            
            result = None
            
            if self.filter_type == "butterworth_lowpass":
                order = self.params.get('order', 4)
                cutoff = self.params.get('cutoff_freq', 0.1)
                
                b, a = signal.butter(order, cutoff, btype='low')
                result = signal.filtfilt(b, a, self.values)
                
            elif self.filter_type == "butterworth_highpass":
                order = self.params.get('order', 4)
                cutoff = self.params.get('cutoff_freq', 0.1)
                
                b, a = signal.butter(order, cutoff, btype='high')
                result = signal.filtfilt(b, a, self.values)
                
            elif self.filter_type == "butterworth_bandpass":
                order = self.params.get('order', 4)
                low_cutoff = self.params.get('cutoff_freq', 0.1)
                high_cutoff = self.params.get('cutoff_freq_high', 0.3)
                
                b, a = signal.butter(order, [low_cutoff, high_cutoff], btype='band')
                result = signal.filtfilt(b, a, self.values)
                
            elif self.filter_type == "gaussian":
                sigma = self.params.get('sigma', 1.0)
                result = gaussian_filter1d(self.values, sigma=sigma)
                
            elif self.filter_type == "median":
                window_size = self.params.get('window_size', 5)
                result = median_filter(self.values, size=window_size)
                
            elif self.filter_type == "outlier_removal":
                threshold = self.params.get('outlier_threshold', 3.0)
                mean = np.mean(self.values)
                std = np.std(self.values)
                
                # Identifica outliers
                outliers = np.abs(self.values - mean) > threshold * std
                
                # Interpola outliers
                result = self.values.copy()
                result[outliers] = np.interp(
                    np.where(outliers)[0],
                    np.where(~outliers)[0],
                    self.values[~outliers]
                )
            else:
                raise ValueError(f"Tipo de filtro desconhecido: {self.filter_type}")
            
            if self._check_cancelled():
                return
            
            self._emit_progress(90, "Finalizando...")
            
            duration = time.perf_counter() - start_time
            
            output = {
                'values_filtered': result,
                'filter_type': self.filter_type,
                'params': self.params,
                'n_points': len(self.values),
                'duration_ms': duration * 1000
            }
            
            logger.info(f"filter_worker_completed: {self.filter_type}, {len(self.values)} pts in {duration * 1000:.1f}ms")
            
            self._emit_progress(100, f"Filtro {self.filter_type} aplicado!")
            self.finished.emit(output)
            
        except Exception as e:
            logger.exception(f"filter_worker_failed: {self.filter_type}")
            self.error.emit(str(e))


class SmoothingWorker(BaseOperationWorker):
    """
    Worker para operações de suavização
    """
    
    def __init__(self, 
                 values: np.ndarray, 
                 method: str,
                 params: Optional[Dict[str, Any]] = None):
        super().__init__("smoothing")
        
        self.values = values
        self.method = method
        self.params = params or {}
    
    def execute(self):
        """Executa suavização"""
        try:
            start_time = time.perf_counter()
            
            self._emit_progress(10, f"Aplicando suavização ({self.method})...")
            
            if self._check_cancelled():
                return
            
            from scipy.ndimage import gaussian_filter1d
            from scipy.signal import savgol_filter
            
            result = None
            
            if self.method == "gaussian":
                sigma = self.params.get('sigma', 1.0)
                result = gaussian_filter1d(self.values, sigma=sigma)
                
            elif self.method == "moving_average":
                window_size = self.params.get('window_size', 5)
                kernel = np.ones(window_size) / window_size
                result = np.convolve(self.values, kernel, mode='same')
                
            elif self.method == "savitzky_golay":
                window_size = self.params.get('window_size', 5)
                polyorder = self.params.get('polyorder', 3)
                
                # Window size deve ser ímpar
                if window_size % 2 == 0:
                    window_size += 1
                    
                result = savgol_filter(self.values, window_size, polyorder)
                
            elif self.method == "exponential":
                alpha = self.params.get('alpha', 0.3)
                result = np.zeros_like(self.values)
                result[0] = self.values[0]
                
                for i in range(1, len(self.values)):
                    result[i] = alpha * self.values[i] + (1 - alpha) * result[i-1]
                    
            elif self.method == "median":
                window_size = self.params.get('window_size', 5)
                from scipy.ndimage import median_filter
                result = median_filter(self.values, size=window_size)
                
            else:
                raise ValueError(f"Método de suavização desconhecido: {self.method}")
            
            if self._check_cancelled():
                return
            
            self._emit_progress(90, "Finalizando...")
            
            duration = time.perf_counter() - start_time
            
            output = {
                'values_smoothed': result,
                'method': self.method,
                'params': self.params,
                'n_points': len(self.values),
                'duration_ms': duration * 1000
            }
            
            logger.info(f"smoothing_worker_completed: {self.method}, {len(self.values)} pts in {duration * 1000:.1f}ms")
            
            self._emit_progress(100, f"Suavização ({self.method}) aplicada!")
            self.finished.emit(output)
            
        except Exception as e:
            logger.exception(f"smoothing_worker_failed: {self.method}")
            self.error.emit(str(e))


class BatchOperationWorker(BaseOperationWorker):
    """
    Worker para executar múltiplas operações em batch
    """
    
    def __init__(self, operations: List[Dict[str, Any]]):
        """
        Args:
            operations: Lista de dicts com {type, data, params}
        """
        super().__init__("batch")
        self.operations = operations
        self.results = []
    
    def execute(self):
        """Executa batch de operações"""
        try:
            start_time = time.perf_counter()
            total = len(self.operations)
            
            self._emit_progress(5, f"Iniciando batch de {total} operações...")
            
            for i, op in enumerate(self.operations):
                if self._check_cancelled():
                    return
                
                percent = int((i / total) * 80) + 10
                self._emit_progress(percent, f"Operação {i+1}/{total}: {op.get('type', 'unknown')}...")
                
                try:
                    # Executa operação individual
                    result = self._execute_single_operation(op)
                    self.results.append({
                        'index': i,
                        'type': op.get('type'),
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    self.results.append({
                        'index': i,
                        'type': op.get('type'),
                        'success': False,
                        'error': str(e)
                    })
            
            self._emit_progress(95, "Finalizando batch...")
            
            duration = time.perf_counter() - start_time
            
            success_count = sum(1 for r in self.results if r['success'])
            
            output = {
                'total_operations': total,
                'successful': success_count,
                'failed': total - success_count,
                'results': self.results,
                'duration_ms': duration * 1000
            }
            
            logger.info(f"batch_worker_completed: {success_count}/{total} ops in {duration * 1000:.1f}ms")
            
            self._emit_progress(100, f"Batch concluído: {success_count}/{total} operações")
            self.finished.emit(output)
            
        except Exception as e:
            logger.exception("batch_worker_failed")
            self.error.emit(str(e))
    
    def _execute_single_operation(self, op: Dict[str, Any]) -> Any:
        """Executa uma única operação do batch"""
        op_type = op.get('type')
        data = op.get('data', {})
        params = op.get('params', {})
        
        if op_type == 'derivative':
            from platform_base.processing.calculus import derivative
            return derivative(
                data.get('values'), 
                data.get('t'),
                order=params.get('order', 1),
                method=params.get('method', 'finite_diff')
            )
            
        elif op_type == 'integral':
            from platform_base.processing.calculus import integral
            return integral(
                data.get('values'), 
                data.get('t'),
                method=params.get('method', 'trapezoid')
            )
            
        elif op_type == 'interpolation':
            from platform_base.processing.interpolation import linear
            return linear(
                data.get('values'), 
                data.get('t'),
                data.get('t_new')
            )
        
        else:
            raise ValueError(f"Tipo de operação desconhecido: {op_type}")
