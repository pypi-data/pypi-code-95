# copyright 2015-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-eac common test tools"""

from os.path import basename

from doctest import Example

from lxml import etree
from lxml.doctestcompare import LXMLOutputChecker

from cubicweb.dataimport.importer import SimpleImportLog


def authority_record(cnx, record_id, name, kind=u"person", **kwargs):
    """Return an AuthorityRecord with specified kind and name."""
    kind_eid = cnx.find("AgentKind", name=kind)[0][0]
    if "reverse_name_entry_for" not in kwargs:
        kwargs["reverse_name_entry_for"] = cnx.create_entity(
            "NameEntry", parts=name, form_variant=u"authorized"
        )
    return cnx.create_entity(
        "AuthorityRecord", record_id=record_id, agent_kind=kind_eid, **kwargs
    )


def eac_import(cnx, fpath):
    import_log = SimpleImportLog(basename(fpath))
    created, updated, _ = cnx.call_service(
        "eac.import", stream=fpath, import_log=import_log, raise_on_error=True
    )
    return created, updated


class XmlTestMixin(object):
    """Mixin class provinding additional assertion methods for checking XML data."""

    def assertXmlEqual(self, actual, expected):
        """Check that both XML strings represent the same XML tree."""
        checker = LXMLOutputChecker()
        if not checker.check_output(expected, actual, 0):
            message = checker.output_difference(Example("", expected), actual, 0)
            self.fail(message)

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningful line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        xml_data = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(xml_data):
            print(etree.tostring(xml_data, pretty_print=True))
        xmlschema.assertValid(xml_data)
