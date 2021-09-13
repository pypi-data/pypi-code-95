from typing import TypedDict, Iterable, Union
from urllib.parse import urlencode

from django import template
from django.core.paginator import Paginator, Page
from django.http import HttpRequest

register = template.Library()


class TypedContext(TypedDict):
    page: Page
    paginator: Paginator
    query: str
    page_range: Iterable[Union[int, str]]


def get_current_page(d: dict) -> int:
    try:
        page_no = int(d.get("page", 1))  # noqa
    except ValueError:
        page_no = 1
    return page_no


def get_query_except_page(d: dict) -> str:
    try:
        d.pop("page")
    except KeyError:
        pass
    return urlencode(d)


@register.inclusion_tag("dj_qiyu_tpl/pagination_v2.html", takes_context=True)
def pagination_render(
    context: template.RequestContext, paginator: Paginator
) -> TypedContext:
    request: HttpRequest = context.request

    get = request.GET.dict()  # noqa

    page_no = get_current_page(get)
    query = get_query_except_page(get)

    page = paginator.page(page_no)

    return {
        "paginator": paginator,
        "page": page,
        "query": query,
        "page_range": paginator.get_elided_page_range(page_no),
    }
