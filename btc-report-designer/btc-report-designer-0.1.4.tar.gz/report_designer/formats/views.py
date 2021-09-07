from report_designer.core.views import DynamicContentTableBaseView, CreateAjaxView
from report_designer.formats.actions import FormatListActionGroup
from report_designer.formats.filters import FormatFilterSet
from report_designer.formats.forms import FormatCreateForm
from report_designer.formats.tables import FormatTable
from report_designer.models import Format


class FormatListView(DynamicContentTableBaseView):
    """
    Представление: Список форматов
    """

    model = Format
    filterset_class = FormatFilterSet
    table_class = FormatTable
    title = 'Форматы'
    ajax_content_name = 'formats'
    action_group_classes = (
        FormatListActionGroup,
    )


class FormatCreateView(CreateAjaxView):
    """
    Представление: Создание таблицы БД
    """

    title = 'Создание формата'
    model = Format
    form_class = FormatCreateForm
    dependent_key = 'dynamic_contents'
    dependent_name = 'formats'
