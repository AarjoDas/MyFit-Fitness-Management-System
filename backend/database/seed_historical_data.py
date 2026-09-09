"""
Synthetic historical enrollment data for ML training.

This script EXTENDS the minimal seed from seed_data.py — it does not wipe
existing rows. All enrollments and extra members/trainers/classes are synthetic
and should be documented as such in the README and resume materials.

Run after base seed:
    cd backend
    python reset_database.py          # optional fresh start
    python -m database.seed_historical_data
"""

from __future__ import annotations

import random
from datetime import date, time, timedelta

from sqlalchemy.orm import joinedload

from database.connection import SessionLocal, engine, Base
from models.class_enrollment import AttendanceStatus, ClassEnrollment
from models.group_class import GroupClass
from models.member import GenderEnum, Member
from models.room import Room
from models.trainer import Trainer

# Reproducible synthetic patterns for demo + eval
RANDOM_SEED = 42
MIN_ENROLLMENTS = 200
TARGET_MEMBERS = 20
TARGET_TRAINERS = 4
HISTORY_DAYS = 90

EXTRA_TRAINERS = [
    {
        "first_name": "Mike",
        "last_name": "Chen",
        "email": "mike@fit.com",
        "specialization": "Cardio",
        "hire_date": date(2023, 6, 1),
    },
    {
        "first_name": "Emma",
        "last_name": "Wilson",
        "email": "emma@fit.com",
        "specialization": "Flexibility",
        "hire_date": date(2023, 8, 15),
    },
]

EXTRA_MEMBERS = [
    ("Carol", "Davis", "carol@test.com", date(1992, 3, 12), GenderEnum.FEMALE),
    ("David", "Lee", "david@test.com", date(1988, 11, 5), GenderEnum.MALE),
    ("Eva", "Martinez", "eva@test.com", date(1996, 7, 22), GenderEnum.FEMALE),
    ("Frank", "Brown", "frank@test.com", date(1991, 1, 30), GenderEnum.MALE),
    ("Grace", "Taylor", "grace@test.com", date(1994, 9, 8), GenderEnum.FEMALE),
    ("Henry", "Anderson", "henry@test.com", date(1987, 4, 17), GenderEnum.MALE),
    ("Ivy", "Thomas", "ivy@test.com", date(1998, 12, 3), GenderEnum.FEMALE),
    ("Jack", "Moore", "jack@test.com", date(1990, 6, 25), GenderEnum.MALE),
    ("Kate", "Jackson", "kate@test.com", date(1993, 2, 14), GenderEnum.FEMALE),
    ("Leo", "White", "leo@test.com", date(1989, 8, 9), GenderEnum.MALE),
    ("Mia", "Harris", "mia@test.com", date(1997, 5, 1), GenderEnum.FEMALE),
    ("Noah", "Clark", "noah@test.com", date(1991, 10, 19), GenderEnum.MALE),
    ("Olivia", "Lewis", "olivia@test.com", date(1995, 4, 6), GenderEnum.FEMALE),
    ("Paul", "Walker", "paul@test.com", date(1986, 7, 28), GenderEnum.MALE),
    ("Quinn", "Hall", "quinn@test.com", date(1999, 1, 11), GenderEnum.OTHER),
    ("Rita", "Allen", "rita@test.com", date(1992, 8, 23), GenderEnum.FEMALE),
    ("Sam", "Young", "sam@test.com", date(1994, 3, 7), GenderEnum.MALE),
    ("Tina", "King", "tina@test.com", date(1990, 11, 16), GenderEnum.FEMALE),
]

# (class_name, trainer_email, room_name, weekday, hour, capacity)
CLASS_SCHEDULE = [
    ("Morning Yoga", "john@fit.com", "Yoga Studio", 0, 9, 15),
    ("Morning Yoga", "john@fit.com", "Yoga Studio", 2, 9, 15),
    ("Morning Yoga", "john@fit.com", "Yoga Studio", 4, 9, 15),
    ("HIIT Blast", "john@fit.com", "Cardio Zone", 1, 17, 20),
    ("HIIT Blast", "john@fit.com", "Cardio Zone", 3, 17, 20),
    ("Evening Strength", "sarah@fit.com", "Weight Room", 1, 18, 18),
    ("Evening Strength", "sarah@fit.com", "Weight Room", 3, 18, 18),
    ("Power Lifting", "sarah@fit.com", "Weight Room", 5, 19, 12),
    ("Spin Class", "mike@fit.com", "Cardio Zone", 2, 12, 25),
    ("Spin Class", "mike@fit.com", "Cardio Zone", 4, 12, 25),
    ("Pilates", "emma@fit.com", "Yoga Studio", 0, 10, 15),
    ("Pilates", "emma@fit.com", "Yoga Studio", 3, 10, 15),
]

