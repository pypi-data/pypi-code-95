from django.urls import reverse_lazy

from report_designer.core.actions import ActionGroup, SimpleModalAction


class FormatListActionGroup(ActionGroup):
    """
    Группа действий в списке форматов
    """

    create = SimpleModalAction(title='Добавить', url=reverse_lazy('report_designer:formats:create'))
