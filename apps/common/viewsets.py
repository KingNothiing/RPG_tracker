from rest_framework import viewsets


class OwnedModelViewSet(viewsets.ModelViewSet):
    """Base viewset for models owned by the authenticated user."""

    owner_field = "user"

    def get_queryset(self):
        base_queryset = super().get_queryset()
        return base_queryset.filter(**{self.owner_field: self.request.user})

    def perform_create(self, serializer):
        serializer.save(**{self.owner_field: self.request.user})