# Learnable member preferences (email -> preferred class names / trainers)
MEMBER_PREFERENCES = {
    "alice@test.com": {
        "class_names": ["Morning Yoga", "Pilates"],
        "trainer_emails": ["john@fit.com", "emma@fit.com"],
        "weight": 0.75,
    },
    "bob@test.com": {
        "class_names": ["Evening Strength", "Power Lifting"],
        "trainer_emails": ["sarah@fit.com"],
        "weight": 0.75,
    },
    "carol@test.com": {
        "class_names": ["Spin Class", "HIIT Blast"],
        "trainer_emails": ["mike@fit.com", "john@fit.com"],
        "weight": 0.65,
    },
    "david@test.com": {
        "class_names": ["Morning Yoga"],
        "trainer_emails": ["john@fit.com"],
        "weight": 0.60,
    },
}


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _get_or_create_trainers(session) -> dict[str, Trainer]:
    trainers_by_email: dict[str, Trainer] = {
        t.email: t for t in session.query(Trainer).all()
    }
    for spec in EXTRA_TRAINERS:
        if spec["email"] not in trainers_by_email:
            trainer = Trainer(**spec)
            session.add(trainer)
            session.flush()
            trainers_by_email[spec["email"]] = trainer
    session.commit()
    return trainers_by_email


def _get_or_create_members(session) -> list[Member]:
    members = session.query(Member).all()
    existing_emails = {m.email for m in members}
    reg_base = date.today() - timedelta(days=HISTORY_DAYS + 10)

    for idx, (first, last, email, dob, gender) in enumerate(EXTRA_MEMBERS):
        if email not in existing_emails:
            member = Member(
                first_name=first,
                last_name=last,
                email=email,
                date_of_birth=dob,
                gender=gender,
                registration_date=reg_base + timedelta(days=idx * 3),
            )
            session.add(member)

    session.commit()
    members = session.query(Member).order_by(Member.member_id).all()
    if len(members) < TARGET_MEMBERS:
        raise RuntimeError(
            f"Expected at least {TARGET_MEMBERS} members after seeding; got {len(members)}."
        )
    return members


def _rooms_by_name(session) -> dict[str, Room]:
    return {room.room_name: room for room in session.query(Room).all()}


def _generate_classes(
    session,
    trainers_by_email: dict[str, Trainer],
    rooms_by_name: dict[str, Room],
    today: date,
) -> list[GroupClass]:
    """Create recurring classes over the past HISTORY_DAYS plus 14 upcoming days."""
    start = today - timedelta(days=HISTORY_DAYS)
    end = today + timedelta(days=14)
    created: list[GroupClass] = []

    existing_keys = {
        (gc.class_name, gc.scheduled_date, gc.start_time)
        for gc in session.query(GroupClass).all()
    }

    for class_name, trainer_email, room_name, weekday, hour, capacity in CLASS_SCHEDULE:
        trainer = trainers_by_email[trainer_email]
        room = rooms_by_name[room_name]
        current = start
        while current <= end:
            if current.weekday() == weekday:
                start_t = time(hour, 0)
                key = (class_name, current, start_t)
                if key not in existing_keys:
                    group_class = GroupClass(
                        class_name=class_name,
                        trainer_id=trainer.trainer_id,
                        room_id=room.room_id,
                        scheduled_date=current,
                        start_time=start_t,
                        end_time=time(hour + 1, 0),
                        capacity=capacity,
                    )
                    session.add(group_class)
                    created.append(group_class)
                    existing_keys.add(key)
            current += timedelta(days=1)

    session.commit()
    return created


