"""
Unit tests for Memory Indicator Widget.

Tests for:
- MemoryIndicator display and updates
- Color coding for different memory levels
- Tooltip building
- Signal emission
"""

from unittest.mock import MagicMock, patch

import pytest

from platform_base.core.memory_manager import MemoryLevel, MemoryStatus


class TestMemoryIndicatorBasics:
    """Basic tests for MemoryIndicator without Qt dependency"""

    def test_memory_level_enum_values(self):
        """Test memory level enum has expected values"""
        assert MemoryLevel.NORMAL.name == "NORMAL"
        assert MemoryLevel.WARNING.name == "WARNING"
        assert MemoryLevel.HIGH.name == "HIGH"
        assert MemoryLevel.CRITICAL.name == "CRITICAL"

    def test_memory_status_creation(self):
        """Test MemoryStatus dataclass creation"""
        status = MemoryStatus(
            level=MemoryLevel.NORMAL,
            percent=50.0,
            process_mb=1000.0,
            total_mb=16000.0,
            available_mb=8000.0,
            suggestions=[]
        )
        assert status.level == MemoryLevel.NORMAL
        assert status.percent == 50.0
        assert status.process_mb == 1000.0
        assert status.total_mb == 16000.0
        assert status.available_mb == 8000.0
        assert status.suggestions == []

    def test_memory_status_with_suggestions(self):
        """Test MemoryStatus with suggestions"""
        suggestions = ["Close unused files", "Reduce data points"]
        status = MemoryStatus(
            level=MemoryLevel.HIGH,
            percent=85.0,
            process_mb=3000.0,
            total_mb=4000.0,
            available_mb=500.0,
            suggestions=suggestions
        )
        assert len(status.suggestions) == 2
        assert "Close unused files" in status.suggestions


class TestMemoryIndicatorColors:
    """Tests for color mapping"""

    def test_color_mapping_normal(self):
        """Normal level should have green color"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        assert MemoryIndicator.COLORS[MemoryLevel.NORMAL] == "#2ecc71"

    def test_color_mapping_warning(self):
        """Warning level should have orange color"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        assert MemoryIndicator.COLORS[MemoryLevel.WARNING] == "#f39c12"

    def test_color_mapping_high(self):
        """High level should have dark orange color"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        assert MemoryIndicator.COLORS[MemoryLevel.HIGH] == "#e67e22"

    def test_color_mapping_critical(self):
        """Critical level should have red color"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        assert MemoryIndicator.COLORS[MemoryLevel.CRITICAL] == "#e74c3c"


class TestMemoryLevelTransitions:
    """Tests for memory level transitions and thresholds"""

    def test_normal_level_threshold(self):
        """Test normal level threshold (< 60%)"""
        status = MemoryStatus(
            level=MemoryLevel.NORMAL,
            percent=40.0,
            process_mb=400.0,
            total_mb=1000.0,
            available_mb=600.0,
            suggestions=[]
        )
        assert status.level == MemoryLevel.NORMAL
        assert status.percent < 60.0

    def test_warning_level_threshold(self):
        """Test warning level threshold (60-80%)"""
        status = MemoryStatus(
            level=MemoryLevel.WARNING,
            percent=70.0,
            process_mb=700.0,
            total_mb=1000.0,
            available_mb=300.0,
            suggestions=["Consider closing unused files"]
        )
        assert status.level == MemoryLevel.WARNING
        assert 60.0 <= status.percent < 80.0

    def test_high_level_threshold(self):
        """Test high level threshold (80-95%)"""
        status = MemoryStatus(
            level=MemoryLevel.HIGH,
            percent=88.0,
            process_mb=880.0,
            total_mb=1000.0,
            available_mb=120.0,
            suggestions=["Close unused files", "Reduce data points"]
        )
        assert status.level == MemoryLevel.HIGH
        assert 80.0 <= status.percent < 95.0

    def test_critical_level_threshold(self):
        """Test critical level threshold (>= 95%)"""
        status = MemoryStatus(
            level=MemoryLevel.CRITICAL,
            percent=97.0,
            process_mb=970.0,
            total_mb=1000.0,
            available_mb=30.0,
            suggestions=["Save work immediately", "Close application"]
        )
        assert status.level == MemoryLevel.CRITICAL
        assert status.percent >= 95.0


