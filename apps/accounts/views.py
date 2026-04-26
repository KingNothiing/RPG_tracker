from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.accounts.serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserIdentitySerializer,
)
from apps.accounts.services import AuthSession, get_or_create_auth_session
from apps.characters.serializers import CharacterProfileSerializer


def build_auth_response_data(
    auth_session: AuthSession, *, include_profile: bool = False
) -> dict[str, object]:
    response_data: dict[str, object] = {
        "token": auth_session.token.key,
        "user": UserIdentitySerializer(auth_session.user).data,
    }
    if include_profile:
        response_data["profile"] = CharacterProfileSerializer(
            auth_session.user.character_profile
        ).data
    return response_data


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(responses={201: AuthResponseSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        auth_session = get_or_create_auth_session(user=user)
        response_data = build_auth_response_data(auth_session, include_profile=True)
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(responses=AuthResponseSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        auth_session = get_or_create_auth_session(user=user)
        return Response(build_auth_response_data(auth_session))
