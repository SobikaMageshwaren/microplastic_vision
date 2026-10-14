import os
import pytest
import numpy as np
import torch
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.ml.models.unet import UNet
from app.ml.dataset import get_dataset_splits
from app.ml.inference import UNetInferenceEngine
from app.ml.explainability.saliency import generate_saliency_heatmap
from app.db.database import SessionLocal, engine, Base
from app.db import crud

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_unet_architecture_forward():
    """Verify PyTorch 4-depth U-Net architecture forward pass tensor dimensions."""
    model = UNet(in_channels=3, out_channels=1, base_features=32)
    dummy_input = torch.randn(1, 3, 256, 256)
    out = model(dummy_input)
    assert out.shape == (1, 1, 256, 256)

def test_dataset_splits():
    """Verify deterministic splitting of 5 matched annotation pairs."""
    dataset_info = get_dataset_splits()
    assert dataset_info["total_pairs"] == 5
    assert len(dataset_info["train_ids"]) == 4
    assert len(dataset_info["val_ids"]) == 1

def test_saliency_heatmap_generation():
    """Verify Input-Gradient Saliency Attribution map generation."""
    model = UNet(in_channels=3, out_channels=1, base_features=32)
    model.eval()
    dummy_image = np.ones((128, 128, 3), dtype=np.uint8) * 120
    saliency_gray, saliency_colored = generate_saliency_heatmap(model, dummy_image, device="cpu")
    assert isinstance(saliency_colored, np.ndarray)
    assert saliency_colored.shape == (128, 128, 3)

def test_inference_engine(tmp_path):
    """Verify U-Net inference engine prediction and thresholding."""
    engine_inst = UNetInferenceEngine()
    dummy_image = np.ones((128, 128, 3), dtype=np.uint8) * 150
    result = engine_inst.predict(dummy_image, analysis_id="test_dl_01", output_dir=tmp_path, threshold=0.5)
    assert "artifacts" in result
    assert "binary_mask" in result["artifacts"]
    assert "particle_count" in result

def test_model_registry_crud(setup_test_db):
    """Verify registration and retrieval of models in model registry."""
    db = setup_test_db
    reg = crud.register_trained_model(
        db=db,
        model_id="test-unet-v1",
        model_name="Test UNet",
        architecture="UNet-4Depth",
        version="v1.0",
        checkpoint_path="checkpoints/unet_classical_cv_v1.pth",
        metrics={"best_val_dice": 0.99}
    )
    assert reg.model_name == "Test UNet"

    models = crud.list_registered_models(db)
    assert len(models) >= 1

def test_api_routes():
    """Verify Phase 3 FastAPI router endpoints."""
    # 1. List models
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 2. Model comparison
    res = client.get("/api/v1/models/comparison?image_id=RR1.tiff")
    assert res.status_code == 200
    data = res.json()
    assert "evaluated_image" in data
    assert "metrics_comparison" in data
    assert len(data["metrics_comparison"]) >= 2

    # 3. Model explainability endpoint
    sample_file_path = Path("dataset/original_size/RR1.tiff")
    if sample_file_path.exists():
        with open(sample_file_path, "rb") as f:
            res = client.post(
                "/api/v1/models/unet-baseline-v1/explain",
                files={"file": ("RR1.tiff", f, "image/tiff")}
            )
        assert res.status_code == 200
        data = res.json()
        assert "heatmap_path" in data
        assert "explainability_method" in data
