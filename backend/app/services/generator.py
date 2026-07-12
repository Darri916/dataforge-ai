import pandas as pd
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
from sdv.metadata import SingleTableMetadata
from app.config import settings
from app.utils.logger import get_logger
from app.services.profiler import recommend_synthesizer

logger = get_logger(__name__)

SYNTHESIZER_MAP = {
    "gaussian_copula": GaussianCopulaSynthesizer,
    "ctgan": CTGANSynthesizer,
    "tvae": TVAESynthesizer,
}

def build_metadata(df: pd.DataFrame) -> SingleTableMetadata:
    """SDV needs metadata to understand column types before fitting."""
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    return metadata

def generate_synthetic_data(
    df: pd.DataFrame,
    synthesizer_name: str = "auto",
    num_rows: int = 100,
) -> tuple[pd.DataFrame, str]:
    """
    Fit a synthesizer on real data and sample synthetic rows.
    Returns (synthetic_df, synthesizer_used).
    """
    if synthesizer_name == "auto":
        synthesizer_name, _ = recommend_synthesizer(df)
        logger.info(f"Auto mode selected: {synthesizer_name}")

    if synthesizer_name not in SYNTHESIZER_MAP:
        raise ValueError(f"Unknown synthesizer: {synthesizer_name}. Choose from {list(SYNTHESIZER_MAP.keys())} or 'auto'.")

    metadata = build_metadata(df)
    SynthesizerClass = SYNTHESIZER_MAP[synthesizer_name]

    logger.info(f"Fitting {synthesizer_name} on {df.shape[0]} rows...")
    synthesizer = SynthesizerClass(metadata, cuda=False)
    synthesizer.fit(df)

    logger.info(f"Sampling {num_rows} synthetic rows...")
    synthetic_df = synthesizer.sample(num_rows=num_rows)

    return synthetic_df, synthesizer_name