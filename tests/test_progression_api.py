from datetime import UTC, date, datetime

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.habits.models import Habit
from apps.progression.models import ProgressEvent
from apps.progression.rules import level_from_total_xp, xp_required_for_level
from apps.progression.services import complete_habit
from apps.quests.models import Quest


def make_authenticated_client(*, username: str, email: str) -> tuple[APIClient, User]:
    user = User.objects.create_user(
        username=username,
        email=email,
        password="strongpass123",
    )
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client, user


def test_complete_habit_action_rewards_profile_and_creates_event(db) -> None:
    client, user = make_authenticated_client(username="hero2", email="hero2@example.com")
    habit = Habit.objects.create(user=user, title="Read", xp_reward=25)

    response = client.post(f"/api/habits/{habit.id}/complete/")

    user.character_profile.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert user.character_profile.total_xp == 25
    assert user.character_profile.current_streak == 1
    assert response.data["profile"]["total_xp"] == 25
    assert response.data["event"]["event_type"] == ProgressEvent.EventType.HABIT_COMPLETED
    assert ProgressEvent.objects.filter(habit=habit).count() == 1


def test_complete_habit_twice_same_day_is_rejected(db) -> None:
    client, user = make_authenticated_client(username="hero3", email="hero3@example.com")
    habit = Habit.objects.create(user=user, title="Journal", xp_reward=15)

    first_response = client.post(f"/api/habits/{habit.id}/complete/")
    second_response = client.post(f"/api/habits/{habit.id}/complete/")

    assert first_response.status_code == status.HTTP_200_OK
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST
    assert ProgressEvent.objects.filter(
        habit=habit,
        event_type=ProgressEvent.EventType.HABIT_COMPLETED,
    ).count() == 1


def test_miss_habit_action_applies_penalty_when_enabled(db) -> None:
    client, user = make_authenticated_client(username="hero4", email="hero4@example.com")
    profile = user.character_profile
    profile.total_xp = 40
    profile.save(update_fields=["total_xp", "updated_at"])
    habit = Habit.objects.create(
        user=user,
        title="Wake up early",
        xp_reward=20,
        penalty_enabled=True,
    )

    response = client.post(f"/api/habits/{habit.id}/miss/")

    profile.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert profile.total_xp == 30
    assert response.data["event"]["xp_delta"] == -10
    assert ProgressEvent.objects.filter(
        habit=habit,
        event_type=ProgressEvent.EventType.HABIT_MISSED,
    ).exists()


def test_complete_quest_action_marks_completed_and_rewards_profile(db) -> None:
    client, user = make_authenticated_client(username="hero5", email="hero5@example.com")
    quest = Quest.objects.create(
        user=user,
        title="Clear the dungeon",
        quest_type=Quest.QuestType.ONE_TIME,
        xp_reward=120,
    )

    response = client.post(f"/api/quests/{quest.id}/complete/")

    quest.refresh_from_db()
    user.character_profile.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert quest.status == Quest.Status.COMPLETED
    assert quest.completed_at is not None
    assert user.character_profile.total_xp == 120
    assert user.character_profile.level == 2
    assert response.data["event"]["event_type"] == ProgressEvent.EventType.QUEST_COMPLETED


def test_fail_quest_action_applies_penalty_and_sets_status_failed(db) -> None:
    client, user = make_authenticated_client(username="hero6", email="hero6@example.com")
    profile = user.character_profile
    profile.total_xp = 50
    profile.save(update_fields=["total_xp", "updated_at"])
    quest = Quest.objects.create(
        user=user,
        title="Escort the caravan",
        xp_reward=30,
    )

    response = client.post(f"/api/quests/{quest.id}/fail/")

    quest.refresh_from_db()
    profile.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert quest.status == Quest.Status.FAILED
    assert quest.completed_at is None
    assert profile.total_xp == 40
    assert response.data["event"]["xp_delta"] == -10


def test_progress_events_endpoint_returns_only_owned_events(db) -> None:
    client, user = make_authenticated_client(username="hero7", email="hero7@example.com")
    other_user = User.objects.create_user(
        username="stranger",
        email="stranger@example.com",
        password="strongpass123",
    )
    own_habit = Habit.objects.create(user=user, title="Own habit")
    foreign_habit = Habit.objects.create(user=other_user, title="Foreign habit")
    ProgressEvent.objects.create(
        user=user,
        profile=user.character_profile,
        habit=own_habit,
        event_type=ProgressEvent.EventType.HABIT_COMPLETED,
        xp_delta=10,
        total_xp_after=10,
        level_after=1,
        streak_after=1,
        occurred_at=datetime(2026, 4, 1, 12, 0, tzinfo=UTC),
        local_date=date(2026, 4, 1),
        timezone="UTC",
    )
    ProgressEvent.objects.create(
        user=other_user,
        profile=other_user.character_profile,
        habit=foreign_habit,
        event_type=ProgressEvent.EventType.HABIT_COMPLETED,
        xp_delta=20,
        total_xp_after=20,
        level_after=1,
        streak_after=1,
        occurred_at=datetime(2026, 4, 1, 13, 0, tzinfo=UTC),
        local_date=date(2026, 4, 1),
        timezone="UTC",
    )

    response = client.get("/api/progress/events/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["habit_title"] == "Own habit"


def test_schema_endpoint_is_available(db) -> None:
    client = APIClient()

    response = client.get("/api/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == status.HTTP_200_OK


def test_timezone_aware_streak_uses_profile_timezone(db) -> None:
    _client, user = make_authenticated_client(username="hero8", email="hero8@example.com")
    profile = user.character_profile
    profile.timezone = "Asia/Tokyo"
    profile.save(update_fields=["timezone", "updated_at"])
    habit = Habit.objects.create(user=user, title="Meditate", xp_reward=10)

    complete_habit(habit=habit, occurred_at=datetime(2026, 4, 1, 14, 0, tzinfo=UTC))
    complete_habit(habit=habit, occurred_at=datetime(2026, 4, 1, 16, 0, tzinfo=UTC))

    profile.refresh_from_db()

    assert profile.current_streak == 2
    assert profile.longest_streak == 2
    assert profile.last_activity_on == date(2026, 4, 2)


def test_progression_rules_calculate_levels_from_thresholds() -> None:
    assert xp_required_for_level(1) == 0
    assert xp_required_for_level(2) == 100
    assert xp_required_for_level(3) == 300
    assert level_from_total_xp(0) == 1
    assert level_from_total_xp(99) == 1
    assert level_from_total_xp(100) == 2
    assert level_from_total_xp(300) == 3
