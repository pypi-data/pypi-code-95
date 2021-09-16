import logging

from django import template

from cms.menus.models import NavigationBarItem

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag()
def is_mega_menu(item):
    if not item: return False
    childs = item.get_childs()
    if not childs: return False
    with_childs = 0
    enum_childs = enumerate(childs)
    for index,child in enum_childs:
        if index>0 and child.has_childs(): return True
        if child.has_childs(): with_childs += 1
        if index>0 and with_childs: return True
    return False
