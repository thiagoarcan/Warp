# UI package"""
Platform Base UI Module

Este módulo contém todos os componentes de interface do usuário:
- Painéis principais (DataPanel, VizPanel, OperationsPanel)
- Diálogos de operação (InterpolationDialog, DerivativeDialog, etc.)
- Diálogo de exportação (ExportDialog)
- Estado da sessão (SessionState)
- Menu de contexto (PlotContextMenu)
- Widgets auxiliares
"""

from platform_base.ui.state import SessionState
from platform_base.ui.operations_panel import OperationsPanel
from platform_base.ui.export_dialog import ExportDialog, show_export_dialog
from platform_base.ui.operation_dialogs import (
    OperationDialogManager,
    get_operation_dialog_manager,
    show_interpolation_dialog,
    show_synchronization_dialog,
    show_calculus_dialog,
    show_derivative_dialog,
    show_integral_dialog,
    show_filter_dialog,
    show_smoothing_dialog,
    InterpolationDialog,
    SynchronizationDialog,
    CalculusDialog,
    DerivativeDialog,
    IntegralDialog,
    FilterDialog,
    SmoothingDialog,
)

__all__ = [
    # State
    'SessionState',
    
    # Panels
    'OperationsPanel',
    
    # Export
    'ExportDialog',
    'show_export_dialog',
    
    # Operation Dialogs
    'OperationDialogManager',
    'get_operation_dialog_manager',
    'show_interpolation_dialog',
    'show_synchronization_dialog',
    'show_calculus_dialog',
    'show_derivative_dialog',
    'show_integral_dialog',
    'show_filter_dialog',
    'show_smoothing_dialog',
    'InterpolationDialog',
    'SynchronizationDialog',
    'CalculusDialog',
    'DerivativeDialog',
    'IntegralDialog',
    'FilterDialog',
    'SmoothingDialog',
]