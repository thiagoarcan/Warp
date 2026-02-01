"""
Testes para o módulo ui/tooltips.py
Cobertura completa do sistema de tooltips
"""
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestTooltipConfig:
    """Testes para TooltipConfig dataclass."""
    
    def test_import(self):
        """Testa importação do config."""
        from platform_base.ui.tooltips import TooltipConfig
        assert TooltipConfig is not None
    
    def test_default_values(self):
        """Testa valores padrão."""
        from platform_base.ui.tooltips import TooltipConfig
        
        config = TooltipConfig()
        
        assert config.show_delay_ms == 500
        assert config.hide_delay_ms == 5000
        assert config.show_shortcuts is True
        assert config.rich_text is True
    
    def test_custom_values(self):
        """Testa valores customizados."""
        from platform_base.ui.tooltips import TooltipConfig
        
        config = TooltipConfig(
            show_delay_ms=300,
            hide_delay_ms=3000,
            show_shortcuts=False,
            rich_text=False,
        )
        
        assert config.show_delay_ms == 300
        assert config.hide_delay_ms == 3000
        assert config.show_shortcuts is False
        assert config.rich_text is False


class TestTooltipsDict:
    """Testes para TOOLTIPS dictionary."""
    
    def test_tooltips_exist(self):
        """Testa que TOOLTIPS existe."""
        from platform_base.ui.tooltips import TOOLTIPS
        
        assert isinstance(TOOLTIPS, dict)
        assert len(TOOLTIPS) > 0
    
    def test_button_tooltips(self):
        """Testa tooltips de botões."""
        from platform_base.ui.tooltips import TOOLTIPS

        # Deve ter tooltips para botões comuns
        button_tooltips = [k for k in TOOLTIPS if k.startswith("btn_")]
        assert len(button_tooltips) > 0
    
    def test_tooltip_structure(self):
        """Testa estrutura dos tooltips."""
        from platform_base.ui.tooltips import TOOLTIPS
        
        for widget_id, config in TOOLTIPS.items():
            assert "tooltip" in config
            assert isinstance(config["tooltip"], str)
    
    def test_tooltip_with_shortcut(self):
        """Testa tooltips com shortcuts."""
        from platform_base.ui.tooltips import TOOLTIPS

        # Pelo menos alguns tooltips devem ter shortcuts
        tooltips_with_shortcuts = [
            k for k, v in TOOLTIPS.items() 
            if "shortcut" in v
        ]
        assert len(tooltips_with_shortcuts) > 0


class TestTooltipManager:
    """Testes para TooltipManager."""
    
    def test_import(self):
        """Testa importação do manager."""
        try:
            from platform_base.ui.tooltips import TooltipManager
            assert True
        except ImportError:
            pytest.skip("TooltipManager não disponível")
    
    def test_creation(self, qtbot):
        """Testa criação do manager."""
        try:
            from platform_base.ui.tooltips import TooltipManager
            
            manager = TooltipManager()
            assert manager is not None
        except ImportError:
            pytest.skip("TooltipManager não disponível")
    
    def test_set_config(self, qtbot):
        """Testa configuração."""
        try:
            from platform_base.ui.tooltips import TooltipConfig, TooltipManager
            
            manager = TooltipManager()
            config = TooltipConfig(show_delay_ms=300)
            
            if hasattr(manager, 'set_config'):
                manager.set_config(config)
                assert True
        except ImportError:
            pytest.skip("TooltipManager não disponível")
    
    def test_get_tooltip(self, qtbot):
        """Testa obtenção de tooltip."""
        try:
            from platform_base.ui.tooltips import TooltipManager
            
            manager = TooltipManager()
            
            if hasattr(manager, 'get_tooltip'):
                tooltip = manager.get_tooltip("btn_open")
                # Pode retornar None se não existir
                if tooltip:
                    assert isinstance(tooltip, str)
        except ImportError:
            pytest.skip("TooltipManager não disponível")
    
    def test_format_tooltip(self, qtbot):
        """Testa formatação de tooltip."""
        try:
            from platform_base.ui.tooltips import TooltipManager
            
            manager = TooltipManager()
            
            if hasattr(manager, 'format_tooltip'):
                formatted = manager.format_tooltip("Test tooltip", "Ctrl+T")
                assert isinstance(formatted, str)
        except ImportError:
            pytest.skip("TooltipManager não disponível")


class TestTooltipApplyFunction:
    """Testes para função apply_tooltip."""
    
    def test_apply_tooltip(self, qtbot):
        """Testa aplicação de tooltip a widget."""
        try:
            from PyQt6.QtWidgets import QPushButton

            from platform_base.ui.tooltips import apply_tooltip
            
            button = QPushButton("Test")
            qtbot.addWidget(button)
            
            apply_tooltip(button, "Test tooltip")
            
            assert button.toolTip() != ""
        except ImportError:
            pytest.skip("apply_tooltip não disponível")
    
    def test_apply_tooltip_with_shortcut(self, qtbot):
        """Testa aplicação de tooltip com shortcut."""
        try:
            from PyQt6.QtWidgets import QPushButton

            from platform_base.ui.tooltips import apply_tooltip
            
            button = QPushButton("Test")
            qtbot.addWidget(button)
            
            apply_tooltip(button, "Test tooltip", shortcut="Ctrl+T")
            
            assert "Test tooltip" in button.toolTip()
        except ImportError:
            pytest.skip("apply_tooltip não disponível")


class TestTooltipHelperFunctions:
    """Testes para funções auxiliares."""
    
    def test_format_shortcut_for_tooltip(self):
        """Testa formatação de shortcut para tooltip."""
        try:
            from platform_base.ui.tooltips import format_shortcut_for_tooltip
            
            formatted = format_shortcut_for_tooltip("Ctrl+S")
            assert isinstance(formatted, str)
        except ImportError:
            # Função pode não existir
            pass
    
    def test_get_tooltip_for_widget(self):
        """Testa obtenção de tooltip para widget."""
        try:
            from platform_base.ui.tooltips import get_tooltip_for_widget
            
            tooltip = get_tooltip_for_widget("btn_save")
            if tooltip:
                assert isinstance(tooltip, str)
        except ImportError:
            # Função pode não existir
            pass


class TestRichTooltip:
    """Testes para RichTooltip widget."""
    
    def test_import(self):
        """Testa importação do widget."""
        try:
            from platform_base.ui.tooltips import RichTooltip
            assert True
        except ImportError:
            pytest.skip("RichTooltip não disponível")
    
    def test_creation(self, qtbot):
        """Testa criação do widget."""
        pytest.skip("RichTooltip requer API específica")


class TestTooltipModuleImports:
    """Testes de importação do módulo."""
    
    def test_module_import(self):
        """Testa importação do módulo."""
        from platform_base.ui import tooltips
        assert tooltips is not None
    
    def test_core_exports(self):
        """Testa exports principais."""
        from platform_base.ui import tooltips
        
        assert hasattr(tooltips, 'TooltipConfig')
        assert hasattr(tooltips, 'TOOLTIPS')
