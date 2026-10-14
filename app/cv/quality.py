import cv2
import numpy as np
from typing import Dict, Any, Tuple, List
from app.core.exceptions import ImageValidationError
from app.schemas.analysis import ImageValidationInfo, ImageQualityAssessment


SUPPORTED_FORMATS = {"PNG", "JPG", "JPEG", "TIFF", "TIF"}


def validate_image_properties(filename: str, img_bgr: np.ndarray, file_size_bytes: int) -> ImageValidationInfo:
    """Validate image format, dimensions, channels, and integrity."""
    ext = filename.split(".")[-1].upper() if "." in filename else ""
    if ext not in SUPPORTED_FORMATS:
        raise ImageValidationError(
            f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    if img_bgr is None or img_bgr.size == 0:
        raise ImageValidationError("Corrupted or unreadable image file.")

    height, width = img_bgr.shape[:2]
    channels = img_bgr.shape[2] if len(img_bgr.shape) == 3 else 1

    if width < 32 or height < 32:
        raise ImageValidationError(f"Image dimensions ({width}x{height}) are too small for microplastic analysis.")

    return ImageValidationInfo(
        valid=True,
        width=width,
        height=height,
        channels=channels,
        format=ext,
        file_size_bytes=file_size_bytes
    )


def assess_image_quality(gray_img: np.ndarray) -> ImageQualityAssessment:
    """
    Assess blur, contrast, noise, and heuristic quality score (0-100).
    """
    warnings: List[str] = []

    # 1. Blur calculation via Variance of Laplacian
    blur_score = float(cv2.Laplacian(gray_img, cv2.CV_64F).var())
    if blur_score < 100.0:
        warnings.append(f"Image appears blurry (Laplacian variance: {blur_score:.1f})")

    # 2. Contrast statistics
    mean_val = float(np.mean(gray_img))
    std_val = float(np.std(gray_img))
    min_val, max_val = float(np.min(gray_img)), float(np.max(gray_img))
    dynamic_range = max_val - min_val
    contrast_score = std_val

    if std_val < 20.0 or dynamic_range < 50:
        warnings.append(f"Low contrast image detected (std: {std_val:.1f}, dynamic range: {dynamic_range:.0f})")

    # 3. High-frequency noise estimation
    # High-pass filter via Median blur difference
    blurred = cv2.medianBlur(gray_img, 3)
    noise_diff = cv2.absdiff(gray_img, blurred)
    noise_score = float(np.mean(noise_diff))
    if noise_score > 25.0:
        warnings.append(f"High background noise detected (noise score: {noise_score:.1f})")

    # 4. Heuristic Quality Score calculation (0 to 100)
    # Norm components:
    blur_norm = min(1.0, blur_score / 500.0)
    contrast_norm = min(1.0, contrast_score / 64.0)
    noise_penalty = max(0.0, 1.0 - (noise_score / 40.0))

    # Weighted quality score calculation
    quality_score = (0.45 * blur_norm + 0.45 * contrast_norm + 0.10 * noise_penalty) * 100.0
    quality_score = round(float(np.clip(quality_score, 0.0, 100.0)), 2)

    return ImageQualityAssessment(
        blur_score=round(blur_score, 2),
        contrast_score=round(contrast_score, 2),
        noise_score=round(noise_score, 2),
        quality_score=quality_score,
        warnings=warnings
    )
