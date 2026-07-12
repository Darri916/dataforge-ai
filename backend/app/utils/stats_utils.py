import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp

def compute_jsd(real: pd.Series, synthetic: pd.Series, bins: int = 50) -> float:
    """Jensen-Shannon Divergence for numerical columns. 0 = identical, 1 = completely different."""
    min_val = min(real.min(), synthetic.min())
    max_val = max(real.max(), synthetic.max())
    real_hist, _ = np.histogram(real.dropna(), bins=bins, range=(min_val, max_val), density=True)
    syn_hist, _ = np.histogram(synthetic.dropna(), bins=bins, range=(min_val, max_val), density=True)
    real_hist += 1e-10
    syn_hist += 1e-10
    return float(jensenshannon(real_hist, syn_hist))

def compute_ks(real: pd.Series, synthetic: pd.Series) -> dict:
    """KS Test: checks if two distributions are statistically the same."""
    stat, p_value = ks_2samp(real.dropna(), synthetic.dropna())
    return {"statistic": round(stat, 4), "p_value": round(p_value, 4)}

def compute_mean_std(real: pd.Series, synthetic: pd.Series) -> dict:
    return {
        "real_mean": round(real.mean(), 4),
        "synthetic_mean": round(synthetic.mean(), 4),
        "real_std": round(real.std(), 4),
        "synthetic_std": round(synthetic.std(), 4),
    }

def compute_categorical_similarity(real: pd.Series, synthetic: pd.Series) -> float:
    """Overlap in category frequency distributions."""
    real_freq = real.value_counts(normalize=True)
    syn_freq = synthetic.value_counts(normalize=True)
    all_cats = set(real_freq.index) | set(syn_freq.index)
    overlap = sum(min(real_freq.get(c, 0), syn_freq.get(c, 0)) for c in all_cats)
    return round(float(overlap), 4)