import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.utils.image_io import save_image


from typing import List, Dict, Any, Tuple, Optional


def extract_particle_regions(
    watershed_labels: np.ndarray,
    img_bgr: np.ndarray,
    analysis_id: str,
    output_dir: Path,
    min_area_pixels: int = 5,
    max_area_pixels: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extract individual particle masks, contours, bounding boxes, crops, and metadata with configurable particle filtering.
    
    Returns:
        Dict with keys:
            - particles: List[Dict[str, Any]]
            - total_detected_objects: int
            - valid_particles: int
            - filtered_objects: int
    """
    total_detected_objects = int(np.max(watershed_labels)) if np.max(watershed_labels) > 0 else 0
    particles_data = []
    filtered_objects = 0

    crops_dir = output_dir / "particles"
    crops_dir.mkdir(parents=True, exist_ok=True)

    for label_id in range(1, total_detected_objects + 1):
        single_mask = (watershed_labels == label_id).astype(np.uint8) * 255
        pixel_count = int(np.count_nonzero(single_mask))

        # Configurable particle area filtering
        if pixel_count < min_area_pixels or (max_area_pixels is not None and pixel_count > max_area_pixels):
            filtered_objects += 1
            continue

        contours, _ = cv2.findContours(single_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            filtered_objects += 1
            continue

        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)

        # Centroid calculation using moments
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = float(M["m10"] / M["m00"])
            cy = float(M["m01"] / M["m00"])
        else:
            cx = float(x + w / 2.0)
            cy = float(y + h / 2.0)

        # Formatted Particle ID
        pid = f"P{len(particles_data) + 1:03d}"

        # Crop particle BGR image and mask
        pad = 2
        img_h, img_w = img_bgr.shape[:2]
        x1, y1 = max(0, x - pad), max(0, y - pad)
        x2, y2 = min(img_w, x + w + pad), min(img_h, y + h + pad)

        crop_img = img_bgr[y1:y2, x1:x2].copy()
        crop_path = crops_dir / f"{pid}_crop.png"
        save_image(crop_path, crop_img)

        particles_data.append({
            "particle_id": pid,
            "label_id": label_id,
            "mask": single_mask,
            "contour": contour,
            "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
            "centroid": {"x": round(cx, 2), "y": round(cy, 2)},
            "crop_path": str(crop_path)
        })

    return {
        "particles": particles_data,
        "total_detected_objects": total_detected_objects,
        "valid_particles": len(particles_data),
        "filtered_objects": filtered_objects
    }
