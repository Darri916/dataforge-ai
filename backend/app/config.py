from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    DEFAULT_SYNTHESIZER: str = "auto"
    RANDOM_SEED: int = 42
    REPORT_DIR: str = "outputs"

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist on startup
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.REPORT_DIR).mkdir(parents=True, exist_ok=True)