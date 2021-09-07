from report_designer.core.filters import (SearchBaseFilterSet, StyledFilterSet,)
from report_designer.models import DBTable


class DBTableFilterSet(StyledFilterSet, SearchBaseFilterSet):
    """
    Фильтр: Таблицы БД
    """

    searching_fields = ('alias',)

    class Meta:
        model = DBTable
        fields = (
            'table',
            'is_visible',
        )
