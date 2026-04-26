from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.characters.models import CharacterProfile


def test_register_creates_user_profile_and_token(db) -> None:
    client = APIClient()

    response = client.post(
        "/api/auth/register/",
        {
            "username": "hero",
            "email": "hero@example.com",
            "password": "strongpass123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="hero").exists()

    user = User.objects.get(username="hero")
    profile = CharacterProfile.objects.get(user=user)
    token = Token.objects.get(user=user)

    assert profile.character_name == "hero"
    assert response.data["token"] == token.key
    assert response.data["profile"]["character_name"] == "hero"
    assert response.data["profile"]["level"] == 1


def test_login_returns_existing_token(db) -> None:
    user = User.objects.create_user(
        username="rogue",
        email="rogue@example.com",
        password="strongpass123",
    )
    token = Token.objects.create(user=user)
    client = APIClient()

    response = client.post(
        "/api/auth/login/",
        {
            "username": "rogue",
            "password": "strongpass123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["token"] == token.key


def test_profile_requires_authentication(db) -> None:
    client = APIClient()

    response = client.get("/api/profile/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticated_user_can_view_and_update_only_own_profile(db) -> None:
    user = User.objects.create_user(
        username="mage",
        email="mage@example.com",
        password="strongpass123",
    )
    other_user = User.objects.create_user(
        username="warrior",
        email="warrior@example.com",
        password="strongpass123",
    )
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    get_response = client.get("/api/profile/")
    patch_response = client.patch(
        "/api/profile/",
        {
            "character_name": "Archmage",
            "level": 99,
        },
        format="json",
    )

    user.character_profile.refresh_from_db()
    other_user.character_profile.refresh_from_db()

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.data["username"] == "mage"
    assert patch_response.status_code == status.HTTP_200_OK
    assert user.character_profile.character_name == "Archmage"
    assert user.character_profile.level == 1
    assert other_user.character_profile.character_name == "warrior"


def test_profile_timezone_can_be_updated_and_validated(db) -> None:
    user = User.objects.create_user(
        username="cleric",
        email="cleric@example.com",
        password="strongpass123",
    )
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    valid_response = client.patch(
        "/api/profile/",
        {"timezone": "Europe/Chisinau"},
        format="json",
    )
    invalid_response = client.patch(
        "/api/profile/",
        {"timezone": "Mars/Olympus"},
        format="json",
    )

    user.character_profile.refresh_from_db()

    assert valid_response.status_code == status.HTTP_200_OK
    assert user.character_profile.timezone == "Europe/Chisinau"
    assert invalid_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "timezone" in invalid_response.data
