import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MicroPlastic-Vision Backend"
    API_V1_STR: str = "/api/v1"
    PIPELINE_VERSION: str = "0.1.0"
    
    # Environment & Database
    DATABASE_URL: str = "sqlite:///./microplastic.db"
    LOG_LEVEL: str = "INFO"
    
    # Storage Directories
    MAX_UPLOAD_SIZE_MB: int = 50
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    MASKS_DIR: Path = BASE_DIR / "data" / "masks"
    OUTPUT_DIR: Path = BASE_DIR / "data" / "outputs"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def init_directories(self) -> None:
        """Ensure all required data directories exist."""
        for directory in [self.UPLOAD_DIR, self.PROCESSED_DIR, self.MASKS_DIR, self.OUTPUT_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_directories()
