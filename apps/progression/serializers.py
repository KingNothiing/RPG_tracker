from rest_framework import serializers

from apps.characters.serializers import CharacterProfileSerializer
from apps.habits.serializers import HabitSerializer
from apps.progression.models import ProgressEvent
from apps.quests.serializers import QuestSerializer


class ProgressEventSerializer(serializers.ModelSerializer):
    habit_title = serializers.CharField(source="habit.title", read_only=True)
    quest_title = serializers.CharField(source="quest.title", read_only=True)

    class Meta:
        model = ProgressEvent
        fields = (
            "id",
            "event_type",
            "xp_delta",
            "total_xp_after",
            "level_after",
            "streak_after",
            "occurred_at",
            "local_date",
            "timezone",
            "habit",
            "habit_title",
            "quest",
            "quest_title",
        )
        read_only_fields = fields


class ProgressionActionResponseSerializer(serializers.Serializer):
    event = ProgressEventSerializer()
    profile = CharacterProfileSerializer()
    habit = HabitSerializer(required=False)
    quest = QuestSerializer(required=False)
