import os
import time
import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
from torch.utils.data import DataLoader

from app.ml.models.unet import UNet
from app.ml.losses import BCEDiceLoss
from app.ml.dataset import MicroscopyDataset, get_dataset_splits
from app.core.logging import logger


def calculate_metrics_tensors(logits: torch.Tensor, targets: torch.Tensor, threshold: float = 0.5) -> Tuple[float, float, float, float]:
    probs = torch.sigmoid(logits)
    preds = (probs > threshold).float()

    preds_flat = preds.view(-1)
    targets_flat = targets.view(-1)

    tp = (preds_flat * targets_flat).sum().item()
    fp = (preds_flat * (1.0 - targets_flat)).sum().item()
    fn = ((1.0 - preds_flat) * targets_flat).sum().item()

    union = tp + fp + fn
    iou = (tp / union) if union > 0 else 1.0
    dice = (2.0 * tp / (2.0 * tp + fp + fn)) if (2.0 * tp + fp + fn) > 0 else 1.0
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0

    return round(iou, 4), round(dice, 4), round(precision, 4), round(recall, 4)


def train_unet_model(
    dataset_dir: Path = Path("dataset"),
    epochs: int = 15,
    batch_size: int = 2,
    lr: float = 1e-3,
    image_size: Tuple[int, int] = (512, 512),
    checkpoint_dir: Path = Path("checkpoints"),
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Train U-Net model on matched microscopy image/mask pairs and save best validation checkpoint.
    """
    start_train_time = time.time()
    torch.manual_seed(random_seed)
    np.random.seed(random_seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Starting U-Net model training on device: {device}")

    splits = get_dataset_splits(dataset_dir=dataset_dir, random_seed=random_seed)
    train_dataset = MicroscopyDataset(splits["train_pairs"], image_size=image_size)
    val_dataset = MicroscopyDataset(splits["val_pairs"] if splits["val_pairs"] else splits["train_pairs"], image_size=image_size)

    train_loader = DataLoader(train_dataset, batch_size=min(batch_size, len(train_dataset)), shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=min(batch_size, len(val_dataset)), shuffle=False)

    model = UNet(in_channels=3, out_channels=1, base_features=32).to(device)
    criterion = BCEDiceLoss(bce_weight=0.5)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "unet_classical_cv_v1.pth"

    best_val_dice = 0.0
    best_epoch = 0
    history = {
        "train_loss": [], "val_loss": [],
        "train_dice": [], "val_dice": [],
        "train_iou": [], "val_iou": []
    }

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss_sum = 0.0
        train_dice_sum = 0.0
        train_iou_sum = 0.0

        for imgs, masks, _ in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            logits = model(imgs)
            loss = criterion(logits, masks)
            loss.backward()
            optimizer.step()

            iou, dice, _, _ = calculate_metrics_tensors(logits, masks)
            train_loss_sum += loss.item()
            train_dice_sum += dice
            train_iou_sum += iou

        avg_train_loss = round(train_loss_sum / len(train_loader), 4)
        avg_train_dice = round(train_dice_sum / len(train_loader), 4)
        avg_train_iou = round(train_iou_sum / len(train_loader), 4)

        # Validation Phase
        model.eval()
        val_loss_sum = 0.0
        val_dice_sum = 0.0
        val_iou_sum = 0.0

        with torch.no_grad():
            for imgs, masks, _ in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                logits = model(imgs)
                loss = criterion(logits, masks)
                iou, dice, _, _ = calculate_metrics_tensors(logits, masks)

                val_loss_sum += loss.item()
                val_dice_sum += dice
                val_iou_sum += iou

        avg_val_loss = round(val_loss_sum / len(val_loader), 4)
        avg_val_dice = round(val_dice_sum / len(val_loader), 4)
        avg_val_iou = round(val_iou_sum / len(val_loader), 4)

        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)
        history["train_dice"].append(avg_train_dice)
        history["val_dice"].append(avg_val_dice)
        history["train_iou"].append(avg_train_iou)
        history["val_iou"].append(avg_val_iou)

        logger.info(f"Epoch {epoch}/{epochs} - Train Loss: {avg_train_loss}, Val Loss: {avg_val_loss}, Val Dice: {avg_val_dice}, Val IoU: {avg_val_iou}")

        if avg_val_dice >= best_val_dice:
            best_val_dice = avg_val_dice
            best_epoch = epoch
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "best_val_dice": best_val_dice,
                "history": history
            }, checkpoint_path)

    total_training_duration = round(time.time() - start_train_time, 2)

    return {
        "model_name": "U-Net Classical Benchmark",
        "architecture": "UNet-4Depth",
        "checkpoint_path": str(checkpoint_path),
        "best_epoch": best_epoch,
        "best_val_dice": best_val_dice,
        "best_val_iou": history["val_iou"][best_epoch - 1] if best_epoch > 0 else 0.0,
        "total_training_duration_s": total_training_duration,
        "device_used": str(device),
        "dataset_split": splits,
        "history": history
    }


if __name__ == "__main__":
    result = train_unet_model()
    print("Training finished! Results summary:")
    print(json.dumps(result, indent=2, default=str))
