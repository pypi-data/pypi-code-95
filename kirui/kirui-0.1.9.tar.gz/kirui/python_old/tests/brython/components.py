from browser import document
from django_brython.testing import location, reverse

from kirui.vdom.components import Component
from kirui.vdom.elements import Element


class ComponentTest:
    @location(reverse('backend:index'))
    def test_component_registered(self):
        el = document.createElement('custom-element')
        assert str(el) == '<HTMLElement>'
        assert getattr(el, 'custom_attribute', None) is None

        @Component(
            tag='custom-element',
            template=''
        )
        class CustomElement(Element):
            custom_attribute = 'test'

        el = document.createElement('custom-element')
        assert isinstance(el, CustomElement)
        assert getattr(el, 'custom_attribute', None) == 'test'

        document.body.appendChild(el)
        print('test finished')

    @location(reverse('backend:index'))
    def test_component_configuration(self):
        @Component(
            tag='custom-element',
            template='<div>Some content</div>'
        )
        class CustomElement:
            pass

        assert CustomElement._component_config.tag == 'custom-element'
        assert CustomElement._component_config.template.tagName == 'BODY'
        assert len(CustomElement._component_config.template.children) == 1
        assert CustomElement._component_config.template.children[0].tagName == 'DIV'
        assert CustomElement._component_config.template.children[0].textContent == 'Some content'
        print('test finished')
