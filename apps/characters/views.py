from rest_framework import generics

from apps.characters.models import CharacterProfile
from apps.characters.serializers import (
    CharacterProfileSerializer,
    CharacterProfileUpdateSerializer,
)
from apps.progression.services import refresh_profile_streak


class CharacterProfileView(generics.RetrieveUpdateAPIView):
    queryset = CharacterProfile.objects.select_related("user")

    def get_object(self) -> CharacterProfile:
        profile = self.request.user.character_profile
        refresh_profile_streak(profile=profile)
        return profile

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return CharacterProfileUpdateSerializer
        return CharacterProfileSerializer
