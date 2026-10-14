import cv2
import numpy as np
import pytest
from app.cv.thresholding import ClassicalSegmentationEngine
from app.cv.watershed import separate_instances_watershed


def test_classical_segmentation():
    # Synthetic image with a white circle particle in the middle
    gray = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(gray, (50, 50), 20, 255, -1)

    engine = ClassicalSegmentationEngine()
    raw_mask, cleaned_mask = engine.segment(gray, {"threshold_method": "otsu"})

    assert raw_mask.shape == (100, 100)
    assert cleaned_mask.shape == (100, 100)
    assert np.count_nonzero(cleaned_mask) > 0


def test_watershed_instance_separation():
    # Synthetic image with two touching circles
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(mask, (35, 50), 15, 255, -1)
    cv2.circle(mask, (65, 50), 15, 255, -1)

    labels, particle_count = separate_instances_watershed(mask, min_distance=5)
    assert labels.shape == (100, 100)
    assert particle_count >= 1
