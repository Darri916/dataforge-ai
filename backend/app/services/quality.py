import pandas as pd
import numpy as np
from app.utils.stats_utils import (
    compute_jsd,
    compute_ks,
    compute_mean_std,
    compute_categorical_similarity,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

def evaluate_quality(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> dict:
    column_metrics = []
    jsd_scores = []

    for col in real_df.columns:
        if col not in synthetic_df.columns:
            continue

        real_col = real_df[col]
        syn_col = synthetic_df[col]
        is_numerical = pd.api.types.is_numeric_dtype(real_col)

        metric = {
            "column": col,
            "type": "numerical" if is_numerical else "categorical",
        }

        if is_numerical:
            metric["jsd"] = compute_jsd(real_col, syn_col)
            ks = compute_ks(real_col, syn_col)
            metric["ks_statistic"] = ks["statistic"]
            metric["ks_p_value"] = ks["p_value"]
            stats = compute_mean_std(real_col, syn_col)
            metric.update(stats)
            jsd_scores.append(metric["jsd"])
        else:
            metric["categorical_similarity"] = compute_categorical_similarity(real_col, syn_col)
            # Convert similarity to JSD-like score for overall scoring
            jsd_scores.append(1 - metric["categorical_similarity"])

        column_metrics.append(metric)
        logger.info(f"Evaluated column: {col}")

    # Overall quality score — lower JSD = better, so invert
    avg_jsd = np.mean(jsd_scores) if jsd_scores else 1.0
    overall_score = round((1 - avg_jsd) * 100, 2)

    # Correlation similarity — only on numerical columns
    numerical_cols = real_df.select_dtypes(include=np.number).columns.tolist()
    if len(numerical_cols) >= 2:
        real_corr = real_df[numerical_cols].corr().values
        syn_corr = synthetic_df[numerical_cols].corr().values
        val = float(np.corrcoef(real_corr.flatten(), syn_corr.flatten())[0, 1])
        corr_similarity = round(val if not np.isnan(val) else 1.0, 4)
    else:
        corr_similarity = 1.0

    return {
        "overall_score": overall_score,
        "column_metrics": column_metrics,
        "correlation_similarity": corr_similarity,
    }