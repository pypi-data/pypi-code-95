"""import importlib
import inspect
import sys

from browser import document, window
from kirui.app import App
from kirui.components.layout import SidebarLayout


# Reloading components HMR hook #
def rerender(event):
    module = sys.modules[event.detail['module_name']]

    importlib.reload(module)
    klasses = [m[1] for m in inspect.getmembers(module, inspect.isclass) if m[1].__module__ == event.detail['module_name']]
    for klass in klasses:
        if hasattr(klass, '_component_config'):
            for el in document.getElementsByTagName(klass._component_config.tag):
                el._component_config = klass._component_config
                el.render()


document.bind('reload_brython_module@after', rerender)


def entrypoint():
    app = App(components=[SidebarLayout])
    app.mount('#app')


if __name__ == '__main__':
    entrypoint()
"""

from browser import ajax, webcomponent, window, document


class Example:
    def connectedCallback(self):
        self.attachShadow({'mode': 'open'})
        self.shadowRoot.innerHTML = 'brython webcomponent'


webcomponent.define('kr-example', Example)

from kirui.app import App
from kirui.components.layout import SidebarLayout

def entrypoint():
    """el = document.createElement('DIV')
    el.innerHTML = '<kr-example attr="value">sldf</kr-example>'
    document.getElementById('app').replaceWith(el)"""

    app = App(components=[Example, SidebarLayout])
    app.mount('#app')
