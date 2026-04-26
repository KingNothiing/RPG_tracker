from django.conf import settings
from django.db import models


class ProgressEvent(models.Model):
    """Immutable history of progression-changing actions."""

    class EventType(models.TextChoices):
        HABIT_COMPLETED = "habit_completed", "Habit Completed"
        HABIT_MISSED = "habit_missed", "Habit Missed"
        QUEST_COMPLETED = "quest_completed", "Quest Completed"
        QUEST_FAILED = "quest_failed", "Quest Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_events",
    )
    profile = models.ForeignKey(
        "characters.CharacterProfile",
        on_delete=models.CASCADE,
        related_name="progress_events",
    )
    habit = models.ForeignKey(
        "habits.Habit",
        on_delete=models.CASCADE,
        related_name="progress_events",
        null=True,
        blank=True,
    )
    quest = models.ForeignKey(
        "quests.Quest",
        on_delete=models.CASCADE,
        related_name="progress_events",
        null=True,
        blank=True,
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    xp_delta = models.IntegerField()
    total_xp_after = models.PositiveIntegerField()
    level_after = models.PositiveIntegerField()
    streak_after = models.PositiveIntegerField()
    occurred_at = models.DateTimeField()
    local_date = models.DateField()
    timezone = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(fields=("user", "occurred_at")),
            models.Index(fields=("event_type", "local_date")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(habit__isnull=False) | models.Q(quest__isnull=False),
                name="progress_event_has_source",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} for {self.user.username} at {self.occurred_at.isoformat()}"
