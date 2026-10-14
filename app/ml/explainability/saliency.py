import cv2
import torch
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, Union
from app.utils.image_io import load_image, save_image


def generate_saliency_heatmap(
    model: torch.nn.Module,
    image_input: Union[str, Path, bytes, np.ndarray],
    device: torch.device,
    target_size: Tuple[int, int] = (512, 512)
) -> Tuple[np.ndarray, np.ndarray, str]:
    """
    Generate Input-Gradient Saliency Attribution heatmap for model explainability.
    Answers: 'Which input image pixels contributed most strongly to the model's segmentation prediction?'

    Returns:
        Tuple[saliency_map_normalized, color_heatmap_bgr, formatted_overlay_path]
    """
    model.eval()
    bgr_img, _ = load_image(image_input)
    orig_h, orig_w = bgr_img.shape[:2]

    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    rgb_resized = cv2.resize(rgb_img, target_size, interpolation=cv2.INTER_AREA)

    img_tensor = torch.from_numpy(rgb_resized.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
    img_tensor = img_tensor.to(device)
    img_tensor.requires_grad = True

    logits = model(img_tensor)
    probs = torch.sigmoid(logits)
    
    # Target loss for gradient attribution (sum of predicted probabilities)
    target = probs.sum()
    model.zero_grad()
    target.backward()

    # Absolute input gradients across channels
    gradients = img_tensor.grad.data.abs().squeeze(0).cpu().numpy()
    saliency_map = np.max(gradients, axis=0)  # Maximum gradient magnitude across RGB channels

    # Normalize to [0, 255]
    if saliency_map.max() > 0:
        saliency_norm = ((saliency_map - saliency_map.min()) / (saliency_map.max() - saliency_map.min()) * 255.0).astype(np.uint8)
    else:
        saliency_norm = np.zeros(target_size, dtype=np.uint8)

    # Resize saliency map back to original image dimensions
    saliency_resized = cv2.resize(saliency_norm, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
    heatmap_bgr = cv2.applyColorMap(saliency_resized, cv2.COLORMAP_JET)

    # Blend heatmap with original BGR image (60% original + 40% heatmap)
    attribution_overlay = cv2.addWeighted(bgr_img, 0.6, heatmap_bgr, 0.4, 0)

    return saliency_resized, attribution_overlay
