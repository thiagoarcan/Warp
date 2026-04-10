"""Regressao: arvore de series deve listar series de todos os datasets carregados."""

from __future__ import annotations

from pathlib import Path

import pytest

from platform_base.core.dataset_store import DatasetStore
from platform_base.core.session_state import SessionState
from platform_base.io.loader import load
from platform_base.ui.panels.data_panel import CompactDataPanel


def test_series_tree_shows_all_loaded_datasets(qapp):
    root = Path(__file__).resolve().parents[2]
    sample = root / "data" / "samples" / "BAR_DT-OP10.xlsx"
    if not sample.exists():
        pytest.skip("Amostra BAR_DT-OP10.xlsx nao encontrada")

    store = DatasetStore()
    state = SessionState(store)
    panel = CompactDataPanel(state)

    d1 = load(str(sample))
    d2 = load(str(sample))

    state.add_dataset(d1)
    state.add_dataset(d2)

    qapp.processEvents()

    # Top-level = datasets; child = series
    assert panel._series_tree.topLevelItemCount() == 2
    assert panel._series_tree.topLevelItem(0).childCount() >= 1
    assert panel._series_tree.topLevelItem(1).childCount() >= 1
