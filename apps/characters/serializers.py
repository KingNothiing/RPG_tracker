from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from apps.characters.models import CharacterProfile


class CharacterProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CharacterProfile
        fields = (
            "username",
            "email",
            "character_name",
            "level",
            "total_xp",
            "current_streak",
            "longest_streak",
            "timezone",
            "last_activity_on",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "username",
            "email",
            "level",
            "total_xp",
            "current_streak",
            "longest_streak",
            "last_activity_on",
            "created_at",
            "updated_at",
        )


class CharacterProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterProfile
        fields = ("character_name", "timezone")

    def validate_timezone(self, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise serializers.ValidationError("Enter a valid IANA timezone name.") from exc
        return value
