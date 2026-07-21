import pandas as pd
import numpy as np
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import SingleTableMetadata
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

def build_metadata(df: pd.DataFrame) -> SingleTableMetadata:
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    return metadata

def generate_synthetic_data(
    df: pd.DataFrame,
    synthesizer_name: str = "auto",
    num_rows: int = 100,
) -> tuple[pd.DataFrame, str]:
    logger.info(f"Requested: {synthesizer_name} → using gaussian_copula (free tier)")
    metadata = build_metadata(df)
    np.random.seed(settings.RANDOM_SEED)
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(df)
    logger.info(f"Sampling {num_rows} synthetic rows...")
    synthetic_df = synthesizer.sample(num_rows=num_rows)
    return synthetic_df, "gaussian_copula"