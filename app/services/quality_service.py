import numpy as np
from typing import Tuple
from app.cv.quality import validate_image_properties, assess_image_quality
from app.schemas.analysis import ImageValidationInfo, ImageQualityAssessment


class QualityService:
    def validate_and_assess(
        self, filename: str, img_bgr: np.ndarray, gray_img: np.ndarray, file_size_bytes: int
    ) -> Tuple[ImageValidationInfo, ImageQualityAssessment]:
        validation_info = validate_image_properties(filename, img_bgr, file_size_bytes)
        quality_assessment = assess_image_quality(gray_img)
        return validation_info, quality_assessment
