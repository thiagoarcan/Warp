"""
Tests for ui/layout.py - Dash Layout Configuration

Tests for layout configuration and panel creation.
"""

import pytest
from pydantic import ValidationError


class TestPanelConfig:
    """Tests for PanelConfig model"""

    def test_panel_config_creation_minimal(self):
        """Test creating PanelConfig with minimal args"""
        from platform_base.ui.layout import PanelConfig
        
        config = PanelConfig(name="test")
        
        assert config.name == "test"
        assert config.position == "center"  # default
        assert config.width == 0.33  # default
        assert config.collapsible is True  # default
        assert config.default_collapsed is False  # default

    def test_panel_config_creation_full(self):
        """Test creating PanelConfig with all args"""
        from platform_base.ui.layout import PanelConfig
        
        config = PanelConfig(
            name="sidebar",
            position="left",
            width=0.25,
            collapsible=False,
            default_collapsed=True
        )
        
        assert config.name == "sidebar"
        assert config.position == "left"
        assert config.width == 0.25
        assert config.collapsible is False
        assert config.default_collapsed is True

    def test_panel_config_position_values(self):
        """Test valid position values"""
        from platform_base.ui.layout import PanelConfig
        
        valid_positions = ["left", "center", "right", "bottom"]
        
        for pos in valid_positions:
            config = PanelConfig(name="test", position=pos)
            assert config.position == pos

    def test_panel_config_invalid_position(self):
        """Test that invalid position raises error"""
        from platform_base.ui.layout import PanelConfig
        
        with pytest.raises(ValidationError):
            PanelConfig(name="test", position="top")  # invalid

    def test_panel_config_width_range(self):
        """Test width accepts various float values"""
        from platform_base.ui.layout import PanelConfig
        
        widths = [0.1, 0.25, 0.5, 0.75, 1.0]
        
        for width in widths:
            config = PanelConfig(name="test", width=width)
            assert config.width == width

    def test_panel_config_model_dump(self):
        """Test that PanelConfig can be serialized"""
        from platform_base.ui.layout import PanelConfig
        
        config = PanelConfig(name="test", position="left")
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert data["name"] == "test"
        assert data["position"] == "left"


