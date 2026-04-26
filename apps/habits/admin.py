from django.contrib import admin

from apps.habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "difficulty",
        "xp_reward",
        "penalty_enabled",
        "is_active",
        "updated_at",
    )
    list_filter = ("difficulty", "penalty_enabled", "is_active")
    search_fields = ("title", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
