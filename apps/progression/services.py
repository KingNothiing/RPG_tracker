from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

from apps.characters.models import CharacterProfile
from apps.habits.models import Habit
from apps.progression.models import ProgressEvent
from apps.progression.rules import (
    get_habit_completion_reward,
    get_habit_miss_penalty,
    get_quest_completion_reward,
    get_quest_failure_penalty,
    level_from_total_xp,
)
from apps.quests.models import Quest


class ProgressionRuleError(Exception):
    """Raised when a requested progression action violates business rules."""


@dataclass(frozen=True)
class ProgressionOutcome:
    profile: CharacterProfile
    event: ProgressEvent
    habit: Habit | None = None
    quest: Quest | None = None

    def to_response_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "profile": self.profile,
            "event": self.event,
        }
        if self.habit is not None:
            payload["habit"] = self.habit
        if self.quest is not None:
            payload["quest"] = self.quest
        return payload


def refresh_profile_streak(
    *, profile: CharacterProfile, occurred_at: datetime | None = None
) -> CharacterProfile:
    occurred_at = _resolve_occurrence(occurred_at)
    local_date = _to_local_date(profile.timezone, occurred_at)

    if (
        profile.last_activity_on is not None
        and local_date > profile.last_activity_on + timedelta(days=1)
        and profile.current_streak != 0
    ):
        profile.current_streak = 0
        profile.save(update_fields=["current_streak", "updated_at"])

    return profile


def complete_habit(*, habit: Habit, occurred_at: datetime | None = None) -> ProgressionOutcome:
    occurred_at = _resolve_occurrence(occurred_at)

    with transaction.atomic():
        habit = (
            Habit.objects.select_for_update()
            .select_related("user__character_profile")
            .get(pk=habit.pk)
        )
        profile = CharacterProfile.objects.select_for_update().get(user=habit.user)
        refresh_profile_streak(profile=profile, occurred_at=occurred_at)
        local_date = _to_local_date(profile.timezone, occurred_at)

        if not habit.is_active:
            raise ProgressionRuleError("Inactive habits cannot be completed.")
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.HABIT_COMPLETED,
            local_date=local_date,
            habit=habit,
        ):
            raise ProgressionRuleError("This habit has already been completed today.")
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.HABIT_MISSED,
            local_date=local_date,
            habit=habit,
        ):
            raise ProgressionRuleError("This habit is already marked as missed for today.")

        _apply_progress_change(profile=profile, xp_delta=get_habit_completion_reward(habit))
        _advance_streak(profile=profile, local_date=local_date)
        profile.save()

        event = _create_event(
            profile=profile,
            event_type=ProgressEvent.EventType.HABIT_COMPLETED,
            xp_delta=get_habit_completion_reward(habit),
            occurred_at=occurred_at,
            local_date=local_date,
            habit=habit,
        )

        return ProgressionOutcome(profile=profile, event=event, habit=habit)


def miss_habit(*, habit: Habit, occurred_at: datetime | None = None) -> ProgressionOutcome:
    occurred_at = _resolve_occurrence(occurred_at)

    with transaction.atomic():
        habit = (
            Habit.objects.select_for_update()
            .select_related("user__character_profile")
            .get(pk=habit.pk)
        )
        profile = CharacterProfile.objects.select_for_update().get(user=habit.user)
        refresh_profile_streak(profile=profile, occurred_at=occurred_at)
        local_date = _to_local_date(profile.timezone, occurred_at)

        if not habit.is_active:
            raise ProgressionRuleError("Inactive habits cannot receive a miss penalty.")
        if not habit.penalty_enabled:
            raise ProgressionRuleError("Penalty tracking is disabled for this habit.")
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.HABIT_MISSED,
            local_date=local_date,
            habit=habit,
        ):
            raise ProgressionRuleError("This habit is already marked as missed today.")
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.HABIT_COMPLETED,
            local_date=local_date,
            habit=habit,
        ):
            raise ProgressionRuleError(
                "A completed habit cannot be marked as missed on the same day."
            )

        xp_delta = -get_habit_miss_penalty(habit)
        _apply_progress_change(profile=profile, xp_delta=xp_delta)
        profile.save()

        event = _create_event(
            profile=profile,
            event_type=ProgressEvent.EventType.HABIT_MISSED,
            xp_delta=xp_delta,
            occurred_at=occurred_at,
            local_date=local_date,
            habit=habit,
        )

        return ProgressionOutcome(profile=profile, event=event, habit=habit)


def complete_quest(*, quest: Quest, occurred_at: datetime | None = None) -> ProgressionOutcome:
    occurred_at = _resolve_occurrence(occurred_at)

    with transaction.atomic():
        quest = (
            Quest.objects.select_for_update()
            .select_related("user__character_profile", "habit")
            .get(pk=quest.pk)
        )
        profile = CharacterProfile.objects.select_for_update().get(user=quest.user)
        refresh_profile_streak(profile=profile, occurred_at=occurred_at)
        local_date = _to_local_date(profile.timezone, occurred_at)

        if _quest_already_completed_for_period(quest=quest, local_date=local_date):
            raise ProgressionRuleError(
                "This quest has already been completed for its allowed period."
            )
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.QUEST_FAILED,
            local_date=local_date,
            quest=quest,
        ):
            raise ProgressionRuleError("A failed quest cannot be completed on the same day.")

        xp_delta = get_quest_completion_reward(quest)
        _apply_progress_change(profile=profile, xp_delta=xp_delta)
        _advance_streak(profile=profile, local_date=local_date)
        profile.save()

        quest.status = Quest.Status.COMPLETED
        quest.completed_at = occurred_at
        quest.save()

        event = _create_event(
            profile=profile,
            event_type=ProgressEvent.EventType.QUEST_COMPLETED,
            xp_delta=xp_delta,
            occurred_at=occurred_at,
            local_date=local_date,
            quest=quest,
        )

        return ProgressionOutcome(profile=profile, event=event, quest=quest)


