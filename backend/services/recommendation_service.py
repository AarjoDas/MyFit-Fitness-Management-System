from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session, joinedload

from ml import METRICS_PATH, MODEL_PATH
from ml.features import POSITIVE_STATUSES, build_feature_vector
from ml.predict import load_artifact, rank_by_popularity, score_features
from models.class_enrollment import ClassEnrollment
from models.group_class import GroupClass
from models.member import Member


def eligible_candidates(
    classes: list[GroupClass],
    enrolled_class_ids: set[int],
) -> list[GroupClass]:
    """Upcoming classes that are not full and not already booked by the member."""
    eligible = []
    for group_class in classes:
        if group_class.class_id in enrolled_class_ids:
            continue
        if group_class.is_full:
            continue
        eligible.append(group_class)
    return eligible


class RecommendationService:
    def __init__(self, db_session: Session, model_path: Path | None = None):
        self.db = db_session
        self.model_path = model_path or MODEL_PATH

    def get_recommendations(self, member_id: int, limit: int = 5) -> list[dict]:
        member = self.db.query(Member).filter(Member.member_id == member_id).first()
        if not member:
            raise ValueError("Member not found.")

        artifact = load_artifact(self.model_path)
        today = date.today()
        upcoming = (
            self.db.query(GroupClass)
            .options(
                joinedload(GroupClass.enrollments),
                joinedload(GroupClass.trainer),
            )
            .filter(GroupClass.scheduled_date >= today)
            .order_by(GroupClass.scheduled_date, GroupClass.start_time)
            .all()
        )

        enrolled_ids = {
            enrollment.class_id
            for enrollment in self.db.query(ClassEnrollment)
            .filter(
                ClassEnrollment.member_id == member_id,
                ClassEnrollment.attendance_status.in_(list(POSITIVE_STATUSES)),
            )
            .all()
        }

        candidates = eligible_candidates(upcoming, enrolled_ids)
        booking_count = self._booking_count(member_id)
        if booking_count == 0:
            ranked = rank_by_popularity(artifact, candidates, limit)
            return [
                self._serialize(
                    group_class,
                    score,
                    self._explain(member, group_class, {}, cold_start=True),
                )
                for group_class, score in ranked
            ]

        scored: list[tuple[GroupClass, float, dict[str, float]]] = []
        for group_class in candidates:
            features = build_feature_vector(self.db, member_id, group_class.class_id, today)
            score = score_features(artifact, features)
            scored.append((group_class, score, features))

        scored.sort(key=lambda item: item[1], reverse=True)
        top = scored[:limit]
        return [
            self._serialize(group_class, score, self._explain(member, group_class, features))
            for group_class, score, features in top
        ]

    def retrain(self) -> dict:
        from ml.train import train

        return train()

    def get_metrics(self) -> dict:
        if not METRICS_PATH.exists():
            raise ValueError("No metrics.json found. Train the model first.")
        import json

        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    def _booking_count(self, member_id: int) -> int:
        return (
            self.db.query(ClassEnrollment)
            .filter(
                ClassEnrollment.member_id == member_id,
                ClassEnrollment.attendance_status.in_(list(POSITIVE_STATUSES)),
            )
            .count()
        )

    def _explain(
        self,
        member: Member,
        group_class: GroupClass,
        features: dict[str, float],
        cold_start: bool = False,
    ) -> str:
        if cold_start:
            return f"{group_class.class_name} is among the most popular classes at the club"

        trainer = group_class.trainer
        trainer_name = f"{trainer.first_name} {trainer.last_name}" if trainer else "this trainer"

        if features.get("same_class_name_before", 0) >= 1:
            return f"You've booked {group_class.class_name} before"
        if features.get("same_trainer_before", 0) >= 1:
            return f"You often train with {trainer_name}"
        if features.get("trainer_specialization_match", 0) >= 1 and trainer:
            return f"{trainer_name} specializes in {trainer.specialization}"
        if features.get("is_morning", 0) == 1 and features.get("books_this_weekday_before", 0) >= 1:
            return "You often book morning classes on this weekday"
        if features.get("is_evening", 0) == 1:
            return "Evening class that matches typical gym hours"
        return f"Recommended based on your booking history ({group_class.class_name})"

    def _serialize(self, group_class: GroupClass, score: float, reason: str) -> dict:
        trainer = group_class.trainer
        trainer_name = f"{trainer.first_name} {trainer.last_name}" if trainer else None
        return {
            "class_id": group_class.class_id,
            "class_name": group_class.class_name,
            "scheduled_date": group_class.scheduled_date,
            "start_time": group_class.start_time,
            "trainer_id": group_class.trainer_id,
            "trainer_name": trainer_name,
            "score": round(float(score), 4),
            "reason": reason,
        }
