import json
from contextlib import contextmanager
from io import StringIO
from typing import Union, TYPE_CHECKING

from simpleeval import NameNotDefined

from . import constants

if TYPE_CHECKING:
    from .elements import BaseElement, AnonymusElement


class RenderedElement:
    node_attributes: dict

    def __init__(self, element: 'BaseElement', context: dict) -> None:
        self._element = element
        self._context = context
        self.node_attributes = self._eval_node_attributes(context)

    @property
    def node_name(self) -> str:
        return self._element.xml_tag

    def _eval_node_attributes(self, context) -> dict:
        retval = {}
        for k, v in self._element.xml_attrs.items():
            if k.startswith(f'{{{constants.XML_NAMESPACE_FLOW_CONTROL}}}'):
                continue
            elif k.startswith(f'{{{constants.XML_NAMESPACE_DATA_BINDING}}}'):
                k = k.replace(f'{{{constants.XML_NAMESPACE_DATA_BINDING}}}', '')

                retval[k] = v.eval(context)
            else:
                retval[k] = v

        return retval

    @property
    def children(self):
        if text := self._element.xml_attrs.get(f'{constants.XML_TEXT_BINDING_TAG}', None):
            yield text.eval(context=self._context)

        for child in self._element.children:
            klass = getattr(child.__class__, 'RENDERED_ELEMENT_CLASS', RenderedElement)

            if child.xml_tag is None:  # type: AnonymusElement
                yield child.text
            elif for_loop_def := child.xml_attrs.get(f'{{{constants.XML_NAMESPACE_FLOW_CONTROL}}}for', None):  # type: ForLoop
                for counter, loop_var_name, loop_var_val in for_loop_def.eval(self._context):
                    self._context['loop'] = {'index': counter, 'index0': counter - 1, 'odd': bool(counter % 2 == 1)}
                    self._context[loop_var_name] = loop_var_val

                    if_def = child.xml_attrs.get(f'{{{constants.XML_NAMESPACE_FLOW_CONTROL}}}if', None)
                    if if_def is None or if_def.eval(self._context):
                        yield klass(element=child, context=self._context)
            else:
                if_def = child.xml_attrs.get(f'{{{constants.XML_NAMESPACE_FLOW_CONTROL}}}if', None)
                if if_def is None or if_def.eval(self._context):
                    yield klass(element=child, context=self._context)

    def to_json(self):
        retval = [self.node_name, self.node_attributes, []]
        for child in self.children:
            if isinstance(child, str):
                retval[2].append(child)
            elif hasattr(child, 'to_json'):
                retval[2].append(child.to_json())
            else:
                retval[2].append(str(child))

        return retval

    @contextmanager
    def frame(self, io, indent):
        indent = constants.INDENT * indent

        xml_attrs = ''
        for k, v in self.node_attributes.items():
            xml_attrs += f' {k}="{v}"'

        prefix = '<!DOCTYPE HTML>' if self.node_name == 'html' else ''
        io.write(f'{indent}{prefix}<{self.node_name}{xml_attrs}>\n')
        yield
        io.write(f'{indent}</{self.node_name}>\n')

    def to_xml(self, io=None, indent=0):
        io = io or StringIO()
        with self.frame(io, indent):
            for child in self.children:
                if isinstance(child, str):
                    io.write(f'{constants.INDENT * (indent + 1)}{child}\n')
                else:
                    if hasattr(child._element, 'to_xml'):
                        child._element.to_xml(io, indent + 1, child)
                    else:
                        child.to_xml(io, indent + 1)

        return io.getvalue()

    def to_jsx(self, io=None):
        io = io or StringIO()
        io.write(f"k('{self.node_name}', {{")
        for k, v in self.node_attributes.items():
            if k == 'class':
                key = 'className'
            else:
                key = k

            if hasattr(v, '__iter__') and not isinstance(v, str):
                v = '[' + ','.join(f"'{_}'" for _ in v) + ']'
            elif v is None:
                v = "null"
            elif isinstance(v, bool):
                v = 'true' if v else 'false'
            else:
                v = json.dumps(v, ensure_ascii=False).replace('\\"', "'")
            io.write(f"'{key}': {v},")
        io.write('}, [')

        for child in self.children:
            if hasattr(child, 'to_jsx'):
                child.to_jsx(io)
            else:
                io.write(json.dumps(str(child), ensure_ascii=False).replace('\\"', "'"))

            io.write(',')

        io.write('])')
        return io.getvalue()

    def serialize(self, output='json'):
        if output == 'json':
            return self.to_json()
        elif output == 'xml':
            return self.to_xml()
        elif output == 'jsx':
            return self.to_jsx()
        else:
            raise NotImplementedError(f'Invalid output format: {output}')
