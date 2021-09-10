from rest_framework import (
    viewsets,
    permissions,
    response,
)

from rest_framework.decorators import action

from .. import (
    serializers,
    models,
)


class EventViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.get_visible_events()

    @action(detail=False, methods=["get"], url_path="open")
    def open_events(self, request):
        objects = models.Event.objects.get_open_events()
        serializer = self.get_serializer_class()
        return response.Response(serializer(objects, many=True).data)
