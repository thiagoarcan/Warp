"""
SessionState - PyQt6 state management replacing Dash client-side store

Conforme especificação seção 12.2, implementa state management unificado
para toda a aplicação PyQt6.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QMutex, QMutexLocker, QObject, pyqtSignal

from platform_base.core.models import (
    Dataset,
    DatasetID,
    SeriesID,
    TimeWindow,
    ViewData,
    ViewID,
)

# Re-export Selection for backward compatibility
from platform_base.ui.selection import Selection
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.core.dataset_store import DatasetStore


logger = get_logger(__name__)

# Export for easy access
__all__ = [
    'SelectionState',
    'OperationState',
    'ViewState',
    'SessionState',
    'Selection',
    'SessionSelection',
    'ProcessingState',
    'SeriesSelection',
]


@dataclass
class SelectionState:
    """Estado de seleção multi-view"""
    time_range: TimeWindow | None = None
    selected_series: list[SeriesID] = field(default_factory=list)
    brush_selections: dict[str, Any] = field(default_factory=dict)
    zoom_state: dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationState:
    """Estado de operações em andamento"""
    is_loading: bool = False
    is_processing: bool = False
    current_operation: str | None = None
    progress_percent: float = 0.0
    status_message: str = ""


@dataclass
class ViewState:
    """Estado de visualização"""
    current_view_type: str = "2d"  # 2d, 3d, heatmap
    layout_mode: str = "single"  # single, dual, quad
    sync_views: bool = True
    show_interpolated: bool = True
    downsampling_enabled: bool = True
    downsampling_threshold: int = 10000


@dataclass
class SessionSelection:
    """Estado de seleção para uso externo."""
    dataset_id: str | None = None
    series_ids: set = field(default_factory=set)


@dataclass
class ProcessingState:
    """Estado de processamento com operações ativas."""
    is_processing: bool = False
    current_operation: str | None = None
    active_operations: dict = field(default_factory=dict)


@dataclass
class SeriesSelection:
    """Seleção individual de série."""
    dataset_id: str | None = None
    series_id: str | None = None


class SessionState(QObject):
    """
    State management centralizado para aplicação PyQt6

    Substitui o dash.Store com funcionalidades:
    - Thread-safe com QMutex
    - Signals para notificação de mudanças
    - Persistência de sessão
    - Estado de seleção multi-view
    - Estado de operações
    """

    # Signals para notificar mudanças de estado
    dataset_changed = pyqtSignal(str)  # dataset_id
    selection_changed = pyqtSignal()  # Selection changed (use selection property)
    operation_started = pyqtSignal(str)  # operation_name
    operation_finished = pyqtSignal(str, bool)  # operation_name, success
    operation_progress = pyqtSignal(float, str)  # percent, message
    view_changed = pyqtSignal()
    ui_state_changed = pyqtSignal(object)  # UI state object

    def __init__(self, dataset_store: DatasetStore):
        super().__init__()

        # Thread safety
        self._mutex = QMutex()

        # Core components
        self._dataset_store = dataset_store

        # Current state - CORRIGIDO: suporta múltiplos datasets
        self._current_dataset: DatasetID | None = None
        self._current_view: ViewID | None = None
        self._loaded_datasets: dict[DatasetID, Dataset] = {}  # Manter todos os datasets

        # Sub-states
        self._selection = SelectionState()
        self._operation = OperationState()
        self._view = ViewState()

        # Session metadata
        self._session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._created_at = datetime.now()

        logger.info("session_state_initialized", session_id=self._session_id)

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def dataset_store(self):
        """Acesso ao DatasetStore central."""
        return self._dataset_store

    @property
    def current_dataset(self) -> DatasetID | None:
        with QMutexLocker(self._mutex):
            return self._current_dataset

    @current_dataset.setter
    def current_dataset(self, dataset_id: DatasetID | None):
        with QMutexLocker(self._mutex):
            if self._current_dataset != dataset_id:
                self._current_dataset = dataset_id
                logger.debug("current_dataset_changed", dataset_id=dataset_id)
                self.dataset_changed.emit(dataset_id or "")

    @property
    def current_view(self) -> ViewID | None:
        with QMutexLocker(self._mutex):
            return self._current_view

    @current_view.setter
    def current_view(self, view_id: ViewID | None):
        with QMutexLocker(self._mutex):
            self._current_view = view_id

    @property
    def loaded_datasets(self) -> list[DatasetID]:
        with QMutexLocker(self._mutex):
            return list(self._loaded_datasets.keys())

    @property
    def selection(self) -> "SessionSelection":
        """Retorna objeto de seleção com dataset_id e series_ids."""
        with QMutexLocker(self._mutex):
            return SessionSelection(
                dataset_id=self._current_dataset,
                series_ids=set(self._selection.selected_series),
            )

    @property
    def processing(self) -> "ProcessingState":
        """Retorna estado de processamento com operações ativas."""
        with QMutexLocker(self._mutex):
            return ProcessingState(
                is_processing=self._operation.is_processing,
                current_operation=self._operation.current_operation,
                active_operations={},  # Mapa de operações ativas
            )

    def get_selected_series(self) -> list | None:
        """Retorna lista de séries selecionadas."""
        with QMutexLocker(self._mutex):
            if not self._current_dataset or not self._selection.selected_series:
                return None
            result = []
            for series_id in self._selection.selected_series:
                result.append(SeriesSelection(
                    dataset_id=self._current_dataset,
                    series_id=series_id,
                ))
            return result if result else None

    def add_dataset(self, dataset: Dataset) -> DatasetID:
        """Adiciona dataset e atualiza estado - CORRIGIDO: mantém todos os datasets"""
        dataset_id = self._dataset_store.add_dataset(dataset)

        with QMutexLocker(self._mutex):
            # Adiciona/atualiza dataset no mapeamento local
            self._loaded_datasets[dataset_id] = dataset

            # Se é o primeiro dataset, torna-o atual
            if self._current_dataset is None:
                self._current_dataset = dataset_id

        logger.info("dataset_added_to_session",
                   dataset_id=dataset_id,
                   total_datasets=len(self._loaded_datasets))

        self.dataset_changed.emit(dataset_id)
        return dataset_id

    def get_dataset(self, dataset_id: DatasetID) -> Dataset:
        """Wrapper thread-safe para dataset store"""
        return self._dataset_store.get_dataset(dataset_id)

    def get_current_dataset(self) -> Dataset | None:
        """Obtém dataset atual"""
        with QMutexLocker(self._mutex):
            if self._current_dataset:
                return self._dataset_store.get_dataset(self._current_dataset)
        return None

    def get_all_datasets(self) -> dict[DatasetID, Dataset]:
        """Obtém todos os datasets carregados"""
        with QMutexLocker(self._mutex):
            return self._loaded_datasets.copy()

    def list_datasets(self) -> list[DatasetID]:
        """Lista IDs de todos os datasets carregados"""
        with QMutexLocker(self._mutex):
            return list(self._loaded_datasets.keys())

    def set_current_dataset(self, dataset_id: DatasetID) -> bool:
        """Define dataset atual"""
        changed = False
        with QMutexLocker(self._mutex):
            if dataset_id in self._loaded_datasets:
                self._current_dataset = dataset_id
                changed = True
        # Emitir sinal FORA do mutex para evitar deadlock
        if changed:
            self.dataset_changed.emit(dataset_id)
        return changed

    def create_view(self, series_ids: list[SeriesID],
                   time_window: TimeWindow | None = None) -> ViewData | None:
        """Cria view para visualização"""
        with QMutexLocker(self._mutex):
            if not self._current_dataset:
                logger.warning("no_current_dataset_for_view")
                return None

            # Usa janela temporal da seleção se não especificado
            if time_window is None and self._selection.time_range:
                time_window = self._selection.time_range
            elif time_window is None:
                # Usa todo o dataset
                dataset = self._dataset_store.get_dataset(self._current_dataset)
                time_window = TimeWindow(
                    start=float(dataset.t_seconds.min()),
                    end=float(dataset.t_seconds.max()),
                )

            return self._dataset_store.create_view(
                self._current_dataset, series_ids, time_window,
            )

    # Selection State Management
    def update_selection(self, **kwargs) -> None:
        """Atualiza estado de seleção"""
        with QMutexLocker(self._mutex):
            for key, value in kwargs.items():
                if hasattr(self._selection, key):
                    setattr(self._selection, key, value)

        logger.debug("selection_updated", **kwargs)
        self.selection_changed.emit()

    def get_selection_state(self) -> SelectionState:
        """Obtém cópia do estado de seleção"""
        with QMutexLocker(self._mutex):
            return SelectionState(
                time_range=self._selection.time_range,
                selected_series=self._selection.selected_series.copy(),
                brush_selections=self._selection.brush_selections.copy(),
                zoom_state=self._selection.zoom_state.copy(),
            )

    # Operation State Management
    def start_operation(self, operation_name: str) -> None:
        """Inicia operação"""
        with QMutexLocker(self._mutex):
            self._operation.is_processing = True
            self._operation.current_operation = operation_name
            self._operation.progress_percent = 0.0
            self._operation.status_message = f"Starting {operation_name}..."

        logger.info("operation_started", operation=operation_name)
        self.operation_started.emit(operation_name)

    def update_operation_progress(self, percent: float, message: str = "") -> None:
        """Atualiza progresso da operação"""
        with QMutexLocker(self._mutex):
            self._operation.progress_percent = percent
            if message:
                self._operation.status_message = message

        # Emitir sinal para UI
        self.operation_progress.emit(percent, message)

    def finish_operation(self, success: bool = True, message: str = "") -> None:
        """Finaliza operação"""
        operation_name = ""
        with QMutexLocker(self._mutex):
            operation_name = self._operation.current_operation or "unknown"
            self._operation.is_processing = False
            self._operation.current_operation = None
            self._operation.progress_percent = 100.0 if success else 0.0
            self._operation.status_message = message or ("Complete" if success else "Failed")

        logger.info("operation_finished", operation=operation_name, success=success)
        self.operation_finished.emit(operation_name, success)

    def get_operation_state(self) -> OperationState:
        """Obtém cópia do estado de operação"""
        with QMutexLocker(self._mutex):
            return OperationState(
                is_loading=self._operation.is_loading,
                is_processing=self._operation.is_processing,
                current_operation=self._operation.current_operation,
                progress_percent=self._operation.progress_percent,
                status_message=self._operation.status_message,
            )

    # View State Management
    def update_view_state(self, **kwargs) -> None:
        """Atualiza estado de visualização"""
        with QMutexLocker(self._mutex):
            for key, value in kwargs.items():
                if hasattr(self._view, key):
                    setattr(self._view, key, value)

        logger.debug("view_state_updated", **kwargs)
        self.view_changed.emit()

    def get_view_state(self) -> ViewState:
        """Obtém cópia do estado de visualização"""
        with QMutexLocker(self._mutex):
            return ViewState(
                current_view_type=self._view.current_view_type,
                layout_mode=self._view.layout_mode,
                sync_views=self._view.sync_views,
                show_interpolated=self._view.show_interpolated,
                downsampling_enabled=self._view.downsampling_enabled,
                downsampling_threshold=self._view.downsampling_threshold,
            )

    # Session Persistence
    def save_session(self, filepath: str) -> None:
        """Salva estado da sessão"""
        with QMutexLocker(self._mutex):
            session_data = {
                "session_id": self._session_id,
                "created_at": self._created_at.isoformat(),
                "current_dataset": self._current_dataset,
                "loaded_datasets": self._loaded_datasets,
                "selection": {
                    "selected_series": self._selection.selected_series,
                    "time_range": {
                        "start": self._selection.time_range.start,
                        "end": self._selection.time_range.end,
                    } if self._selection.time_range else None,
                },
                "view": {
                    "current_view_type": self._view.current_view_type,
                    "layout_mode": self._view.layout_mode,
                    "sync_views": self._view.sync_views,
                    "show_interpolated": self._view.show_interpolated,
                    "downsampling_enabled": self._view.downsampling_enabled,
                    "downsampling_threshold": self._view.downsampling_threshold,
                },
            }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        logger.info("session_saved", filepath=filepath)

    def load_session(self, filepath: str) -> None:
        """Carrega estado da sessão"""
        with open(filepath, encoding="utf-8") as f:
            session_data = json.load(f)

        with QMutexLocker(self._mutex):
            self._loaded_datasets = session_data.get("loaded_datasets", [])
            self._current_dataset = session_data.get("current_dataset")

            # Restaura seleção
            selection_data = session_data.get("selection", {})
            self._selection.selected_series = selection_data.get("selected_series", [])
            if selection_data.get("time_range"):
                tr = selection_data["time_range"]
                self._selection.time_range = TimeWindow(start=tr["start"], end=tr["end"])

            # Restaura view
            view_data = session_data.get("view", {})
            for key, value in view_data.items():
                if hasattr(self._view, key):
                    setattr(self._view, key, value)

        logger.info("session_loaded", filepath=filepath)
        self.dataset_changed.emit(self._current_dataset or "")
        self.view_changed.emit()
        self.selection_changed.emit()

    def clear_session(self) -> None:
        """Limpa estado da sessão"""
        with QMutexLocker(self._mutex):
            self._current_dataset = None
            self._current_view = None
            self._loaded_datasets.clear()
            self._selection = SelectionState()
            self._operation = OperationState()
            self._view = ViewState()

        logger.info("session_cleared")
        self.dataset_changed.emit("")
        self.view_changed.emit()
        self.selection_changed.emit()

    def get_summary(self) -> dict[str, Any]:
        """Obtém resumo do estado atual"""
        with QMutexLocker(self._mutex):
            return {
                "session_id": self._session_id,
                "current_dataset": self._current_dataset,
                "loaded_datasets": len(self._loaded_datasets),
                "is_processing": self._operation.is_processing,
                "current_operation": self._operation.current_operation,
                "view_type": self._view.current_view_type,
                "selected_series": len(self._selection.selected_series),
            }
