from rest_framework import serializers

from apps.habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = (
            "id",
            "title",
            "description",
            "difficulty",
            "xp_reward",
            "penalty_enabled",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
