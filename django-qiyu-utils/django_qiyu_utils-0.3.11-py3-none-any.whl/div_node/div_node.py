from typing import Callable

from django.template.context import Context
from django.template.defaulttags import Node, NodeList

__all__ = ["DivNode"]


class DivNode(Node):
    """
    Django custom node like html div
    with function `fn` indicate if should render the inner `nodes`
    """

    def __init__(self, name: str, node_list: NodeList, fn: Callable[[Context], bool]):
        """
        :param name:  the name of the node [for debug and django inner use]
        :param node_list: the inner node list
                          [if `fn` return true then render the inner node otherwise render nothing]
        :param fn: the function to indicate if need render the inner code
                   accept the `Context` as argument, return bool
        """
        self._name = name
        self._node_list = node_list
        self._fn = fn

    def __str__(self):
        return f"<{self._name}>"

    def render(self, context: Context):
        if self._fn(context):
            return self._node_list.render(context)
        return ""
