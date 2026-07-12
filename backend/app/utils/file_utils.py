import pandas as pd
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".csv"}

def validate_file(file: UploadFile) -> None:
    name = file.filename or ""
    if "." not in name:
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    ext = "." + name.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

def check_file_size(file_size_bytes: int) -> None:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

def load_csv(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")
        logger.info(f"Loaded CSV: {filepath} — {df.shape[0]} rows, {df.shape[1]} cols")
        return df
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {str(e)}")
       