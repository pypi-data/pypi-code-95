import django_filters

from ..models import OperationLog


class OperationLogFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username')
    desc = django_filters.CharFilter(field_name='desc')

    class Meta:
        model = OperationLog
        fields = ['desc', 'username']
