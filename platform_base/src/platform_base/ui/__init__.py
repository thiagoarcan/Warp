"""
Platform Base UI Module

Este módulo contém todos os componentes de interface do usuário:
- Painéis principais (DataPanel, VizPanel, OperationsPanel)
- Diálogos de operação (InterpolationDialog, DerivativeDialog, etc.)
- Diálogo de exportação (ExportDialog)
- Estado da sessão (SessionState)
- Menu de contexto (PlotContextMenu)
- Widgets auxiliares
"""

from platform_base.ui.export_dialog import ExportDialog, show_export_dialog
from platform_base.ui.operation_dialogs import (
    CalculusDialog,
    DerivativeDialog,
    FilterDialog,
    IntegralDialog,
    InterpolationDialog,
    OperationDialogManager,
    SmoothingDialog,
    SynchronizationDialog,
    get_operation_dialog_manager,
    show_calculus_dialog,
    show_derivative_dialog,
    show_filter_dialog,
    show_integral_dialog,
    show_interpolation_dialog,
    show_smoothing_dialog,
    show_synchronization_dialog,
)
from platform_base.ui.panels.operations_panel import OperationsPanel
from platform_base.ui.plot_sync import PlotSyncManager, get_sync_manager
from platform_base.ui.preview_dialog import (
    OperationPreviewDialog,
    PreviewCanvas,
    show_preview_dialog,
)
from platform_base.ui.state import SessionState
from platform_base.ui.undo_redo import (
    BaseCommand,
    DataOperationCommand,
    SelectionCommand,
    UndoRedoManager,
    ViewConfigCommand,
    get_undo_manager,
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
    
    # Preview
    'OperationPreviewDialog',
    'PreviewCanvas',
    'show_preview_dialog',
    
    # Plot Sync
    'PlotSyncManager',
    'get_sync_manager',
    
    # Undo/Redo
    'UndoRedoManager',
    'get_undo_manager',
    'BaseCommand',
    'DataOperationCommand',
    'SelectionCommand',
    'ViewConfigCommand',
]