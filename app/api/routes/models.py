from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.db.database import get_db
from app.services.ml_service import MLService
from app.services.comparison_service import ModelComparisonService

router = APIRouter(tags=["Deep Learning & Explainability"])
ml_service = MLService()
comparison_service = ModelComparisonService()


def format_web_path(path_str: Optional[str]) -> Optional[str]:
    if not path_str:
        return path_str
    normalized = str(path_str).replace("\\", "/")
    if "/data/outputs/" in normalized:
        return "/data/outputs/" + normalized.split("/data/outputs/")[1]
    elif "data/outputs/" in normalized:
        return "/data/outputs/" + normalized.split("data/outputs/")[1]
    return normalized


def _resolve_image_content(
    upload: Optional[UploadFile],
    analysis_id: Optional[str] = None
) -> bytes:
    """Helper to retrieve image bytes either from uploaded file or from saved analysis disk artifacts."""
    if upload is not None:
        try:
            content = upload.file.read()
            if content and len(content) > 0:
                return content
        except Exception:
            pass

    outputs_dir = Path("data/outputs")
    image_exts = ["original.png", "original.jpg", "original.jpeg", "original.tiff", "original.tif"]

    if analysis_id and analysis_id != "latest":
        for ext in image_exts:
            candidate_file = outputs_dir / analysis_id / ext
            if candidate_file.is_file():
                return candidate_file.read_bytes()

        analysis_dir = outputs_dir / analysis_id
        if analysis_dir.is_dir():
            for f in analysis_dir.iterdir():
                if f.is_file() and f.suffix.lower() in [".png", ".jpg", ".jpeg", ".tiff", ".tif"]:
                    if "heatmap" not in f.name and "mask" not in f.name:
                        return f.read_bytes()

    # Fallback to scanning any analysis folder on disk with an original image
    if outputs_dir.exists():
        analysis_dirs = sorted(
            [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("ana_")],
            key=lambda d: d.stat().st_mtime,
            reverse=True
        )
        for ad in analysis_dirs:
            for ext in image_exts:
                orig_file = ad / ext
                if orig_file.is_file():
                    return orig_file.read_bytes()

    # Fallback to dataset sample if exists
    dataset_samples = (
        list(Path("dataset").glob("*.tiff")) +
        list(Path("dataset").glob("*.png")) +
        list(Path("dataset").glob("*.jpg"))
    )
    if dataset_samples:
        return dataset_samples[0].read_bytes()

    return b""


@router.get("/models", response_model=List[Dict[str, Any]])
def list_models(db: Session = Depends(get_db)):
    """List all registered deep-learning benchmark models."""
    return ml_service.get_registered_models(db)


@router.get("/models/comparison", response_model=Dict[str, Any])
def compare_classical_vs_unet_models():
    """Run side-by-side evaluation comparison between Classical CV (Otsu + Watershed) and PyTorch U-Net."""
    return comparison_service.compare_classical_vs_unet()


@router.post("/models/train", response_model=Dict[str, Any])
def train_model(epochs: int = Query(15, ge=1, le=100), db: Session = Depends(get_db)):
    """Trigger U-Net model training on annotated dataset image/mask pairs."""
    return ml_service.train_and_register_model(db, epochs=epochs)


@router.post("/models/{model_id}/predict", response_model=Dict[str, Any])
@router.post("/models/predict", response_model=Dict[str, Any])
async def predict_with_unet(
    model_id: str = "unet-baseline-v1",
    analysis_id: Optional[str] = Query(None),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    threshold: float = Form(0.5),
    min_area_pixels: int = Form(5),
    pixel_size_um: Optional[float] = Form(None)
):
    """Execute U-Net deep learning learned segmentation inference."""
    upload = file or image
    content = _resolve_image_content(upload, analysis_id)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Microscopy image file or valid analysis_id is required for inference."
        )

    res = ml_service.predict_unet(
        image_input=content,
        threshold=threshold,
        min_area_pixels=min_area_pixels,
        pixel_size_um=pixel_size_um
    )

    # Convert artifact file paths for web access
    formatted_artifacts = {k: format_web_path(v) for k, v in res["artifacts"].items()}
    res["artifacts"] = formatted_artifacts
    return res


@router.post("/models/{model_id}/explain", response_model=Dict[str, Any])
@router.post("/models/explain", response_model=Dict[str, Any])
async def explain_model_saliency(
    model_id: str = "unet-baseline-v1",
    analysis_id: Optional[str] = Query(None),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    """Generate Input-Gradient Saliency Attribution heatmap visualization for model explainability."""
    upload = file or image
    content = _resolve_image_content(upload, analysis_id)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Microscopy image file or valid analysis_id is required to compute attribution heatmap."
        )

    res = ml_service.explain_unet_saliency(image_input=content, target_analysis_id=analysis_id)
    res["heatmap_path"] = format_web_path(res["heatmap_path"])
    return res

