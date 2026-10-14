from fastapi import HTTPException, status


class MPVException(HTTPException):
    def __init__(self, status_code: int, error_code: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class ImageValidationError(MPVException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_IMAGE_FORMAT",
            detail=detail
        )


class AnalysisNotFoundError(MPVException):
    def __init__(self, analysis_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ANALYSIS_NOT_FOUND",
            detail=f"Analysis session with ID '{analysis_id}' was not found."
        )


class ParticleNotFoundError(MPVException):
    def __init__(self, particle_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PARTICLE_NOT_FOUND",
            detail=f"Particle with ID '{particle_id}' was not found."
        )


class ArtifactNotFoundError(MPVException):
    def __init__(self, artifact_type: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ARTIFACT_NOT_FOUND",
            detail=f"Artifact of type '{artifact_type}' was not found."
        )


class ProcessingError(MPVException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PIPELINE_PROCESSING_ERROR",
            detail=f"Pipeline processing failed: {detail}"
        )


class DatabaseError(MPVException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            detail=f"Database operational error: {detail}"
        )
