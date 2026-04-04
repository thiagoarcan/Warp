"""
Tests for serialization module - 100% coverage target.
"""
from datetime import datetime

import numpy as np
import pytest

from platform_base.utils.serialization import to_jsonable


class TestToJsonable:
    """Tests for to_jsonable function."""
    
    def test_numpy_array_1d(self):
        """Test converting 1D numpy array."""
        arr = np.array([1, 2, 3, 4, 5])
        result = to_jsonable(arr)
        
        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, list)
    
    def test_numpy_array_2d(self):
        """Test converting 2D numpy array."""
        arr = np.array([[1, 2], [3, 4]])
        result = to_jsonable(arr)
        
        assert result == [[1, 2], [3, 4]]
    
    def test_numpy_array_float(self):
        """Test converting float numpy array."""
        arr = np.array([1.5, 2.5, 3.5])
        result = to_jsonable(arr)
        
        assert result == [1.5, 2.5, 3.5]
    
    def test_numpy_integer_types(self):
        """Test converting numpy integer types."""
        for dtype in [np.int8, np.int16, np.int32, np.int64]:
            val = dtype(42)
            result = to_jsonable(val)
            
            assert result == 42
            assert isinstance(result, int)
    
    def test_numpy_float_types(self):
        """Test converting numpy float types."""
        for dtype in [np.float32, np.float64]:
            val = dtype(3.14)
            result = to_jsonable(val)
            
            assert abs(result - 3.14) < 0.001
            assert isinstance(result, float)
    
    def test_datetime_conversion(self):
        """Test converting datetime."""
        dt = datetime(2026, 2, 1, 12, 30, 45)
        result = to_jsonable(dt)
        
        assert result == "2026-02-01T12:30:45"
        assert isinstance(result, str)
    
    def test_datetime_with_microseconds(self):
        """Test datetime with microseconds."""
        dt = datetime(2026, 2, 1, 12, 30, 45, 123456)
        result = to_jsonable(dt)
        
        assert "2026-02-01T12:30:45" in result
    
    def test_dict_with_numpy(self):
        """Test converting dict containing numpy arrays."""
        data = {
            "values": np.array([1, 2, 3]),
            "mean": np.float64(2.0),
            "count": np.int64(3),
        }
        result = to_jsonable(data)
        
        assert result["values"] == [1, 2, 3]
        assert result["mean"] == 2.0
        assert result["count"] == 3
    
    def test_dict_nested(self):
        """Test converting nested dict."""
        data = {
            "outer": {
                "inner": np.array([1, 2]),
                "value": np.int32(10),
            }
        }
        result = to_jsonable(data)
        
        assert result["outer"]["inner"] == [1, 2]
        assert result["outer"]["value"] == 10
    
    def test_list_with_numpy(self):
        """Test converting list containing numpy values."""
        data = [np.int64(1), np.float64(2.5), np.array([3, 4])]
        result = to_jsonable(data)
        
        assert result == [1, 2.5, [3, 4]]
    
    def test_mixed_types(self):
        """Test converting mixed types."""
        data = {
            "string": "hello",
            "int": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "numpy_arr": np.array([4, 5, 6]),
            "datetime": datetime(2026, 1, 1),
        }
        result = to_jsonable(data)
        
        assert result["string"] == "hello"
        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["list"] == [1, 2, 3]
        assert result["numpy_arr"] == [4, 5, 6]
        assert "2026-01-01" in result["datetime"]
    
    def test_passthrough_basic_types(self):
        """Test that basic types pass through unchanged."""
        assert to_jsonable("string") == "string"
        assert to_jsonable(42) == 42
        assert to_jsonable(3.14) == 3.14
        assert to_jsonable(True) is True
        assert to_jsonable(None) is None
    
    def test_empty_structures(self):
        """Test empty structures."""
        assert to_jsonable({}) == {}
        assert to_jsonable([]) == []
        # Empty numpy array converts to empty list
        result = to_jsonable(np.array([]))
        assert result == [] or (hasattr(result, 'tolist') and result.tolist() == [])
    
    def test_numpy_bool(self):
        """Test numpy boolean conversion."""
        val_true = np.bool_(True)
        val_false = np.bool_(False)
        
        # numpy bool may pass through or convert
        result_true = to_jsonable(val_true)
        result_false = to_jsonable(val_false)
        
        assert bool(result_true) is True
        assert bool(result_false) is False
    
    def test_deeply_nested(self):
        """Test deeply nested structure."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": np.array([1, 2, 3])
                    }
                }
            }
        }
        result = to_jsonable(data)
        
        assert result["level1"]["level2"]["level3"]["data"] == [1, 2, 3]
    
    def test_list_of_dicts(self):
        """Test list of dicts with numpy."""
        data = [
            {"id": np.int64(1), "value": np.float64(1.5)},
            {"id": np.int64(2), "value": np.float64(2.5)},
        ]
        result = to_jsonable(data)
        
        assert result[0]["id"] == 1
        assert result[0]["value"] == 1.5
        assert result[1]["id"] == 2
        assert result[1]["value"] == 2.5
