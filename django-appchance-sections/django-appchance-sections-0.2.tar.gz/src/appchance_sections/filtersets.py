import django_filters
from django_filters.rest_framework import FilterSet


class SectionListFilter(FilterSet):
    placement = django_filters.CharFilter(method="get_by_placements", field_name="placement")

    @staticmethod
    def get_by_placements(queryset, _field_name, value):
        return queryset.filter(placement__in=value.split(","))

    class Meta:
        fields = ["placement"]
