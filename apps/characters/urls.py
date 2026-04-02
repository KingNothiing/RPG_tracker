from django.urls import path

from apps.characters.views import CharacterProfileView

urlpatterns = [
    path("profile/", CharacterProfileView.as_view(), name="profile-detail"),
]
