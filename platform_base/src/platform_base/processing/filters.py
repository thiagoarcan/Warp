"""
Signal Filtering Module - Lowpass, Highpass, and Bandpass Filters

Provides comprehensive digital filtering capabilities for time series data:
- Lowpass filters (remove high-frequency noise)
- Highpass filters (remove low-frequency trends)
- Bandpass filters (isolate specific frequency ranges)
- Bandstop/notch filters (remove specific frequencies)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import numpy as np
from scipy import signal

from platform_base.utils.errors import ValidationError
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from numpy.typing import NDArray


logger = get_logger(__name__)


FilterType = Literal["lowpass", "highpass", "bandpass", "bandstop"]
FilterMethod = Literal["butter", "chebyshev1", "chebyshev2", "elliptic", "bessel"]


@dataclass
class FilterResult:
    """Result of filter operation"""
    filtered_values: NDArray[np.float64]  # Filtered signal
    original_values: NDArray[np.float64]  # Original signal (for reference)
    filter_type: str                       # Type of filter applied
    cutoff_frequency: float | tuple[float, float]  # Cutoff frequency/frequencies (Hz)
    sampling_rate: float                   # Sampling rate (Hz)
    filter_order: int                      # Filter order
    method: str                            # Filter design method


def apply_filter(
    values: NDArray[np.float64],
    sampling_rate: float,
    filter_type: FilterType,
    cutoff_frequency: float | tuple[float, float],
    filter_order: int = 4,
    method: FilterMethod = "butter",
    zero_phase: bool = True,
) -> FilterResult:
    """
    Apply digital filter to signal.
    
    Args:
        values: Input signal values
        sampling_rate: Sampling rate in Hz
        filter_type: Type of filter ('lowpass', 'highpass', 'bandpass', 'bandstop')
        cutoff_frequency: Cutoff frequency in Hz (single value for lowpass/highpass,
                         tuple of (low, high) for bandpass/bandstop)
        filter_order: Filter order (higher = sharper transition, more ringing)
        method: Filter design method ('butter', 'chebyshev1', 'chebyshev2', 'elliptic', 'bessel')
        zero_phase: Use zero-phase filtering (filtfilt instead of lfilter)
        
    Returns:
        FilterResult with filtered signal
        
    Raises:
        ValidationError: If input parameters are invalid
    """
    # Validate inputs
    if len(values) < 2:
        raise ValidationError("Filtering requires at least 2 data points")
    
    if sampling_rate <= 0:
        raise ValidationError(f"Sampling rate must be positive, got {sampling_rate}")
    
    if filter_order < 1:
        raise ValidationError(f"Filter order must be at least 1, got {filter_order}")
    
    # Remove NaN values
    clean_values = values[~np.isnan(values)]
    
    if len(clean_values) < 2 * filter_order:
        raise ValidationError(
            f"Not enough valid data points for filter order {filter_order} "
            f"(need at least {2 * filter_order})"
        )
    
    # Normalize cutoff frequencies to Nyquist frequency
    nyquist_freq = sampling_rate / 2
    
    if filter_type in ("lowpass", "highpass"):
        if isinstance(cutoff_frequency, tuple):
            raise ValidationError(
                f"{filter_type} filter requires single cutoff frequency, got tuple"
            )
        
        if cutoff_frequency <= 0 or cutoff_frequency >= nyquist_freq:
            raise ValidationError(
                f"Cutoff frequency must be between 0 and Nyquist frequency "
                f"({nyquist_freq} Hz), got {cutoff_frequency} Hz"
            )
        
        normalized_cutoff = cutoff_frequency / nyquist_freq
        
    elif filter_type in ("bandpass", "bandstop"):
        if not isinstance(cutoff_frequency, tuple) or len(cutoff_frequency) != 2:
            raise ValidationError(
                f"{filter_type} filter requires tuple of (low, high) frequencies"
            )
        
        low_freq, high_freq = cutoff_frequency
        
        if low_freq >= high_freq:
            raise ValidationError(
                f"Low frequency must be less than high frequency, "
                f"got {low_freq} >= {high_freq}"
            )
        
        if low_freq <= 0 or high_freq >= nyquist_freq:
            raise ValidationError(
                f"Frequencies must be between 0 and Nyquist frequency "
                f"({nyquist_freq} Hz), got ({low_freq}, {high_freq})"
            )
        
        normalized_cutoff = (low_freq / nyquist_freq, high_freq / nyquist_freq)
    
    else:
        raise ValidationError(f"Unknown filter type: {filter_type}")
    
    # Design filter
    try:
        if method == "butter":
            b, a = signal.butter(filter_order, normalized_cutoff, btype=filter_type)
        elif method == "chebyshev1":
            ripple_db = 0.5  # 0.5 dB passband ripple
            b, a = signal.cheby1(filter_order, ripple_db, normalized_cutoff, btype=filter_type)
        elif method == "chebyshev2":
            attenuation_db = 40  # 40 dB stopband attenuation
            b, a = signal.cheby2(filter_order, attenuation_db, normalized_cutoff, btype=filter_type)
        elif method == "elliptic":
            ripple_db = 0.5  # 0.5 dB passband ripple
            attenuation_db = 40  # 40 dB stopband attenuation
            b, a = signal.ellip(filter_order, ripple_db, attenuation_db, normalized_cutoff, btype=filter_type)
        elif method == "bessel":
            b, a = signal.bessel(filter_order, normalized_cutoff, btype=filter_type, norm='phase')
        else:
            raise ValidationError(f"Unknown filter method: {method}")
    
    except Exception as e:
        raise ValidationError(f"Filter design failed: {str(e)}")
    
    # Apply filter
    try:
        if zero_phase:
            # Zero-phase filtering (no phase distortion)
            filtered_values = signal.filtfilt(b, a, clean_values)
        else:
            # Standard filtering (may have phase shift)
            filtered_values = signal.lfilter(b, a, clean_values)
    
    except Exception as e:
        raise ValidationError(f"Filter application failed: {str(e)}")
    
    logger.info(
        "filter_applied",
        filter_type=filter_type,
        cutoff_frequency=cutoff_frequency,
        method=method,
        order=filter_order,
        n_points=len(values),
        zero_phase=zero_phase,
    )
    
    return FilterResult(
        filtered_values=filtered_values,
        original_values=clean_values,
        filter_type=filter_type,
        cutoff_frequency=cutoff_frequency,
        sampling_rate=sampling_rate,
        filter_order=filter_order,
        method=method,
    )


def apply_lowpass_filter(
    values: NDArray[np.float64],
    sampling_rate: float,
    cutoff_frequency: float,
    filter_order: int = 4,
    method: FilterMethod = "butter",
) -> FilterResult:
    """
    Apply lowpass filter to remove high-frequency noise.
    
    Args:
        values: Input signal values
        sampling_rate: Sampling rate in Hz
        cutoff_frequency: Cutoff frequency in Hz (frequencies above this are attenuated)
        filter_order: Filter order (default: 4)
        method: Filter design method (default: 'butter')
        
    Returns:
        FilterResult with filtered signal
    """
    return apply_filter(
        values=values,
        sampling_rate=sampling_rate,
        filter_type="lowpass",
        cutoff_frequency=cutoff_frequency,
        filter_order=filter_order,
        method=method,
    )


def apply_highpass_filter(
    values: NDArray[np.float64],
    sampling_rate: float,
    cutoff_frequency: float,
    filter_order: int = 4,
    method: FilterMethod = "butter",
) -> FilterResult:
    """
    Apply highpass filter to remove low-frequency trends.
    
    Args:
        values: Input signal values
        sampling_rate: Sampling rate in Hz
        cutoff_frequency: Cutoff frequency in Hz (frequencies below this are attenuated)
        filter_order: Filter order (default: 4)
        method: Filter design method (default: 'butter')
        
    Returns:
        FilterResult with filtered signal
    """
    return apply_filter(
        values=values,
        sampling_rate=sampling_rate,
        filter_type="highpass",
        cutoff_frequency=cutoff_frequency,
        filter_order=filter_order,
        method=method,
    )


def apply_bandpass_filter(
    values: NDArray[np.float64],
    sampling_rate: float,
    low_frequency: float,
    high_frequency: float,
    filter_order: int = 4,
    method: FilterMethod = "butter",
) -> FilterResult:
    """
    Apply bandpass filter to isolate a specific frequency range.
    
    Args:
        values: Input signal values
        sampling_rate: Sampling rate in Hz
        low_frequency: Lower cutoff frequency in Hz
        high_frequency: Upper cutoff frequency in Hz
        filter_order: Filter order (default: 4)
        method: Filter design method (default: 'butter')
        
    Returns:
        FilterResult with filtered signal
    """
    return apply_filter(
        values=values,
        sampling_rate=sampling_rate,
        filter_type="bandpass",
        cutoff_frequency=(low_frequency, high_frequency),
        filter_order=filter_order,
        method=method,
    )


def apply_bandstop_filter(
    values: NDArray[np.float64],
    sampling_rate: float,
    low_frequency: float,
    high_frequency: float,
    filter_order: int = 4,
    method: FilterMethod = "butter",
) -> FilterResult:
    """
    Apply bandstop (notch) filter to remove a specific frequency range.
    
    Useful for removing interference at specific frequencies (e.g., 50/60 Hz power line noise).
    
    Args:
        values: Input signal values
        sampling_rate: Sampling rate in Hz
        low_frequency: Lower cutoff frequency in Hz
        high_frequency: Upper cutoff frequency in Hz
        filter_order: Filter order (default: 4)
        method: Filter design method (default: 'butter')
        
    Returns:
        FilterResult with filtered signal
    """
    return apply_filter(
        values=values,
        sampling_rate=sampling_rate,
        filter_type="bandstop",
        cutoff_frequency=(low_frequency, high_frequency),
        filter_order=filter_order,
        method=method,
    )
