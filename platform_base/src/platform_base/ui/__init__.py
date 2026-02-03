"""
Platform Base UI Module

Este módulo contém todos os componentes de interface do usuário:
- Painéis principais (DataPanel, VizPanel, OperationsPanel)
- Diálogos de operação (InterpolationDialog, DerivativeDialog, etc.)
- Diálogo de exportação (ExportDialog)
- Estado da sessão (SessionState)
- Menu de contexto (PlotContextMenu)
- Widgets auxiliares

Note: Este módulo usa lazy imports para evitar carregar matplotlib no startup.
      Importe os submódulos diretamente quando precisar deles.
"""

# Lazy imports - só carregam quando acessados
def __getattr__(name):
    """Lazy loading para evitar carregar matplotlib no startup"""
    if name in ("ExportDialog", "show_export_dialog"):
        from platform_base.ui.export_dialog import ExportDialog, show_export_dialog
        return ExportDialog if name == "ExportDialog" else show_export_dialog
    
    if name in ("CalculusDialog", "DerivativeDialog", "FilterDialog", "IntegralDialog",
                "InterpolationDialog", "OperationDialogManager", "SmoothingDialog",
                "SynchronizationDialog", "get_operation_dialog_manager",
                "show_calculus_dialog", "show_derivative_dialog", "show_filter_dialog",
                "show_integral_dialog", "show_interpolation_dialog", "show_smoothing_dialog",
                "show_synchronization_dialog"):
        from platform_base.ui import operation_dialogs
        return getattr(operation_dialogs, name)
    
    if name == "OperationsPanel":
        from platform_base.ui.panels.operations_panel import OperationsPanel
        return OperationsPanel
    
    if name in ("PlotSyncManager", "get_sync_manager"):
        from platform_base.ui.plot_sync import PlotSyncManager, get_sync_manager
        return PlotSyncManager if name == "PlotSyncManager" else get_sync_manager
    
    if name in ("OperationPreviewDialog", "PreviewCanvas", "show_preview_dialog"):
        from platform_base.ui import preview_dialog
        return getattr(preview_dialog, name)
    
    if name == "SessionState":
        from platform_base.ui.state import SessionState
        return SessionState
    
    if name in ("BaseCommand", "DataOperationCommand", "SelectionCommand",
                "UndoRedoManager", "ViewConfigCommand", "get_undo_manager"):
        from platform_base.ui import undo_redo
        return getattr(undo_redo, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseCommand",
    "CalculusDialog",
    "DataOperationCommand",
    "DerivativeDialog",
    # Export
    "ExportDialog",
    "FilterDialog",
    "IntegralDialog",
    "InterpolationDialog",
    # Operation Dialogs
    "OperationDialogManager",
    # Preview
    "OperationPreviewDialog",
    # Panels
    "OperationsPanel",
    # Plot Sync
    "PlotSyncManager",
    "PreviewCanvas",
    "SelectionCommand",
    # State
    "SessionState",
    "SmoothingDialog",
    "SynchronizationDialog",
    # Undo/Redo
    "UndoRedoManager",
    "ViewConfigCommand",
    "get_operation_dialog_manager",
    "get_sync_manager",
    "get_undo_manager",
    "show_calculus_dialog",
    "show_derivative_dialog",
    "show_export_dialog",
    "show_filter_dialog",
    "show_integral_dialog",
    "show_interpolation_dialog",
    "show_preview_dialog",
    "show_smoothing_dialog",
    "show_synchronization_dialog",
]
