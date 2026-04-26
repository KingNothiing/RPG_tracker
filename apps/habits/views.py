from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.common.viewsets import OwnedModelViewSet
from apps.habits.models import Habit
from apps.habits.serializers import HabitSerializer
from apps.progression.serializers import ProgressionActionResponseSerializer
from apps.progression.services import (
    ProgressionRuleError,
    complete_habit,
    miss_habit,
)


class HabitViewSet(OwnedModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    @extend_schema(
        request=None,
        responses=ProgressionActionResponseSerializer,
        description="Complete a habit, award XP, update streak, and create a progress event.",
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, *args, **kwargs):
        habit = self.get_object()
        try:
            outcome = complete_habit(habit=habit)
        except ProgressionRuleError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        serializer = ProgressionActionResponseSerializer(instance=outcome.to_response_payload())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses=ProgressionActionResponseSerializer,
        description="Apply a miss penalty to a habit and create a progress event.",
    )
    @action(detail=True, methods=["post"])
    def miss(self, request, *args, **kwargs):
        habit = self.get_object()
        try:
            outcome = miss_habit(habit=habit)
        except ProgressionRuleError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        serializer = ProgressionActionResponseSerializer(instance=outcome.to_response_payload())
        return Response(serializer.data, status=status.HTTP_200_OK)
