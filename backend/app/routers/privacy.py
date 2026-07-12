import os
from fastapi import APIRouter, HTTPException
from app.config import settings
from app.utils.file_utils import load_csv
from app.services.privacy import evaluate_privacy
from app.models.schemas import PrivacyResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/{file_id}", response_model=PrivacyResponse)
def get_privacy(file_id: str):
    real_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")
    synthetic_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_synthetic.csv")

    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="Original file not found.")
    if not os.path.exists(synthetic_path):
        raise HTTPException(status_code=404, detail="Synthetic file not found. Please generate first.")

    real_df = load_csv(real_path)
    synthetic_df = load_csv(synthetic_path)
    results = evaluate_privacy(real_df, synthetic_df)

    return PrivacyResponse(file_id=file_id, **results)