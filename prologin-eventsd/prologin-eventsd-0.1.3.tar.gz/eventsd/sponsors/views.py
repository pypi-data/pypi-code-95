from rest_framework import viewsets
from . import models, serializers


class SponsorViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SponsorSerializer

    def get_queryset(self):
        return models.Sponsor.objects.filter(enabled=True)
