from itertools import zip_longest


def patch_dom_with_vdom(dom_element, virtual_element, level=0, debug=False):
    level += 1

    if dom_element.nodeType == 3:  # text node
        if virtual_element.nodeType == 3:
            if dom_element.textContent != virtual_element.textContent:
                dom_element.textContent = virtual_element.textContent
        else:
            dom_element.replaceWith(virtual_element)
    else:
        if level < 2:  # root element is ignored
            if debug:
                print('ignored', dom_element.nodeName, virtual_element.nodeName)
        else:
            if debug:
                print(dom_element.nodeName, virtual_element.nodeName)

            if dom_element.nodeName != virtual_element.nodeName:
                dom_element.replaceWith(virtual_element)
                return

            for attr in dom_element.attributes:
                if not virtual_element.hasAttribute(attr.name):
                    dom_element.removeAttribute(attr.name)

            for attr in virtual_element.attributes:
                dom_element.setAttribute(attr.name, attr.value)

            if hasattr(virtual_element, 'value'):  # input actual value
                dom_element.value = virtual_element.value

        for old_child, new_child in zip_longest(dom_element.childNodes, virtual_element.childNodes):
            if new_child is None:
                old_child.remove()
            elif old_child is None:
                dom_element.appendChild(new_child)
            else:
                patch_dom_with_vdom(old_child, new_child, level=level)
