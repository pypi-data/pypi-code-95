from io import BytesIO
from typing import TYPE_CHECKING
from xml import sax

from .. import constants

if TYPE_CHECKING:
    from ..environment import Environment


class XmlParser(sax.ContentHandler):
    def __init__(self, environment: 'Environment'):
        self.environment = environment

        self.template = None
        self.act_parent = None

    def parse(self, source: bytes, template_name: str):
        self.template = self.environment.template_class()
        self.act_parent = None

        parser = sax.make_parser()
        #parser.setFeature(sax.handler.feature_external_pes, False)
        #parser.setFeature(sax.handler.feature_external_ges, False)
        parser.setFeature(sax.handler.feature_namespaces, True)
        #parser.setProperty(sax.handler.property_lexical_handler, self)
        parser.setContentHandler(self)

        isource = sax.xmlreader.InputSource()
        isource.setByteStream(BytesIO(source))
        isource.setSystemId(template_name)

        parser.parse(isource)

        return self.template

    def startElementNS(self, name, qname, attrs):
        ns, name = name

        if ns:
            fqdn = '{' + ns + '}' + name
        else:
            fqdn = name

        if (constants.XML_NAMESPACE_FLOW_CONTROL, 'include',) in attrs.keys():  # include another template
            template = self.environment.get_template(attrs[(constants.XML_NAMESPACE_FLOW_CONTROL, 'include')])
            assert template.root_element.xml_tag == name
            element = template.root_element
            self.act_parent.add_child(element)
            self.act_parent = element
        else:
            klass = self.environment.registry.get_class_by_name(fqdn)
            element = klass(xml_tag=name, xml_attrs=attrs)
            if self.act_parent is None:
                assert self.template.root_element is None
                self.template.root_element = self.act_parent = element
            else:
                self.act_parent.add_child(element)
                self.act_parent = element

    def endElementNS(self, *args, **kwargs):
        self.act_parent = self.act_parent.parent

    def characters(self, content):
        if len(content.strip()) == 0:
            return

        content = sax.saxutils.escape(content).strip()
        element = self.environment.registry.anonymus_element_klass(text=content)
        self.act_parent.add_child(element)
