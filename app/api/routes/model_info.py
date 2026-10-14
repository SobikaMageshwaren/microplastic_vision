from fastapi import APIRouter
from app.schemas.common import ModelInfoResponse
from app.core.config import settings

router = APIRouter(tags=["Model Info"])


@router.get("/model-info", response_model=ModelInfoResponse)
def get_model_info():
    """Return computer-vision model and pipeline configuration information."""
    return ModelInfoResponse(
        pipeline="classical_cv",
        segmentation_method="watershed",
        version=settings.PIPELINE_VERSION
    )
