from .core import render, patch_dom_with_vdom, minify

from browser import document


class App:
    el: 'document.HTMLElement'
    components: []

    def __init__(self, components):
        self.components = components

    def mount(self, selector):
        el = document.querySelector(selector)
        #el.style['display'] = 'block'
        #return

        vdom = document.createElement('DIV')
        for attr in el.attributes:
            vdom.setAttribute(attr.name, attr.value)

        minify(el.content)
        patch_dom_with_vdom(vdom, el.content.getRootNode())
        # print(vdom.innerHTML)
        # el.replaceWith(vdom)
        #document.body.appendChild(vdom)
        el.replaceWith(vdom)
