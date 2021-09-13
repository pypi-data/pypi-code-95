from typing import Callable

from django.template.base import Parser
from django.template.context import Context

from .div_node import DivNode

__all__ = ["custom_div_node_helper"]


def custom_div_node_helper(name: str, parser: Parser, fn: Callable[[Context], bool]):
    """
    :param name: 节点的名称
    解析形式如下:

    .. code-blocks: django

        {% $name %}
        # this is django html template content
        {% end_$name %}

    :param parser: django parser [pass as is]
    :param fn: 一个判断是否需要渲染子节点的函数
              这个函数的参数为: 模版的 Context
              True  -> 渲染子节点
              False -> 不需要渲染子节点

    example:

    .. code-blocks: python

        from django import template
        register = template.Library()

        @register.tag
        def custom_node_name(parser, token):
            def fn(ctx: Context) -> bool:
                return True
            return custom_div_node_helper("custom_node_name", parser, fn)

    """
    nodelist = parser.parse((f"end_{name}",))
    parser.delete_first_token()
    return DivNode(name, nodelist, fn)
