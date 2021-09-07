from django import template


register = template.Library()


@register.inclusion_tag('report_designer/core/blocks/preloader.html')
def preloader(is_disable=False):
    """
    Прелоадер
    :param is_disable: абсолютное позиционирование. Родительский элемент должен иметь {style: relative}
    """
    return {'is_disable': is_disable}
