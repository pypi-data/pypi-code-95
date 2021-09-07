from browser import document, window, webcomponent


class Component:
    slot_elements: dict

    def __init__(self, tag, template, encapsulate_slot=False):
        self.tag = tag

        parser = window.DOMParser.new()
        self.template = parser.parseFromString(template, 'text/html').body

        self.encapsulate_slot = encapsulate_slot

    def __call__(self, klass):
        setattr(klass, '_component_config', self)

        if webcomponent.get(self.tag) is None:
            webcomponent.define(self.tag, klass)

        return klass
