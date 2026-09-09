"""
Feature engineering for (member_id, class_id) recommendation pairs.

Features are computed from historical ClassEnrollment rows and the target
GroupClass metadata. Used by train.py and recommendation_service.py.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session, joinedload

from models.class_enrollment import AttendanceStatus, ClassEnrollment
from models.group_class import GroupClass
from models.member import Member

POSITIVE_STATUSES = {AttendanceStatus.REGISTERED, AttendanceStatus.ATTENDED}

FEATURE_NAMES = [
    "same_class_name_before",
    "same_trainer_before",
    "hour_of_day",
    "is_morning",
    "is_evening",
    "days_until_class",
    "class_fill_ratio",
    "trainer_specialization_match",
    "member_total_bookings",
    "member_attendance_rate",
    "books_this_weekday_before",
]

SPECIALIZATION_KEYWORDS = {
    "yoga": {"yoga", "flexibility"},
    "pilates": {"flexibility", "yoga"},
    "strength": {"strength"},
    "lifting": {"strength"},
    "hiit": {"hiit", "cardio"},
    "spin": {"cardio"},
    "cardio": {"cardio"},
}


def _active_enrollments(group_class: GroupClass) -> list[ClassEnrollment]:
    return [
        e
        for e in group_class.enrollments
        if e.attendance_status in POSITIVE_STATUSES
    ]


def _member_history(
    session: Session,
    member_id: int,
    reference_date: date,
) -> list[tuple[ClassEnrollment, GroupClass]]:
    rows = (
        session.query(ClassEnrollment, GroupClass)
        .join(GroupClass, ClassEnrollment.class_id == GroupClass.class_id)
        .filter(
            ClassEnrollment.member_id == member_id,
            ClassEnrollment.attendance_status.in_(list(POSITIVE_STATUSES)),
            GroupClass.scheduled_date < reference_date,
        )
        .all()
    )
    return [(enrollment, group_class) for enrollment, group_class in rows]


def _trainer_specialization_match(class_name: str, specialization: str | None) -> float:
    if not specialization:
        return 0.0
    class_lower = class_name.lower()
    spec_lower = specialization.lower()
    if spec_lower in class_lower:
        return 1.0
    for keyword, specs in SPECIALIZATION_KEYWORDS.items():
        if keyword in class_lower and spec_lower in specs:
            return 1.0
    return 0.0


def build_feature_vector(
    session: Session,
    member_id: int,
    class_id: int,
    reference_date: date | None = None,
) -> dict[str, float]:
    """
    Build a feature dict for one (member, class) candidate pair.

    reference_date: cutoff for history features and days_until_class
                    (defaults to today).
    """
    ref_date = reference_date or date.today()

    group_class = (
        session.query(GroupClass)
        .options(
            joinedload(GroupClass.enrollments),
            joinedload(GroupClass.trainer),
        )
        .filter(GroupClass.class_id == class_id)
        .first()
    )
    if not group_class:
        raise ValueError(f"Class {class_id} not found")

    member = session.query(Member).filter(Member.member_id == member_id).first()
    if not member:
        raise ValueError(f"Member {member_id} not found")

    history = _member_history(session, member_id, ref_date)

    same_class_name_before = sum(
        1 for _, gc in history if gc.class_name == group_class.class_name
    )
    same_trainer_before = sum(
        1 for _, gc in history if gc.trainer_id == group_class.trainer_id
    )

    hour = group_class.start_time.hour if group_class.start_time else 12
    is_morning = 1.0 if hour < 12 else 0.0
    is_evening = 1.0 if hour >= 17 else 0.0
    days_until = (group_class.scheduled_date - ref_date).days

    active = _active_enrollments(group_class)
    fill_ratio = len(active) / group_class.capacity if group_class.capacity else 0.0

    trainer_spec = group_class.trainer.specialization if group_class.trainer else None
    spec_match = _trainer_specialization_match(group_class.class_name, trainer_spec)

    member_total = len(history)
    attended = sum(
        1
        for enrollment, gc in history
        if enrollment.attendance_status == AttendanceStatus.ATTENDED
        and gc.scheduled_date < ref_date
    )
    attendance_rate = attended / member_total if member_total else 0.0

    target_weekday = group_class.scheduled_date.weekday()
    weekday_bookings = sum(
        1 for _, gc in history if gc.scheduled_date.weekday() == target_weekday
    )

    return {
        "same_class_name_before": float(same_class_name_before),
        "same_trainer_before": float(same_trainer_before),
        "hour_of_day": float(hour),
        "is_morning": is_morning,
        "is_evening": is_evening,
        "days_until_class": float(days_until),
        "class_fill_ratio": float(fill_ratio),
        "trainer_specialization_match": spec_match,
        "member_total_bookings": float(member_total),
        "member_attendance_rate": float(attendance_rate),
        "books_this_weekday_before": float(weekday_bookings),
    }


def feature_vector_to_list(features: dict[str, float]) -> list[float]:
    return [features[name] for name in FEATURE_NAMES]


def build_training_row(
    session: Session,
    member_id: int,
    class_id: int,
    label: int,
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Build one labeled row for model training."""
    features = build_feature_vector(session, member_id, class_id, reference_date)
    return {"member_id": member_id, "class_id": class_id, "label": label, **features}


if __name__ == "__main__":
    from database.connection import SessionLocal

    session = SessionLocal()
    try:
        sample_member = session.query(Member).filter(Member.email == "alice@test.com").first()
        sample_class = (
            session.query(GroupClass)
            .filter(GroupClass.class_name == "Morning Yoga")
            .order_by(GroupClass.scheduled_date.desc())
            .first()
        )
        if not sample_member or not sample_class:
            print("Run seed + seed_historical_data first.")
        else:
            features = build_feature_vector(
                session, sample_member.member_id, sample_class.class_id
            )
            print(f"Member: {sample_member.first_name} ({sample_member.email})")
            print(f"Class:  {sample_class.class_name} on {sample_class.scheduled_date}")
            for name in FEATURE_NAMES:
                print(f"  {name:30s} {features[name]}")
    finally:
        session.close()
