from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import logger
from app.db.database import init_db
from app.api.routes import health, analysis, evaluation, model_info, experiments


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(f"Initialized Database and directories. Service ready at {settings.API_V1_STR}")
    yield


def create_application() -> FastAPI:
    """Initialize FastAPI application with database, CORS, and API routes."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PIPELINE_VERSION,
        description="Automated Microplastic Analysis Backend via Classical Computer Vision",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS settings for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files for generated outputs and dataset
    app.mount("/data/outputs", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="outputs")
    from pathlib import Path
    if Path("dataset").exists():
        app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")

    # Custom Exception Handlers for Structured JSON Error Responses
    from fastapi.requests import Request
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError, HTTPException
    from app.core.exceptions import MPVException

    @app.exception_handler(MPVException)
    async def mpv_exception_handler(request: Request, exc: MPVException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.error_code, "message": exc.detail}}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": f"Invalid request payload parameters: {str(exc)}"}}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        code_str = getattr(exc, "error_code", "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": code_str, "message": str(exc.detail)}}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected server error occurred during processing."}}
        )

    from app.api.routes import health, analysis, evaluation, model_info, experiments, models

    # Include API Routers under /api/v1
    app.include_router(health.router, prefix=settings.API_V1_STR)
    app.include_router(analysis.router, prefix=settings.API_V1_STR)
    app.include_router(evaluation.router, prefix=settings.API_V1_STR)
    app.include_router(experiments.router, prefix=settings.API_V1_STR)
    app.include_router(models.router, prefix=settings.API_V1_STR)
    app.include_router(model_info.router, prefix=settings.API_V1_STR)

    return app



app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
