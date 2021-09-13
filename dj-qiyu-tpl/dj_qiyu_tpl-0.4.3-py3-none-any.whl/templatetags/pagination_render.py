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


@register.inclusion_tag("dj_qiyu_tpl/pagination_v2.html", takes_context=True)
def pagination_render(
    context: template.RequestContext, paginator: Paginator
) -> TypedContext:
    request: HttpRequest = context.request
    try:
        page_no = request.GET.get("page", 1)  # noqa
    except ValueError:
        page_no = 1
    query = urlencode(request.GET.dict())  # noqa
    page = paginator.page(page_no)
    return {
        "paginator": paginator,
        "page": page,
        "query": query,
        "page_range": paginator.get_elided_page_range(),
    }
