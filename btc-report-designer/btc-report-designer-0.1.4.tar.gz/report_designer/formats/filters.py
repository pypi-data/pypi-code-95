from report_designer.core.filters import (StyledFilterSet, SearchBaseFilterSet,)
from report_designer.models import Format


class FormatFilterSet(StyledFilterSet, SearchBaseFilterSet):
    """
    Фильтр: Форматы
    """

    searching_fields = ('name',)

    class Meta:
        model = Format
        fields = (
            'internal_type',
        )
