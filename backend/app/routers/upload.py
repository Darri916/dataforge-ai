import uuid
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.utils.file_utils import validate_file, check_file_size, load_csv
from app.services.profiler import profile_dataframe
from app.models.schemas import UploadResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    validate_file(file)

    file_id = str(uuid.uuid4())
    save_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")

    # Save uploaded file to disk
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path)
    check_file_size(file_size)

    df = load_csv(save_path)
    profile = profile_dataframe(df)

    logger.info(f"File uploaded: {file.filename} → {file_id}")

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        **profile,
    )