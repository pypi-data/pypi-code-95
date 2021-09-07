import datetime

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe


class RenderMixin:
    """
    Миксин, добалвяющий возможность рендера шаблона
    """

    template_name = None
    context_object_name = None

    def __str__(self):
        return self.render()

    def render(self):
        """
        Рендер шаблона
        """
        return mark_safe(render_to_string(self.get_template_name(), self.get_context_data()))

    def get_template_name(self):
        """
        Шаблон
        """
        return self.template_name

    def get_context_data(self):
        """
        Контекст шаблона
        """
        return {
            self.context_object_name: self,
        }


def format_date(date, format='d.m.Y', default=''):
    """
    Возвращает отформатированную дату
    :param date: Дата
    :param format: смотри https://docs.djangoproject.com/en/2.2/ref/templates/builtins/#date
    :param default: вернётся, если нет date
    :return:
    """

    if date is not None:
        if isinstance(date, datetime.datetime) and timezone.is_aware(date):
            date = timezone.localtime(date)
        return date_format(date, format)
    return default
