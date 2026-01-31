"""
DatasetModel - QAbstractItemModel for datasets and series tree view

Provides model-view integration for dataset/series hierarchical data display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.core.dataset_store import DatasetStore


logger = get_logger(__name__)


class TreeItem:
    """Tree item for hierarchical model"""

    def __init__(self, data: list[Any], parent_item: TreeItem | None = None):
        self.item_data = data
        self.parent_item = parent_item
        self.child_items: list[TreeItem] = []

        # Additional properties for dataset/series items
        self.item_type = "unknown"  # "dataset", "series"
        self.dataset_id: str | None = None
        self.series_id: str | None = None
        self.is_derived = False
        self.is_checked = True  # Default to checked (visible)

    def append_child(self, item: TreeItem):
        """Add child item"""
        self.child_items.append(item)

    def child(self, row: int) -> TreeItem | None:
        """Get child at row"""
        if 0 <= row < len(self.child_items):
            return self.child_items[row]
        return None

    def child_count(self) -> int:
        """Get number of children"""
        return len(self.child_items)

    def column_count(self) -> int:
        """Get number of columns"""
        return len(self.item_data)

    def data(self, column: int) -> Any:
        """Get data for column"""
        if 0 <= column < len(self.item_data):
            return self.item_data[column]
        return None

    def parent(self) -> TreeItem | None:
        """Get parent item"""
        return self.parent_item

    def row(self) -> int:
        """Get row index in parent"""
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0


class DatasetTreeModel(QAbstractItemModel):
    """
    Tree model for datasets and series hierarchy.

    Structure:
    - Root
      - Dataset 1
        - Series 1.1
        - Series 1.2 (derived)
      - Dataset 2
        - Series 2.1
    """

    # Signals
    datasetSelectionChanged = pyqtSignal(str)  # dataset_id
    seriesSelectionChanged = pyqtSignal(str, str)  # dataset_id, series_id
    seriesVisibilityChanged = pyqtSignal(str, str, bool)  # dataset_id, series_id, visible

    def __init__(self, dataset_store: DatasetStore, parent=None):
        super().__init__(parent)

        self.dataset_store = dataset_store
        self.headers = ["Name", "Type", "Points", "Unit", "Status"]

        # Create root item
        self.root_item = TreeItem(self.headers)

        # Load initial data
        self.refresh_data()

        logger.debug("dataset_tree_model_initialized")

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of columns"""
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for the given index and role"""
        if not index.isValid():
            return None

        item: TreeItem = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            return item.data(index.column())

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            # Return checkbox state for first column (series items only)
            if item.item_type == "series":
                return Qt.CheckState.Checked if item.is_checked else Qt.CheckState.Unchecked
            elif item.item_type == "dataset":
                # Dataset is checked if all children are checked
                if item.child_count() == 0:
                    return Qt.CheckState.Unchecked
                all_checked = all(child.is_checked for child in item.child_items)
                none_checked = not any(child.is_checked for child in item.child_items)
                if all_checked:
                    return Qt.CheckState.Checked
                elif none_checked:
                    return Qt.CheckState.Unchecked
                else:
                    return Qt.CheckState.PartiallyChecked

        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            # Return icon for first column
            if item.item_type == "dataset":
                return self._get_dataset_icon()
            if item.item_type == "series":
                if item.is_derived:
                    return self._get_derived_series_icon()
                return self._get_series_icon()

        elif role == Qt.ItemDataRole.ToolTipRole:
            return self._get_tooltip(item)

        elif role == Qt.ItemDataRole.UserRole:
            # Return custom data
            return {
                "item_type": item.item_type,
                "dataset_id": item.dataset_id,
                "series_id": item.series_id,
                "is_derived": item.is_derived,
                "is_checked": item.is_checked,
            }

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """Set data for the given index"""
        if not index.isValid():
            return False

        item: TreeItem = index.internalPointer()

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            new_state = value == Qt.CheckState.Checked.value or value == Qt.CheckState.Checked

            if item.item_type == "series":
                item.is_checked = new_state
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

                # Emit visibility change signal
                self.seriesVisibilityChanged.emit(item.dataset_id, item.series_id, new_state)

                # Update parent dataset checkbox state
                parent_index = self.parent(index)
                if parent_index.isValid():
                    self.dataChanged.emit(parent_index, parent_index, [Qt.ItemDataRole.CheckStateRole])

                logger.debug("series_visibility_changed",
                           dataset_id=item.dataset_id, series_id=item.series_id, visible=new_state)
                return True

            elif item.item_type == "dataset":
                # Toggle all children
                for child in item.child_items:
                    child.is_checked = new_state
                    self.seriesVisibilityChanged.emit(child.dataset_id, child.series_id, new_state)

                # Emit data changed for all children
                first_child = self.index(0, 0, index)
                last_child = self.index(item.child_count() - 1, 0, index)
                if first_child.isValid() and last_child.isValid():
                    self.dataChanged.emit(first_child, last_child, [Qt.ItemDataRole.CheckStateRole])
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

                logger.debug("dataset_visibility_changed",
                           dataset_id=item.dataset_id, visible=new_state)
                return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return item flags"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        base_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        # Add checkbox flag for first column
        if index.column() == 0:
            item: TreeItem = index.internalPointer()
            if item.item_type in ("dataset", "series"):
                base_flags |= Qt.ItemFlag.ItemIsUserCheckable

        return base_flags

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return header data"""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self.headers):
                return self.headers[section]

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for the given row and column"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self.root_item if not parent.isValid() else parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Return parent index"""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of rows under the given parent"""
        if parent.column() > 0:
            return 0

        parent_item = self.root_item if not parent.isValid() else parent.internalPointer()

        return parent_item.child_count()

    def refresh_data(self):
        """Refresh model data from dataset store"""
        logger.debug("refreshing_dataset_model_data")

        self.beginResetModel()

        # Clear existing data
        self.root_item.child_items.clear()

        try:
            # Get datasets
            dataset_summaries = self.dataset_store.list_datasets()

            for summary in dataset_summaries:
                # Get dataset to get filename
                try:
                    dataset = self.dataset_store.get_dataset(summary.dataset_id)
                    # Use filename for display, fallback to dataset_id
                    from pathlib import Path
                    if hasattr(dataset, 'source') and dataset.source and hasattr(dataset.source, 'filename'):
                        display_name = Path(dataset.source.filename).stem  # Remove extension
                    else:
                        display_name = summary.dataset_id
                except Exception:
                    display_name = summary.dataset_id
                    dataset = None

                # Create dataset item with filename
                dataset_item = TreeItem([
                    display_name,  # BUG-007 FIX: Use filename instead of dataset_id
                    "Dataset",
                    f"{summary.n_points:,}",
                    "",
                    "Loaded",
                ], self.root_item)

                dataset_item.item_type = "dataset"
                dataset_item.dataset_id = summary.dataset_id

                self.root_item.append_child(dataset_item)

                try:
                    # Get dataset details for series (if not already loaded)
                    if dataset is None:
                        dataset = self.dataset_store.get_dataset(summary.dataset_id)

                    for series_id, series in dataset.series.items():
                        # Create series item
                        status = "Derived" if series.lineage else "Original"

                        series_item = TreeItem([
                            series.name,
                            "Series",
                            f"{len(series.values):,}",
                            str(series.unit),
                            status,
                        ], dataset_item)

                        series_item.item_type = "series"
                        series_item.dataset_id = summary.dataset_id
                        series_item.series_id = series_id
                        series_item.is_derived = series.lineage is not None

                        dataset_item.append_child(series_item)

                except Exception as e:
                    logger.exception("failed_to_load_series_for_dataset",
                               dataset_id=summary.dataset_id, error=str(e))

                    # Add error item
                    error_item = TreeItem([
                        "Error loading series",
                        "Error",
                        "",
                        "",
                        str(e),
                    ], dataset_item)
                    error_item.item_type = "error"
                    dataset_item.append_child(error_item)

        except Exception as e:
            logger.exception("failed_to_refresh_dataset_model", error=str(e))

            # Add error item to root
            error_item = TreeItem([
                "Error loading datasets",
                "Error",
                "",
                "",
                str(e),
            ], self.root_item)
            error_item.item_type = "error"
            self.root_item.append_child(error_item)

        self.endResetModel()
        logger.debug("dataset_model_data_refreshed",
                    datasets=self.root_item.child_count())

    def add_dataset(self, dataset_id: str):
        """Add new dataset to model"""
        logger.debug("adding_dataset_to_model", dataset_id=dataset_id)

        try:
            # Find insertion point
            row = self.root_item.child_count()

            self.beginInsertRows(QModelIndex(), row, row)

            # Get dataset summary
            summary = None
            for s in self.dataset_store.list_datasets():
                if s.dataset_id == dataset_id:
                    summary = s
                    break

            if summary:
                # Create dataset item
                dataset_item = TreeItem([
                    summary.dataset_id,
                    "Dataset",
                    f"{summary.n_points:,}",
                    "",
                    "Loaded",
                ], self.root_item)

                dataset_item.item_type = "dataset"
                dataset_item.dataset_id = summary.dataset_id

                self.root_item.append_child(dataset_item)

                # Load series
                self._load_series_for_dataset(dataset_item)

            self.endInsertRows()

        except Exception as e:
            logger.exception("failed_to_add_dataset_to_model",
                        dataset_id=dataset_id, error=str(e))

    def remove_dataset(self, dataset_id: str):
        """Remove dataset from model"""
        logger.debug("removing_dataset_from_model", dataset_id=dataset_id)

        # Find dataset item
        for row in range(self.root_item.child_count()):
            item = self.root_item.child(row)
            if item and item.dataset_id == dataset_id:
                self.beginRemoveRows(QModelIndex(), row, row)
                self.root_item.child_items.pop(row)
                self.endRemoveRows()
                break

    def add_series(self, dataset_id: str, series_id: str):
        """Add new series to dataset"""
        logger.debug("adding_series_to_model",
                    dataset_id=dataset_id, series_id=series_id)

        # Find dataset item
        for dataset_row in range(self.root_item.child_count()):
            dataset_item = self.root_item.child(dataset_row)
            if dataset_item and dataset_item.dataset_id == dataset_id:

                try:
                    # Get series details
                    dataset = self.dataset_store.get_dataset(dataset_id)
                    series = dataset.series[series_id]

                    # Insert new series
                    series_row = dataset_item.child_count()
                    dataset_index = self.createIndex(dataset_row, 0, dataset_item)

                    self.beginInsertRows(dataset_index, series_row, series_row)

                    status = "Derived" if series.lineage else "Original"

                    series_item = TreeItem([
                        series.name,
                        "Series",
                        f"{len(series.values):,}",
                        str(series.unit),
                        status,
                    ], dataset_item)

                    series_item.item_type = "series"
                    series_item.dataset_id = dataset_id
                    series_item.series_id = series_id
                    series_item.is_derived = series.lineage is not None

                    dataset_item.append_child(series_item)

                    self.endInsertRows()

                except Exception as e:
                    logger.exception("failed_to_add_series_to_model",
                                dataset_id=dataset_id, series_id=series_id, error=str(e))
                break

    def _load_series_for_dataset(self, dataset_item: TreeItem):
        """Load series for a dataset item"""
        try:
            dataset = self.dataset_store.get_dataset(dataset_item.dataset_id)

            for series_id, series in dataset.series.items():
                status = "Derived" if series.lineage else "Original"

                series_item = TreeItem([
                    series.name,
                    "Series",
                    f"{len(series.values):,}",
                    str(series.unit),
                    status,
                ], dataset_item)

                series_item.item_type = "series"
                series_item.dataset_id = dataset_item.dataset_id
                series_item.series_id = series_id
                series_item.is_derived = series.lineage is not None

                dataset_item.append_child(series_item)

        except Exception as e:
            logger.exception("failed_to_load_series",
                        dataset_id=dataset_item.dataset_id, error=str(e))

    def _get_tooltip(self, item: TreeItem) -> str:
        """Get tooltip for item"""
        if item.item_type == "dataset":
            try:
                dataset = self.dataset_store.get_dataset(item.dataset_id)
                return (f"Dataset: {dataset.source.filename}\n"
                       f"Full Path: {dataset.source.filepath}\n"
                       f"Format: {dataset.source.format.upper()}\n"
                       f"Size: {dataset.source.size_bytes / 1024 / 1024:.2f} MB\n"
                       f"Points: {len(dataset.t_seconds):,}\n"
                       f"Series: {len(dataset.series)}\n"
                       f"ID: {item.dataset_id}")
            except Exception:
                return f"Dataset: {item.dataset_id}"

        elif item.item_type == "series":
            try:
                dataset = self.dataset_store.get_dataset(item.dataset_id)
                series = dataset.series[item.series_id]
                nan_count = np.isnan(series.values).sum()
                valid_count = len(series.values) - nan_count
                return (f"Series: {series.name}\n"
                       f"Unit: {series.unit or 'N/A'}\n"
                       f"Points: {len(series.values):,}\n"
                       f"Valid: {valid_count:,} ({100*valid_count/len(series.values):.1f}%)\n"
                       f"NaN: {nan_count:,}\n"
                       f"Type: {'Derived' if series.lineage else 'Original'}\n"
                       f"ID: {item.series_id}")
            except Exception:
                return f"Series: {item.series_id}"

        return ""

    def _get_dataset_icon(self) -> QIcon:
        """Get icon for dataset items"""
        # In a real implementation, load from resources
        return QIcon()

    def _get_series_icon(self) -> QIcon:
        """Get icon for series items"""
        return QIcon()

    def _get_derived_series_icon(self) -> QIcon:
        """Get icon for derived series items"""
        return QIcon()

    def get_item_info(self, index: QModelIndex) -> dict[str, Any] | None:
        """Get detailed information about an item"""
        if not index.isValid():
            return None

        item: TreeItem = index.internalPointer()

        return {
            "item_type": item.item_type,
            "dataset_id": item.dataset_id,
            "series_id": item.series_id,
            "is_derived": item.is_derived,
            "display_text": item.data(0),
        }

    def find_dataset_index(self, dataset_id: str) -> QModelIndex:
        """Find index for dataset"""
        for row in range(self.root_item.child_count()):
            item = self.root_item.child(row)
            if item and item.dataset_id == dataset_id:
                return self.createIndex(row, 0, item)
        return QModelIndex()

    def find_series_index(self, dataset_id: str, series_id: str) -> QModelIndex:
        """Find index for series"""
        dataset_index = self.find_dataset_index(dataset_id)
        if not dataset_index.isValid():
            return QModelIndex()

        dataset_item = dataset_index.internalPointer()
        for row in range(dataset_item.child_count()):
            item = dataset_item.child(row)
            if item and item.series_id == series_id:
                return self.createIndex(row, 0, item)

        return QModelIndex()
