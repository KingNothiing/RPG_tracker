from django.contrib import admin

from apps.progression.models import ProgressEvent


@admin.register(ProgressEvent)
class ProgressEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event_type",
        "xp_delta",
        "level_after",
        "streak_after",
        "local_date",
        "occurred_at",
    )
    list_filter = ("event_type", "timezone")
    search_fields = (
        "user__username",
        "user__email",
        "habit__title",
        "quest__title",
    )
    readonly_fields = (
        "created_at",
        "occurred_at",
        "local_date",
        "timezone",
        "xp_delta",
        "total_xp_after",
        "level_after",
        "streak_after",
    )
