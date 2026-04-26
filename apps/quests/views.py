from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.common.viewsets import OwnedModelViewSet
from apps.progression.serializers import ProgressionActionResponseSerializer
from apps.progression.services import (
    ProgressionRuleError,
    complete_quest,
    fail_quest,
)
from apps.quests.models import Quest
from apps.quests.serializers import QuestSerializer


class QuestViewSet(OwnedModelViewSet):
    queryset = Quest.objects.select_related("habit")
    serializer_class = QuestSerializer

    @extend_schema(
        request=None,
        responses=ProgressionActionResponseSerializer,
        description="Complete a quest, award XP, update streak, and create a progress event.",
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, *args, **kwargs):
        quest = self.get_object()
        try:
            outcome = complete_quest(quest=quest)
        except ProgressionRuleError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        serializer = ProgressionActionResponseSerializer(instance=outcome.to_response_payload())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses=ProgressionActionResponseSerializer,
        description="Mark a quest as failed, apply an XP penalty, and create a progress event.",
    )
    @action(detail=True, methods=["post"], url_path="fail")
    def fail_action(self, request, *args, **kwargs):
        quest = self.get_object()
        try:
            outcome = fail_quest(quest=quest)
        except ProgressionRuleError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        serializer = ProgressionActionResponseSerializer(instance=outcome.to_response_payload())
        return Response(serializer.data, status=status.HTTP_200_OK)
