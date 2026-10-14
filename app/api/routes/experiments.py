from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List, Optional

from app.db.database import get_db
from app.services.ablation_service import AblationService
from app.schemas.common import AblationExperimentResponse
from app.db.models import ExperimentModel

router = APIRouter(tags=["Experiments"])


def get_ablation_service() -> AblationService:
    return AblationService()


@router.post("/experiments/ablation", response_model=AblationExperimentResponse, status_code=status.HTTP_201_CREATED)
async def run_ablation_experiment(
    image: Optional[UploadFile] = File(None, description="Microscopy image file (PNG/JPG/TIFF)"),
    ground_truth_mask: Optional[UploadFile] = File(None, description="Ground-truth binary mask file"),
    use_dataset_default: bool = Form(False, description="Use default dataset sample (RR1.tiff & RR1.png)"),
    db: Session = Depends(get_db),
    service: AblationService = Depends(get_ablation_service)
):
    """
    Execute 4-stage ablation experiment (Baseline Otsu, + Preprocessing, + Morphology, + Watershed)
    against ground-truth mask to measure stage performance.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    
    if use_dataset_default or (not image and not ground_truth_mask):
        img_path = base_dir / "dataset" / "original_size" / "RR1.tiff"
        gt_path = base_dir / "dataset" / "annotations" / "Annotatied masks" / "RR1.png"

        if not img_path.exists() or not gt_path.exists():
            raise HTTPException(status_code=400, detail="Default dataset files (RR1.tiff / RR1.png) not found.")

        result = service.run_ablation_study(img_path, gt_path, image_name="RR1.tiff", db=db)
        return result

    if not image or not ground_truth_mask:
        raise HTTPException(status_code=400, detail="Both image and ground_truth_mask must be provided.")

    img_bytes = await image.read()
    gt_bytes = await ground_truth_mask.read()

    result = service.run_ablation_study(img_bytes, gt_bytes, image_name=image.filename or "uploaded_image", db=db)
    return result


@router.get("/experiments/ablation/{experiment_id}", response_model=AblationExperimentResponse)
def get_ablation_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Retrieve stored ablation experiment results by experiment_id."""
    exp = db.query(ExperimentModel).filter(
        ExperimentModel.experiment_id == experiment_id,
        ExperimentModel.experiment_type == "ablation"
    ).first()

    if not exp:
        raise HTTPException(status_code=404, detail=f"Ablation experiment '{experiment_id}' not found.")

    return AblationExperimentResponse(
        experiment_id=exp.experiment_id,
        experiment_name=exp.experiment_name,
        pipeline_version=exp.pipeline_version,
        configuration_hash=exp.configuration_hash or "N/A",
        evaluated_image_name=exp.experiment_name,
        results_table=exp.metrics_json,
        created_at=exp.created_at.isoformat()
    )
