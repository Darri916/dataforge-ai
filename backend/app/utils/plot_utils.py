import io
import pandas as pd
import matplotlib.pyplot as plt

def histogram_to_bytes(real: pd.Series, synthetic: pd.Series, column: str) -> bytes:
    """Returns a histogram comparison as PNG bytes for embedding in PDF."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(real.dropna(), bins=30, alpha=0.5, label="Real", color="#4F8EF7")
    ax.hist(synthetic.dropna(), bins=30, alpha=0.5, label="Synthetic", color="#F76F4F")
    ax.set_title(f"{column} — Real vs Synthetic")
    ax.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return buf.read()