import cv2
import numpy as np
import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()



def test_full_analysis_endpoint_synthetic_image():
    # Create synthetic test image in memory
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 15, (255, 255, 255), -1)
    cv2.rectangle(img, (120, 120), (160, 160), (255, 255, 255), -1)

    is_success, buffer = cv2.imencode(".png", img)
    assert is_success

    file_bytes = io.BytesIO(buffer.tobytes())

    response = client.post(
        "/api/v1/analysis",
        files={"file": ("test_microscopy.png", file_bytes, "image/png")}
    )

    assert response.status_code == 201
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "completed"
    assert data["particle_count"] >= 1
    assert "quality_score" in data

    analysis_id = data["analysis_id"]

    # Test retrieval of analysis details
    detail_res = client.get(f"/api/v1/analysis/{analysis_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["analysis_id"] == analysis_id
    assert len(detail_data["particles"]) >= 1
    assert "original" in detail_data["artifacts"]

    # Test retrieval of particles endpoint
    particles_res = client.get(f"/api/v1/analysis/{analysis_id}/particles")
    assert particles_res.status_code == 200
    particles_data = particles_res.json()
    assert len(particles_data) >= 1

    # Test retrieval of individual particle
    pid = particles_data[0]["particle_id"]
    single_p_res = client.get(f"/api/v1/analysis/{analysis_id}/particles/{pid}")
    assert single_p_res.status_code == 200
    assert single_p_res.json()["particle_id"] == pid

    # Test retrieval of artifacts endpoint
    artifacts_res = client.get(f"/api/v1/analysis/{analysis_id}/artifacts")
    assert artifacts_res.status_code == 200
    assert "original" in artifacts_res.json()
