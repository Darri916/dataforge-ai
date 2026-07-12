import pandas as pd
import numpy as np
from app.utils.logger import get_logger

logger = get_logger(__name__)

def detect_column_types(df: pd.DataFrame) -> dict:
    """Classify each column as numerical or categorical."""
    types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            types[col] = "numerical"
        else:
            types[col] = "categorical"
    return types

def compute_health_score(df: pd.DataFrame) -> tuple[float, dict]:
    """
    Dataset Health Score out of 100.
    Penalises: missing values, duplicates, outliers, class imbalance.
    """
    scores = {}

    # 1. Missing values — penalise proportionally
    missing_rate = df.isnull().mean().mean()
    scores["missing_values"] = round((1 - missing_rate) * 25, 2)

    # 2. Duplicates
    duplicate_rate = df.duplicated().mean()
    scores["duplicates"] = round((1 - duplicate_rate) * 25, 2)

    # 3. Outliers (IQR method on numerical columns)
    numerical_cols = df.select_dtypes(include=np.number).columns
    if len(numerical_cols) > 0:
        outlier_flags = []
        for col in numerical_cols:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).mean()
            outlier_flags.append(outliers)
        avg_outlier_rate = np.mean(outlier_flags)
        scores["outliers"] = round((1 - avg_outlier_rate) * 25, 2)
    else:
        scores["outliers"] = 25.0

    # 4. Class imbalance (on categorical columns)
    categorical_cols = df.select_dtypes(include="object").columns
    if len(categorical_cols) > 0:
        imbalance_scores = []
        for col in categorical_cols:
            freqs = df[col].value_counts(normalize=True)
            # Perfectly balanced = 1/n for each class; penalise deviation
            imbalance = 1 - (freqs.max() - freqs.min())
            imbalance_scores.append(imbalance)
        scores["imbalance"] = round(np.mean(imbalance_scores) * 25, 2)
    else:
        scores["imbalance"] = 25.0

    total = round(sum(scores.values()), 2)
    return total, scores

def recommend_synthesizer(df: pd.DataFrame) -> tuple[str, str]:
    """
    Auto-recommend a synthesizer based on dataset characteristics.
    - Small dataset + mostly numerical → Gaussian Copula (fast, good for correlations)
    - Mixed types or medium size → CTGAN (handles mixed data well)
    - Large dataset + complex distributions → TVAE (deep learning based)
    """
    n_rows, n_cols = df.shape
    numerical_cols = df.select_dtypes(include=np.number).columns
    numerical_ratio = len(numerical_cols) / n_cols if n_cols > 0 else 0

    if n_rows < 1000 and numerical_ratio > 0.7:
        return "gaussian_copula", "Small dataset with mostly numerical columns - Gaussian Copula is fast and preserves correlations well."
    elif n_rows >= 5000:
        return "tvae", "Large dataset detected - TVAE handles complex distributions better at scale."
    else:
        return "ctgan", "Mixed data types or medium-sized dataset - CTGAN is the most versatile choice."

def profile_dataframe(df: pd.DataFrame) -> dict:
    """Full profile: types, health score, recommendation."""
    logger.info(f"Profiling dataframe: {df.shape}")
    column_types = detect_column_types(df)
    health_score, health_breakdown = compute_health_score(df)
    recommended_synthesizer, recommendation_reason = recommend_synthesizer(df)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_types": column_types,
        "health_score": health_score,
        "health_breakdown": health_breakdown,
        "recommended_synthesizer": recommended_synthesizer,
        "recommendation_reason": recommendation_reason,
    }