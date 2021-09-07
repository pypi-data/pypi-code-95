from report_designer.core.views import DynamicContentTableBaseView, CreateAjaxView
from report_designer.models import DBTable
from report_designer.tables.actions import TablesListActionGroup
from report_designer.tables.filters import DBTableFilterSet
from report_designer.tables.forms import DBTableCreateForm
from report_designer.tables.tables import DBTableTable


class DBTableListView(DynamicContentTableBaseView):
    """
    Представление: Список добавленных таблиц БД
    """

    model = DBTable
    filterset_class = DBTableFilterSet
    table_class = DBTableTable
    title = 'Таблицы БД'
    ajax_content_name = 'db_tables'
    action_group_classes = (
        TablesListActionGroup,
    )


class DBTableCreateView(CreateAjaxView):
    """
    Представление: Создание таблицы БД
    """

    title = 'Создание таблицы БД'
    model = DBTable
    form_class = DBTableCreateForm
    dependent_key = 'dynamic_contents'
    dependent_name = 'db_tables'

    def after_save(self):
        super().after_save()
        self.object.reload_fields()