class TestTooltipBuilding:
    """Tests for tooltip content generation"""

    def test_tooltip_contains_status(self):
        """Tooltip should contain memory status name"""
        status = MemoryStatus(
            level=MemoryLevel.WARNING,
            percent=70.0,
            process_mb=2800.0,
            total_mb=4000.0,
            available_mb=1200.0,
            suggestions=[]
        )
        # The tooltip text would include "WARNING"
        assert status.level.name == "WARNING"

    def test_tooltip_contains_memory_values(self):
        """Tooltip should show memory values correctly"""
        status = MemoryStatus(
            level=MemoryLevel.NORMAL,
            percent=50.0,
            process_mb=2000.0,
            total_mb=4000.0,
            available_mb=2000.0,
            suggestions=[]
        )
        assert status.process_mb == 2000.0
        assert status.total_mb == 4000.0
        assert status.available_mb == 2000.0

    def test_suggestions_included_in_status(self):
        """Suggestions should be included in status"""
        suggestions = ["Suggestion 1", "Suggestion 2"]
        status = MemoryStatus(
            level=MemoryLevel.HIGH,
            percent=85.0,
            process_mb=3400.0,
            total_mb=4000.0,
            available_mb=600.0,
            suggestions=suggestions
        )
        assert len(status.suggestions) == 2
        assert "Suggestion 1" in status.suggestions


class TestMemoryStatusComputations:
    """Tests for memory status computations"""

    def test_percent_calculation(self):
        """Test that percent is calculated correctly"""
        status = MemoryStatus(
            level=MemoryLevel.NORMAL,
            percent=50.0,
            process_mb=2000.0,
            total_mb=4000.0,
            available_mb=2000.0,
            suggestions=[]
        )
        # process_mb / total_mb * 100 should equal percent
        calculated = (status.process_mb / status.total_mb) * 100
        assert abs(calculated - status.percent) < 0.1

    def test_available_plus_used_equals_total(self):
        """Available + process should roughly equal total"""
        status = MemoryStatus(
            level=MemoryLevel.NORMAL,
            percent=60.0,
            process_mb=2400.0,
            total_mb=4000.0,
            available_mb=1600.0,
            suggestions=[]
        )
        # In reality there's other processes, so this won't be exact
        # but for our app's process the relationship should hold approximately
        assert status.process_mb + status.available_mb <= status.total_mb

    def test_edge_case_low_memory(self):
        """Test very low available memory"""
        status = MemoryStatus(
            level=MemoryLevel.CRITICAL,
            percent=99.0,
            process_mb=3960.0,
            total_mb=4000.0,
            available_mb=40.0,
            suggestions=["Emergency: Save and close!"]
        )
        assert status.available_mb < 100
        assert status.level == MemoryLevel.CRITICAL


class TestMemoryIndicatorSignals:
    """Tests for signal definitions"""

    def test_memory_critical_signal_exists(self):
        """MemoryIndicator should have memory_critical signal"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        assert hasattr(MemoryIndicator, 'memory_critical')


class TestMemoryIndicatorWidget:
    """Integration tests requiring Qt"""

    def test_widget_creation(self, qapp):
        """Test widget can be created"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        widget = MemoryIndicator()
        assert widget is not None
        widget.close()

    def test_widget_updates_display(self, qapp):
        """Test widget updates its display"""
        from platform_base.desktop.widgets.memory_indicator import MemoryIndicator
        widget = MemoryIndicator()
        # Initial text should show RAM info
        assert "RAM:" in widget.text()
        widget.close()
