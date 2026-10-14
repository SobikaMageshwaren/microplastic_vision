import cv2
import numpy as np
import pytest
from app.cv.features import extract_particle_features


def test_particle_features_extraction():
    # Synthetic circular particle
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(mask, (50, 50), 20, 255, -1)
    gray = mask.copy()

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]

    particle_info = {
        "particle_id": "P001",
        "mask": mask,
        "contour": contour,
        "bbox": {"x": 30, "y": 30, "width": 40, "height": 40},
        "centroid": {"x": 50.0, "y": 50.0},
        "crop_path": None
    }

    features = extract_particle_features(particle_info, gray, "ana_test")
    assert features.particle_id == "P001"
    assert features.area > 1000.0  # pi * 20^2 approx 1256
    assert features.circularity > 0.8
    assert features.solidity > 0.9
