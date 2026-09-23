from types import SimpleNamespace

from ml.evaluate import precision_at_k
from ml.features import FEATURE_NAMES, _trainer_specialization_match, feature_vector_to_list
from ml.predict import rank_by_popularity
from services.recommendation_service import eligible_candidates


def test_feature_names_cover_required_signals():
    required = {
        "same_class_name_before",
        "same_trainer_before",
        "hour_of_day",
        "is_morning",
        "is_evening",
        "days_until_class",
        "class_fill_ratio",
        "trainer_specialization_match",
        "member_total_bookings",
    }
    assert required.issubset(set(FEATURE_NAMES))
    assert 8 <= len(FEATURE_NAMES) <= 12


def test_feature_vector_to_list_preserves_order():
    features = {name: float(i) for i, name in enumerate(FEATURE_NAMES)}
    assert feature_vector_to_list(features) == [float(i) for i in range(len(FEATURE_NAMES))]


def test_trainer_specialization_match():
    assert _trainer_specialization_match("Morning Yoga", "Flexibility") == 1.0
    assert _trainer_specialization_match("Evening Strength", "Strength") == 1.0
    assert _trainer_specialization_match("Spin Class", "HIIT") == 0.0


def test_full_classes_excluded_from_recommendations():
    open_class = SimpleNamespace(class_id=1, is_full=False)
    full_class = SimpleNamespace(class_id=2, is_full=True)
    result = eligible_candidates([open_class, full_class], enrolled_class_ids=set())
    assert [c.class_id for c in result] == [1]


def test_already_enrolled_classes_excluded():
    booked = SimpleNamespace(class_id=10, is_full=False)
    other = SimpleNamespace(class_id=11, is_full=False)
    result = eligible_candidates([booked, other], enrolled_class_ids={10})
    assert [c.class_id for c in result] == [11]


def test_cold_start_ranks_by_popularity():
    yoga = SimpleNamespace(class_name="Morning Yoga")
    hiit = SimpleNamespace(class_name="HIIT Blast")
    artifact = {"popularity": {"Morning Yoga": 40, "HIIT Blast": 5}}
    ranked = rank_by_popularity(artifact, [hiit, yoga], limit=1)
    assert ranked[0][0].class_name == "Morning Yoga"


def test_precision_at_3():
    ranked = [1, 2, 3, 4]
    assert precision_at_k(ranked, {3, 9}, k=3) == 1 / 3
    assert precision_at_k(ranked, {1, 2, 3}, k=3) == 1.0
