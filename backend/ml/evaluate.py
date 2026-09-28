"""Precision@k evaluation vs a popularity baseline."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd

from ml.features import FEATURE_NAMES, feature_vector_to_list


def precision_at_k(
    ranked_ids: list[int],
    relevant_ids: set[int],
    k: int = 3,
) -> float:
    if k <= 0:
        return 0.0
    top = ranked_ids[:k]
    hits = sum(1 for class_id in top if class_id in relevant_ids)
    return hits / k


def evaluate_split(
    model: Any,
    test_df: pd.DataFrame,
    popularity: dict[str, int],
    k: int = 3,
) -> dict[str, float]:
    """
    For each test member, rank all test-window candidate classes and
    compute precision@k against classes they actually booked.
    """
    if test_df.empty:
        return {"precision_at_3": 0.0, "baseline_precision_at_3": 0.0, "test_members": 0}

    member_metrics: list[float] = []
    baseline_metrics: list[float] = []

    grouped = test_df.groupby("member_id")
    for member_id, group in grouped:
        positives = set(group.loc[group["label"] == 1, "class_id"].tolist())
        if not positives:
            continue

        X = np.array([feature_vector_to_list(row) for row in group.to_dict(orient="records")])
        class_ids = group["class_id"].tolist()
        class_names = group["class_name"].tolist()

        if hasattr(model, "predict_proba"):
            scores = model.predict_proba(X)[:, 1]
        else:
            scores = model.decision_function(X)

        ranked = [cid for _, cid in sorted(zip(scores, class_ids), reverse=True)]
        member_metrics.append(precision_at_k(ranked, positives, k))

        pop_ranked = [
            cid
            for _, cid in sorted(
                zip([popularity.get(name, 0) for name in class_names], class_ids),
                reverse=True,
            )
        ]
        baseline_metrics.append(precision_at_k(pop_ranked, positives, k))

    n = len(member_metrics) or 1
    return {
        "precision_at_3": float(sum(member_metrics) / n) if member_metrics else 0.0,
        "baseline_precision_at_3": float(sum(baseline_metrics) / n) if baseline_metrics else 0.0,
        "test_members": len(member_metrics),
    }


def row_feature_dict(row: dict[str, Any]) -> dict[str, float]:
    return {name: float(row[name]) for name in FEATURE_NAMES}
