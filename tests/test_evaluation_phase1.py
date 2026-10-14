import cv2
import numpy as np
import pytest
from app.services.evaluation_service import EvaluationService


def test_evaluation_service_error_maps():
    # Synthetic ground truth circle
    gt = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(gt, (50, 50), 20, 255, -1)

    # Synthetic prediction circle slightly shifted
    pred = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(pred, (55, 50), 20, 255, -1)

    eval_service = EvaluationService()
    res = eval_service.evaluate_masks(
        predicted_mask_input=pred,
        ground_truth_mask_input=gt,
        image_name="test_synthetic_sample"
    )

    assert res.iou > 0.5
    assert res.dice > 0.6
    assert res.tp_pixels > 0
    assert res.fp_pixels > 0
    assert res.fn_pixels > 0
    assert res.error_map_path is not None
    assert res.overlay_path is not None
