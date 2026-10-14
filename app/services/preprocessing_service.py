import numpy as np
from typing import Tuple, Dict
from app.cv.preprocessing import preprocess_image
from app.schemas.analysis import PreprocessingConfig


class PreprocessingService:
    def process(
        self, img_bgr: np.ndarray, gray_img: np.ndarray, config: PreprocessingConfig
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        return preprocess_image(img_bgr, gray_img, config)
