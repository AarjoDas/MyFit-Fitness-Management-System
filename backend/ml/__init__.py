"""Machine learning module for class recommendations."""

from pathlib import Path

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "rec_v1.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
