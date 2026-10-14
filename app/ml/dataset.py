import cv2
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Dict, Any, Optional
from app.utils.image_io import load_image


class MicroscopyDataset(Dataset):
    """
    PyTorch Dataset for Microscopy Images and Ground Truth Masks.
    Resizes images to target_size (512x512) and normalizes pixel intensities to [0, 1].
    """
    def __init__(self, sample_pairs: List[Tuple[Path, Path]], image_size: Tuple[int, int] = (512, 512)):
        self.sample_pairs = sample_pairs
        self.image_size = image_size

    def __len__(self) -> int:
        return len(self.sample_pairs)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str]:
        img_path, mask_path = self.sample_pairs[idx]

        bgr_img, _ = load_image(img_path)
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        rgb_resized = cv2.resize(rgb_img, self.image_size, interpolation=cv2.INTER_AREA)

        # Ground truth mask loading
        mask_raw = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if mask_raw is None:
            mask_raw = np.zeros((bgr_img.shape[0], bgr_img.shape[1]), dtype=np.uint8)
        mask_resized = cv2.resize(mask_raw, self.image_size, interpolation=cv2.INTER_NEAREST)
        binary_mask = (mask_resized > 127).astype(np.float32)

        # Convert to PyTorch tensors (CHW for image, 1HW for mask)
        img_tensor = torch.from_numpy(rgb_resized.transpose(2, 0, 1)).float() / 255.0
        mask_tensor = torch.from_numpy(binary_mask).unsqueeze(0).float()

        return img_tensor, mask_tensor, img_path.name


def get_dataset_splits(
    dataset_dir: Path = Path("dataset"),
    random_seed: int = 42,
    test_size: float = 0.2
) -> Dict[str, Any]:
    """
    Find matched microscopy image & mask pairs and partition deterministically.
    """
    img_dir = dataset_dir / "original_size"
    mask_dir = dataset_dir / "annotations" / "Annotatied masks"

    matched_pairs = []
    annotated_names = ["RR1", "RR2", "RR3", "RR4", "RR5"]
    
    for name in annotated_names:
        img_file = img_dir / f"{name}.tiff"
        if not img_file.exists():
            img_file = img_dir / f"{name}.png"
        mask_file = mask_dir / f"{name}.png"

        if img_file.exists() and mask_file.exists():
            matched_pairs.append((img_file, mask_file))

    # Fallback to any matched stem pairs if specific list isn't present
    if not matched_pairs:
        for m_file in mask_dir.glob("*.png"):
            stem = m_file.stem
            i_file = img_dir / f"{stem}.tiff"
            if not i_file.exists():
                i_file = img_dir / f"{stem}.png"
            if i_file.exists():
                matched_pairs.append((i_file, m_file))

    # Deterministic train/val split using seed
    rng = np.random.RandomState(random_seed)
    shuffled_indices = rng.permutation(len(matched_pairs))
    
    val_count = max(1, int(len(matched_pairs) * test_size)) if len(matched_pairs) > 1 else 0
    val_indices = shuffled_indices[:val_count]
    train_indices = shuffled_indices[val_count:]

    train_pairs = [matched_pairs[i] for i in train_indices]
    val_pairs = [matched_pairs[i] for i in val_indices]

    return {
        "train_pairs": train_pairs,
        "val_pairs": val_pairs,
        "all_pairs": matched_pairs,
        "train_ids": [p[0].name for p in train_pairs],
        "val_ids": [p[0].name for p in val_pairs],
        "total_pairs": len(matched_pairs),
        "random_seed": random_seed,
        "split_version": "v1.0-deterministic"
    }
