from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model()


@transaction.atomic
def register_user(*, username: str, email: str, password: str):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    token, _ = Token.objects.get_or_create(user=user)
    return user, token
