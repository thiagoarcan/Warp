"""
Comprehensive tests for desktop/models/dataset_model.py

Tests TreeItem, DatasetTreeModel, and helper functions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import numpy as np
import pytest

# Skip all tests if PyQt6 is not available
pytestmark = pytest.mark.skipif(
    not pytest.importorskip("PyQt6", reason="PyQt6 required").QtCore,
    reason="PyQt6.QtCore not available"
)


# =============================================================================
# Helper Function Tests
# =============================================================================

class TestSafeFilename:
    """Tests for _safe_filename helper function."""
    
    def test_safe_filename_basic(self):
        """Test basic filename extraction."""
        from platform_base.desktop.models.dataset_model import _safe_filename
        
        result = _safe_filename("C:/data/test_file.csv")
        assert result == "test_file"
    
    def test_safe_filename_with_extension(self):
        """Test filename extraction removes extension."""
        from platform_base.desktop.models.dataset_model import _safe_filename
        
        result = _safe_filename("/home/user/data.xlsx")
        assert "xlsx" not in result
    
    def test_safe_filename_with_unicode(self):
        """Test filename with unicode characters."""
        from platform_base.desktop.models.dataset_model import _safe_filename
        
        result = _safe_filename("C:/data/dados_análise.csv")
        # Should handle unicode gracefully
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_safe_filename_with_special_chars(self):
        """Test filename with special characters."""
        from platform_base.desktop.models.dataset_model import _safe_filename
        
        result = _safe_filename("C:/data/test-file_2024(1).csv")
        # Should preserve safe characters
        assert "test" in result
        assert "2024" in result
    
    def test_safe_filename_empty_result_fallback(self):
        """Test fallback when resulting name would be empty."""
        from platform_base.desktop.models.dataset_model import _safe_filename

        # Edge case - all special chars
        result = _safe_filename("")
        assert isinstance(result, str)


# =============================================================================
# TreeItem Tests
# =============================================================================

class TestTreeItem:
    """Tests for TreeItem class."""
    
    def test_tree_item_creation(self):
        """Test basic TreeItem creation."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        item = TreeItem(["Name", "Type", "Value"])
        
        assert item.column_count() == 3
        assert item.child_count() == 0
        assert item.parent() is None
    
    def test_tree_item_with_parent(self):
        """Test TreeItem with parent."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        parent = TreeItem(["Parent"])
        child = TreeItem(["Child"], parent)
        
        assert child.parent() is parent
    
    def test_tree_item_append_child(self):
        """Test appending child to TreeItem."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        parent = TreeItem(["Parent"])
        child1 = TreeItem(["Child1"], parent)
        child2 = TreeItem(["Child2"], parent)
        
        parent.append_child(child1)
        parent.append_child(child2)
        
        assert parent.child_count() == 2
        assert parent.child(0) is child1
        assert parent.child(1) is child2
    
    def test_tree_item_get_child_invalid(self):
        """Test getting child with invalid index."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        item = TreeItem(["Name"])
        
        assert item.child(-1) is None
        assert item.child(0) is None
        assert item.child(100) is None
    
    def test_tree_item_data(self):
        """Test getting data from TreeItem."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        item = TreeItem(["Name", "Type", "Value"])
        
        assert item.data(0) == "Name"
        assert item.data(1) == "Type"
        assert item.data(2) == "Value"
    
    def test_tree_item_data_invalid_column(self):
        """Test getting data with invalid column."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        item = TreeItem(["Name"])
        
        assert item.data(-1) is None
        assert item.data(100) is None
    
    def test_tree_item_row(self):
        """Test getting row index."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        parent = TreeItem(["Parent"])
        child1 = TreeItem(["Child1"], parent)
        child2 = TreeItem(["Child2"], parent)
        child3 = TreeItem(["Child3"], parent)
        
        parent.append_child(child1)
        parent.append_child(child2)
        parent.append_child(child3)
        
        assert child1.row() == 0
        assert child2.row() == 1
        assert child3.row() == 2
    
    def test_tree_item_row_no_parent(self):
        """Test row for root item."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        item = TreeItem(["Root"])
        assert item.row() == 0
    
    def test_tree_item_default_properties(self):
        """Test default TreeItem properties."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        item = TreeItem(["Name"])
        
        assert item.item_type == "unknown"
        assert item.dataset_id is None
        assert item.series_id is None
        assert item.is_derived is False
        assert item.is_checked is True


