"""
Advanced Selection System - Platform Base v2.0

Provides sophisticated selection capabilities:
- Temporal selection with time ranges
- Graphical selection with interactive regions
- Conditional selection with value-based filters
- Multi-series coordinated selection
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtCore import QObject, QPointF, QRectF, pyqtSignal

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

    from platform_base.core.models import DatasetID, SeriesID


logger = get_logger(__name__)


class SelectionType(Enum):
    """Types of selection available"""
    TEMPORAL = "temporal"
    GRAPHICAL = "graphical"
    CONDITIONAL = "conditional"
    COMBINED = "combined"


class SelectionMode(Enum):
    """Selection interaction modes"""
    REPLACE = "replace"    # Replace current selection
    ADD = "add"           # Add to current selection
    SUBTRACT = "subtract"  # Remove from current selection
    INTERSECT = "intersect" # Intersect with current selection


@dataclass
class SelectionCriteria:
    """Base class for selection criteria"""
    selection_type: SelectionType
    mode: SelectionMode = SelectionMode.REPLACE

    def matches_point(self, t: float, value: float, **kwargs) -> bool:
        """Check if a point matches the selection criteria"""
        raise NotImplementedError


@dataclass
class TemporalSelection(SelectionCriteria):
    """Time-based selection criteria"""
    start_time: float
    end_time: float

    def __post_init__(self):
        self.selection_type = SelectionType.TEMPORAL
        if self.start_time > self.end_time:
            self.start_time, self.end_time = self.end_time, self.start_time

    def matches_point(self, t: float, value: float, **kwargs) -> bool:
        return self.start_time <= t <= self.end_time

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class GraphicalSelection(SelectionCriteria):
    """Graphical region-based selection"""
    region: QRectF  # Rectangle in plot coordinates

    def __post_init__(self):
        self.selection_type = SelectionType.GRAPHICAL

    def matches_point(self, t: float, value: float, **kwargs) -> bool:
        return self.region.contains(QPointF(t, value))

    @property
    def time_range(self) -> tuple[float, float]:
        return self.region.left(), self.region.right()

    @property
    def value_range(self) -> tuple[float, float]:
        return self.region.bottom(), self.region.top()


@dataclass
class ConditionalSelection(SelectionCriteria):
    """Value-based conditional selection"""
    condition: str  # Python expression string
    compiled_condition: Callable | None = None

    def __post_init__(self):
        self.selection_type = SelectionType.CONDITIONAL
        self._compile_condition()

    def _compile_condition(self):
        """Compile the condition string into a callable"""
        try:
            # Safe evaluation context
            safe_dict = {
                "__builtins__": {},
                "abs": abs, "min": min, "max": max,
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "sqrt": np.sqrt, "log": np.log, "exp": np.exp,
                "pi": np.pi, "e": np.e,
            }

            # Create lambda function from condition
            # Examples: "value > 10", "abs(value) < 5", "sin(t) > 0.5"
            func_code = f"lambda t, value: {self.condition}"
            self.compiled_condition = eval(func_code, safe_dict)

        except Exception as e:
            logger.exception("conditional_selection_compile_error",
                        condition=self.condition, error=str(e))
            self.compiled_condition = lambda t, value: False

    def matches_point(self, t: float, value: float, **kwargs) -> bool:
        if self.compiled_condition is None:
            return False

        try:
            return bool(self.compiled_condition(t, value))
        except Exception:
            return False


class SelectionState:
    """Current selection state for a dataset/series"""

    def __init__(self, dataset_id: DatasetID, series_id: SeriesID | None = None):
        self.dataset_id = dataset_id
        self.series_id = series_id

        # Selection masks - boolean arrays indicating selected points
        self.selected_mask: np.ndarray | None = None
        self.total_points = 0

        # Active selection criteria
        self.active_criteria: list[SelectionCriteria] = []

        # Cached derived properties
        self._selected_indices: np.ndarray | None = None
        self._time_ranges: list[tuple[float, float]] | None = None
        self._value_stats: dict[str, float] | None = None
        self._dirty = True

    def set_data_size(self, n_points: int):
        """Set the size of the dataset"""
        if self.total_points != n_points:
            self.total_points = n_points
            self.selected_mask = np.zeros(n_points, dtype=bool)
            self._dirty = True

    def apply_criteria(self, criteria: SelectionCriteria,
                      t_data: np.ndarray, value_data: np.ndarray):
        """Apply selection criteria to data"""
        if len(t_data) != len(value_data):
            raise ValueError("Time and value arrays must have same length")

        self.set_data_size(len(t_data))

        # Calculate new selection mask
        new_mask = np.zeros(len(t_data), dtype=bool)
        for i, (t, val) in enumerate(zip(t_data, value_data, strict=False)):
            new_mask[i] = criteria.matches_point(t, val)

        # Apply selection mode
        if criteria.mode == SelectionMode.REPLACE:
            self.selected_mask = new_mask
            self.active_criteria = [criteria]
        elif criteria.mode == SelectionMode.ADD:
            self.selected_mask |= new_mask
            self.active_criteria.append(criteria)
        elif criteria.mode == SelectionMode.SUBTRACT:
            self.selected_mask &= ~new_mask
            self.active_criteria.append(criteria)
        elif criteria.mode == SelectionMode.INTERSECT:
            self.selected_mask &= new_mask
            self.active_criteria.append(criteria)

        self._dirty = True
        logger.debug("selection_criteria_applied",
                    dataset_id=self.dataset_id,
                    series_id=self.series_id,
                    selection_type=criteria.selection_type.value,
                    selected_points=int(np.sum(self.selected_mask)))

    def clear_selection(self):
        """Clear all selections"""
        if self.selected_mask is not None:
            self.selected_mask.fill(False)
        self.active_criteria.clear()
        self._dirty = True
        logger.debug("selection_cleared",
                    dataset_id=self.dataset_id,
                    series_id=self.series_id)

    @property
    def selected_indices(self) -> np.ndarray:
        """Get indices of selected points"""
        if self._dirty or self._selected_indices is None:
            if self.selected_mask is not None:
                self._selected_indices = np.where(self.selected_mask)[0]
            else:
                self._selected_indices = np.array([], dtype=int)
            self._dirty = False
        return self._selected_indices

    @property
    def n_selected(self) -> int:
        """Number of selected points"""
        return len(self.selected_indices)

    @property
    def selection_ratio(self) -> float:
        """Ratio of selected points to total points"""
        if self.total_points == 0:
            return 0.0
        return self.n_selected / self.total_points

    def get_time_ranges(self, t_data: np.ndarray) -> list[tuple[float, float]]:
        """Get continuous time ranges of selection"""
        if self._dirty or self._time_ranges is None:
            self._time_ranges = []

            if self.selected_mask is not None and np.any(self.selected_mask):
                # Find continuous ranges
                selected_indices = self.selected_indices
                if len(selected_indices) > 0:
                    # Group consecutive indices
                    ranges = []
                    start_idx = selected_indices[0]
                    end_idx = selected_indices[0]

                    for i in range(1, len(selected_indices)):
                        if selected_indices[i] == end_idx + 1:
                            end_idx = selected_indices[i]
                        else:
                            # End of continuous range
                            ranges.append((start_idx, end_idx))
                            start_idx = selected_indices[i]
                            end_idx = selected_indices[i]

                    # Add final range
                    ranges.append((start_idx, end_idx))

                    # Convert to time ranges
                    self._time_ranges = [
                        (t_data[start], t_data[end]) for start, end in ranges
                    ]

            self._dirty = False

        return self._time_ranges

    def get_value_statistics(self, value_data: np.ndarray) -> dict[str, float]:
        """Get statistics for selected values"""
        if self._dirty or self._value_stats is None:
            if self.selected_mask is not None and np.any(self.selected_mask):
                selected_values = value_data[self.selected_mask]
                self._value_stats = {
                    "min": float(np.min(selected_values)),
                    "max": float(np.max(selected_values)),
                    "mean": float(np.mean(selected_values)),
                    "std": float(np.std(selected_values)),
                    "median": float(np.median(selected_values)),
                }
            else:
                self._value_stats = {
                    "min": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0, "median": 0.0,
                }
            self._dirty = False

        return self._value_stats


class SelectionManager(QObject):
    """
    Manages advanced selections across datasets and series.

    Features:
    - Multiple selection types (temporal, graphical, conditional)
    - Coordinated selection across multiple series
    - Selection history and undo/redo
    - Export/import of selection criteria
    """

    # Signals
    selection_changed = pyqtSignal(str, str)  # dataset_id, series_id
    selection_cleared = pyqtSignal()
    criteria_applied = pyqtSignal(object)  # SelectionCriteria

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        # Selection states by dataset/series
        self._selection_states: dict[tuple[DatasetID, SeriesID | None], SelectionState] = {}

        # Selection history for undo/redo
        self._history: list[dict[str, Any]] = []
        self._history_index = -1
        self._max_history = 50

        # Coordinate selection across series
        self._coordinated_selection = True
        self._primary_series: tuple[DatasetID, SeriesID] | None = None

        logger.debug("selection_manager_initialized")

    def get_selection_state(self, dataset_id: DatasetID,
                          series_id: SeriesID | None = None) -> SelectionState:
        """Get or create selection state for dataset/series"""
        key = (dataset_id, series_id)

        if key not in self._selection_states:
            self._selection_states[key] = SelectionState(dataset_id, series_id)

        return self._selection_states[key]

    def apply_temporal_selection(self, dataset_id: DatasetID, series_id: SeriesID | None,
                               start_time: float, end_time: float,
                               t_data: np.ndarray, value_data: np.ndarray,
                               mode: SelectionMode = SelectionMode.REPLACE):
        """Apply temporal selection"""
        criteria = TemporalSelection(start_time=start_time, end_time=end_time, mode=mode)
        self._apply_criteria(dataset_id, series_id, criteria, t_data, value_data)

    def apply_graphical_selection(self, dataset_id: DatasetID, series_id: SeriesID | None,
                                region: QRectF, t_data: np.ndarray, value_data: np.ndarray,
                                mode: SelectionMode = SelectionMode.REPLACE):
        """Apply graphical region selection"""
        criteria = GraphicalSelection(region=region, mode=mode)
        self._apply_criteria(dataset_id, series_id, criteria, t_data, value_data)

    def apply_conditional_selection(self, dataset_id: DatasetID, series_id: SeriesID | None,
                                  condition: str, t_data: np.ndarray, value_data: np.ndarray,
                                  mode: SelectionMode = SelectionMode.REPLACE):
        """Apply conditional value-based selection"""
        criteria = ConditionalSelection(condition=condition, mode=mode)
        self._apply_criteria(dataset_id, series_id, criteria, t_data, value_data)

    def _apply_criteria(self, dataset_id: DatasetID, series_id: SeriesID | None,
                       criteria: SelectionCriteria, t_data: np.ndarray, value_data: np.ndarray):
        """Internal method to apply selection criteria"""
        # Save state for undo
        self._save_state_for_undo()

        # Apply to primary series
        state = self.get_selection_state(dataset_id, series_id)
        state.apply_criteria(criteria, t_data, value_data)

        # Apply coordinated selection if enabled
        if self._coordinated_selection and criteria.selection_type == SelectionType.TEMPORAL:
            self._apply_coordinated_temporal_selection(criteria, dataset_id, series_id)

        # Emit signals
        self.criteria_applied.emit(criteria)
        self.selection_changed.emit(dataset_id, series_id or "")

        logger.info("selection_applied",
                   dataset_id=dataset_id,
                   series_id=series_id,
                   selection_type=criteria.selection_type.value,
                   mode=criteria.mode.value)

    def _apply_coordinated_temporal_selection(self, criteria: TemporalSelection,
                                            primary_dataset: DatasetID,
                                            primary_series: SeriesID | None):
        """Apply temporal selection to all other series"""
        if not isinstance(criteria, TemporalSelection):
            return

        # Apply same temporal criteria to all other series
        for (dataset_id, series_id) in self._selection_states:
            if dataset_id == primary_dataset and series_id == primary_series:
                continue  # Skip primary series (already applied)

            # Create coordinated criteria with ADD mode to preserve existing selections
            TemporalSelection(
                start_time=criteria.start_time,
                end_time=criteria.end_time,
                mode=SelectionMode.INTERSECT,  # Intersect with existing selections
            )

            # Note: This would need actual data to apply, which would require
            # integration with data storage/session state

    def clear_selection(self, dataset_id: DatasetID | None = None,
                       series_id: SeriesID | None = None):
        """Clear selection for specific series or all"""
        self._save_state_for_undo()

        if dataset_id is not None:
            key = (dataset_id, series_id)
            if key in self._selection_states:
                self._selection_states[key].clear_selection()
                self.selection_changed.emit(dataset_id, series_id or "")
        else:
            # Clear all selections
            for state in self._selection_states.values():
                state.clear_selection()
            self.selection_cleared.emit()

        logger.debug("selection_cleared",
                    dataset_id=dataset_id,
                    series_id=series_id)

    def _save_state_for_undo(self):
        """Save current selection state for undo functionality"""
        # Create snapshot of current state
        state_snapshot = {}
        for key, state in self._selection_states.items():
            if state.selected_mask is not None:
                state_snapshot[key] = {
                    "selected_mask": state.selected_mask.copy(),
                    "active_criteria": state.active_criteria.copy(),
                }

        # Add to history
        self._history = self._history[:self._history_index + 1]  # Remove future history
        self._history.append(state_snapshot)

        # Limit history size
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        self._history_index = len(self._history) - 1

    def undo_selection(self) -> bool:
        """Undo last selection operation"""
        if self._history_index > 0:
            self._history_index -= 1
            self._restore_state(self._history[self._history_index])
            self.selection_cleared.emit()
            logger.debug("selection_undone")
            return True
        return False

    def redo_selection(self) -> bool:
        """Redo selection operation"""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._restore_state(self._history[self._history_index])
            self.selection_cleared.emit()
            logger.debug("selection_redone")
            return True
        return False

    def _restore_state(self, state_snapshot: dict):
        """Restore selection state from snapshot"""
        # Clear all current selections
        for state in self._selection_states.values():
            state.clear_selection()

        # Restore saved state
        for key, saved_state in state_snapshot.items():
            if key in self._selection_states:
                state = self._selection_states[key]
                state.selected_mask = saved_state["selected_mask"].copy()
                state.active_criteria = saved_state["active_criteria"].copy()
                state._dirty = True

    def get_selection_summary(self) -> dict[str, Any]:
        """Get summary of current selections"""
        summary = {
            "total_series": len(self._selection_states),
            "series_with_selection": 0,
            "total_selected_points": 0,
            "selection_types": set(),
            "coordinated_selection": self._coordinated_selection,
        }

        for state in self._selection_states.values():
            if state.n_selected > 0:
                summary["series_with_selection"] += 1
                summary["total_selected_points"] += state.n_selected

                for criteria in state.active_criteria:
                    summary["selection_types"].add(criteria.selection_type.value)

        summary["selection_types"] = list(summary["selection_types"])
        return summary

    def set_coordinated_selection(self, enabled: bool):
        """Enable/disable coordinated selection across series"""
        self._coordinated_selection = enabled
        logger.debug("coordinated_selection_changed", enabled=enabled)

    def export_selection_criteria(self) -> dict[str, Any]:
        """Export current selection criteria for persistence"""
        exported = {}

        for key, state in self._selection_states.items():
            if state.active_criteria:
                dataset_id, series_id = key
                criteria_data = []

                for criteria in state.active_criteria:
                    if isinstance(criteria, TemporalSelection):
                        criteria_data.append({
                            "type": "temporal",
                            "start_time": criteria.start_time,
                            "end_time": criteria.end_time,
                            "mode": criteria.mode.value,
                        })
                    elif isinstance(criteria, GraphicalSelection):
                        criteria_data.append({
                            "type": "graphical",
                            "region": {
                                "left": criteria.region.left(),
                                "right": criteria.region.right(),
                                "top": criteria.region.top(),
                                "bottom": criteria.region.bottom(),
                            },
                            "mode": criteria.mode.value,
                        })
                    elif isinstance(criteria, ConditionalSelection):
                        criteria_data.append({
                            "type": "conditional",
                            "condition": criteria.condition,
                            "mode": criteria.mode.value,
                        })

                exported[f"{dataset_id}:{series_id or 'all'}"] = criteria_data

        return exported

    def import_selection_criteria(self, imported_data: dict[str, Any]):
        """Import selection criteria from persistence"""
        self._save_state_for_undo()

        for key_str, criteria_list in imported_data.items():
            # Parse key
            if ":" in key_str:
                dataset_id, series_id_str = key_str.split(":", 1)
                series_id = series_id_str if series_id_str != "all" else None
            else:
                continue

            for criteria_data in criteria_list:
                try:
                    criteria_type = criteria_data["type"]
                    mode = SelectionMode(criteria_data.get("mode", "replace"))

                    if criteria_type == "temporal":
                        criteria = TemporalSelection(
                            start_time=criteria_data["start_time"],
                            end_time=criteria_data["end_time"],
                            mode=mode,
                        )
                    elif criteria_type == "graphical":
                        region_data = criteria_data["region"]
                        region = QRectF(
                            region_data["left"], region_data["bottom"],
                            region_data["right"] - region_data["left"],
                            region_data["top"] - region_data["bottom"],
                        )
                        criteria = GraphicalSelection(region=region, mode=mode)
                    elif criteria_type == "conditional":
                        criteria = ConditionalSelection(
                            condition=criteria_data["condition"],
                            mode=mode,
                        )
                    else:
                        continue

                    # Note: Would need actual data integration to apply criteria
                    # For now, just store the criteria structure
                    state = self.get_selection_state(dataset_id, series_id)
                    state.active_criteria.append(criteria)

                except Exception as e:
                    logger.exception("selection_import_error",
                               key=key_str, error=str(e))

        logger.info("selection_criteria_imported",
                   series_count=len(imported_data))
