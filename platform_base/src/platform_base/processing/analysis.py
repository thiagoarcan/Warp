"""
Signal Analysis Module - FFT, Correlation, and Outlier Detection

Provides comprehensive signal analysis capabilities for time series data:
- Fast Fourier Transform (FFT) analysis
- Cross-correlation and auto-correlation
- Outlier detection using multiple methods
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy import signal, stats

from platform_base.utils.errors import ValidationError
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from numpy.typing import NDArray


logger = get_logger(__name__)


@dataclass
class FFTResult:
    """Result of FFT analysis"""
    frequencies: NDArray[np.float64]  # Frequency bins (Hz)
    magnitude: NDArray[np.float64]    # Magnitude spectrum
    phase: NDArray[np.float64]        # Phase spectrum (radians)
    power: NDArray[np.float64]        # Power spectral density
    dominant_frequency: float         # Frequency with highest magnitude
    sampling_rate: float              # Original sampling rate (Hz)


@dataclass
class CorrelationResult:
    """Result of correlation analysis"""
    correlation: NDArray[np.float64]  # Correlation values
    lags: NDArray[np.float64]         # Time lags
    peak_correlation: float           # Maximum correlation value
    peak_lag: float                   # Lag at maximum correlation
    confidence_interval: tuple[float, float]  # 95% confidence interval


@dataclass
class OutlierResult:
    """Result of outlier detection"""
    outlier_indices: NDArray[np.int64]  # Indices of detected outliers
    outlier_mask: NDArray[np.bool_]     # Boolean mask (True = outlier)
    scores: NDArray[np.float64]         # Outlier scores for each point
    threshold: float                     # Threshold used for detection
    method: str                          # Detection method used
    n_outliers: int                      # Count of outliers detected


def compute_fft(
    values: NDArray[np.float64],
    sampling_rate: float,
    window: str = "hann",
    detrend: bool = True,
) -> FFTResult:
    """
    Compute Fast Fourier Transform of a signal.
    
    Args:
        values: Input signal values
        sampling_rate: Sampling rate in Hz
        window: Window function to apply ('hann', 'hamming', 'blackman', 'bartlett', None)
        detrend: Whether to remove linear trend before FFT
        
    Returns:
        FFTResult with frequency domain analysis
        
    Raises:
        ValidationError: If input data is invalid
    """
    if len(values) < 2:
        raise ValidationError("FFT requires at least 2 data points")

    if sampling_rate <= 0:
        raise ValidationError(f"Sampling rate must be positive, got {sampling_rate}")

    # Remove NaN values
    clean_values = values[~np.isnan(values)]
    if len(clean_values) < 2:
        raise ValidationError("Not enough valid data points for FFT (need at least 2)")

    # Detrend if requested
    if detrend:
        clean_values = signal.detrend(clean_values)

    # Apply window function
    if window:
        if window == "hann":
            window_func = np.hanning(len(clean_values))
        elif window == "hamming":
            window_func = np.hamming(len(clean_values))
        elif window == "blackman":
            window_func = np.blackman(len(clean_values))
        elif window == "bartlett":
            window_func = np.bartlett(len(clean_values))
        else:
            raise ValidationError(f"Unknown window function: {window}")

        clean_values = clean_values * window_func

    # Compute FFT
    fft_values = np.fft.fft(clean_values)
    n = len(clean_values)

    # Compute frequencies
    frequencies = np.fft.fftfreq(n, d=1/sampling_rate)

    # Take only positive frequencies
    positive_freq_idx = frequencies >= 0
    frequencies = frequencies[positive_freq_idx]
    fft_values = fft_values[positive_freq_idx]

    # Compute magnitude, phase, and power
    magnitude = np.abs(fft_values)
    phase = np.angle(fft_values)
    power = magnitude ** 2

    # Find dominant frequency
    dominant_idx = np.argmax(magnitude[1:]) + 1  # Skip DC component
    dominant_frequency = frequencies[dominant_idx]

    logger.info(
        "fft_computed",
        n_points=len(values),
        sampling_rate=sampling_rate,
        dominant_freq=dominant_frequency,
        window=window,
    )

    return FFTResult(
        frequencies=frequencies,
        magnitude=magnitude,
        phase=phase,
        power=power,
        dominant_frequency=dominant_frequency,
        sampling_rate=sampling_rate,
    )


def compute_correlation(
    signal1: NDArray[np.float64],
    signal2: NDArray[np.float64] | None = None,
    mode: str = "auto",
    max_lag: int | None = None,
    normalize: bool = True,
) -> CorrelationResult:
    """
    Compute correlation between signals.
    
    Args:
        signal1: First signal
        signal2: Second signal (if None, computes autocorrelation)
        mode: 'auto' for autocorrelation, 'cross' for cross-correlation
        max_lag: Maximum lag to compute (None = full range)
        normalize: Whether to normalize correlation to [-1, 1]
        
    Returns:
        CorrelationResult with correlation analysis
        
    Raises:
        ValidationError: If input data is invalid
    """
    if len(signal1) < 2:
        raise ValidationError("Correlation requires at least 2 data points")

    # Remove NaN values
    clean_signal1 = signal1[~np.isnan(signal1)]

    if len(clean_signal1) < 2:
        raise ValidationError("Not enough valid data points for correlation")

    # Auto-correlation if signal2 not provided
    if signal2 is None or mode == "auto":
        correlation = np.correlate(clean_signal1, clean_signal1, mode='full')
        lags = np.arange(-len(clean_signal1) + 1, len(clean_signal1))
    else:
        # Cross-correlation
        clean_signal2 = signal2[~np.isnan(signal2)]

        if len(clean_signal2) < 2:
            raise ValidationError("Not enough valid data points in signal2")

        correlation = np.correlate(clean_signal1, clean_signal2, mode='full')
        lags = np.arange(-len(clean_signal1) + 1, len(clean_signal1))

    # Normalize if requested
    if normalize:
        correlation = correlation / (np.std(clean_signal1) * len(clean_signal1))
        if signal2 is not None and mode != "auto":
            correlation = correlation / np.std(clean_signal2)

    # Limit to max_lag if specified
    if max_lag is not None:
        lag_mask = np.abs(lags) <= max_lag
        correlation = correlation[lag_mask]
        lags = lags[lag_mask]

    # Find peak correlation
    peak_idx = np.argmax(np.abs(correlation))
    peak_correlation = correlation[peak_idx]
    peak_lag = lags[peak_idx]

    # Compute confidence interval (95%)
    n = len(clean_signal1)
    confidence_bound = 1.96 / np.sqrt(n)  # 95% confidence
    confidence_interval = (-confidence_bound, confidence_bound)

    logger.info(
        "correlation_computed",
        mode=mode,
        peak_correlation=peak_correlation,
        peak_lag=peak_lag,
        n_points=len(signal1),
    )

    return CorrelationResult(
        correlation=correlation,
        lags=lags,
        peak_correlation=peak_correlation,
        peak_lag=peak_lag,
        confidence_interval=confidence_interval,
    )


def detect_outliers(
    values: NDArray[np.float64],
    method: str = "zscore",
    threshold: float | None = None,
    **kwargs,
) -> OutlierResult:
    """
    Detect outliers in a signal using various methods.
    
    Args:
        values: Input signal values
        method: Detection method ('zscore', 'iqr', 'isolation_forest', 'lof')
        threshold: Threshold for outlier detection (method-dependent)
        **kwargs: Additional method-specific parameters
        
    Returns:
        OutlierResult with outlier detection results
        
    Raises:
        ValidationError: If input data or method is invalid
    """
    if len(values) < 3:
        raise ValidationError("Outlier detection requires at least 3 data points")

    # Remove NaN values for computation
    valid_mask = ~np.isnan(values)
    clean_values = values[valid_mask]

    if len(clean_values) < 3:
        raise ValidationError("Not enough valid data points for outlier detection")

    # Initialize result arrays
    outlier_mask_clean = np.zeros(len(clean_values), dtype=bool)
    scores_clean = np.zeros(len(clean_values))

    # Apply detection method
    if method == "zscore":
        # Z-score method
        default_threshold = threshold or 3.0
        mean = np.mean(clean_values)
        std = np.std(clean_values)

        if std == 0:
            logger.warning("zscore_zero_std", message="Standard deviation is zero")
            scores_clean = np.zeros(len(clean_values))
        else:
            scores_clean = np.abs((clean_values - mean) / std)

        outlier_mask_clean = scores_clean > default_threshold
        used_threshold = default_threshold

    elif method == "iqr":
        # Interquartile range method
        default_threshold = threshold or 1.5
        q1 = np.percentile(clean_values, 25)
        q3 = np.percentile(clean_values, 75)
        iqr = q3 - q1

        lower_bound = q1 - default_threshold * iqr
        upper_bound = q3 + default_threshold * iqr

        # Distance from bounds as score
        scores_clean = np.maximum(
            lower_bound - clean_values,
            clean_values - upper_bound
        )
        scores_clean = np.maximum(scores_clean, 0)

        outlier_mask_clean = (clean_values < lower_bound) | (clean_values > upper_bound)
        used_threshold = default_threshold

    elif method == "modified_zscore":
        # Modified Z-score using median absolute deviation
        default_threshold = threshold or 3.5
        median = np.median(clean_values)
        mad = np.median(np.abs(clean_values - median))

        if mad == 0:
            logger.warning("mad_zero", message="Median absolute deviation is zero")
            scores_clean = np.zeros(len(clean_values))
        else:
            # Modified z-score
            scores_clean = 0.6745 * np.abs(clean_values - median) / mad

        outlier_mask_clean = scores_clean > default_threshold
        used_threshold = default_threshold

    elif method == "percentile":
        # Percentile-based method
        lower_percentile = kwargs.get("lower_percentile", 1)
        upper_percentile = kwargs.get("upper_percentile", 99)

        lower_bound = np.percentile(clean_values, lower_percentile)
        upper_bound = np.percentile(clean_values, upper_percentile)

        scores_clean = np.maximum(
            lower_bound - clean_values,
            clean_values - upper_bound
        )
        scores_clean = np.maximum(scores_clean, 0)

        outlier_mask_clean = (clean_values < lower_bound) | (clean_values > upper_bound)
        used_threshold = 0  # Not applicable for percentile method

    else:
        raise ValidationError(f"Unknown outlier detection method: {method}")

    # Map back to original indices
    outlier_mask_full = np.zeros(len(values), dtype=bool)
    scores_full = np.zeros(len(values))

    outlier_mask_full[valid_mask] = outlier_mask_clean
    scores_full[valid_mask] = scores_clean

    # Get outlier indices
    outlier_indices = np.where(outlier_mask_full)[0]

    logger.info(
        "outliers_detected",
        method=method,
        n_outliers=len(outlier_indices),
        n_total=len(values),
        threshold=used_threshold,
    )

    return OutlierResult(
        outlier_indices=outlier_indices,
        outlier_mask=outlier_mask_full,
        scores=scores_full,
        threshold=used_threshold,
        method=method,
        n_outliers=len(outlier_indices),
    )
