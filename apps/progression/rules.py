from apps.habits.models import Habit
from apps.quests.models import Quest

BASE_XP_PER_LEVEL = 100


def xp_required_for_level(level: int) -> int:
    if level < 1:
        raise ValueError("Level must be at least 1.")
    return BASE_XP_PER_LEVEL * (level - 1) * level // 2


def level_from_total_xp(total_xp: int) -> int:
    if total_xp < 0:
        raise ValueError("Total XP cannot be negative.")

    level = 1
    while total_xp >= xp_required_for_level(level + 1):
        level += 1
    return level


def get_habit_completion_reward(habit: Habit) -> int:
    return max(habit.xp_reward, 1)


def get_habit_miss_penalty(habit: Habit) -> int:
    if not habit.penalty_enabled:
        return 0
    return max(get_habit_completion_reward(habit) // 2, 1)


def get_quest_completion_reward(quest: Quest) -> int:
    return max(quest.xp_reward, 1)


def get_quest_failure_penalty(quest: Quest) -> int:
    return max(get_quest_completion_reward(quest) // 3, 5)
