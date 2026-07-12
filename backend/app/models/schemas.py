from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# ─── Upload ───────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    rows: int
    columns: int
    column_types: Dict[str, str]
    health_score: float
    health_breakdown: Dict[str, Any]
    recommended_synthesizer: str
    recommendation_reason: str

# ─── Generate ─────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    file_id: str
    synthesizer: str = "auto"       # gaussian_copula | ctgan | tvae | auto
    num_rows: int = 100

class GenerateResponse(BaseModel):
    file_id: str
    synthetic_file_id: str
    synthesizer_used: str
    rows_generated: int

# ─── Quality ──────────────────────────────────────────────────────────────────

class ColumnQualityMetrics(BaseModel):
    column: str
    type: str                        # numerical | categorical
    jsd: Optional[float] = None
    ks_statistic: Optional[float] = None
    ks_p_value: Optional[float] = None
    real_mean: Optional[float] = None
    synthetic_mean: Optional[float] = None
    real_std: Optional[float] = None
    synthetic_std: Optional[float] = None
    categorical_similarity: Optional[float] = None

class QualityResponse(BaseModel):
    file_id: str
    overall_score: float
    column_metrics: List[ColumnQualityMetrics]
    correlation_similarity: float

# ─── Privacy ──────────────────────────────────────────────────────────────────

class PrivacyResponse(BaseModel):
    file_id: str
    duplicate_rate: float
    nearest_neighbor_distance: float
    attribute_disclosure_risk: float
    reidentification_score: float
    overall_privacy_score: float

# ─── Export ───────────────────────────────────────────────────────────────────

class ExportResponse(BaseModel):
    file_id: str
    csv_path: str
    pdf_path: str