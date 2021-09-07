from django.urls import reverse, reverse_lazy

from report_designer.core.actions import ActionGroup, SimpleModalAction


class TablesListActionGroup(ActionGroup):
    """
    Группа действий в списке таблиц
    """

    create = SimpleModalAction(title='Добавить', url=reverse_lazy('report_designer:tables:create'))
