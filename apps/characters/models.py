from django.conf import settings
from django.db import models


class CharacterProfile(models.Model):
    """Gameplay state for a single user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="character_profile",
    )
    character_name = models.CharField(max_length=100)
    level = models.PositiveIntegerField(default=1)
    total_xp = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    timezone = models.CharField(max_length=64, default="UTC")
    last_activity_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.character_name} ({self.user.username})"
