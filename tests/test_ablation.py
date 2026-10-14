import cv2
import numpy as np
import pytest
from app.services.ablation_service import AblationService


def test_ablation_service_execution():
    # Synthetic microscopy image with a white particle
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 15, (200, 200, 200), -1)

    # Synthetic ground truth mask
    gt = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(gt, (50, 50), 15, 255, -1)

    ablation_service = AblationService()
    res = ablation_service.run_ablation_study(img, gt, image_name="test_ablation_sample")

    assert res.experiment_id.startswith("ABLATION-")
    assert res.pipeline_version == "classical-cv-v1.1"
    assert len(res.results_table) == 4
    
    stages = [r.config_name for r in res.results_table]
    assert "Baseline Otsu" in stages
    assert "+ Preprocessing" in stages
    assert "+ Morphology" in stages
    assert "+ Watershed Instance Split" in stages

    for r in res.results_table:
        assert 0.0 <= r.iou <= 1.0
        assert 0.0 <= r.dice <= 1.0
