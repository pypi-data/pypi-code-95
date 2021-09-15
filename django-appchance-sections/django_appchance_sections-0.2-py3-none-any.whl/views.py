import logging

import django_filters
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from appchance_sections.filtersets import SectionListFilter
from appchance_sections.serializers import SectionSerializer
from appchance_sections.utils import get_section_model

logger = logging.getLogger(__name__)

Section = get_section_model()


class SectionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List of all sections."""

    permission_classes = (AllowAny,)
    queryset = Section.objects.filter(is_active=True)
    serializer_class = SectionSerializer
    pagination_class = None
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_class = SectionListFilter