def fail_quest(*, quest: Quest, occurred_at: datetime | None = None) -> ProgressionOutcome:
    occurred_at = _resolve_occurrence(occurred_at)

    with transaction.atomic():
        quest = (
            Quest.objects.select_for_update()
            .select_related("user__character_profile", "habit")
            .get(pk=quest.pk)
        )
        profile = CharacterProfile.objects.select_for_update().get(user=quest.user)
        refresh_profile_streak(profile=profile, occurred_at=occurred_at)
        local_date = _to_local_date(profile.timezone, occurred_at)

        if quest.quest_type == Quest.QuestType.ONE_TIME and _quest_has_any_completion(quest=quest):
            raise ProgressionRuleError(
                "A one-time quest cannot fail after it has already been completed."
            )
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.QUEST_FAILED,
            local_date=local_date,
            quest=quest,
        ):
            raise ProgressionRuleError("This quest has already been marked as failed today.")
        if _has_event_for_day(
            event_type=ProgressEvent.EventType.QUEST_COMPLETED,
            local_date=local_date,
            quest=quest,
        ):
            raise ProgressionRuleError("A completed quest cannot be failed on the same day.")

        xp_delta = -get_quest_failure_penalty(quest)
        _apply_progress_change(profile=profile, xp_delta=xp_delta)
        profile.save()

        quest.status = Quest.Status.FAILED
        quest.completed_at = None
        quest.save()

        event = _create_event(
            profile=profile,
            event_type=ProgressEvent.EventType.QUEST_FAILED,
            xp_delta=xp_delta,
            occurred_at=occurred_at,
            local_date=local_date,
            quest=quest,
        )

        return ProgressionOutcome(profile=profile, event=event, quest=quest)


def _resolve_occurrence(occurred_at: datetime | None) -> datetime:
    value = occurred_at or timezone.now()
    if timezone.is_naive(value):
        return timezone.make_aware(value, timezone=UTC)
    return value


def _to_local_date(timezone_name: str, occurred_at: datetime) -> date:
    return occurred_at.astimezone(ZoneInfo(timezone_name)).date()


def _apply_progress_change(*, profile: CharacterProfile, xp_delta: int) -> None:
    profile.total_xp = max(profile.total_xp + xp_delta, 0)
    profile.level = level_from_total_xp(profile.total_xp)


def _advance_streak(*, profile: CharacterProfile, local_date: date) -> None:
    if profile.last_activity_on is None:
        profile.current_streak = 1
        profile.last_activity_on = local_date
    elif local_date == profile.last_activity_on:
        return
    elif local_date == profile.last_activity_on + timedelta(days=1):
        profile.current_streak += 1
        profile.last_activity_on = local_date
    elif local_date > profile.last_activity_on:
        profile.current_streak = 1
        profile.last_activity_on = local_date

    profile.longest_streak = max(profile.longest_streak, profile.current_streak)


def _create_event(
    *,
    profile: CharacterProfile,
    event_type: str,
    xp_delta: int,
    occurred_at: datetime,
    local_date: date,
    habit: Habit | None = None,
    quest: Quest | None = None,
) -> ProgressEvent:
    return ProgressEvent.objects.create(
        user=profile.user,
        profile=profile,
        habit=habit,
        quest=quest,
        event_type=event_type,
        xp_delta=xp_delta,
        total_xp_after=profile.total_xp,
        level_after=profile.level,
        streak_after=profile.current_streak,
        occurred_at=occurred_at,
        local_date=local_date,
        timezone=profile.timezone,
    )


def _has_event_for_day(
    *,
    event_type: str,
    local_date: date,
    habit: Habit | None = None,
    quest: Quest | None = None,
) -> bool:
    queryset = ProgressEvent.objects.filter(event_type=event_type, local_date=local_date)
    if habit is not None:
        queryset = queryset.filter(habit=habit)
    if quest is not None:
        queryset = queryset.filter(quest=quest)
    return queryset.exists()


def _quest_already_completed_for_period(*, quest: Quest, local_date: date) -> bool:
    queryset = _quest_completion_events(quest=quest)
    if quest.quest_type == Quest.QuestType.ONE_TIME:
        return queryset.exists()
    return queryset.filter(local_date=local_date).exists()


def _quest_has_any_completion(*, quest: Quest) -> bool:
    return _quest_completion_events(quest=quest).exists()


def _quest_completion_events(*, quest: Quest):
    return ProgressEvent.objects.filter(
        quest=quest,
        event_type=ProgressEvent.EventType.QUEST_COMPLETED,
    )
