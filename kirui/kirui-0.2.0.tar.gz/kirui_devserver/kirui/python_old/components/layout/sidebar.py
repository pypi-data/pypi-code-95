from django_brython.assets import require
from kirui.core import Component, Element, render

from browser import window, ajax, document, webcomponent


TEMPLATE = """
asdf sadfd
asdasdasd dddd eee fff ggg
"""
@Component(
    tag='kr-layout-sidebar',
    template=require('sidebar.html'),
    encapsulate_slot=False
)
class SidebarLayout(Element):
    _sidebar_is_open: bool = False
    _sidebar_is_moving: bool = False
    is_pwa: bool
    sidebar: "document.Element"
    main: "document.Element"

    def connectedCallback(self):
        print('connected23456789asdlkaasdassssdsdssdsdddssddssdsd')
        super().connectedCallback()
