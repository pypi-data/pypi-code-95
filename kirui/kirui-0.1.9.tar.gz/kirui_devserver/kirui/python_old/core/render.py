from browser import document, window


class VDOMRenderer:
    def render(self, velement: window.HTMLElement):
        tag_name = 'DIV' if velement.tagName == 'TEMPLATE' else velement.tagName
        element = document.createElement(tag_name)
        for vchild in velement.childNodes:
            if vchild.nodeType == 3:
                child = document.createTextNode(vchild.textContent)
            else:
                child = self.render(vchild)

            element.appendChild(child)

        return element

    def __call__(self, velement: window.HTMLElement):
        return self.render(velement)


render = VDOMRenderer()
