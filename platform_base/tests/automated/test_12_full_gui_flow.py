"""Smoke E2E do fluxo GUI: upload multiplo -> lista de datasets -> plot."""

from __future__ import annotations

from pathlib import Path

import pytest

from platform_base.core.dataset_store import DatasetStore
from platform_base.core.signal_hub import SignalHub
from platform_base.core.session_state import SessionState
from platform_base.desktop.dialogs.upload_dialog import UploadDialog
from platform_base.io.loader import load
from platform_base.ui.panels.data_panel import CompactDataPanel
from platform_base.ui.panels.viz_panel import ModernVizPanel


def test_full_gui_multi_upload_and_plot_flow(qapp):
    """Carregar 2 arquivos deve mostrar 2 datasets e permitir plot."""
    root = Path(__file__).resolve().parents[2]
    sample = root / "data" / "samples" / "BAR_DT-OP10.xlsx"
    if not sample.exists():
        pytest.skip("Amostra BAR_DT-OP10.xlsx nao encontrada")

    store = DatasetStore()
    state = SessionState(store)
    signal_hub = SignalHub()

    data_panel = CompactDataPanel(state)
    viz_panel = ModernVizPanel(state)
    upload_dialog = UploadDialog(state, signal_hub)

    upload_dialog.pending_files = ["file1.xlsx", "file2.xlsx"]
    upload_dialog.load_errors = []
    upload_dialog.loaded_datasets = []

    dataset_1 = load(str(sample))
    dataset_2 = load(str(sample))

    upload_dialog._on_multi_file_loaded("file1.xlsx", dataset_1)
    upload_dialog._on_multi_file_loaded("file2.xlsx", dataset_2)
    qapp.processEvents()

    datasets = state.get_all_datasets()
    assert len(datasets) == 2
    assert data_panel._datasets_tree.topLevelItemCount() == 2

    # Validar plot para cada dataset carregado
    for dataset_id, dataset in datasets.items():
        state.set_current_dataset(dataset_id)
        first_series_id = next(iter(dataset.series.keys()))
        viz_panel.create_plot_for_series(dataset_id, first_series_id, "2d")

    # A implementacao pode abrir nova aba ou reutilizar aba existente
    # adicionando nova serie no mesmo plot.
    assert viz_panel._viz_tabs.count() >= 2
