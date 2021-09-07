from itertools import zip_longest

from browser import document, window
from .components import Component


class Element:
    _component_config: Component

    def connectedCallback(self):
        self.shadow = self.attachShadow({'mode': 'open'})

        try:
            self.shadow.adoptedStyleSheets = document.adoptedStyleSheets
            adopted = True
        except AttributeError:
            adopted = False

        self.render()

    def render(self):
        self.shadow.innerHTML = self._component_config.template.innerHTML