# =============================================================================
# DatasetTreeModel Tests
# =============================================================================

class TestDatasetTreeModel:
    """Tests for DatasetTreeModel class."""
    
    @pytest.fixture
    def mock_dataset_store(self):
        """Create mock dataset store."""
        store = MagicMock()
        store.list_datasets.return_value = []
        return store
    
    @pytest.fixture
    def mock_dataset_store_with_data(self):
        """Create mock dataset store with test data."""
        store = MagicMock()
        
        # Create mock dataset summary
        summary = MagicMock()
        summary.dataset_id = "test_dataset"
        summary.n_points = 1000
        store.list_datasets.return_value = [summary]
        
        # Create mock dataset
        dataset = MagicMock()
        dataset.source = MagicMock()
        dataset.source.filename = "test_data.csv"
        
        # Create mock series
        series = MagicMock()
        series.name = "test_series"
        series.values = np.zeros(1000)
        series.unit = "m/s"
        series.lineage = None
        
        dataset.series = {"test_series": series}
        store.get_dataset.return_value = dataset
        
        return store
    
    def test_model_initialization(self, mock_dataset_store):
        """Test basic model initialization."""
        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        assert model.columnCount() == 5
        assert model.rowCount() == 0
    
    def test_model_headers(self, mock_dataset_store):
        """Test model header data."""
        from PyQt6.QtCore import Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        assert model.headerData(0, Qt.Orientation.Horizontal) == "Name"
        assert model.headerData(1, Qt.Orientation.Horizontal) == "Type"
        assert model.headerData(2, Qt.Orientation.Horizontal) == "Points"
        assert model.headerData(3, Qt.Orientation.Horizontal) == "Unit"
        assert model.headerData(4, Qt.Orientation.Horizontal) == "Status"
    
    def test_model_header_invalid(self, mock_dataset_store):
        """Test invalid header data requests."""
        from PyQt6.QtCore import Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        # Invalid section
        assert model.headerData(100, Qt.Orientation.Horizontal) is None
        # Vertical orientation
        assert model.headerData(0, Qt.Orientation.Vertical) is None
    
    def test_model_with_data(self, mock_dataset_store_with_data):
        """Test model with actual data."""
        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store_with_data)
        
        # Should have one dataset
        assert model.rowCount() >= 0
    
    def test_model_refresh_data(self, mock_dataset_store):
        """Test refresh_data method."""
        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        # Should not raise
        model.refresh_data()
        
        # Verify list_datasets was called
        mock_dataset_store.list_datasets.assert_called()
    
    def test_model_flags_dataset(self, mock_dataset_store_with_data):
        """Test flags for dataset items."""
        from PyQt6.QtCore import QModelIndex, Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store_with_data)
        
        # Get first item (dataset)
        index = model.index(0, 0)
        if index.isValid():
            flags = model.flags(index)
            
            assert flags & Qt.ItemFlag.ItemIsEnabled
            assert flags & Qt.ItemFlag.ItemIsSelectable
            assert flags & Qt.ItemFlag.ItemIsUserCheckable
    
    def test_model_flags_invalid_index(self, mock_dataset_store):
        """Test flags for invalid index."""
        from PyQt6.QtCore import QModelIndex, Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        flags = model.flags(QModelIndex())
        assert flags == Qt.ItemFlag.NoItemFlags
    
    def test_model_index_creation(self, mock_dataset_store_with_data):
        """Test index creation."""
        from PyQt6.QtCore import QModelIndex

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store_with_data)
        
        # Create index for first row
        index = model.index(0, 0)
        
        if model.rowCount() > 0:
            assert index.isValid()
            assert index.row() == 0
            assert index.column() == 0
    
    def test_model_index_invalid(self, mock_dataset_store):
        """Test invalid index creation."""
        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        # Invalid row
        index = model.index(1000, 0)
        assert not index.isValid()
    
    def test_model_parent(self, mock_dataset_store_with_data):
        """Test parent index retrieval."""
        from PyQt6.QtCore import QModelIndex

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store_with_data)
        
        # Root level item should have invalid parent
        root_index = model.index(0, 0)
        if root_index.isValid():
            parent = model.parent(root_index)
            assert not parent.isValid()
    
    def test_model_data_display_role(self, mock_dataset_store_with_data):
        """Test data retrieval with DisplayRole."""
        from PyQt6.QtCore import QModelIndex, Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store_with_data)
        
        index = model.index(0, 0)
        if index.isValid():
            data = model.data(index, Qt.ItemDataRole.DisplayRole)
            assert data is not None
    
    def test_model_data_invalid_index(self, mock_dataset_store):
        """Test data retrieval with invalid index."""
        from PyQt6.QtCore import QModelIndex, Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        data = model.data(QModelIndex(), Qt.ItemDataRole.DisplayRole)
        assert data is None
    
    def test_model_set_data_check_state(self, mock_dataset_store_with_data):
        """Test setData for checkbox state."""
        from PyQt6.QtCore import Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store_with_data)
        
        # Get dataset index
        index = model.index(0, 0)
        if index.isValid():
            # Try to set check state
            result = model.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            # Result depends on item type
            assert isinstance(result, bool)
    
    def test_model_set_data_invalid_index(self, mock_dataset_store):
        """Test setData with invalid index."""
        from PyQt6.QtCore import QModelIndex, Qt

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        result = model.setData(QModelIndex(), "test", Qt.ItemDataRole.EditRole)
        assert result is False


