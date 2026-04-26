from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model()


@dataclass(frozen=True)
class AuthSession:
    user: User
    token: Token


def get_or_create_auth_session(*, user: User) -> AuthSession:
    token, _ = Token.objects.get_or_create(user=user)
    return AuthSession(user=user, token=token)


@transaction.atomic
def register_user(*, username: str, email: str, password: str):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    return user
