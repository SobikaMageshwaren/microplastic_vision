import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "degraded"}
    assert "api" in data
    assert "database" in data
    assert "storage" in data
    assert "pipeline" in data


def test_missing_analysis_404_json_error():
    response = client.get("/api/v1/analysis/MPV-NONEXISTENT-999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "ANALYSIS_NOT_FOUND"
    assert "not found" in data["error"]["message"].lower()


def test_invalid_image_upload_400():
    files = {'file': ('empty.txt', b'', 'text/plain')}
    response = client.post("/api/v1/analysis", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_validation_error_422():
    response = client.post("/api/v1/analysis", data={"min_area_pixels": -100})
    assert response.status_code in {400, 422}
    data = response.json()
    assert "error" in data
