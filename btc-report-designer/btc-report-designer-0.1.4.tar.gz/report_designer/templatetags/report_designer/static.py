from django import template


register = template.Library()


@register.inclusion_tag('report_designer/scripts.html')
def report_designer_scripts(is_all=False):
    """
    Скрипты конструктора отчетов
    :param is_all: Загрузка всех требуюущихся скриптов
    """
    return {'is_all': is_all}
