"""
Tests for viz/datetime_axis.py - DateTime Axis System

Tests the datetime axis for time series plots.
"""

from datetime import datetime, timedelta

import numpy as np
import pytest

# Skip if pyqtgraph not available
pg = pytest.importorskip("pyqtgraph")


class TestDateTimeFormat:
    """Tests for DateTimeFormat enum."""
    
    def test_all_formats_exist(self):
        """All datetime formats should exist."""
        from platform_base.viz.datetime_axis import DateTimeFormat
        
        assert hasattr(DateTimeFormat, "ISO")
        assert hasattr(DateTimeFormat, "LOCALE")
        assert hasattr(DateTimeFormat, "CUSTOM")
        assert hasattr(DateTimeFormat, "RELATIVE")


class TestZoomLevel:
    """Tests for ZoomLevel enum."""
    
    def test_all_levels_exist(self):
        """All zoom levels should exist."""
        from platform_base.viz.datetime_axis import ZoomLevel
        
        assert hasattr(ZoomLevel, "YEARS")
        assert hasattr(ZoomLevel, "MONTHS")
        assert hasattr(ZoomLevel, "DAYS")
        assert hasattr(ZoomLevel, "HOURS")
        assert hasattr(ZoomLevel, "MINUTES")
        assert hasattr(ZoomLevel, "SECONDS")
        assert hasattr(ZoomLevel, "MILLISECONDS")


class TestTimestampConversion:
    """Tests for timestamp conversion utilities."""
    
    def test_datetime_to_timestamp(self):
        """Should convert datetime to timestamp."""
        from platform_base.viz.datetime_axis import datetime_to_timestamp
        
        dt = datetime(2024, 1, 1, 12, 0, 0)
        ts = datetime_to_timestamp(dt)
        
        assert isinstance(ts, float)
        assert ts > 0
    
    def test_timestamp_to_datetime(self):
        """Should convert timestamp to datetime."""
        from platform_base.viz.datetime_axis import timestamp_to_datetime
        
        ts = 1704110400.0  # 2024-01-01 12:00:00 UTC
        dt = timestamp_to_datetime(ts)
        
        assert isinstance(dt, datetime)
    
    def test_round_trip_conversion(self):
        """Conversion should be reversible."""
        from platform_base.viz.datetime_axis import (
            datetime_to_timestamp,
            timestamp_to_datetime,
        )
        
        original = datetime(2024, 6, 15, 10, 30, 45)
        ts = datetime_to_timestamp(original)
        result = timestamp_to_datetime(ts)
        
        # Should be very close (might have microsecond differences)
        assert abs((result - original).total_seconds()) < 1


class TestDetectZoomLevel:
    """Tests for detect_zoom_level function."""
    
    def test_detect_years(self):
        """Should detect years level for large ranges."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 400 days range
        level = detect_zoom_level(400 * 24 * 3600)
        assert level == ZoomLevel.YEARS
    
    def test_detect_months(self):
        """Should detect months level for medium ranges."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 60 days range
        level = detect_zoom_level(60 * 24 * 3600)
        assert level == ZoomLevel.MONTHS
    
    def test_detect_days(self):
        """Should detect days level."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 5 days range
        level = detect_zoom_level(5 * 24 * 3600)
        assert level == ZoomLevel.DAYS
    
    def test_detect_hours(self):
        """Should detect hours level."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 12 hours range
        level = detect_zoom_level(12 * 3600)
        assert level == ZoomLevel.HOURS
    
    def test_detect_minutes(self):
        """Should detect minutes level."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 30 minutes range
        level = detect_zoom_level(30 * 60)
        assert level == ZoomLevel.MINUTES
    
    def test_detect_seconds(self):
        """Should detect seconds level."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 30 seconds range
        level = detect_zoom_level(30)
        assert level == ZoomLevel.SECONDS
    
    def test_detect_milliseconds(self):
        """Should detect milliseconds level."""
        from platform_base.viz.datetime_axis import ZoomLevel, detect_zoom_level

        # 0.5 seconds range
        level = detect_zoom_level(0.5)
        assert level == ZoomLevel.MILLISECONDS


class TestDateTimeAxisItem:
    """Tests for DateTimeAxisItem."""
    
    def test_create_axis(self, qtbot):
        """Should be able to create datetime axis."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        
        axis = DateTimeAxisItem(orientation='bottom')
        
        assert axis is not None
    
    def test_set_format_mode(self, qtbot):
        """Should be able to set format mode via property."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem, DateTimeFormat
        
        axis = DateTimeAxisItem()
        axis.format_mode = DateTimeFormat.ISO
        
        assert axis.format_mode == DateTimeFormat.ISO
    
    def test_set_custom_format(self, qtbot):
        """Should be able to set custom format via property."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem, DateTimeFormat
        
        axis = DateTimeAxisItem()
        axis.format_mode = DateTimeFormat.CUSTOM
        axis.custom_format = "%Y-%m-%d"
        
        assert axis.format_mode == DateTimeFormat.CUSTOM
        assert axis.custom_format == "%Y-%m-%d"
    
    def test_epoch_property(self, qtbot):
        """Should be able to get and set epoch."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        
        axis = DateTimeAxisItem()
        new_epoch = datetime(2024, 1, 1)
        axis.epoch = new_epoch
        
        assert axis.epoch == new_epoch
    
    def test_tick_strings(self, qtbot):
        """tickStrings should return formatted strings."""
        from platform_base.viz.datetime_axis import DateTimeAxisItem
        
        axis = DateTimeAxisItem()
        
        values = [1704110400.0, 1704196800.0]  # Two timestamps
        strings = axis.tickStrings(values, scale=1, spacing=86400)
        
        assert len(strings) == len(values)
        assert all(isinstance(s, str) for s in strings)


class TestDateTimePlotWidget:
    """Tests for DateTimePlotWidget."""
    
    def test_create_widget(self, qtbot):
        """Should create widget with datetime axis."""
        from platform_base.viz.datetime_axis import DateTimePlotWidget
        
        widget = DateTimePlotWidget()
        qtbot.addWidget(widget)
        
        assert widget is not None
        assert widget.datetime_axis is not None
    
    def test_set_epoch(self, qtbot):
        """Should be able to set epoch via widget."""
        from platform_base.viz.datetime_axis import DateTimePlotWidget
        
        widget = DateTimePlotWidget()
        qtbot.addWidget(widget)
        
        new_epoch = datetime(2024, 6, 1)
        widget.set_epoch(new_epoch)
        
        assert widget.datetime_axis.epoch == new_epoch
    
    def test_set_format_mode(self, qtbot):
        """Should be able to set format mode via widget."""
        from platform_base.viz.datetime_axis import DateTimeFormat, DateTimePlotWidget
        
        widget = DateTimePlotWidget()
        qtbot.addWidget(widget)
        
        widget.set_format_mode(DateTimeFormat.LOCALE)
        
        assert widget.datetime_axis.format_mode == DateTimeFormat.LOCALE
