import os
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any
from app.utils.image_io import save_image
from app.schemas.particle import ParticleFeatures


def generate_visual_artifacts(
    output_dir: Path,
    original_bgr: np.ndarray,
    preprocessed_dict: Dict[str, np.ndarray],
    threshold_mask: np.ndarray,
    cleaned_mask: np.ndarray,
    watershed_labels: np.ndarray,
    particles: List[ParticleFeatures]
) -> Dict[str, str]:
    """
    Generate all required visual artifacts and save them to output_dir.
    
    Returns:
        Dict[artifact_type, file_path_string]
    """
    artifact_paths = {}

    # 1. Original image
    orig_path = output_dir / "original.png"
    save_image(orig_path, original_bgr)
    artifact_paths["original"] = str(orig_path)

    # 2. Preprocessed images
    for key, img_step in preprocessed_dict.items():
        step_filename = f"{key}.png"
        step_path = output_dir / step_filename
        if len(img_step.shape) == 2:
            step_bgr = cv2.cvtColor(img_step, cv2.COLOR_GRAY2BGR)
        else:
            step_bgr = img_step
        save_image(step_path, step_bgr)
        artifact_paths[key] = str(step_path)

    # 3. Threshold mask
    thresh_path = output_dir / "threshold_mask.png"
    save_image(thresh_path, threshold_mask)
    artifact_paths["threshold_mask"] = str(thresh_path)

    # 4. Cleaned mask
    cleaned_path = output_dir / "cleaned_mask.png"
    save_image(cleaned_path, cleaned_mask)
    artifact_paths["cleaned_mask"] = str(cleaned_path)

    # 4b. Morphological Cleaning Delta Map (Visualizes exact morphological impact)
    delta_bgr = np.zeros((threshold_mask.shape[0], threshold_mask.shape[1], 3), dtype=np.uint8)
    removed_noise = (threshold_mask > 127) & (cleaned_mask <= 127)
    filled_voids = (threshold_mask <= 127) & (cleaned_mask > 127)
    stable_particles = (threshold_mask > 127) & (cleaned_mask > 127)
    
    delta_bgr[stable_particles] = [210, 210, 210]  # Preserved particles (Light Gray)
    delta_bgr[removed_noise] = [0, 0, 255]          # Noise removed by opening (Red)
    delta_bgr[filled_voids] = [0, 255, 0]           # Voids sealed by closing (Green)
    
    delta_path = output_dir / "morphology_delta.png"
    save_image(delta_path, delta_bgr)
    artifact_paths["morphology_delta"] = str(delta_path)

    # 5. Watershed instance map (Color-coded labels)
    ws_path = output_dir / "watershed_instances.png"
    num_labels = np.max(watershed_labels)
    if num_labels > 0:
        # Create a colormap for instance visualization
        np.random.seed(42)
        colors = np.random.randint(50, 255, size=(num_labels + 1, 3), dtype=np.uint8)
        colors[0] = [0, 0, 0]  # Background is black
        colored_instances = colors[watershed_labels]
        save_image(ws_path, colored_instances)
    else:
        save_image(ws_path, cv2.cvtColor(cleaned_mask, cv2.COLOR_GRAY2BGR))
    artifact_paths["watershed_instances"] = str(ws_path)

    # 6. Segmentation Overlay
    overlay_path = output_dir / "segmentation_overlay.png"
    overlay = original_bgr.copy()
    contours_cleaned, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours_cleaned, -1, (0, 255, 0), 2)
    save_image(overlay_path, overlay)
    artifact_paths["segmentation_overlay"] = str(overlay_path)

    # 7. Particle ID Map
    ids_path = output_dir / "particle_ids.png"
    id_map = original_bgr.copy()
    for p in particles:
        cx, cy = int(p.centroid.x), int(p.centroid.y)
        cv2.putText(
            id_map, p.particle_id, (cx - 15, cy + 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA
        )
    save_image(ids_path, id_map)
    artifact_paths["particle_ids"] = str(ids_path)

    # 8. Particle Bounding Boxes & Contours
    contours_path = output_dir / "particle_contours.png"
    contours_vis = original_bgr.copy()
    for p in particles:
        # Bounding box
        bx, by, bw, bh = p.bbox.x, p.bbox.y, p.bbox.width, p.bbox.height
        cv2.rectangle(contours_vis, (bx, by), (bx + bw, by + bh), (255, 0, 0), 2)
        # Centroid dot
        cv2.circle(contours_vis, (int(p.centroid.x), int(p.centroid.y)), 3, (0, 255, 255), -1)
    save_image(contours_path, contours_vis)
    artifact_paths["particle_contours"] = str(contours_path)

    # 9. Size Distribution Plot
    size_plot_path = output_dir / "size_distribution.png"
    areas = [p.area for p in particles]
    plt.figure(figsize=(7, 4.5))
    if areas:
        plt.hist(areas, bins=max(5, min(20, len(areas))), color='#2b5c8f', edgecolor='black', alpha=0.8)
    plt.title("Particle Area Distribution (pixels)")
    plt.xlabel("Area (px²)")
    plt.ylabel("Frequency")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(size_plot_path, dpi=150)
    plt.close()
    artifact_paths["size_distribution"] = str(size_plot_path)

    # 10. Circularity Distribution Plot
    circ_plot_path = output_dir / "circularity_distribution.png"
    circs = [p.circularity for p in particles]
    plt.figure(figsize=(7, 4.5))
    if circs:
        plt.hist(circs, bins=max(5, min(20, len(circs))), color='#2e8b57', edgecolor='black', alpha=0.8)
    plt.title("Particle Circularity Distribution")
    plt.xlabel("Circularity (4πA / P²)")
    plt.ylabel("Frequency")
    plt.xlim(0, 1.05)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(circ_plot_path, dpi=150)
    plt.close()
    artifact_paths["circularity_distribution"] = str(circ_plot_path)

    # 11. Spatial Distribution Plot
    spatial_plot_path = output_dir / "spatial_distribution.png"
    xs = [p.centroid.x for p in particles]
    ys = [p.centroid.y for p in particles]
    plt.figure(figsize=(7, 4.5))
    if xs and ys:
        plt.scatter(xs, ys, c=areas if areas else 'blue', cmap='viridis', s=60, edgecolors='k', alpha=0.85)
        plt.colorbar(label='Particle Area (px²)')
    plt.gca().invert_yaxis()  # Image coordinate system
    plt.title("Particle Spatial Distribution (Centroids)")
    plt.xlabel("X (px)")
    plt.ylabel("Y (px)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(spatial_plot_path, dpi=150)
    plt.close()
    artifact_paths["spatial_distribution"] = str(spatial_plot_path)

    return artifact_paths
