import sys
from io import StringIO

from .elements import BaseElement


class Template:
    def __init__(self):
        self.root_element = None  # type: BaseElement
        self.source_path = None  # type: Path

    def _show_element_subtree(self, element: BaseElement, stdout, indent: int=1):
        spaces = ' ' * (indent - 1) * 4
        print(f'{spaces} {element.__class__.__name__} <{element.xml_tag}>', file=stdout)
        for child in element.children:
            self._show_element_subtree(child, stdout=stdout, indent=indent + 1)

    def show_element_tree(self, stdout=sys.stdout):
        return self._show_element_subtree(element=self.root_element, stdout=stdout)

    def _as_xml_subtree(self, element: BaseElement, io, newline: str, indent: int=1):
        spaces = ' ' * (indent - 1) * 4

        if not element.xml_tag:  # anonymus elements
            print(f'{spaces}{element.text}', file=io, end=newline)
        else:
            closing = '>' if len(element.children) else '/>'
            print(f'{spaces}<{element.xml_tag}{element.attrs_as_xml}{closing}', file=io, end=newline)
            for i, child in enumerate(element.children):
                self._as_xml_subtree(child, io, newline=newline, indent=indent + 1)

            if len(element.children):
                print(f'{spaces}</{element.xml_tag}>', file=io, end=newline)

    def serialize(self, output='xml'):
        if output == 'xml':
            io = StringIO()
            self.root_element.xml_attrs = {
                'xmlns:c': "https://doculabs.io/2020/xtmpl#control",
                'xmlns:b': "https://doculabs.io/2020/xtmpl#data-binding"
            }
            self._as_xml_subtree(element=self.root_element, io=io, newline='\n', indent=1)
            return io.getvalue()
        else:
            raise NotImplementedError(f'Invalid output type: {output}')
