from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.common import EvaluationResponse, AggregateEvaluationResponse
from app.services.evaluation_service import EvaluationService
from app.api.dependencies import get_evaluation_service
from app.db.database import get_db

router = APIRouter(tags=["Evaluation"])


@router.post("/evaluation", response_model=EvaluationResponse)
async def evaluate_segmentation_masks(
    predicted_mask: UploadFile = File(..., description="Predicted binary mask image file"),
    ground_truth_mask: UploadFile = File(..., description="Ground-truth binary mask image file"),
    original_image: Optional[UploadFile] = File(None, description="Original microscopy image for boundary overlay"),
    image_name: str = Form("evaluated_sample"),
    analysis_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Evaluate predicted segmentation mask against ground-truth mask.
    Calculates IoU, Dice, Precision, Recall, F1 score, particle counts, and generates error map + boundary overlay visual artifacts.
    """
    pred_bytes = await predicted_mask.read()
    gt_bytes = await ground_truth_mask.read()

    if not pred_bytes or not gt_bytes:
        raise HTTPException(status_code=400, detail="Mask files cannot be empty.")

    orig_bytes = await original_image.read() if original_image else None

    metrics = service.evaluate_masks(
        predicted_mask_input=pred_bytes,
        ground_truth_mask_input=gt_bytes,
        image_name=image_name,
        analysis_id=analysis_id,
        original_image_input=orig_bytes,
        db=db
    )
    return metrics


@router.get("/evaluations/aggregate", response_model=AggregateEvaluationResponse)
def get_aggregate_evaluations(
    db: Session = Depends(get_db),
    service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Retrieve per-image evaluation results and aggregate statistics (Mean and Std for IoU, Dice, Precision, Recall, F1).
    """
    return service.get_aggregate_evaluations(db)
