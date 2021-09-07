from kirui.vdom.components import Component
from kirui.vdom.elements import Element

@Component(
    tag='kl-proba',
    template='12345678910sdsd',
    encapsulate_slot=True
)
class Proba(Element):
    def render(self):
        super().render()
