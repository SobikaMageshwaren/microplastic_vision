import cv2
import numpy as np
import math
from typing import Dict, Any, Optional
from skimage.morphology import skeletonize
from skimage.feature import graycomatrix, graycoprops
from app.schemas.particle import ParticleFeatures, BoundingBox, Centroid


def extract_particle_features(
    particle_info: Dict[str, Any],
    gray_img: np.ndarray,
    analysis_id: str,
    pixel_size_um: Optional[float] = None
) -> ParticleFeatures:
    """
    Extract comprehensive geometric, shape, skeleton, texture, and intensity features, with optional physical calibration.
    """
    mask = particle_info["mask"]
    contour = particle_info["contour"]
    bbox_dict = particle_info["bbox"]
    centroid_dict = particle_info["centroid"]

    # 1. Geometry
    area = float(cv2.contourArea(contour))
    if area == 0.0:
        area = float(np.count_nonzero(mask))
    
    perimeter = float(cv2.arcLength(contour, closed=True))
    w = float(bbox_dict["width"])
    h = float(bbox_dict["height"])
    aspect_ratio = float(w / h) if h > 0 else 1.0

    # 2. Shape Metrics
    # Circularity: 4 * pi * A / P^2
    if perimeter > 0:
        circularity = (4.0 * math.pi * area) / (perimeter ** 2)
    else:
        circularity = 0.0
    circularity = min(1.0, max(0.0, circularity))

    # Compactness: P^2 / A
    compactness = (perimeter ** 2) / area if area > 0 else 0.0

    # Extent: area / (w * h)
    extent = area / (w * h) if (w * h) > 0 else 0.0

    # Convex Hull & Solidity
    hull = cv2.convexHull(contour)
    convex_hull_area = float(cv2.contourArea(hull))
    if convex_hull_area > 0:
        solidity = area / convex_hull_area
    else:
        solidity = 1.0
    solidity = min(1.0, max(0.0, solidity))

    # Eccentricity via fitted ellipse
    eccentricity = 0.0
    if len(contour) >= 5:
        try:
            (x_e, y_e), (MA, ma), angle = cv2.fitEllipse(contour)
            a = max(MA, ma) / 2.0
            b = min(MA, ma) / 2.0
            if a > 0:
                eccentricity = math.sqrt(max(0.0, 1.0 - (b / a) ** 2))
        except Exception:
            eccentricity = 0.0

    # 3. Skeleton Features
    binary_bool = (mask > 0)
    skeleton = skeletonize(binary_bool)
    skeleton_length = float(np.count_nonzero(skeleton))
    mean_thickness = float(area / skeleton_length) if skeleton_length > 0 else 0.0

    # 4. Optional Physical Calibration Calculations
    area_um2 = round(area * (pixel_size_um ** 2), 2) if pixel_size_um else None
    perimeter_um = round(perimeter * pixel_size_um, 2) if pixel_size_um else None
    width_um = round(w * pixel_size_um, 2) if pixel_size_um else None
    height_um = round(h * pixel_size_um, 2) if pixel_size_um else None
    skeleton_length_um = round(skeleton_length * pixel_size_um, 2) if pixel_size_um else None
    mean_thickness_um = round(mean_thickness * pixel_size_um, 2) if pixel_size_um else None

    # 5. Intensity Features
    if mask.shape == gray_img.shape:
        masked_pixels = gray_img[mask > 0]
    else:
        x, y = bbox_dict["x"], bbox_dict["y"]
        w_b, h_b = bbox_dict["width"], bbox_dict["height"]
        crop_gray = gray_img[y:y+h_b, x:x+w_b]
        crop_mask = mask if mask.shape == crop_gray.shape else mask[:crop_gray.shape[0], :crop_gray.shape[1]]
        masked_pixels = crop_gray[crop_mask > 0] if crop_gray.shape == crop_mask.shape else crop_gray.flatten()

    if len(masked_pixels) > 0:
        mean_intensity = float(np.mean(masked_pixels))
        std_intensity = float(np.std(masked_pixels))
        min_intensity = float(np.min(masked_pixels))
        max_intensity = float(np.max(masked_pixels))
    else:
        mean_intensity = std_intensity = min_intensity = max_intensity = 0.0

    # 6. GLCM Texture Features
    glcm_contrast = glcm_energy = glcm_homogeneity = glcm_correlation = None
    try:
        x, y = bbox_dict["x"], bbox_dict["y"]
        w_b, h_b = bbox_dict["width"], bbox_dict["height"]
        crop_gray = gray_img[y:y+h_b, x:x+w_b]
        crop_mask = mask[y:y+h_b, x:x+w_b]
        
        if crop_gray.shape[0] >= 4 and crop_gray.shape[1] >= 4:
            # Quantize intensity to 16 levels for speed and stability
            quantized = (crop_gray // 16).astype(np.uint8)
            glcm = graycomatrix(quantized, distances=[1], angles=[0], levels=16, symmetric=True, normed=True)
            glcm_contrast = float(graycoprops(glcm, 'contrast')[0, 0])
            glcm_energy = float(graycoprops(glcm, 'energy')[0, 0])
            glcm_homogeneity = float(graycoprops(glcm, 'homogeneity')[0, 0])
            glcm_correlation = float(graycoprops(glcm, 'correlation')[0, 0])
    except Exception:
        pass

    return ParticleFeatures(
        particle_id=particle_info["particle_id"],
        analysis_id=analysis_id,
        bbox=BoundingBox(**bbox_dict),
        centroid=Centroid(**centroid_dict),
        area=round(area, 2),
        perimeter=round(perimeter, 2),
        width=round(w, 2),
        height=round(h, 2),
        aspect_ratio=round(aspect_ratio, 3),
        circularity=round(circularity, 4),
        eccentricity=round(eccentricity, 4),
        solidity=round(solidity, 4),
        extent=round(extent, 4),
        compactness=round(compactness, 2),
        convex_hull_area=round(convex_hull_area, 2),
        skeleton_length=round(skeleton_length, 2),
        mean_thickness=round(mean_thickness, 2),
        pixel_size_um=pixel_size_um,
        area_um2=area_um2,
        perimeter_um=perimeter_um,
        width_um=width_um,
        height_um=height_um,
        skeleton_length_um=skeleton_length_um,
        mean_thickness_um=mean_thickness_um,
        mean_intensity=round(mean_intensity, 2),
        std_intensity=round(std_intensity, 2),
        min_intensity=round(min_intensity, 2),
        max_intensity=round(max_intensity, 2),
        glcm_contrast=round(glcm_contrast, 4) if glcm_contrast is not None else None,
        glcm_energy=round(glcm_energy, 4) if glcm_energy is not None else None,
        glcm_homogeneity=round(glcm_homogeneity, 4) if glcm_homogeneity is not None else None,
        glcm_correlation=round(glcm_correlation, 4) if glcm_correlation is not None else None,
        crop_path=particle_info.get("crop_path")
    )
