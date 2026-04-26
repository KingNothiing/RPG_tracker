from rest_framework import serializers

from apps.habits.models import Habit
from apps.quests.models import Quest


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = (
            "id",
            "habit",
            "title",
            "description",
            "quest_type",
            "xp_reward",
            "status",
            "due_date",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "completed_at", "created_at", "updated_at")

    def validate_habit(self, habit: Habit | None) -> Habit | None:
        if habit is None:
            return None

        request = self.context["request"]
        # This guards ownership explicitly: a quest cannot point to another user's habit.
        if habit.user_id != request.user.id:
            raise serializers.ValidationError("You can only attach your own habits to a quest.")
        return habit
