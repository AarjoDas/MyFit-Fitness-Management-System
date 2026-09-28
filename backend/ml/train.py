"""
Offline training for class recommendations.

Time-based split: history starts ~90 days ago; train uses the first 60 days,
test uses days 60–90. Labels are synthetic enrollments from seed_historical_data.

Run from backend/:
    python -m ml.train
"""

from __future__ import annotations

import json
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

from database.connection import SessionLocal
from ml import ARTIFACTS_DIR, METRICS_PATH, MODEL_PATH
from ml.evaluate import evaluate_split
from ml.features import (
    FEATURE_NAMES,
    POSITIVE_STATUSES,
    build_feature_vector,
    feature_vector_to_list,
)
from models.class_enrollment import ClassEnrollment
from models.group_class import GroupClass
from models.member import Member

HISTORY_DAYS = 90
TRAIN_DAYS = 60
NEGATIVE_RATIO = 2
RANDOM_SEED = 42
ALGORITHM = "LogisticRegression"


def _split_bounds(today: date | None = None) -> tuple[date, date, date]:
    today = today or date.today()
    start = today - timedelta(days=HISTORY_DAYS)
    train_end = start + timedelta(days=TRAIN_DAYS)
    test_end = start + timedelta(days=HISTORY_DAYS)
    return start, train_end, test_end


def _positive_pairs(session) -> list[tuple[int, int, date, str]]:
    rows = (
        session.query(ClassEnrollment, GroupClass)
        .join(GroupClass, ClassEnrollment.class_id == GroupClass.class_id)
        .filter(ClassEnrollment.attendance_status.in_(list(POSITIVE_STATUSES)))
        .all()
    )
    return [
        (enrollment.member_id, group_class.class_id, group_class.scheduled_date, group_class.class_name)
        for enrollment, group_class in rows
    ]


def _sample_negatives(
    session,
    positives: list[tuple[int, int, date, str]],
    start: date,
    end: date,
) -> list[tuple[int, int, date]]:
    classes = (
        session.query(GroupClass)
        .filter(GroupClass.scheduled_date >= start, GroupClass.scheduled_date < end)
        .all()
    )
    members = session.query(Member).all()
    booked = {(member_id, class_id) for member_id, class_id, _, _ in positives}

    negatives: list[tuple[int, int, date]] = []
    target = len([p for p in positives if start <= p[2] < end]) * NEGATIVE_RATIO
    attempts = 0
    max_attempts = max(target * 20, 500)

    while len(negatives) < target and attempts < max_attempts:
        attempts += 1
        member = random.choice(members)
        group_class = random.choice(classes)
        pair = (member.member_id, group_class.class_id)
        if pair in booked:
            continue
        if member.registration_date and member.registration_date > group_class.scheduled_date:
            continue
        booked.add(pair)
        negatives.append((member.member_id, group_class.class_id, group_class.scheduled_date))

    return negatives


def _build_frame(session, pairs: list[tuple[int, int, date]], labels: list[int], class_names: dict[int, str]) -> pd.DataFrame:
    rows = []
    for (member_id, class_id, scheduled), label in zip(pairs, labels):
        features = build_feature_vector(session, member_id, class_id, reference_date=scheduled)
        rows.append(
            {
                "member_id": member_id,
                "class_id": class_id,
                "class_name": class_names.get(class_id, ""),
                "label": label,
                **features,
            }
        )
    return pd.DataFrame(rows)


def train(output_dir: Path | None = None) -> dict:
    random.seed(RANDOM_SEED)
    artifacts_dir = output_dir or ARTIFACTS_DIR
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    session = SessionLocal()
    try:
        start, train_end, test_end = _split_bounds()
        positives = _positive_pairs(session)
        if not positives:
            raise RuntimeError(
                "No positive enrollments found. Run: python -m database.seed_historical_data"
            )

        class_names = {
            gc.class_id: gc.class_name for gc in session.query(GroupClass).all()
        }

        train_pos = [p for p in positives if start <= p[2] < train_end]
        test_pos = [p for p in positives if train_end <= p[2] < test_end]

        train_neg = _sample_negatives(session, positives, start, train_end)
        test_neg = _sample_negatives(session, positives, train_end, test_end)

        train_pairs = [(m, c, d) for m, c, d, _ in train_pos] + train_neg
        train_labels = [1] * len(train_pos) + [0] * len(train_neg)
        test_pairs = [(m, c, d) for m, c, d, _ in test_pos] + test_neg
        test_labels = [1] * len(test_pos) + [0] * len(test_neg)

        train_df = _build_frame(session, train_pairs, train_labels, class_names)
        test_df = _build_frame(session, test_pairs, test_labels, class_names)

        X_train = [feature_vector_to_list(row) for row in train_df.to_dict(orient="records")]
        y_train = train_df["label"].tolist()

        model = LogisticRegression(max_iter=1000, class_weight="balanced")
        model.fit(X_train, y_train)

        popularity = dict(Counter(name for _, _, _, name in train_pos))
        eval_metrics = evaluate_split(model, test_df, popularity, k=3)

        artifact = {
            "model": model,
            "feature_names": FEATURE_NAMES,
            "popularity": popularity,
            "algorithm": ALGORITHM,
        }
        model_path = artifacts_dir / MODEL_PATH.name
        joblib.dump(artifact, model_path)

        metrics = {
            "algorithm": ALGORITHM,
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "train_positives": int(len(train_pos)),
            "test_positives": int(len(test_pos)),
            "precision_at_3": round(eval_metrics["precision_at_3"], 4),
            "baseline_precision_at_3": round(eval_metrics["baseline_precision_at_3"], 4),
            "test_members": int(eval_metrics["test_members"]),
            "data_notes": "Synthetic historical enrollments from seed_historical_data.py",
        }
        metrics_path = artifacts_dir / METRICS_PATH.name
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

        print(f"Saved model to {model_path}")
        print(f"Saved metrics to {metrics_path}")
        print(json.dumps(metrics, indent=2))
        return metrics
    finally:
        session.close()


if __name__ == "__main__":
    train()
