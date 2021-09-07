from django.forms import ModelForm

from report_designer.core.forms import StyledFormMixin
from report_designer.models import Format


class FormatCreateForm(StyledFormMixin, ModelForm):
    """
    Форма: создание форматов
    """

    class Meta:
        model = Format
        fields = (
            'name',
            'internal_type',
            'representation',
        )
