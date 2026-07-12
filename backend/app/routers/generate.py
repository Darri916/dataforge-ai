import os
from fastapi import APIRouter, HTTPException
from app.config import settings
from app.utils.file_utils import load_csv
from app.services.generator import generate_synthetic_data
from app.models.schemas import GenerateRequest, GenerateResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    real_path = os.path.join(settings.UPLOAD_DIR, f"{request.file_id}.csv")
    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="Original file not found. Please upload first.")

    df = load_csv(real_path)
    synthetic_df, synthesizer_used = generate_synthetic_data(
        df,
        synthesizer_name=request.synthesizer,
        num_rows=request.num_rows,
    )

    synthetic_file_id = f"{request.file_id}_synthetic"
    synthetic_path = os.path.join(settings.UPLOAD_DIR, f"{synthetic_file_id}.csv")
    synthetic_df.to_csv(synthetic_path, index=False)

    logger.info(f"Synthetic data saved: {synthetic_path}")

    return GenerateResponse(
        file_id=request.file_id,
        synthetic_file_id=synthetic_file_id,
        synthesizer_used=synthesizer_used,
        rows_generated=len(synthetic_df),
    )