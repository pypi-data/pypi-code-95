from rest_framework import (
    viewsets,
    permissions,
)

from .. import (
    models,
    serializers,
)


class FormViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Form.objects.all()
    serializer_class = serializers.FormSerializer


class AttendeeViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AttendeeSerializer
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return models.Attendee.objects.filter(
            owner=self.request.user,
        )
