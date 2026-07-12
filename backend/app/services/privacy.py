import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors
from app.utils.logger import get_logger

logger = get_logger(__name__)

def encode_dataframe(df: pd.DataFrame) -> np.ndarray:
    """Encode all columns to numeric for distance calculations."""
    df_encoded = df.copy()
    for col in df_encoded.select_dtypes(include="object").columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
    return df_encoded.fillna(0).values.astype(float)

def detect_duplicates(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> float:
    """Proportion of synthetic rows that are exact duplicates of real rows."""
    real_set = set(map(tuple, real_df.values))
    duplicates = sum(1 for row in synthetic_df.values if tuple(row) in real_set)
    rate = round(duplicates / len(synthetic_df), 4)
    logger.info(f"Duplicate rate: {rate}")
    return rate

def nearest_neighbor_distance(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> float:
    """
    Average minimum distance from each synthetic row to the nearest real row.
    Higher = more privacy (synthetic rows are far from real ones).
    Normalized to 0-1.
    """
    real_encoded = encode_dataframe(real_df)
    syn_encoded = encode_dataframe(synthetic_df)

    nbrs = NearestNeighbors(n_neighbors=1, algorithm="auto").fit(real_encoded)
    distances, _ = nbrs.kneighbors(syn_encoded)
    avg_distance = float(np.mean(distances))

    # Normalize by the max possible distance in this space
    max_possible = float(np.sqrt(real_encoded.shape[1]) * np.max(np.abs(real_encoded)))
    normalized = round(min(avg_distance / max_possible, 1.0), 4) if max_possible > 0 else 0.0
    logger.info(f"Nearest neighbor distance (normalized): {normalized}")
    return normalized

def attribute_disclosure_risk(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> float:
    """
    Measures how closely synthetic categorical distributions match real ones.
    Very high similarity = risk that an attacker could infer real attribute values.
    Returns risk score 0-1 (lower = safer).
    """
    cat_cols = real_df.select_dtypes(include="object").columns
    if len(cat_cols) == 0:
        return 0.0

    risks = []
    for col in cat_cols:
        real_freq = real_df[col].value_counts(normalize=True)
        syn_freq = synthetic_df[col].value_counts(normalize=True)
        all_cats = set(real_freq.index) | set(syn_freq.index)
        overlap = sum(min(real_freq.get(c, 0), syn_freq.get(c, 0)) for c in all_cats)
        risks.append(overlap)

    return round(float(np.mean(risks)), 4)

def compute_reidentification_score(
    duplicate_rate: float,
    nn_distance: float,
    disclosure_risk: float,
) -> float:
    """
    Weighted combination of privacy signals into a single re-id risk score.
    0 = no risk, 1 = high risk.
    """
    # High nn_distance = low risk, so invert it
    score = (
        0.4 * duplicate_rate +
        0.3 * (1 - nn_distance) +
        0.3 * disclosure_risk
    )
    return round(score, 4)

def evaluate_privacy(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> dict:
    logger.info("Evaluating privacy metrics...")

    duplicate_rate = detect_duplicates(real_df, synthetic_df)
    nn_dist = nearest_neighbor_distance(real_df, synthetic_df)
    disclosure_risk = attribute_disclosure_risk(real_df, synthetic_df)
    reid_score = compute_reidentification_score(duplicate_rate, nn_dist, disclosure_risk)

    # Privacy score — inverse of re-id risk, out of 100
    overall_privacy_score = round((1 - reid_score) * 100, 2)

    return {
        "duplicate_rate": duplicate_rate,
        "nearest_neighbor_distance": nn_dist,
        "attribute_disclosure_risk": disclosure_risk,
        "reidentification_score": reid_score,
        "overall_privacy_score": overall_privacy_score,
    }