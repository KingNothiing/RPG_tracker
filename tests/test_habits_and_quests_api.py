from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.habits.models import Habit
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


def test_user_can_create_and_list_only_own_habits(db) -> None:
    client, user = make_authenticated_client(username="hero", email="hero@example.com")
    other_user = User.objects.create_user(
        username="other",
        email="other@example.com",
        password="strongpass123",
    )
    Habit.objects.create(user=other_user, title="Other habit")

    create_response = client.post(
        "/api/habits/",
        {
            "title": "Read daily",
            "description": "Read 20 pages",
            "difficulty": "easy",
            "xp_reward": 15,
            "penalty_enabled": True,
            "is_active": True,
        },
        format="json",
    )
    list_response = client.get("/api/habits/")

    assert create_response.status_code == status.HTTP_201_CREATED
    assert Habit.objects.filter(user=user, title="Read daily").exists()
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data) == 1
    assert list_response.data[0]["title"] == "Read daily"


def test_user_cannot_access_or_modify_foreign_habit(db) -> None:
    owner = User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="strongpass123",
    )
    foreign_habit = Habit.objects.create(user=owner, title="Owner habit")
    client, _user = make_authenticated_client(username="intruder", email="intruder@example.com")

    detail_response = client.get(f"/api/habits/{foreign_habit.id}/")
    patch_response = client.patch(
        f"/api/habits/{foreign_habit.id}/",
        {"title": "Hacked"},
        format="json",
    )
    delete_response = client.delete(f"/api/habits/{foreign_habit.id}/")

    foreign_habit.refresh_from_db()

    assert detail_response.status_code == status.HTTP_404_NOT_FOUND
    assert patch_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert foreign_habit.title == "Owner habit"


def test_user_can_create_quest_linked_to_own_habit(db) -> None:
    client, user = make_authenticated_client(username="mage", email="mage@example.com")
    habit = Habit.objects.create(user=user, title="Study magic")

    response = client.post(
        "/api/quests/",
        {
            "habit": habit.id,
            "title": "Finish one chapter",
            "description": "Chapter on elemental control",
            "quest_type": "daily",
            "status": "open",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    quest = Quest.objects.get(title="Finish one chapter")
    assert quest.user == user
    assert quest.habit == habit


def test_user_cannot_attach_foreign_habit_to_quest(db) -> None:
    owner = User.objects.create_user(
        username="owner2",
        email="owner2@example.com",
        password="strongpass123",
    )
    foreign_habit = Habit.objects.create(user=owner, title="Foreign habit")
    client, user = make_authenticated_client(username="rogue", email="rogue@example.com")

    response = client.post(
        "/api/quests/",
        {
            "habit": foreign_habit.id,
            "title": "Sneaky quest",
            "description": "Should fail",
            "quest_type": "one_time",
            "status": "open",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "habit" in response.data
    assert Quest.objects.filter(user=user).count() == 0


def test_user_sees_only_own_quests(db) -> None:
    client, user = make_authenticated_client(username="warrior", email="warrior@example.com")
    other_user = User.objects.create_user(
        username="otherwarrior",
        email="otherwarrior@example.com",
        password="strongpass123",
    )
    Quest.objects.create(user=user, title="Own quest")
    Quest.objects.create(user=other_user, title="Foreign quest")

    response = client.get("/api/quests/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Own quest"


def test_quest_status_is_server_managed_on_create(db) -> None:
    client, _user = make_authenticated_client(username="paladin", email="paladin@example.com")

    response = client.post(
        "/api/quests/",
        {
            "title": "Defeat the dungeon boss",
            "quest_type": "one_time",
            "xp_reward": 80,
            "status": "completed",
            "completed_at": "2000-01-01T00:00:00Z",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    quest = Quest.objects.get(title="Defeat the dungeon boss")
    assert quest.status == Quest.Status.OPEN
    assert quest.completed_at is None
    assert response.data["status"] == Quest.Status.OPEN
    assert response.data["completed_at"] is None


def test_quest_status_cannot_be_changed_via_patch(db) -> None:
    client, user = make_authenticated_client(username="ranger", email="ranger@example.com")
    quest = Quest.objects.create(
        user=user,
        title="Scout the forest",
        status=Quest.Status.OPEN,
    )

    response = client.patch(
        f"/api/quests/{quest.id}/",
        {"status": "failed"},
        format="json",
    )

    quest.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert quest.status == Quest.Status.OPEN
    assert quest.completed_at is None
    assert response.data["completed_at"] is None
