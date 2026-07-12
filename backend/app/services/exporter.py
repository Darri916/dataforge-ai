import pandas as pd
from fpdf import FPDF
from app.utils.plot_utils import histogram_to_bytes
from app.utils.logger import get_logger
import tempfile, os

logger = get_logger(__name__)

class DataForgeReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "DataForge AI — Synthetic Data Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def key_value(self, key: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.cell(70, 7, key + ":")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

def generate_report(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    profile: dict,
    quality: dict,
    privacy: dict,
    output_path: str,
) -> str:
    logger.info("Generating PDF report...")
    pdf = DataForgeReport()
    pdf.add_page()

    # ── Dataset Overview ──────────────────────────────────────────────────────
    pdf.section_title("1. Dataset Overview")
    pdf.key_value("Original Rows", str(profile["rows"]))
    pdf.key_value("Columns", str(profile["columns"]))
    pdf.key_value("Dataset Health Score", f"{profile['health_score']} / 100")
    pdf.key_value("Synthesizer Used", profile["recommended_synthesizer"])
    pdf.key_value("Reason", profile["recommendation_reason"])
    pdf.ln(4)

    # ── Quality Metrics ───────────────────────────────────────────────────────
    pdf.section_title("2. Quality Metrics")
    pdf.key_value("Overall Quality Score", f"{quality['overall_score']} / 100")
    pdf.key_value("Correlation Similarity", str(quality["correlation_similarity"]))
    pdf.ln(2)

    for col_metric in quality["column_metrics"]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"  {col_metric['column']} ({col_metric['type']})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        if col_metric["type"] == "numerical":
            pdf.cell(0, 5, f"    JSD: {col_metric.get('jsd')}   KS stat: {col_metric.get('ks_statistic')}   p-value: {col_metric.get('ks_p_value')}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 5, f"    Mean (real/syn): {col_metric.get('real_mean')} / {col_metric.get('synthetic_mean')}   Std: {col_metric.get('real_std')} / {col_metric.get('synthetic_std')}", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 5, f"    Categorical Similarity: {col_metric.get('categorical_similarity')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Privacy Metrics ───────────────────────────────────────────────────────
    pdf.section_title("3. Privacy Metrics")
    pdf.key_value("Overall Privacy Score", f"{privacy['overall_privacy_score']} / 100")
    pdf.key_value("Duplicate Rate", str(privacy["duplicate_rate"]))
    pdf.key_value("Nearest Neighbor Distance", str(privacy["nearest_neighbor_distance"]))
    pdf.key_value("Attribute Disclosure Risk", str(privacy["attribute_disclosure_risk"]))
    pdf.key_value("Re-identification Score", str(privacy["reidentification_score"]))
    pdf.ln(4)

    # ── Visual Comparisons ────────────────────────────────────────────────────
    pdf.section_title("4. Column Distribution Comparisons")
    numerical_cols = real_df.select_dtypes(include="number").columns[:4]  # max 4 charts

    for col in numerical_cols:
        img_bytes = histogram_to_bytes(real_df[col], synthetic_df[col], col)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name
        pdf.image(tmp_path, w=170)
        os.unlink(tmp_path)
        pdf.ln(2)

    pdf.output(output_path)
    logger.info(f"PDF saved to {output_path}")
    return output_path