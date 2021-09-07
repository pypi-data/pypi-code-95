import itertools

from django.db.models import Q
from django.forms import TextInput, NullBooleanSelect
from django_filters import FilterSet, CharFilter, TypedChoiceFilter

from report_designer.core.forms import StyledFormMixin


class SearchFieldWidget(TextInput):
    """
    Виджет для поля поиска в фильтрах
    """

    template_name = 'report_designer/core/fields/search.html'


class SearchBaseFilterSet(FilterSet):
    """
    Базовый фильтр поиска
    """

    search_placeholder = 'Начните вводить название для поиска'
    searching_fields = ()
    search_lookup = 'icontains'
    search = CharFilter(method='search_filter', widget=SearchFieldWidget, label='Поиск')

    def search_filter(self, queryset, _, value):
        """
        Метод фильтрации по введенной строке
        """
        if not self.searching_fields or not value:
            return queryset
        pairs = itertools.product(self.searching_fields, value.split())
        query = Q(*[Q(**{f'{field}__{self.search_lookup}': val}) for field, val in pairs], _connector=Q.OR)
        return queryset.filter(query)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['search'].widget.attrs.update({'placeholder': self.search_placeholder, 'style': 'width:100%'})


class StyledFilterSet(StyledFormMixin, FilterSet):
    """
    Дополнительные методы и стилизация фильтра
    """

    js_class_prefix = 'js-rd-filter'
    empty_choice_filter = 'Все'

    def get_form_fields(self):
        return self.form.fields.copy()

