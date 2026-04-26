from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from apps.accounts.services import register_user
from apps.characters.serializers import CharacterProfileSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        return register_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs


class UserIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserIdentitySerializer()
    profile = CharacterProfileSerializer(required=False)