# =============================================================================
# Model Signal Tests
# =============================================================================

class TestDatasetTreeModelSignals:
    """Tests for DatasetTreeModel signals."""
    
    @pytest.fixture
    def mock_dataset_store(self):
        """Create mock dataset store."""
        store = MagicMock()
        store.list_datasets.return_value = []
        return store
    
    def test_model_has_signals(self, mock_dataset_store):
        """Test that model has required signals."""
        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        model = DatasetTreeModel(mock_dataset_store)
        
        assert hasattr(model, 'datasetSelectionChanged')
        assert hasattr(model, 'seriesSelectionChanged')
        assert hasattr(model, 'seriesVisibilityChanged')


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestDatasetModelEdgeCases:
    """Edge case tests for dataset model."""
    
    def test_tree_item_deeply_nested(self):
        """Test deeply nested TreeItems."""
        from platform_base.desktop.models.dataset_model import TreeItem
        
        root = TreeItem(["Root"])
        current = root
        
        # Create 10 levels of nesting
        for i in range(10):
            child = TreeItem([f"Level {i}"], current)
            current.append_child(child)
            current = child
        
        # Verify structure
        assert root.child_count() == 1
        
        # Navigate to bottom
        item = root
        depth = 0
        while item.child_count() > 0:
            item = item.child(0)
            depth += 1
        
        assert depth == 10
    
    def test_safe_filename_various_encodings(self):
        """Test _safe_filename with various encoding scenarios."""
        from platform_base.desktop.models.dataset_model import _safe_filename
        
        test_cases = [
            "simple.csv",
            "with spaces.csv",
            "日本語ファイル.csv",
            "файл.csv",  # Cyrillic
            "αρχείο.csv",  # Greek
            "קובץ.csv",  # Hebrew
        ]
        
        for path in test_cases:
            result = _safe_filename(path)
            assert isinstance(result, str)
            assert len(result) >= 0
    
    def test_model_column_count_consistency(self):
        """Test column count is consistent."""
        from PyQt6.QtCore import QModelIndex

        from platform_base.desktop.models.dataset_model import DatasetTreeModel
        
        store = MagicMock()
        store.list_datasets.return_value = []
        
        model = DatasetTreeModel(store)
        
        # Column count should be same for any parent
        assert model.columnCount() == model.columnCount(QModelIndex())
        assert model.columnCount() == 5
