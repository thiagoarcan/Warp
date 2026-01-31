"""
Data Filtering System for Streaming - Platform Base v2.0

Implements real-time filtering for streaming time series data:
- Quality filters (outlier detection, noise reduction)
- Temporal filters (time windows, rate limiting)
- Value filters (range checks, threshold detection)
- Conditional filters (custom expressions)
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any

import numpy as np


try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


class FilterAction(Enum):
    """Actions to take when filter condition is met"""
    PASS = "pass"          # Let data through unchanged
    BLOCK = "block"        # Block/reject the data point
    MODIFY = "modify"      # Modify the data point
    FLAG = "flag"          # Add flag but pass data through
    INTERPOLATE = "interpolate"  # Replace with interpolated value


class FilterResult:
    """Result of applying a filter to data"""

    def __init__(self, action: FilterAction, value: float | None = None,
                 flag: str | None = None, confidence: float = 1.0,
                 metadata: dict[str, Any] | None = None):
        self.action = action
        self.value = value  # Modified value if action is MODIFY
        self.flag = flag    # Flag description if action is FLAG
        self.confidence = confidence  # Confidence in filter decision
        self.metadata = metadata or {}


class StreamFilter(ABC):
    """Base class for all streaming filters"""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.statistics = {
            "total_processed": 0,
            "passed": 0,
            "blocked": 0,
            "modified": 0,
            "flagged": 0,
        }

    @abstractmethod
    def apply(self, timestamp: float, value: float,
              context: dict[str, Any] | None = None) -> FilterResult:
        """Apply filter to a data point"""

    @abstractmethod
    def reset(self):
        """Reset filter state"""

    def update_statistics(self, result: FilterResult):
        """Update filter statistics"""
        self.statistics["total_processed"] += 1

        if result.action == FilterAction.PASS:
            self.statistics["passed"] += 1
        elif result.action == FilterAction.BLOCK:
            self.statistics["blocked"] += 1
        elif result.action == FilterAction.MODIFY:
            self.statistics["modified"] += 1
        elif result.action == FilterAction.FLAG:
            self.statistics["flagged"] += 1

    def get_efficiency(self) -> float:
        """Get filter pass-through efficiency (0.0 to 1.0)"""
        total = self.statistics["total_processed"]
        if total == 0:
            return 1.0
        return (self.statistics["passed"] + self.statistics["flagged"]) / total


class QualityFilter(StreamFilter):
    """
    Quality-based filter for outlier detection and noise reduction.

    Methods:
    - Statistical outlier detection (z-score, IQR)
    - Moving window outlier detection
    - Noise level filtering
    - Rate of change limiting
    """

    def __init__(self, name: str = "quality_filter",
                 outlier_method: str = "zscore",
                 outlier_threshold: float = 3.0,
                 window_size: int = 20,
                 noise_threshold: float | None = None,
                 max_rate_change: float | None = None,
                 enabled: bool = True):
        super().__init__(name, enabled)

        self.outlier_method = outlier_method
        self.outlier_threshold = outlier_threshold
        self.window_size = window_size
        self.noise_threshold = noise_threshold
        self.max_rate_change = max_rate_change

        # Moving window for statistics
        self._window_values: list[float] = []
        self._window_times: list[float] = []
        self._last_value: float | None = None
        self._last_time: float | None = None

    def apply(self, timestamp: float, value: float,
              context: dict[str, Any] | None = None) -> FilterResult:
        if not self.enabled:
            return FilterResult(FilterAction.PASS)

        # Add to moving window
        self._window_values.append(value)
        self._window_times.append(timestamp)

        # Maintain window size
        if len(self._window_values) > self.window_size:
            self._window_values.pop(0)
            self._window_times.pop(0)

        # Skip filtering until we have enough data
        if len(self._window_values) < 3:
            self._last_value = value
            self._last_time = timestamp
            return FilterResult(FilterAction.PASS)

        # Check rate of change limit
        if self.max_rate_change is not None and self._last_value is not None:
            dt = timestamp - self._last_time
            if dt > 0:
                rate = abs(value - self._last_value) / dt
                if rate > self.max_rate_change:
                    return FilterResult(
                        FilterAction.BLOCK,
                        flag=f"Rate of change {rate:.3f} exceeds limit {self.max_rate_change}",
                    )

        # Outlier detection
        if self.outlier_method == "zscore":
            result = self._zscore_outlier_detection(value)
        elif self.outlier_method == "iqr":
            result = self._iqr_outlier_detection(value)
        elif self.outlier_method == "modified_zscore":
            result = self._modified_zscore_outlier_detection(value)
        else:
            result = FilterResult(FilterAction.PASS)

        # Noise filtering
        if result.action == FilterAction.PASS and self.noise_threshold is not None:
            noise_result = self._noise_filtering(value)
            if noise_result.action != FilterAction.PASS:
                result = noise_result

        self._last_value = value
        self._last_time = timestamp

        return result

    def _zscore_outlier_detection(self, value: float) -> FilterResult:
        """Z-score based outlier detection"""
        values = np.array(self._window_values)
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return FilterResult(FilterAction.PASS)

        zscore = abs(value - mean) / std

        if zscore > self.outlier_threshold:
            return FilterResult(
                FilterAction.BLOCK,
                flag=f"Z-score outlier: {zscore:.2f} > {self.outlier_threshold}",
            )

        return FilterResult(FilterAction.PASS)

    def _iqr_outlier_detection(self, value: float) -> FilterResult:
        """IQR-based outlier detection"""
        values = np.array(self._window_values)
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        if iqr == 0:
            return FilterResult(FilterAction.PASS)

        lower_bound = q1 - self.outlier_threshold * iqr
        upper_bound = q3 + self.outlier_threshold * iqr

        if value < lower_bound or value > upper_bound:
            return FilterResult(
                FilterAction.BLOCK,
                flag=f"IQR outlier: {value:.3f} outside [{lower_bound:.3f}, {upper_bound:.3f}]",
            )

        return FilterResult(FilterAction.PASS)

    def _modified_zscore_outlier_detection(self, value: float) -> FilterResult:
        """Modified Z-score using median absolute deviation"""
        values = np.array(self._window_values)
        median = np.median(values)
        mad = np.median(np.abs(values - median))

        if mad == 0:
            return FilterResult(FilterAction.PASS)

        modified_zscore = 0.6745 * (value - median) / mad

        if abs(modified_zscore) > self.outlier_threshold:
            return FilterResult(
                FilterAction.BLOCK,
                flag=f"Modified Z-score outlier: {modified_zscore:.2f} > {self.outlier_threshold}",
            )

        return FilterResult(FilterAction.PASS)

    def _noise_filtering(self, value: float) -> FilterResult:
        """Filter based on noise threshold"""
        if len(self._window_values) < 2:
            return FilterResult(FilterAction.PASS)

        # Calculate moving average
        recent_values = self._window_values[-min(5, len(self._window_values)):]
        moving_avg = np.mean(recent_values)
        noise_level = abs(value - moving_avg)

        if noise_level < self.noise_threshold:
            # Replace with moving average if noise is too small
            return FilterResult(
                FilterAction.MODIFY,
                value=moving_avg,
                flag=f"Noise filtered: {noise_level:.3f} < {self.noise_threshold}",
            )

        return FilterResult(FilterAction.PASS)

    def reset(self):
        """Reset filter state"""
        self._window_values.clear()
        self._window_times.clear()
        self._last_value = None
        self._last_time = None
        self.statistics = dict.fromkeys(self.statistics.keys(), 0)


class TemporalFilter(StreamFilter):
    """
    Temporal-based filter for time window and rate management.

    Features:
    - Time window filtering
    - Rate limiting
    - Minimum/maximum time intervals
    - Time gap detection
    """

    def __init__(self, name: str = "temporal_filter",
                 min_interval: float | None = None,
                 max_interval: float | None = None,
                 rate_limit: float | None = None,
                 time_window: tuple[float, float] | None = None,
                 enabled: bool = True):
        super().__init__(name, enabled)

        self.min_interval = min_interval  # Minimum seconds between points
        self.max_interval = max_interval  # Maximum seconds between points
        self.rate_limit = rate_limit      # Maximum points per second
        self.time_window = time_window    # (start_hour, end_hour) in 24h format

        self._last_timestamp: float | None = None
        self._rate_window_start: float | None = None
        self._rate_window_count = 0
        self._rate_window_duration = 1.0  # 1 second window for rate limiting

    def apply(self, timestamp: float, value: float,
              context: dict[str, Any] | None = None) -> FilterResult:
        if not self.enabled:
            return FilterResult(FilterAction.PASS)

        # Time window check (e.g., only accept data during business hours)
        if self.time_window is not None:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            hour = dt.hour + dt.minute / 60.0

            start_hour, end_hour = self.time_window
            if not (start_hour <= hour <= end_hour):
                return FilterResult(
                    FilterAction.BLOCK,
                    flag=f"Outside time window: {hour:.1f}h not in [{start_hour}-{end_hour}]",
                )

        # Check intervals
        if self._last_timestamp is not None:
            interval = timestamp - self._last_timestamp

            # Minimum interval check
            if self.min_interval is not None and interval < self.min_interval:
                return FilterResult(
                    FilterAction.BLOCK,
                    flag=f"Too frequent: {interval:.3f}s < {self.min_interval}s",
                )

            # Maximum interval check (detect gaps)
            if self.max_interval is not None and interval > self.max_interval:
                return FilterResult(
                    FilterAction.FLAG,
                    flag=f"Large time gap: {interval:.3f}s > {self.max_interval}s",
                )

        # Rate limiting check
        if self.rate_limit is not None:
            current_time = time.time()

            # Initialize or reset rate window
            if (self._rate_window_start is None or
                current_time - self._rate_window_start >= self._rate_window_duration):
                self._rate_window_start = current_time
                self._rate_window_count = 0

            self._rate_window_count += 1

            # Check if rate limit exceeded
            elapsed = current_time - self._rate_window_start
            current_rate = self._rate_window_count / max(elapsed, 0.001)

            if current_rate > self.rate_limit:
                return FilterResult(
                    FilterAction.BLOCK,
                    flag=f"Rate limit exceeded: {current_rate:.1f} > {self.rate_limit} pts/s",
                )

        self._last_timestamp = timestamp
        return FilterResult(FilterAction.PASS)

    def reset(self):
        """Reset filter state"""
        self._last_timestamp = None
        self._rate_window_start = None
        self._rate_window_count = 0
        self.statistics = dict.fromkeys(self.statistics.keys(), 0)


class ValueFilter(StreamFilter):
    """
    Value-based filter for range checks and thresholds.

    Features:
    - Min/max range filtering
    - Threshold detection
    - Value change detection
    - Custom validation functions
    """

    def __init__(self, name: str = "value_filter",
                 min_value: float | None = None,
                 max_value: float | None = None,
                 valid_ranges: list[tuple[float, float]] | None = None,
                 threshold_alerts: dict[str, float] | None = None,
                 max_change: float | None = None,
                 validation_func: Callable[[float], bool] | None = None,
                 enabled: bool = True):
        super().__init__(name, enabled)

        self.min_value = min_value
        self.max_value = max_value
        self.valid_ranges = valid_ranges or []
        self.threshold_alerts = threshold_alerts or {}
        self.max_change = max_change
        self.validation_func = validation_func

        self._last_value: float | None = None

    def apply(self, timestamp: float, value: float,
              context: dict[str, Any] | None = None) -> FilterResult:
        if not self.enabled:
            return FilterResult(FilterAction.PASS)

        # Basic range check
        if self.min_value is not None and value < self.min_value:
            return FilterResult(
                FilterAction.BLOCK,
                flag=f"Below minimum: {value:.3f} < {self.min_value}",
            )

        if self.max_value is not None and value > self.max_value:
            return FilterResult(
                FilterAction.BLOCK,
                flag=f"Above maximum: {value:.3f} > {self.max_value}",
            )

        # Valid ranges check
        if self.valid_ranges:
            in_valid_range = any(
                min_val <= value <= max_val
                for min_val, max_val in self.valid_ranges
            )
            if not in_valid_range:
                return FilterResult(
                    FilterAction.BLOCK,
                    flag=f"Outside valid ranges: {value:.3f} not in {self.valid_ranges}",
                )

        # Threshold alerts
        for alert_name, threshold in self.threshold_alerts.items():
            if value >= threshold:
                return FilterResult(
                    FilterAction.FLAG,
                    flag=f"{alert_name} threshold exceeded: {value:.3f} >= {threshold}",
                )

        # Maximum change check
        if self.max_change is not None and self._last_value is not None:
            change = abs(value - self._last_value)
            if change > self.max_change:
                return FilterResult(
                    FilterAction.BLOCK,
                    flag=f"Excessive change: {change:.3f} > {self.max_change}",
                )

        # Custom validation function
        if self.validation_func is not None:
            try:
                if not self.validation_func(value):
                    return FilterResult(
                        FilterAction.BLOCK,
                        flag="Failed custom validation",
                    )
            except Exception as e:
                return FilterResult(
                    FilterAction.FLAG,
                    flag=f"Validation error: {e!s}",
                )

        self._last_value = value
        return FilterResult(FilterAction.PASS)

    def reset(self):
        """Reset filter state"""
        self._last_value = None
        self.statistics = dict.fromkeys(self.statistics.keys(), 0)


class ConditionalFilter(StreamFilter):
    """
    Conditional filter using custom expressions.

    Allows complex filtering logic using Python expressions
    with access to current and historical data.
    """

    def __init__(self, name: str, condition: str,
                 action: FilterAction = FilterAction.BLOCK,
                 history_size: int = 10,
                 enabled: bool = True):
        super().__init__(name, enabled)

        self.condition = condition
        self.action = action
        self.history_size = history_size

        # Compile condition
        self._compiled_condition = None
        self._compile_condition()

        # History for condition evaluation
        self._value_history: list[float] = []
        self._time_history: list[float] = []

    def _compile_condition(self):
        """Compile condition string to callable"""
        try:
            # Safe evaluation context
            safe_dict = {
                "__builtins__": {},
                "abs": abs, "min": min, "max": max, "len": len,
                "sum": sum, "avg": lambda x: sum(x) / len(x) if x else 0,
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "sqrt": np.sqrt, "log": np.log, "exp": np.exp,
                "pi": np.pi, "e": np.e,
            }

            # Create function that has access to current value, time, and history
            func_code = f"lambda t, value, t_hist, v_hist: {self.condition}"
            self._compiled_condition = eval(func_code, safe_dict)

        except Exception as e:
            logger.exception("conditional_filter_compile_error",
                        condition=self.condition, error=str(e))
            self._compiled_condition = None

    def apply(self, timestamp: float, value: float,
              context: dict[str, Any] | None = None) -> FilterResult:
        if not self.enabled or self._compiled_condition is None:
            return FilterResult(FilterAction.PASS)

        # Update history
        self._value_history.append(value)
        self._time_history.append(timestamp)

        # Maintain history size
        if len(self._value_history) > self.history_size:
            self._value_history.pop(0)
            self._time_history.pop(0)

        # Evaluate condition
        try:
            condition_met = self._compiled_condition(
                timestamp, value,
                self._time_history.copy(),
                self._value_history.copy(),
            )

            if condition_met:
                return FilterResult(
                    self.action,
                    flag=f"Condition met: {self.condition}",
                )
            return FilterResult(FilterAction.PASS)

        except Exception as e:
            return FilterResult(
                FilterAction.FLAG,
                flag=f"Condition evaluation error: {e!s}",
            )

    def reset(self):
        """Reset filter state"""
        self._value_history.clear()
        self._time_history.clear()
        self.statistics = dict.fromkeys(self.statistics.keys(), 0)


class FilterChain:
    """
    Chain of filters applied sequentially to streaming data.

    Processes data through multiple filters in order,
    with early termination if any filter blocks the data.
    """

    def __init__(self, name: str = "filter_chain"):
        self.name = name
        self.filters: list[StreamFilter] = []
        self.statistics = {
            "total_processed": 0,
            "passed": 0,
            "blocked": 0,
            "modified": 0,
            "flagged": 0,
        }

    def add_filter(self, filter_instance: StreamFilter):
        """Add filter to the chain"""
        self.filters.append(filter_instance)
        logger.debug("filter_added_to_chain",
                    filter_name=filter_instance.name,
                    chain_name=self.name)

    def remove_filter(self, filter_name: str) -> bool:
        """Remove filter from chain by name"""
        for i, f in enumerate(self.filters):
            if f.name == filter_name:
                self.filters.pop(i)
                logger.debug("filter_removed_from_chain",
                           filter_name=filter_name,
                           chain_name=self.name)
                return True
        return False

    def process_point(self, timestamp: float, value: float,
                     context: dict[str, Any] | None = None) -> FilterResult:
        """Process a single data point through the filter chain"""
        self.statistics["total_processed"] += 1

        current_value = value
        flags = []
        final_action = FilterAction.PASS

        for filter_instance in self.filters:
            if not filter_instance.enabled:
                continue

            result = filter_instance.apply(timestamp, current_value, context)
            filter_instance.update_statistics(result)

            # Handle filter result
            if result.action == FilterAction.BLOCK:
                final_action = FilterAction.BLOCK
                if result.flag:
                    flags.append(f"{filter_instance.name}: {result.flag}")
                break  # Stop processing - data blocked

            if result.action == FilterAction.MODIFY:
                current_value = result.value
                final_action = FilterAction.MODIFY
                if result.flag:
                    flags.append(f"{filter_instance.name}: {result.flag}")

            elif result.action == FilterAction.FLAG:
                if result.flag:
                    flags.append(f"{filter_instance.name}: {result.flag}")
                # Continue processing

            elif result.action == FilterAction.INTERPOLATE:
                # Could implement interpolation logic here
                current_value = result.value or current_value
                final_action = FilterAction.MODIFY
                if result.flag:
                    flags.append(f"{filter_instance.name}: {result.flag}")

        # Update chain statistics
        if final_action == FilterAction.PASS:
            self.statistics["passed"] += 1
        elif final_action == FilterAction.BLOCK:
            self.statistics["blocked"] += 1
        elif final_action == FilterAction.MODIFY:
            self.statistics["modified"] += 1

        if flags:
            self.statistics["flagged"] += 1

        return FilterResult(
            action=final_action,
            value=current_value if final_action == FilterAction.MODIFY else value,
            flag="; ".join(flags) if flags else None,
        )

    def process_batch(self, timestamps: np.ndarray, values: np.ndarray,
                     context: dict[str, Any] | None = None) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """Process a batch of data points"""
        passed_times = []
        passed_values = []
        flags = []

        for t, v in zip(timestamps, values, strict=False):
            result = self.process_point(t, v, context)

            if result.action in [FilterAction.PASS, FilterAction.MODIFY, FilterAction.FLAG]:
                passed_times.append(t)
                passed_values.append(result.value if result.value is not None else v)
                flags.append(result.flag or "")

        return (np.array(passed_times),
                np.array(passed_values),
                flags)

    def reset_all_filters(self):
        """Reset all filters in the chain"""
        for filter_instance in self.filters:
            filter_instance.reset()
        self.statistics = dict.fromkeys(self.statistics.keys(), 0)

    def get_filter_by_name(self, name: str) -> StreamFilter | None:
        """Get filter by name"""
        for filter_instance in self.filters:
            if filter_instance.name == name:
                return filter_instance
        return None

    def get_summary_statistics(self) -> dict[str, Any]:
        """Get summary statistics for the entire chain"""
        summary = {
            "chain_stats": self.statistics.copy(),
            "filter_stats": {},
        }

        for filter_instance in self.filters:
            summary["filter_stats"][filter_instance.name] = {
                "enabled": filter_instance.enabled,
                "efficiency": filter_instance.get_efficiency(),
                "statistics": filter_instance.statistics.copy(),
            }

        return summary


# Factory functions for common filter configurations
def create_quality_filter(outlier_threshold: float = 3.0,
                         window_size: int = 20) -> QualityFilter:
    """Create a standard quality filter"""
    return QualityFilter(
        name="standard_quality",
        outlier_method="zscore",
        outlier_threshold=outlier_threshold,
        window_size=window_size,
    )


def create_range_filter(min_value: float, max_value: float) -> ValueFilter:
    """Create a simple range filter"""
    return ValueFilter(
        name="range_filter",
        min_value=min_value,
        max_value=max_value,
    )


def create_rate_limit_filter(max_rate: float) -> TemporalFilter:
    """Create a rate limiting filter"""
    return TemporalFilter(
        name="rate_limiter",
        rate_limit=max_rate,
    )


def create_business_hours_filter(start_hour: int = 8, end_hour: int = 18) -> TemporalFilter:
    """Create a business hours filter"""
    return TemporalFilter(
        name="business_hours",
        time_window=(start_hour, end_hour),
    )


def create_standard_filter_chain() -> FilterChain:
    """Create a standard filter chain with common filters"""
    chain = FilterChain("standard_chain")

    # Add basic quality filter
    chain.add_filter(create_quality_filter())

    # Add rate limiting
    chain.add_filter(create_rate_limit_filter(100.0))  # 100 points per second max

    return chain
