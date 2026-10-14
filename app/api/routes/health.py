from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.common import HealthResponse
from app.core.config import settings
from app.db.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Comprehensive system readiness and health check endpoint."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    storage_status = "healthy"
    try:
        if not settings.OUTPUT_DIR.exists():
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        storage_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" and storage_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.PIPELINE_VERSION,
        api="healthy",
        database=db_status,
        storage=storage_status,
        pipeline="ready"
    )
