import json
from io import StringIO

from samon.elements import BaseElement
from samon.render import RenderedElement


class KrApp(BaseElement):
    def to_xml(self, io: StringIO, indent: int, rendered_element: RenderedElement):

        with rendered_element.frame(io, indent):
            print('<script type="text/javascript">', file=io, end='')
            print(f'var ${self.xml_attrs["id"]}_data = `', file=io, end='')
            rendered_element.to_jsx(io)
            print('`;</script>', file=io)