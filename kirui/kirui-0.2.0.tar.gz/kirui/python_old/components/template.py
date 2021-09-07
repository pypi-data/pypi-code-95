from browser import ajax, webcomponent, window, document


class TemplateLike:
    def connectedCallback(self):
        parent_config = getattr(self.parent, '_component_config', None)
        if parent_config:
            encapsulate_slot = getattr(parent_config, 'encapsulate_slot', None)
            if encapsulate_slot is None:
                encapsulate_slot = self.parent.attrs.get('data-encapsulate-slot', False)

            if encapsulate_slot:
                self.attachShadow({'mode': 'open'})


# webcomponent.define('kr-template', TemplateLike)
