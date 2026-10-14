import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from typing import Tuple, List, Dict, Any


def separate_instances_watershed(cleaned_mask: np.ndarray, min_distance: int = 7) -> Tuple[np.ndarray, int]:
    """
    Perform Watershed instance separation on touching/overlapping microplastic particles.
    
    Args:
        cleaned_mask: Binary uint8 mask (0 or 255)
        min_distance: Minimum distance separating local maxima peaks
        
    Returns:
        Tuple[label_matrix, particle_count]
        label_matrix has 0 for background and 1..N for distinct particle IDs.
    """
    if np.count_nonzero(cleaned_mask) == 0:
        return np.zeros_like(cleaned_mask, dtype=np.int32), 0

    # 1. Exact Distance Transform
    dist_transform = cv2.distanceTransform(cleaned_mask, cv2.DIST_L2, 5)

    # 2. Extract Local Maxima (Peaks)
    local_maxi = peak_local_max(
        dist_transform,
        min_distance=min_distance,
        labels=cleaned_mask > 0,
        exclude_border=False
    )

    # If no local maxima peaks are found, fallback to connected components
    if len(local_maxi) == 0:
        particle_count, labels = cv2.connectedComponents(cleaned_mask)
        return labels.astype(np.int32), max(0, particle_count - 1)

    # 3. Create Markers for Watershed
    markers_mask = np.zeros(dist_transform.shape, dtype=bool)
    markers_mask[tuple(local_maxi.T)] = True
    markers, num_features = ndi.label(markers_mask)

    # 4. Apply Watershed algorithm
    labels = watershed(-dist_transform, markers, mask=(cleaned_mask > 0))
    labels = labels.astype(np.int32)
    particle_count = int(np.max(labels))

    return labels, particle_count
