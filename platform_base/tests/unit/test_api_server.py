"""
Unit tests for API Server module.

Tests for:
- FastAPI app creation
- Request/Response models
- API endpoints
"""

import pytest
from pydantic import ValidationError

try:
    from platform_base.api.server import FASTAPI_AVAILABLE
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    from platform_base.api.server import InterpolationRequest, ViewRequest, create_app
    from platform_base.core.dataset_store import DatasetStore

pytestmark = pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")


class TestInterpolationRequest:
    """Tests for InterpolationRequest model"""

    def test_basic_creation(self):
        """Test basic request creation"""
        request = InterpolationRequest(method="linear")
        assert request.method == "linear"
        assert request.params == {}

    def test_with_params(self):
        """Test request with parameters"""
        request = InterpolationRequest(
            method="cubic",
            params={"fill_value": "extrapolate"}
        )
        assert request.method == "cubic"
        assert request.params["fill_value"] == "extrapolate"

    def test_method_required(self):
        """Method field should be required"""
        with pytest.raises(ValidationError):
            InterpolationRequest()

    def test_various_methods(self):
        """Test various interpolation methods"""
        methods = ["linear", "cubic", "nearest", "spline", "akima"]
        for method in methods:
            request = InterpolationRequest(method=method)
            assert request.method == method


class TestViewRequest:
    """Tests for ViewRequest model"""

    def test_basic_creation(self):
        """Test basic view request creation"""
        request = ViewRequest(
            series_ids=["series1", "series2"],
            window={"start": 0.0, "end": 10.0}
        )
        assert len(request.series_ids) == 2
        assert "series1" in request.series_ids

    def test_single_series(self):
        """Test view request with single series"""
        request = ViewRequest(
            series_ids=["only_series"],
            window={"start": 0.0, "end": 100.0}
        )
        assert len(request.series_ids) == 1

    def test_empty_series_ids(self):
        """Test view request with empty series list"""
        request = ViewRequest(
            series_ids=[],
            window={"start": 0.0, "end": 10.0}
        )
        assert len(request.series_ids) == 0


class TestCreateApp:
    """Tests for app creation"""

    def test_app_creation_without_store(self):
        """Test app creation without providing store"""
        app = create_app()
        assert app is not None
        assert app.title == "Platform Base API"
        assert app.version == "2.0.0"

    def test_app_creation_with_store(self):
        """Test app creation with custom store"""
        store = DatasetStore()
        app = create_app(store=store)
        assert app is not None
        assert app.title == "Platform Base API"

    def test_app_has_cors_middleware(self):
        """Test that CORS middleware is added"""
        app = create_app()
        # Check if middleware is configured
        middleware_names = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_names

    def test_app_routes_exist(self):
        """Test that expected routes are defined"""
        app = create_app()
        routes = [r.path for r in app.routes]
        
        assert "/datasets/upload" in routes
        assert "/datasets" in routes


class TestAPIEndpointsUnit:
    """Unit tests for API endpoints (no actual HTTP calls)"""

    def test_list_datasets_empty(self):
        """Test listing datasets when empty"""
        store = DatasetStore()
        # Store starts empty
        datasets = store.list_datasets()
        assert len(datasets) == 0

    def test_store_operations(self):
        """Test dataset store operations"""
        store = DatasetStore()
        
        # Initially empty
        assert len(store.list_datasets()) == 0


class TestInterpolationRequestValidation:
    """Tests for request validation"""

    def test_valid_params_types(self):
        """Test various param types"""
        request = InterpolationRequest(
            method="spline",
            params={
                "order": 3,
                "smooth": 0.5,
                "extrapolate": True
            }
        )
        assert request.params["order"] == 3
        assert request.params["smooth"] == 0.5
        assert request.params["extrapolate"] is True

    def test_nested_params(self):
        """Test nested parameters"""
        request = InterpolationRequest(
            method="custom",
            params={
                "options": {
                    "fill_value": 0,
                    "bounds_error": False
                }
            }
        )
        assert request.params["options"]["fill_value"] == 0


class TestViewRequestValidation:
    """Tests for view request validation"""

    def test_multiple_series(self):
        """Test request with multiple series"""
        series_ids = [f"series_{i}" for i in range(10)]
        request = ViewRequest(
            series_ids=series_ids,
            window={"start": 0.0, "end": 1000.0}
        )
        assert len(request.series_ids) == 10

    def test_window_types(self):
        """Test various window specifications"""
        request = ViewRequest(
            series_ids=["test"],
            window={"start": 0, "end": 100}  # Int values
        )
        assert request.window["start"] == 0
        assert request.window["end"] == 100


# Integration tests would require TestClient from fastapi
@pytest.mark.skipif(True, reason="Integration test - requires full server setup")
class TestAPIIntegration:
    """Integration tests for API - skipped without full setup"""
    
    def test_upload_and_list(self):
        """Test upload dataset and list it"""
        pass

    def test_interpolate_endpoint(self):
        """Test interpolation endpoint"""
        pass