def _member_booking_probability(
    member: Member,
    group_class: GroupClass,
    trainer_email_by_id: dict[int, str],
) -> float:
    prefs = MEMBER_PREFERENCES.get(member.email)
    base = 0.12
    if not prefs:
        return base

    trainer_email = trainer_email_by_id.get(group_class.trainer_id, "")
    class_match = group_class.class_name in prefs["class_names"]
    trainer_match = trainer_email in prefs["trainer_emails"]

    if class_match and trainer_match:
        return prefs["weight"]
    if class_match or trainer_match:
        return prefs["weight"] * 0.55
    return base * 0.5


def _pick_attendance_status(class_date: date, today: date) -> AttendanceStatus:
    if class_date >= today:
        return AttendanceStatus.REGISTERED

    roll = random.random()
    if roll < 0.08:
        return AttendanceStatus.CANCELLED
    if roll < 0.15:
        return AttendanceStatus.ABSENT
    return AttendanceStatus.ATTENDED


def _generate_enrollments(session, members: list[Member], today: date) -> int:
    classes = (
        session.query(GroupClass)
        .options(joinedload(GroupClass.enrollments))
        .order_by(GroupClass.scheduled_date)
        .all()
    )
    trainers = session.query(Trainer).all()
    trainer_email_by_id = {t.trainer_id: t.email for t in trainers}

    existing_pairs = {
        (e.member_id, e.class_id)
        for e in session.query(ClassEnrollment).all()
    }

    created = 0
    for group_class in classes:
        if group_class.scheduled_date > today + timedelta(days=14):
            continue

        candidates: list[tuple[Member, float]] = []
        for member in members:
            if member.registration_date > group_class.scheduled_date:
                continue
            prob = _member_booking_probability(member, group_class, trainer_email_by_id)
            if random.random() < prob:
                candidates.append((member, prob))

        if not candidates:
            continue

        random.shuffle(candidates)
        max_enroll = min(group_class.capacity - 1, len(candidates))
        min_enroll = min(3, max_enroll)
        if max_enroll <= 0:
            continue

        target_count = random.randint(max(1, min_enroll), max_enroll)
        selected = candidates[:target_count]

        for member, _ in selected:
            pair = (member.member_id, group_class.class_id)
            if pair in existing_pairs:
                continue

            enroll_date = max(
                member.registration_date,
                group_class.scheduled_date - timedelta(days=random.randint(1, 5)),
            )
            enrollment = ClassEnrollment(
                member_id=member.member_id,
                class_id=group_class.class_id,
                enrollment_date=enroll_date,
                attendance_status=_pick_attendance_status(group_class.scheduled_date, today),
            )
            session.add(enrollment)
            existing_pairs.add(pair)
            created += 1

    session.commit()
    return created


def seed_historical_data() -> None:
    random.seed(RANDOM_SEED)
    _ensure_tables()

    session = SessionLocal()
    try:
        if not session.query(Room).first():
            print("Base seed missing. Run: python reset_database.py")
            return

        existing_count = session.query(ClassEnrollment).count()
        if existing_count >= MIN_ENROLLMENTS:
            print(
                f"Historical data already present ({existing_count} enrollments). Skipping."
            )
            return

        today = date.today()
        trainers_by_email = _get_or_create_trainers(session)
        if len(trainers_by_email) < TARGET_TRAINERS:
            raise RuntimeError("Could not ensure 4 trainers.")

        members = _get_or_create_members(session)
        rooms_by_name = _rooms_by_name(session)

        new_classes = _generate_classes(session, trainers_by_email, rooms_by_name, today)
        new_enrollments = _generate_enrollments(session, members, today)

        total_members = session.query(Member).count()
        total_trainers = session.query(Trainer).count()
        total_classes = session.query(GroupClass).count()
        total_enrollments = session.query(ClassEnrollment).count()

        print("Historical seed complete (synthetic data for ML).")
        print(f"  Members:      {total_members}")
        print(f"  Trainers:     {total_trainers}")
        print(f"  Classes:      {total_classes} (+{len(new_classes)} new this run)")
        print(f"  Enrollments:  {total_enrollments} (+{new_enrollments} new this run)")

        if total_enrollments < MIN_ENROLLMENTS:
            print(
                f"WARNING: Only {total_enrollments} enrollments "
                f"(target {MIN_ENROLLMENTS}+). Re-run or adjust probabilities."
            )
    finally:
        session.close()


if __name__ == "__main__":
    seed_historical_data()
