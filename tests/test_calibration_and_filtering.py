import pytest
import numpy as np
import cv2
from pathlib import Path
from app.cv.contours import extract_particle_regions
from app.cv.features import extract_particle_features


def test_particle_min_area_filtering(tmp_path):
    # Create watershed labels with 3 synthetic particles (areas: 2 px, 20 px, 200 px)
    labels = np.zeros((100, 100), dtype=np.int32)
    labels[10:12, 10:11] = 1   # Area = 2 px (noise)
    labels[20:25, 20:24] = 2   # Area = 20 px (valid)
    labels[40:50, 40:60] = 3   # Area = 200 px (valid)

    dummy_bgr = np.zeros((100, 100, 3), dtype=np.uint8)
    
    result = extract_particle_regions(
        watershed_labels=labels,
        img_bgr=dummy_bgr,
        analysis_id="test_filter",
        output_dir=tmp_path,
        min_area_pixels=5
    )

    assert result["total_detected_objects"] == 3
    assert result["valid_particles"] == 2
    assert result["filtered_objects"] == 1
    assert len(result["particles"]) == 2


def test_physical_calibration_conversions():
    dummy_info = {
        "particle_id": "P001",
        "mask": np.ones((10, 10), dtype=np.uint8) * 255,
        "contour": np.array([[[0, 0]], [[10, 0]], [[10, 10]], [[0, 10]]]),
        "bbox": {"x": 0, "y": 0, "width": 10, "height": 10},
        "centroid": {"x": 5.0, "y": 5.0}
    }
    gray_img = np.ones((20, 20), dtype=np.uint8) * 128
    
    # Test without calibration
    feat_uncalibrated = extract_particle_features(
        particle_info=dummy_info,
        gray_img=gray_img,
        analysis_id="test_calib",
        pixel_size_um=None
    )
    assert feat_uncalibrated.pixel_size_um is None
    assert feat_uncalibrated.area_um2 is None

    # Test with calibration 0.85 um/pixel
    pixel_scale = 0.85
    feat_calibrated = extract_particle_features(
        particle_info=dummy_info,
        gray_img=gray_img,
        analysis_id="test_calib",
        pixel_size_um=pixel_scale
    )
    assert feat_calibrated.pixel_size_um == 0.85
    assert feat_calibrated.area_um2 == round(feat_calibrated.area * (pixel_scale ** 2), 2)
    assert feat_calibrated.width_um == round(10 * pixel_scale, 2)
    assert feat_calibrated.height_um == round(10 * pixel_scale, 2)
