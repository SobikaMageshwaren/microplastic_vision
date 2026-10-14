import numpy as np
from typing import Tuple
from app.cv.watershed import separate_instances_watershed


class InstanceService:
    def separate_instances(self, cleaned_mask: np.ndarray, min_distance: int = 7) -> Tuple[np.ndarray, int]:
        return separate_instances_watershed(cleaned_mask, min_distance=min_distance)