class TestLayoutConfig:
    """Tests for LayoutConfig model"""

    def test_layout_config_defaults(self):
        """Test LayoutConfig with default values"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig()
        
        assert config.responsive is True
        assert len(config.areas) == 3
        assert "mobile" in config.breakpoints
        assert "tablet" in config.breakpoints
        assert "desktop" in config.breakpoints

    def test_layout_config_default_areas(self):
        """Test default area configurations"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig()
        
        area_names = [a.name for a in config.areas]
        assert "data" in area_names
        assert "viz" in area_names
        assert "config" in area_names

    def test_layout_config_custom_areas(self):
        """Test LayoutConfig with custom areas"""
        from platform_base.ui.layout import LayoutConfig, PanelConfig
        
        custom_areas = [
            PanelConfig(name="nav", position="left", width=0.15),
            PanelConfig(name="main", position="center", width=0.70),
            PanelConfig(name="sidebar", position="right", width=0.15),
        ]
        
        config = LayoutConfig(areas=custom_areas)
        
        assert len(config.areas) == 3
        assert config.areas[0].name == "nav"

    def test_layout_config_custom_breakpoints(self):
        """Test LayoutConfig with custom breakpoints"""
        from platform_base.ui.layout import LayoutConfig
        
        custom_breakpoints = {
            "small": 600,
            "medium": 900,
            "large": 1200,
        }
        
        config = LayoutConfig(breakpoints=custom_breakpoints)
        
        assert config.breakpoints["small"] == 600
        assert config.breakpoints["large"] == 1200

    def test_layout_config_non_responsive(self):
        """Test LayoutConfig with responsive disabled"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig(responsive=False)
        
        assert config.responsive is False

    def test_layout_config_model_dump(self):
        """Test that LayoutConfig can be serialized"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig()
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert "areas" in data
        assert "responsive" in data
        assert "breakpoints" in data

    def test_layout_config_empty_areas(self):
        """Test LayoutConfig with empty areas list"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig(areas=[])
        
        assert len(config.areas) == 0


class TestCreateDataPanel:
    """Tests for _create_data_panel function"""

    def test_create_data_panel_returns_card(self):
        """Test that _create_data_panel returns a dbc.Card"""
        import dash_bootstrap_components as dbc

        from platform_base.ui.layout import _create_data_panel
        
        result = _create_data_panel()
        
        assert isinstance(result, dbc.Card)

    def test_create_data_panel_has_header(self):
        """Test that data panel has a header"""
        from platform_base.ui.layout import _create_data_panel
        
        result = _create_data_panel()
        
        # Card should have children (header and body)
        assert result.children is not None
        assert len(result.children) >= 2

    def test_create_data_panel_has_upload(self):
        """Test that data panel includes upload component"""
        from dash import dcc

        from platform_base.ui.layout import _create_data_panel
        
        result = _create_data_panel()
        
        # Search for upload component in children
        def find_component(component, component_type):
            if isinstance(component, component_type):
                return True
            if hasattr(component, 'children'):
                children = component.children
                if children is None:
                    return False
                if isinstance(children, (list, tuple)):
                    return any(find_component(c, component_type) for c in children)
                return find_component(children, component_type)
            return False
        
        assert find_component(result, dcc.Upload)

    def test_create_data_panel_has_dropdowns(self):
        """Test that data panel includes dropdown components"""
        from dash import dcc

        from platform_base.ui.layout import _create_data_panel
        
        result = _create_data_panel()
        
        def count_components(component, component_type):
            count = 0
            if isinstance(component, component_type):
                count += 1
            if hasattr(component, 'children'):
                children = component.children
                if children is None:
                    return count
                if isinstance(children, (list, tuple)):
                    for c in children:
                        count += count_components(c, component_type)
                else:
                    count += count_components(children, component_type)
            return count
        
        dropdown_count = count_components(result, dcc.Dropdown)
        assert dropdown_count >= 2  # dataset and series dropdowns

    def test_create_data_panel_has_range_slider(self):
        """Test that data panel includes range slider"""
        from dash import dcc

        from platform_base.ui.layout import _create_data_panel
        
        result = _create_data_panel()
        
        def find_component(component, component_type):
            if isinstance(component, component_type):
                return True
            if hasattr(component, 'children'):
                children = component.children
                if children is None:
                    return False
                if isinstance(children, (list, tuple)):
                    return any(find_component(c, component_type) for c in children)
                return find_component(children, component_type)
            return False
        
        assert find_component(result, dcc.RangeSlider)


class TestPanelConfigEdgeCases:
    """Edge case tests for PanelConfig"""

    def test_panel_config_zero_width(self):
        """Test PanelConfig with zero width"""
        from platform_base.ui.layout import PanelConfig
        
        config = PanelConfig(name="hidden", width=0.0)
        assert config.width == 0.0

    def test_panel_config_empty_name(self):
        """Test PanelConfig with empty name"""
        from platform_base.ui.layout import PanelConfig

        # Empty string is technically valid
        config = PanelConfig(name="")
        assert config.name == ""

    def test_panel_config_special_chars_name(self):
        """Test PanelConfig with special characters in name"""
        from platform_base.ui.layout import PanelConfig
        
        config = PanelConfig(name="data-panel_v2")
        assert config.name == "data-panel_v2"


class TestLayoutConfigEdgeCases:
    """Edge case tests for LayoutConfig"""

    def test_layout_config_many_areas(self):
        """Test LayoutConfig with many areas"""
        from platform_base.ui.layout import LayoutConfig, PanelConfig
        
        areas = [PanelConfig(name=f"panel_{i}") for i in range(10)]
        
        config = LayoutConfig(areas=areas)
        assert len(config.areas) == 10

    def test_layout_config_total_width(self):
        """Test that panel widths can be verified"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig()
        
        total_width = sum(area.width for area in config.areas)
        assert 0.99 <= total_width <= 1.01  # Should be close to 1.0

    def test_layout_config_breakpoint_order(self):
        """Test default breakpoints are in ascending order"""
        from platform_base.ui.layout import LayoutConfig
        
        config = LayoutConfig()
        
        assert config.breakpoints["mobile"] < config.breakpoints["tablet"]
        assert config.breakpoints["tablet"] < config.breakpoints["desktop"]
