"""Regressao: solicitacao de plot do DataPanel deve criar grafico no VizPanel."""

from __future__ import annotations

from pathlib import Path

import pytest

from platform_base.core.dataset_store import DatasetStore
from platform_base.core.signal_hub import SignalHub
from platform_base.core.session_state import SessionState
from platform_base.io.loader import load
from platform_base.ui.main_window_unified import ModernMainWindow


def test_plot_request_from_data_panel_creates_plot_tab(qapp):
    root = Path(__file__).resolve().parents[2]
    sample = root / "data" / "samples" / "BAR_DT-OP10.xlsx"
    if not sample.exists():
        pytest.skip("Amostra BAR_DT-OP10.xlsx nao encontrada")

    store = DatasetStore()
    state = SessionState(store)
    hub = SignalHub()

    window = ModernMainWindow(state, hub)

    dataset = load(str(sample))
    state.add_dataset(dataset)

    dataset_id = next(iter(state.get_all_datasets().keys()))
    first_series_id = next(iter(dataset.series.keys()))

    initial_tabs = window.viz_panel._viz_tabs.count()

    window.data_panel.plot_requested.emit(dataset_id, first_series_id, "2d")
    qapp.processEvents()

    assert window.viz_panel._viz_tabs.count() == initial_tabs + 1

    window.close()
