import cv2
import torch
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, Union, Optional

from app.ml.models.unet import UNet
from app.utils.image_io import load_image, save_image
from app.cv.contours import extract_particle_regions
from app.cv.features import extract_particle_features
from app.core.exceptions import ProcessingError
from app.core.logging import logger


class UNetInferenceEngine:
    """
    Inference Engine for PyTorch U-Net Learned Segmentation Model.
    Supports GPU/CPU device selection, probability map output, variable thresholding, and particle morphometrics extraction.
    """
    def __init__(self, checkpoint_path: Union[str, Path] = Path("checkpoints/unet_classical_cv_v1.pth")):
        self.checkpoint_path = Path(checkpoint_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[UNet] = None
        self._load_checkpoint()

    def _load_checkpoint(self):
        if not self.checkpoint_path.exists():
            logger.warning(f"U-Net checkpoint not found at {self.checkpoint_path}. Learned DL benchmark inference disabled.")
            return

        try:
            self.model = UNet(in_channels=3, out_channels=1, base_features=32).to(self.device)
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.eval()
            logger.info(f"Loaded U-Net checkpoint from {self.checkpoint_path} on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load U-Net checkpoint: {str(e)}")
            self.model = None

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(
        self,
        image_input: Union[str, Path, bytes, np.ndarray],
        analysis_id: str,
        output_dir: Path,
        threshold: float = 0.5,
        target_size: Tuple[int, int] = (512, 512),
        min_area_pixels: int = 5,
        pixel_size_um: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute U-Net deep learning inference.
        Returns:
            - prob_map (np.ndarray): Continuous probabilities [0.0, 1.0]
            - binary_mask (np.ndarray): Thresholded binary mask [0, 255]
            - particles (List[ParticleFeatures])
            - artifact_paths (Dict[str, str])
        """
        if not self.is_ready():
            raise ProcessingError(f"U-Net checkpoint file not found at '{self.checkpoint_path}'. Deep-learning benchmark model must be trained first.")

        bgr_img, gray_img = load_image(image_input)
        orig_h, orig_w = bgr_img.shape[:2]

        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        rgb_resized = cv2.resize(rgb_img, target_size, interpolation=cv2.INTER_AREA)

        img_tensor = torch.from_numpy(rgb_resized.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
        img_tensor = img_tensor.to(self.device)

        with torch.no_grad():
            logits = self.model(img_tensor)
            probs_tensor = torch.sigmoid(logits)
            prob_map_resized = probs_tensor.squeeze().cpu().numpy()

        # Resize probability map back to original image dimensions
        prob_map = cv2.resize(prob_map_resized, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        binary_mask = ((prob_map >= threshold) * 255).astype(np.uint8)

        # Watershed instance separation on U-Net predicted binary mask
        from app.services.instance_service import InstanceService
        instance_service = InstanceService()
        watershed_labels, particle_count_raw = instance_service.separate_instances(binary_mask)

        # Particle feature extraction
        extraction_result = extract_particle_regions(
            watershed_labels=watershed_labels,
            img_bgr=bgr_img,
            analysis_id=analysis_id,
            output_dir=output_dir,
            min_area_pixels=min_area_pixels
        )
        particle_infos = extraction_result["particles"]

        particles = []
        for info in particle_infos:
            feat = extract_particle_features(
                particle_info=info,
                gray_img=gray_img,
                analysis_id=analysis_id,
                pixel_size_um=pixel_size_um
            )
            particles.append(feat)

        # Save DL Visual Artifacts
        dl_dir = output_dir / "dl_artifacts"
        dl_dir.mkdir(parents=True, exist_ok=True)

        prob_vis = (prob_map * 255).astype(np.uint8)
        prob_heatmap = cv2.applyColorMap(prob_vis, cv2.COLORMAP_MAGMA)
        
        prob_path = str(dl_dir / "unet_probability_map.png")
        mask_path = str(dl_dir / "unet_binary_mask.png")
        overlay_path = str(dl_dir / "unet_overlay.png")

        save_image(prob_path, prob_heatmap)
        save_image(mask_path, binary_mask)

        # Overlay on original BGR
        overlay = bgr_img.copy()
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (255, 0, 255), 2)  # Magenta contours for DL
        save_image(overlay_path, overlay)

        return {
            "prob_map": prob_map,
            "binary_mask": binary_mask,
            "threshold": threshold,
            "device_used": str(self.device),
            "particle_count": len(particles),
            "total_detected_objects": extraction_result["total_detected_objects"],
            "filtered_objects": extraction_result["filtered_objects"],
            "particles": particles,
            "artifacts": {
                "probability_map": prob_path,
                "binary_mask": mask_path,
                "overlay": overlay_path
            }
        }
