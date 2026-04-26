from django.conf import settings
from django.db import models
from django.utils import timezone


class Quest(models.Model):
    """A concrete objective the player can complete."""

    class QuestType(models.TextChoices):
        DAILY = "daily", "Daily"
        ONE_TIME = "one_time", "One Time"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quests",
    )
    habit = models.ForeignKey(
        "habits.Habit",
        on_delete=models.SET_NULL,
        related_name="quests",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    quest_type = models.CharField(max_length=10, choices=QuestType.choices, default=QuestType.DAILY)
    xp_reward = models.PositiveIntegerField(default=25)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def sync_completion_state(self) -> None:
        if self.status == self.Status.COMPLETED:
            self.completed_at = self.completed_at or timezone.now()
            return

        self.completed_at = None

    def save(self, *args, **kwargs):
        self.sync_completion_state()
        super().save(*args, **kwargs)
