import logging
import sys
from app.core.config import settings


def setup_logging():
    """Configure structured logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("microplastic_vision")
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


logger = setup_logging()


def log_stage(analysis_id: str, stage: str, duration: float, status: str = "success", extra_info: str = ""):
    """Log pipeline stage timing and details in a structured format."""
    msg = f"analysis_id={analysis_id} stage={stage} duration={duration:.4f}s status={status}"
    if extra_info:
        msg += f" info={extra_info}"
    logger.info(msg)
