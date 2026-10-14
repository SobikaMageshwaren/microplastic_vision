from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.analysis_service import AnalysisService
from app.services.evaluation_service import EvaluationService


def get_analysis_service() -> AnalysisService:
    return AnalysisService()


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()
