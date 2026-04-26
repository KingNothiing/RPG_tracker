from rest_framework import generics

from apps.progression.models import ProgressEvent
from apps.progression.serializers import ProgressEventSerializer


class ProgressEventListView(generics.ListAPIView):
    serializer_class = ProgressEventSerializer

    def get_queryset(self):
        queryset = ProgressEvent.objects.filter(user=self.request.user).select_related(
            "habit",
            "quest",
            "profile",
        )

        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset
