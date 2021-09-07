from django.forms import ModelForm

from report_designer.core.forms import StyledFormMixin
from report_designer.models import DBTable


class DBTableCreateForm(StyledFormMixin, ModelForm):
    """
    Форма: создание таблиц БД
    """

    class Meta:
        model = DBTable
        fields = (
            'table',
            'alias',
            'is_visible',
        )
