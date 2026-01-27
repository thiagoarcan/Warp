"""
Dialogs package - Diálogos de interface

Diálogos disponíveis:
- FilterDialog: Configuração de filtros (Butterworth, Outliers, Rolling)
- SmoothingDialog: Configuração de suavização (Gaussian, MA, Savitzky-Golay, etc.)
- SettingsDialog: Configurações da aplicação
- InterpolationDialog: Configuração de interpolação
- DerivativeDialog: Configuração de derivadas
- IntegralDialog: Configuração de integrais
- ExportDialog: Exportação de dados
"""

from platform_base.ui.dialogs.filter_dialog import FilterDialog, show_filter_dialog
from platform_base.ui.dialogs.settings_dialog import (
    AppSettings,
    SettingsDialog,
    load_app_settings,
    show_settings_dialog,
)
from platform_base.ui.dialogs.smoothing_dialog import (
    SmoothingDialog,
    show_smoothing_dialog,
)

__all__ = [
    'FilterDialog',
    'show_filter_dialog',
    'SmoothingDialog', 
    'show_smoothing_dialog',
    'SettingsDialog',
    'AppSettings',
    'show_settings_dialog',
    'load_app_settings',
]
