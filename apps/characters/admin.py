from django.contrib import admin

from apps.characters.models import CharacterProfile


@admin.register(CharacterProfile)
class CharacterProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "character_name",
        "level",
        "total_xp",
        "current_streak",
        "longest_streak",
        "updated_at",
    )
    search_fields = ("user__username", "user__email", "character_name")
    readonly_fields = ("created_at", "updated_at")
