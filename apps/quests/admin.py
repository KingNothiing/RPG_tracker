from django.contrib import admin

from apps.quests.models import Quest


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "quest_type",
        "status",
        "habit",
        "due_date",
        "updated_at",
    )
    list_filter = ("quest_type", "status")
    search_fields = ("title", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
