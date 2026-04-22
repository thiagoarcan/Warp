"""Compatibility facade for desktop panel classes.

This module provides a stable import surface for panel classes regardless of
whether the active implementation lives in ``platform_base.ui.panels`` or in
legacy ``platform_base.desktop.widgets`` modules.

Use cases:
- ``from platform_base.desktop import panels``
- ``from platform_base.desktop.panels import DataPanel, VizPanel``

The facade uses lazy imports to avoid importing heavy UI modules at startup.
"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Dict, Iterable, Tuple


_EXPORT_SOURCES: Dict[str, Tuple[str, ...]] = {
    # Core panel widgets
    "DataPanel": (
        "platform_base.ui.panels.data_panel",
        "platform_base.desktop.widgets.data_panel",
    ),
    "CompactDataPanel": (
        "platform_base.ui.panels.data_panel",
    ),
    "VizPanel": (
        "platform_base.ui.panels.viz_panel",
        "platform_base.desktop.widgets.viz_panel",
    ),
    "ModernVizPanel": (
        "platform_base.ui.panels.viz_panel",
    ),
    "OperationsPanel": (
        "platform_base.ui.panels.operations_panel",
        "platform_base.desktop.widgets.operations_panel",
    ),
    "ResultsPanel": (
        "platform_base.ui.panels.results_panel",
        "platform_base.desktop.widgets.results_panel",
    ),
    "StreamingPanel": (
        "platform_base.ui.panels.streaming_panel",
        "platform_base.desktop.widgets.streaming_panel",
    ),
    "ConfigPanel": (
        "platform_base.ui.panels.config_panel",
        "platform_base.desktop.widgets.config_panel",
    ),
    # Auxiliary/utility panel widgets
    "ResourceMonitorPanel": (
        "platform_base.ui.panels.resource_monitor_panel",
    ),
    "ActivityLogPanel": (
        "platform_base.ui.panels.activity_log_panel",
    ),
    "DataTablesPanel": (
        "platform_base.ui.panels.data_tables_panel",
    ),
    "DetachedManager": (
        "platform_base.ui.panels.detached_manager",
    ),
    # Public panel-related helper classes/types used by the app/tests
    "ColorButton": (
        "platform_base.ui.panels.config_panel",
    ),
    "OperationHistoryItem": (
        "platform_base.ui.panels.operations_panel",
        "platform_base.desktop.widgets.operations_panel",
    ),
    "StatisticsResult": (
        "platform_base.ui.panels.results_panel",
    ),
    "ComparisonResult": (
        "platform_base.ui.panels.results_panel",
    ),
    "PlaybackState": (
        "platform_base.ui.panels.streaming_panel",
        "platform_base.desktop.widgets.streaming_panel",
    ),
    "PlaybackMode": (
        "platform_base.ui.panels.streaming_panel",
        "platform_base.desktop.widgets.streaming_panel",
    ),
}


def _load_symbol(name: str):
    module_names = _EXPORT_SOURCES.get(name)
    if module_names is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    last_error: Exception | None = None
    for module_name in module_names:
        try:
            module = import_module(module_name)
        except Exception as exc:  # pragma: no cover - defensive compatibility
            last_error = exc
            continue

        if hasattr(module, name):
            value = getattr(module, name)
            globals()[name] = value
            return value

    if last_error is not None:
        raise AttributeError(
            f"Could not resolve {name!r} from configured panel modules"
        ) from last_error

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __getattr__(name: str):
    return _load_symbol(name)


def __dir__() -> Iterable[str]:
    return sorted(set(list(globals().keys()) + list(_EXPORT_SOURCES.keys())))


def get_panel_module(name: str) -> ModuleType:
    """Return the module that currently provides a given exported symbol."""

    _load_symbol(name)
    module_name = getattr(globals()[name], "__module__", "")
    return import_module(module_name)


__all__ = sorted(_EXPORT_SOURCES.keys())
