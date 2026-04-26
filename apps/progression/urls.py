from django.urls import path

from apps.progression.views import ProgressEventListView

urlpatterns = [
    path("progress/events/", ProgressEventListView.as_view(), name="progress-event-list"),
]
