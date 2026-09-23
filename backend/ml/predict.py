"""Score candidate classes with the trained recommendation model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

from ml import MODEL_PATH
from ml.features import FEATURE_NAMES, feature_vector_to_list


def load_artifact(path: Path | None = None) -> dict[str, Any]:
    model_path = path or MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"No trained model at {model_path}. Run: python -m ml.train"
        )
    return joblib.load(model_path)


def score_features(artifact: dict[str, Any], features: dict[str, float]) -> float:
    model = artifact["model"]
    x = np.array([feature_vector_to_list(features)])
    if hasattr(model, "predict_proba"):
        return float(model.predict_proba(x)[0][1])
    return float(model.decision_function(x)[0])


def popularity_score(artifact: dict[str, Any], class_name: str) -> float:
    counts = artifact.get("popularity", {})
    total = sum(counts.values()) or 1
    return float(counts.get(class_name, 0)) / total


def rank_by_popularity(
    artifact: dict[str, Any],
    candidates: list[Any],
    limit: int,
) -> list[tuple[Any, float]]:
    scored = [(c, popularity_score(artifact, c.class_name)) for c in candidates]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]
