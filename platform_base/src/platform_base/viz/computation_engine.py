"""
Computation Engine - Mathematical operations on time series data
Original implementation for Platform Base v2.0
"""

import numpy as np
from typing import Tuple, Dict, Optional, List
from scipy import integrate, interpolate, signal, stats
from datetime import datetime, timedelta

# Small constant to avoid division by zero
EPSILON = 1e-10


class ComputationEngine:
    """Performs mathematical computations on time series data"""
    
    @staticmethod
    def compute_derivative(timestamps: np.ndarray, values: np.ndarray, 
                          order: int = 1, apply_smoothing: bool = False,
                          smoothing_span: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute nth order derivative of time series
        
        Args:
            timestamps: Time axis data
            values: Value axis data
            order: Derivative order (1, 2, or 3)
            apply_smoothing: Whether to smooth before differentiation
            smoothing_span: Window size for smoothing
            
        Returns:
            (timestamps, derivative_values)
        """
        working_values = np.array(values, dtype=float)
        
        if apply_smoothing and smoothing_span > 1:
            kernel = np.ones(smoothing_span) / smoothing_span
            working_values = np.convolve(working_values, kernel, mode='same')
        
        result_values = working_values
        result_times = timestamps
        
        for _ in range(order):
            dt = np.diff(result_times)
            dv = np.diff(result_values)
            
            # Avoid division by zero
            dt = np.where(dt == 0, EPSILON, dt)
            
            result_values = dv / dt
            result_times = result_times[:-1]
            
        return result_times, result_values
    
    @staticmethod
    def compute_area_under_curve(timestamps: np.ndarray, values: np.ndarray,
                                 method: str = 'trapezoid') -> float:
        """
        Compute integral (area under curve)
        
        Args:
            timestamps: Time axis
            values: Value axis
            method: Integration method ('trapezoid', 'simpson')
            
        Returns:
            Total area value
        """
        if method == 'simpson' and len(values) >= 3:
            area = integrate.simpson(values, x=timestamps)
        else:
            area = integrate.trapezoid(values, x=timestamps)
            
        return float(area)
    
    @staticmethod
    def compute_area_between_curves(timestamps1: np.ndarray, values1: np.ndarray,
                                    timestamps2: np.ndarray, values2: np.ndarray) -> float:
        """
        Compute area between two curves after temporal alignment
        
        Args:
            timestamps1, values1: First curve
            timestamps2, values2: Second curve
            
        Returns:
            Area between curves
        """
        # Find common time range
        t_min = max(timestamps1.min(), timestamps2.min())
        t_max = min(timestamps1.max(), timestamps2.max())
        
        # Create common time grid
        num_points = min(len(timestamps1), len(timestamps2))
        common_times = np.linspace(t_min, t_max, num_points)
        
        # Interpolate both curves onto common grid
        interp1 = interpolate.interp1d(timestamps1, values1, kind='linear', 
                                      fill_value='extrapolate')
        interp2 = interpolate.interp1d(timestamps2, values2, kind='linear',
                                      fill_value='extrapolate')
        
        aligned_values1 = interp1(common_times)
        aligned_values2 = interp2(common_times)
        
        # Compute area between
        difference = np.abs(aligned_values1 - aligned_values2)
        area = integrate.trapezoid(difference, x=common_times)
        
        return float(area)
    
    @staticmethod
    def compute_statistics(values: np.ndarray) -> Dict[str, float]:
        """
        Compute statistical measures
        
        Returns:
            Dictionary with mean, median, mode, min, max, std, variance
        """
        clean_vals = values[~np.isnan(values)]
        
        if len(clean_vals) == 0:
            return {
                'mean': np.nan, 'median': np.nan, 'mode': np.nan,
                'min': np.nan, 'max': np.nan, 'std': np.nan, 'variance': np.nan
            }
        
        mode_result = stats.mode(clean_vals, keepdims=True)
        
        return {
            'mean': float(np.mean(clean_vals)),
            'median': float(np.median(clean_vals)),
            'mode': float(mode_result.mode[0]) if len(mode_result.mode) > 0 else np.nan,
            'min': float(np.min(clean_vals)),
            'max': float(np.max(clean_vals)),
            'std': float(np.std(clean_vals)),
            'variance': float(np.var(clean_vals))
        }
    
    @staticmethod
    def compute_std_deviation_bands(values: np.ndarray, multiplier: float = 1.0) -> Dict[str, np.ndarray]:
        """
        Compute standard deviation bands around mean
        
        Args:
            values: Input data
            multiplier: Std deviation multiplier (1.0, 1.5, 2.0, etc.)
            
        Returns:
            Dictionary with 'mean', 'upper_band', 'lower_band'
        """
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        upper_band = mean_val + (multiplier * std_val)
        lower_band = mean_val - (multiplier * std_val)
        
        return {
            'mean': np.full_like(values, mean_val),
            'upper_band': np.full_like(values, upper_band),
            'lower_band': np.full_like(values, lower_band)
        }
    
    @staticmethod
    def compute_trend_line(timestamps: np.ndarray, values: np.ndarray,
                          degree: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute polynomial trend line
        
        Args:
            timestamps: Time axis
            values: Value axis
            degree: Polynomial degree (1 = linear)
            
        Returns:
            (timestamps, trend_values)
        """
        coefficients = np.polyfit(timestamps, values, degree)
        trend_values = np.polyval(coefficients, timestamps)
        
        return timestamps, trend_values
    
    @staticmethod
    def compute_regression(timestamps: np.ndarray, values: np.ndarray,
                          regression_type: str = 'linear',
                          polynomial_order: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply various regression methods
        
        Args:
            timestamps: Time axis
            values: Value axis
            regression_type: Type of regression
                'linear', 'polynomial', 'exponential', 'logarithmic', 'power'
            polynomial_order: Order for polynomial regression
            
        Returns:
            (timestamps, fitted_values)
        """
        if regression_type == 'linear':
            coeffs = np.polyfit(timestamps, values, 1)
            fitted = np.polyval(coeffs, timestamps)
            
        elif regression_type == 'polynomial':
            coeffs = np.polyfit(timestamps, values, polynomial_order)
            fitted = np.polyval(coeffs, timestamps)
            
        elif regression_type == 'exponential':
            # y = a * exp(b * x)
            # ln(y) = ln(a) + b * x
            log_vals = np.log(np.abs(values) + EPSILON)
            coeffs = np.polyfit(timestamps, log_vals, 1)
            fitted = np.exp(coeffs[1]) * np.exp(coeffs[0] * timestamps)
            
        elif regression_type == 'logarithmic':
            # y = a + b * ln(x)
            log_times = np.log(np.abs(timestamps) + EPSILON)
            coeffs = np.polyfit(log_times, values, 1)
            fitted = coeffs[0] * log_times + coeffs[1]
            
        elif regression_type == 'power':
            # y = a * x^b
            # ln(y) = ln(a) + b * ln(x)
            log_times = np.log(np.abs(timestamps) + EPSILON)
            log_vals = np.log(np.abs(values) + EPSILON)
            coeffs = np.polyfit(log_times, log_vals, 1)
            fitted = np.exp(coeffs[1]) * (timestamps ** coeffs[0])
            
        else:
            raise ValueError(f"Unknown regression type: {regression_type}")
            
        return timestamps, fitted
    
    @staticmethod
    def compute_interpolation(timestamps: np.ndarray, values: np.ndarray,
                             target_interval_seconds: float,
                             interpolation_kind: str = 'linear') -> Tuple[np.ndarray, np.ndarray]:
        """
        Interpolate time series to regular interval
        
        Args:
            timestamps: Original time axis (as numeric values or datetime)
            values: Original values
            target_interval_seconds: Target sampling interval
            interpolation_kind: Type of interpolation
                'linear', 'cubic', 'quadratic', 'nearest', 'slinear'
                
        Returns:
            (new_timestamps, interpolated_values)
        """
        t_min = timestamps.min()
        t_max = timestamps.max()
        
        num_points = int((t_max - t_min) / target_interval_seconds) + 1
        new_timestamps = np.linspace(t_min, t_max, num_points)
        
        interpolator = interpolate.interp1d(timestamps, values, kind=interpolation_kind,
                                           fill_value='extrapolate')
        new_values = interpolator(new_timestamps)
        
        return new_timestamps, new_values
    
    @staticmethod
    def compute_rate_of_change(timestamps: np.ndarray, values: np.ndarray,
                               window_size: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute rate of change over time
        
        Args:
            timestamps: Time axis
            values: Value axis
            window_size: Number of points to average over
            
        Returns:
            (timestamps, rate_values)
        """
        if window_size == 1:
            return ComputationEngine.compute_derivative(timestamps, values, order=1)
        
        # Compute derivative first
        deriv_times, deriv_vals = ComputationEngine.compute_derivative(timestamps, values, order=1)
        
        # Apply moving average
        kernel = np.ones(window_size) / window_size
        smoothed_rate = np.convolve(deriv_vals, kernel, mode='same')
        
        return deriv_times, smoothed_rate
    
    @staticmethod
    def synchronize_time_series(datasets: List[Tuple[np.ndarray, np.ndarray]],
                                target_interval_seconds: float) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Synchronize multiple time series to common time grid
        
        Args:
            datasets: List of (timestamps, values) tuples
            target_interval_seconds: Common sampling interval
            
        Returns:
            List of synchronized (timestamps, values) tuples
        """
        if not datasets:
            return []
        
        # Find common time range
        t_min = max(ts.min() for ts, _ in datasets)
        t_max = min(ts.max() for ts, _ in datasets)
        
        # Create common time grid
        num_points = int((t_max - t_min) / target_interval_seconds) + 1
        common_times = np.linspace(t_min, t_max, num_points)
        
        # Interpolate all datasets to common grid
        synchronized = []
        for timestamps, values in datasets:
            interp_func = interpolate.interp1d(timestamps, values, kind='linear',
                                              fill_value='extrapolate')
            sync_values = interp_func(common_times)
            synchronized.append((common_times, sync_values))
        
        return synchronized
