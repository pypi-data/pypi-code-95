import browser
from browser import document
from django_brython.testing import location, reverse

from kirui.vdom.render import render


class RenderTest:
    @location(reverse('backend:index'))
    def test_render_base(self):
        el = document.createElement('DIV')
        el.innerHTML = '<span>text</span>'

        el2 = render(el)
        assert isinstance(el2, browser.DOMNode)
        assert el2.outerHTML == '<div><span>text</span></div>'

    @location(reverse('backend:index'))
    def test_render_text_strip(self):
        el = document.createElement('DIV')
        el.innerHTML = """
        <span style="font-weight: bold">
            text
        </span>
        sdfsdfsdf
        """

        el2 = render(el)
        document.body.appendChild(el2)

        print(el.outerHTML)
        print(el2.outerHTML)
