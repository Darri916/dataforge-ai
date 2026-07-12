import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.utils.file_utils import load_csv
from app.services.profiler import profile_dataframe
from app.services.quality import evaluate_quality
from app.services.privacy import evaluate_privacy
from app.services.exporter import generate_report
from app.models.schemas import ExportResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/{file_id}/report")
def export_report(file_id: str):
    real_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")
    synthetic_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_synthetic.csv")

    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="Original file not found.")
    if not os.path.exists(synthetic_path):
        raise HTTPException(status_code=404, detail="Synthetic file not found. Please generate first.")

    real_df = load_csv(real_path)
    synthetic_df = load_csv(synthetic_path)

    profile = profile_dataframe(real_df)
    quality = evaluate_quality(real_df, synthetic_df)
    privacy = evaluate_privacy(real_df, synthetic_df)

    pdf_path = os.path.join(settings.REPORT_DIR, f"{file_id}_report.pdf")
    generate_report(real_df, synthetic_df, profile, quality, privacy, pdf_path)

    return FileResponse(pdf_path, media_type="application/pdf", filename=f"dataforge_{file_id}_report.pdf")

@router.get("/{file_id}/csv")
def export_csv(file_id: str):
    synthetic_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_synthetic.csv")
    if not os.path.exists(synthetic_path):
        raise HTTPException(status_code=404, detail="Synthetic file not found.")
    return FileResponse(synthetic_path, media_type="text/csv", filename=f"synthetic_{file_id}.csv")