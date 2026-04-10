"""Regressoes do fluxo de upload dialog (single e multi-file)."""

from __future__ import annotations

from unittest.mock import MagicMock

from platform_base.desktop.dialogs.upload_dialog import UploadDialog


class _DummyDataset:
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id


def test_upload_dialog_single_file_uses_session_state_add_dataset(qapp, mock_session_state, mock_signal_hub):
    """Upload simples deve registrar dataset via SessionState, nao via dataset_store."""
    dialog = UploadDialog(mock_session_state, mock_signal_hub)

    dataset = _DummyDataset("ds_single")
    mock_session_state.add_dataset = MagicMock(return_value="ds_single")

    dialog._on_file_loaded("C:/tmp/sample.csv", dataset)

    mock_session_state.add_dataset.assert_called_once_with(dataset)
    assert mock_signal_hub.emit_dataset_loaded.call_count == 1


def test_upload_dialog_multi_file_uses_session_state_add_dataset(qapp, mock_session_state, mock_signal_hub):
    """Upload multiplo deve registrar cada dataset via SessionState."""
    dialog = UploadDialog(mock_session_state, mock_signal_hub)

    # estado minimo para o fluxo interno
    dialog.pending_files = ["a.csv", "b.csv"]
    dialog.load_errors = []
    dialog.loaded_datasets = []

    dataset = _DummyDataset("ds_multi")
    mock_session_state.add_dataset = MagicMock(return_value="ds_multi")

    dialog._on_multi_file_loaded("C:/tmp/a.csv", dataset)

    mock_session_state.add_dataset.assert_called_once_with(dataset)
    assert "ds_multi" in dialog.loaded_datasets
    assert mock_signal_hub.emit_dataset_loaded.call_count == 1
