from collections import namedtuple

from django import template
from django.core.paginator import Page
from django.template import RequestContext


register = template.Library()


# Страница пагинатора
PaginatorPage = namedtuple(typename='PaginatorPage', field_names=['display', 'page', 'is_hidden'])


def generate_paginator_pages(pages, start, stop, hidden_pages):
    """
    Генерация страниц пагинатора
    """
    for page in sorted(pages):
        if not (start <= page <= stop):
            continue
        yield PaginatorPage(str(page), page, page in hidden_pages)


@register.inclusion_tag(filename='report_designer/core/blocks/paginator.html', takes_context=True)
def paginator(context: RequestContext, page_obj: Page, **kwargs):
    """
    Пагинация
    """
    page_range: range = page_obj.paginator.page_range

    # Видимый диапазон страниц
    visible_length: int = kwargs.get('visible_length', 3) + 1

    # Скрытые номера страниц
    start_page, end_page = page_obj.number - visible_length, page_obj.number + visible_length
    hidden_pages = [start_page, end_page]

    # Отобращаемые номера страницы
    pages_numbers = {page_range.start, *range(start_page, end_page + 1), page_range.stop - 1}
    pages = generate_paginator_pages(pages_numbers, page_range.start, page_range.stop - 1, hidden_pages)
    context.update({'pages': pages, 'current_paginator_page': page_obj.number, **kwargs})
    return context


@register.inclusion_tag(filename='report_designer/core/blocks/paginator_page.html', takes_context=True)
def paginator_page(context: RequestContext, display: str, page: int, current_page: int, **kwargs):
    """
    Страница пагинации
    """
    base_classes = context.get('pagination_page_list_classes', '')
    if page == current_page:
        base_classes += ' active'
    return {
        'display': display,
        'page': page,
        'pagination_page_list_base_classes': base_classes.strip(),
        'pagination_page_classes': context.get('pagination_page_classes'),
        **kwargs,
    }
