from browser import document
from django_brython.testing import location, reverse

from kirui.vdom.components import Component
from kirui.vdom.elements import Element


class ElementTest:
    @location(reverse('backend:index'))
    def test_shadow_inserted(self):
        @Component(
            tag='custom-element',
            template="""<div>
                     content
                     </div>"""
        )
        class CustomElement(Element):
            pass

        obj = CustomElement()
        el = document.createElement('custom-element')
        document.body.appendChild(el)
        assert document.getElementsByTagName('custom-element')[0].shadowRoot.innerHTML == '<div>content</div>', document.getElementsByTagName('custom-element')[0].shadowRoot.innerHTML
