# coding: utf-8
# copyright 2016-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-eac entity's classes"""

import json

from functools import wraps

from lxml import etree

from logilab.common.date import ustrftime

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entity import EntityAdapter

from cubicweb_eac import TYPE_MAPPING, ADDRESS_MAPPING, MAINTENANCETYPE_MAPPING


class DateRelationMixin(object):
    @property
    def start_date(self):
        if self.date_relation:
            return self.date_relation[0].start_date

    @property
    def end_date(self):
        if self.date_relation:
            return self.date_relation[0].end_date


class AuthorityRecord(AnyEntity):
    __regid__ = "AuthorityRecord"
    fetch_attrs, cw_fetch_order = fetch_config(("agent_kind",))

    def dc_title(self):
        """A NameEntry of "authorized" form variant, if any; otherwise any
        NameEntry.
        """
        rset = self._cw.find(
            "NameEntry", name_entry_for=self, form_variant=u"authorized"
        )
        if not rset:
            rset = self._cw.find("NameEntry", name_entry_for=self)
        return next(rset.entities()).parts

    @property
    def kind(self):
        """The kind of agent"""
        return self.agent_kind[0].name

    @property
    def printable_kind(self):
        """The kind of agent, for display"""
        return self.agent_kind[0].printable_value("name")

    @property
    def other_record_ids(self):
        return sorted(
            [(r.local_type, r.value) for r in self.reverse_eac_other_record_id_of],
            key=lambda x: (x[0] or "", x[1] or ""),
        )


class AgentKind(AnyEntity):
    __regid__ = "AgentKind"
    fetch_attrs, cw_fetch_order = fetch_config(("name",))


class _Relation(DateRelationMixin, AnyEntity):
    __abstract__ = True

    def dc_description(self):
        if self.description:
            return self.description


class ChronologicalRelation(_Relation):
    __regid__ = "ChronologicalRelation"

    @property
    def subject(self):
        return self.chronological_predecessor[0]

    @property
    def object(self):
        return self.chronological_successor[0]


class AssociationRelation(_Relation):
    __regid__ = "AssociationRelation"

    @property
    def subject(self):
        return self.association_from[0]

    @property
    def object(self):
        return self.association_to[0]


class HierarchicalRelation(_Relation):
    __regid__ = "HierarchicalRelation"

    @property
    def subject(self):
        return self.hierarchical_parent[0]

    @property
    def object(self):
        return self.hierarchical_child[0]


class FamilyRelation(_Relation):
    __regid__ = "HierarchicalRelation"

    @property
    def subject(self):
        return self.family_from[0]

    @property
    def object(self):
        return self.family_to[0]


class IdentityRelation(_Relation):
    __regid__ = "HierarchicalRelation"

    @property
    def subject(self):
        return self.identity_from[0]

    @property
    def object(self):
        return self.identity_to[0]


class GeneralContext(AnyEntity):
    __regid__ = "GeneralContext"
    fetch_attrs, cw_fetch_order = fetch_config(("content",))


class JsonAttrsMixin(object):
    @property
    def json_attrs(self):
        return json.loads(self.xml_attributes)


class EACResourceRelation(DateRelationMixin, AnyEntity, JsonAttrsMixin):
    __regid__ = "EACResourceRelation"
    fetch_attrs, cw_fetch_order = fetch_config(
        ("agent_role", "xml_attributes", "resource_role", "description")
    )

    @property
    def record(self):
        return self.resource_relation_agent[0]

    @property
    def resource(self):
        return self.resource_relation_resource[0]

    def dc_title(self):
        agent_title = self.record.dc_title()
        if self.agent_role:
            agent_title += u" (%s)" % self.printable_value("agent_role")
        resource_title = self.resource.dc_title()
        if self.resource_role:
            resource_title += u" (%s)" % self.printable_value("resource_role")
        return self._cw._("Relation from %(from)s to %(to)s ") % {
            "from": agent_title,
            "to": resource_title,
        }


class EACFunctionRelation(DateRelationMixin, AnyEntity, JsonAttrsMixin):
    __regid__ = "EACFunctionRelation"
    fetch_attrs, cw_fetch_order = fetch_config(
        (
            "r_type",
            "description",
            "relation_entry",
            "place_entry",
            "xml_attributes",
        )
    )

    @property
    def record(self):
        return self.function_relation_agent[0]

    @property
    def resource(self):
        if self.function_relation_function:
            return self.function_relation_function[0]


class DateEntity(AnyEntity):
    __regid__ = "DateEntity"
    fetch_attrs, cw_fetch_order = fetch_config(("start_date", "end_date"))


class SameAsMixIn(object):
    """Mix-in class for entity types supporting vocabulary_source and
    equivalent_concept relations.
    """

    @property
    def scheme(self):
        return self.vocabulary_source and self.vocabulary_source[0] or None

    @property
    def concept(self):
        return self.equivalent_concept and self.equivalent_concept[0] or None


class AgentPlace(DateRelationMixin, SameAsMixIn, AnyEntity):
    __regid__ = "AgentPlace"
    fetch_attrs, cw_fetch_order = fetch_config(("role",))


class AgentFunction(DateRelationMixin, SameAsMixIn, AnyEntity):
    __regid__ = "AgentFunction"
    fetch_attrs, cw_fetch_order = fetch_config(("name", "description"))


class Citation(SameAsMixIn, AnyEntity):
    __regid__ = "Citation"
    fetch_attrs, cw_fetch_order = fetch_config(("uri", "note"))


class Mandate(DateRelationMixin, SameAsMixIn, AnyEntity):
    __regid__ = "Mandate"
    fetch_attrs, cw_fetch_order = fetch_config(("term", "description"))


class LegalStatus(DateRelationMixin, SameAsMixIn, AnyEntity):
    __regid__ = "LegalStatus"


class Occupation(DateRelationMixin, SameAsMixIn, AnyEntity):
    __regid__ = "Occupation"
    fetch_attrs, cw_fetch_order = fetch_config(("term", "description"))


class Structure(AnyEntity):
    __regid__ = "Structure"
    fetch_attrs, cw_fetch_order = fetch_config(("description",))


class EACSource(AnyEntity):
    __regid__ = "EACSource"
    fetch_attrs, cw_fetch_order = fetch_config(("title", "url", "description"))


class EACOtherRecordId(AnyEntity):
    __regid__ = "EACOtherRecordId"
    fetch_attrs, cw_fetch_order = fetch_config(("local_type", "value"))


class History(AnyEntity):
    __regid__ = "History"
    fetch_attrs, cw_fetch_order = fetch_config(("abstract", "text"))


class HistoricalEvent(DateRelationMixin, AnyEntity):
    __regid__ = "HistoricalEvent"
    fetch_attrs, cw_fetch_order = fetch_config(("event",))


class NameEntry(DateRelationMixin, AnyEntity):
    __regid__ = "NameEntry"
    fetch_attrs, cw_fetch_order = fetch_config(
        (
            "language",
            "preferred_form",
            "alternative_form",
            "authorized_form",
            "script_code",
            "parts",
        )
    )


class PlaceEntry(SameAsMixIn, AnyEntity):
    __regid__ = "PlaceEntry"
    fetch_attrs, cw_fetch_order = fetch_config(
        ("name", "latitude", "longitude", "local_type")
    )


class ParallelNames(DateRelationMixin, AnyEntity):
    __regid__ = "ParallelNames"
    fetch_attrs, cw_fetch_order = fetch_config(("authorized_form", "alternative_form"))


# XML export


def substitute_xml_prefix(prefix_name, namespaces):
    """Given an XML prefixed name in the form `'ns:name'`, return the string `'{<ns_uri>}name'`
    where `<ns_uri>` is the URI for the namespace prefix found in `namespaces`.

    This new string is then suitable to build an LXML etree.Element object.

    Example::

        >>> substitude_xml_prefix('xlink:href', {'xlink': 'http://wwww.w3.org/1999/xlink'})
        '{http://www.w3.org/1999/xlink}href'

    """
    try:
        prefix, name = prefix_name.split(":", 1)
    except ValueError:
        return prefix_name
    assert prefix in namespaces, "Unknown namespace prefix: {0}".format(prefix)
    return "{{{0}}}".format(namespaces[prefix]) + name


class AbstractXmlAdapter(EntityAdapter):
    """Abstract adapter to produce XML documents."""

    content_type = "text/xml"
    encoding = "utf-8"
    namespaces = {}

    @property
    def file_name(self):
        """Return a file name for the dump."""
        raise NotImplementedError

    def dump(self):
        """Return an XML string for the adapted entity."""
        raise NotImplementedError

    def element(self, tag, parent=None, attributes=None, text=None):
        """Generic function to build a XSD element tag.

        Params:

        * `name`, value for the 'name' attribute of the xsd:element

        * `parent`, the parent etree node

        * `attributes`, dictionary of attributes
        """
        attributes = attributes or {}
        tag = substitute_xml_prefix(tag, self.namespaces)
        for attr, value in list(attributes.items()):
            newattr = substitute_xml_prefix(attr, self.namespaces)
            attributes[newattr] = value
            if newattr != attr:
                attributes.pop(attr)
        if parent is None:
            elt = etree.Element(tag, attributes, nsmap=self.namespaces)
        else:
            elt = etree.SubElement(parent, tag, attributes)
        if text is not None:
            elt.text = text
        return elt

    @staticmethod
    def cwuri_url(entity):
        """Return an absolute URL for entity's cwuri, necessary for one head ahead application
        handling relative path in cwuri.
        """
        return entity.cwuri


def add_object_xml_wrap(func):
    """Add an objectXMLWrap sub-element to the element returned by `func`."""

    def wrapper(self, entity, *args, **kwargs):
        elem = func(self, entity, *args, **kwargs)
        if entity.xml_wrap is not None:
            objectXMLWrap = self.element("objectXMLWrap", parent=elem)
            objectXMLWrap.append(etree.parse(entity.xml_wrap).getroot())
        return elem

    return wraps(func)(wrapper)


def add_descriptive_note(func):
    @wraps(func)
    def wrapper(self, entity, *args, **kwargs):
        element = func(self, entity, *args, **kwargs)
        description = self._eac_richstring_paragraph_elements(entity, "description")
        if element is not None and description:
            self.element("descriptiveNote", parent=element).extend(description)
        return element

    return wrapper


def add_citation(func):
    @wraps(func)
    def wrapper(self, entity, *args, **kwargs):
        element = func(self, entity, *args, **kwargs)
        for citation in entity.has_citation:
            attrs = {"xlink:type": "simple"}
            if citation.uri:
                attrs["xlink:href"] = citation.uri
            self.element(
                "citation", parent=element, attributes=attrs, text=citation.note
            )
        return element

    return wrapper


class AuthorityRecordEACAdapter(AbstractXmlAdapter):
    __regid__ = "EAC-CPF"
    __select__ = is_instance("AuthorityRecord")

    namespaces = {
        None: u"urn:isbn:1-931666-33-4",
        u"xsi": u"http://www.w3.org/2001/XMLSchema-instance",
        u"xlink": u"http://www.w3.org/1999/xlink",
    }
    datetime_fmt = "%Y-%m-%dT%H:%M:%S"

    @property
    def file_name(self):
        """Return a file name for the dump."""
        if self.entity.isni:
            name = self.entity.isni.replace("/", "_")
        else:
            name = str(self.entity.eid)
        return u"EAC_{0}.xml".format(name)

    def dump(self):
        """Return an XML string representing the given agent using the EAC-CPF schema."""
        # Keep related activities since they are used multiple times
        self.activities = sorted(
            self.entity.reverse_generated, key=lambda x: x.start, reverse=True
        )
        # Root element
        eac_cpf_elt = self.element(
            "eac-cpf",
            attributes={
                "xsi:schemaLocation": (
                    "urn:isbn:1-931666-33-4 "
                    "http://eac.staatsbibliothek-berlin.de/schema/cpf.xsd"
                )
            },
        )
        # Top elements: control & cpfDescription
        self.control_element(eac_cpf_elt)
        self.cpfdescription_element(eac_cpf_elt)
        tree = etree.ElementTree(eac_cpf_elt)
        return etree.tostring(
            tree, xml_declaration=True, encoding=self.encoding, pretty_print=True
        )

    def control_element(self, eac_cpf_elt):
        control_elt = self.element("control", parent=eac_cpf_elt)
        self.recordid_element(control_elt)
        self.maintenance_status_element(control_elt)
        self.publication_status_element(control_elt)
        self.maintenance_agency_element(control_elt)
        self.language_declaration_element(control_elt)
        self.maintenance_history_element(control_elt)
        self.sources_element(control_elt)

    def recordid_element(self, control_elt):
        record_id = self.entity.record_id
        if record_id is None:
            record_id = str(self.entity.eid)
        self.element("recordId", parent=control_elt, text=record_id)
        for local_type, value in self.entity.other_record_ids:
            attrs = {}
            if local_type is not None:
                attrs["localType"] = local_type
            self.element(
                "otherRecordId", parent=control_elt, attributes=attrs, text=value
            )

    def cpfdescription_element(self, eac_cpf_elt):
        cpfdescription_elt = self.element("cpfDescription", parent=eac_cpf_elt)
        self.identity_element(cpfdescription_elt)
        self.description_element(cpfdescription_elt)
        self.relations_element(cpfdescription_elt)

    def maintenance_status_element(self, control_elt):
        if any(activity.type == "modify" for activity in self.activities):
            status = "revised"
        else:
            status = "new"
        self.element("maintenanceStatus", parent=control_elt, text=status)

    def publication_status_element(self, control_elt):
        self.element(
            "publicationStatus", parent=control_elt, text="inProcess"
        )  # or approved?

    def maintenance_agency_element(self, control_elt):
        agency_elt = self.element("maintenanceAgency", parent=control_elt)
        self.element("agencyName", parent=agency_elt)

    def language_declaration_element(self, control_elt):
        lang_decl_elt = self.element("languageDeclaration", parent=control_elt)
        self.element(
            "language",
            parent=lang_decl_elt,
            attributes={"languageCode": "fre"},
            text=u"français",
        )
        self.element(
            "script",
            parent=lang_decl_elt,
            attributes={"scriptCode": "Latn"},
            text="latin",
        )

    def maintenance_history_element(self, control_elt):
        if self.activities:
            history_elt = self.element("maintenanceHistory", parent=control_elt)
            for activity in self.activities:
                self.maintenance_event_element(activity, history_elt)

    def sources_element(self, control_elt):
        sources_elt = self.element("sources")
        for eac_source in self.entity.reverse_source_agent:
            sources_elt.append(self.source_element(eac_source))
        if len(sources_elt):
            control_elt.append(sources_elt)

    def identity_element(self, cpfdescription_elt):
        identity_elt = self.element("identity", parent=cpfdescription_elt)
        self._elt_text_from_attr("entityId", self.entity, "isni", parent=identity_elt)
        type_mapping = dict((v, k) for k, v in TYPE_MAPPING.items())
        eac_type = type_mapping.get(self.entity.kind)
        self.element("entityType", parent=identity_elt, text=eac_type)
        for name_entry in self.entity.reverse_name_entry_for:
            elem = self.element("nameEntry", parent=identity_elt)
            for part in name_entry.parts.split(u", "):
                self.element("part", parent=elem, text=part)
            if name_entry.form_variant == u"authorized":
                self.element(
                    "authorizedForm", text=u"conventionDeclaration", parent=elem
                )
            if name_entry.form_variant == u"alternative":
                self.element(
                    "alternativeForm", text=u"conventionDeclaration", parent=elem
                )

    def description_element(self, cpfdescription_elt):
        agent = self.entity
        description_elt = self.element("description", parent=cpfdescription_elt)
        self.exist_dates_element(description_elt)
        for relation, group_tagname, get_element in [
            ("reverse_place_agent", "places", self.place_element),
            ("reverse_function_agent", "functions", self.function_element),
            ("reverse_legal_status_agent", "legalStatuses", self.legal_status_element),
            ("reverse_occupation_agent", "occupations", self.occupation_element),
            ("reverse_mandate_agent", "mandates", self.mandate_element),
        ]:
            relateds = getattr(agent, relation)
            if relateds:
                group_elt = self.element(group_tagname, parent=description_elt)
                for related in relateds:
                    group_elt.append(get_element(related))
        for structure in agent.reverse_structure_agent:
            structure_elt = self.structure_element(structure)
            if len(structure_elt):
                description_elt.append(structure_elt)
        for generalcontext in agent.reverse_general_context_of:
            generalcontext_elt = self.generalcontext_element(generalcontext)
            if len(generalcontext_elt):
                description_elt.append(generalcontext_elt)
        for history in agent.reverse_history_agent:
            bioghist_elt = self.bioghist_element(history)
            if len(bioghist_elt):
                description_elt.append(bioghist_elt)

    def relations_element(self, cpfdescription_elt):
        relations_elt = self.element("relations")
        for rtype, rel_rtype, eac_rtype in [
            (
                "reverse_hierarchical_child",
                "hierarchical_parent",
                "hierarchical-parent",
            ),
            ("reverse_hierarchical_parent", "hierarchical_child", "hierarchical-child"),
            (
                "reverse_chronological_successor",
                "chronological_predecessor",
                "temporal-earlier",
            ),
            (
                "reverse_chronological_predecessor",
                "chronological_successor",
                "temporal-later",
            ),
            ("reverse_association_to", "association_from", "associative"),
            ("reverse_association_from", "association_to", "associative"),
        ]:
            for relation in getattr(self.entity, rtype):
                relations_elt.append(
                    self.cpfrelation_element(relation, rel_rtype, eac_rtype)
                )
        for resource_relation in self.entity.reverse_resource_relation_agent:
            relations_elt.append(self.resource_relation_element(resource_relation))
        if len(relations_elt):
            cpfdescription_elt.append(relations_elt)

    def maintenance_event_element(self, activity, history_elt):
        event_elt = self.element("maintenanceEvent", parent=history_elt)
        type_mapping = dict((v, k) for k, v in MAINTENANCETYPE_MAPPING.items())
        activity_type = type_mapping.get(activity.type, "created")
        self.element("eventType", parent=event_elt, text=activity_type)
        self.element(
            "eventDateTime",
            parent=event_elt,
            attributes={
                "standardDateTime": ustrftime(activity.start, fmt=self.datetime_fmt)
            },
            text=ustrftime(activity.start, fmt=self.datetime_fmt),
        )
        self.agent_element(activity, event_elt)
        self._elt_text_from_attr(
            "eventDescription", activity, "description", parent=event_elt
        )

    @add_descriptive_note
    @add_object_xml_wrap
    def source_element(self, eac_source):
        url = eac_source.url
        attributes = {"xlink:href": url, "xlink:type": "simple"} if url else None
        source_elt = self.element("source", attributes=attributes)
        self.element("sourceEntry", parent=source_elt, text=eac_source.title)
        return source_elt

    def exist_dates_element(self, description_elt):
        date_range = self._eac_date_range_xml_elt(
            self.entity.start_date, self.entity.end_date
        )
        if date_range is not None:
            exist_dates = self.element("existDates", parent=description_elt)
            exist_dates.append(date_range)

    @add_citation
    def place_element(self, place):
        place_elt = self.element("place")
        for attr, eac_name in [("role", "placeRole")]:
            self._elt_text_from_attr(eac_name, place, attr, parent=place_elt)
        for place_entry in place.place_entry_relation:
            place_entry_elt = self.element(
                "placeEntry", parent=place_elt, text=place_entry.name
            )
            if place_entry.equivalent_concept:
                place_entry_elt.attrib["vocabularySource"] = self.cwuri_url(
                    place_entry.equivalent_concept[0]
                )
            for attr, eac_name in (
                ("longitude", "longitude"),
                ("latitude", "latitude"),
                ("local_type", "localType"),
            ):
                value = getattr(place_entry, attr)
                if value:
                    place_entry_elt.attrib[eac_name] = str(value)
        for address in place.place_address:
            self.address_element(address, place_elt)
        return place_elt

    @add_descriptive_note
    @add_citation
    def function_element(self, function):
        function_elt = self.element("function")
        term_elt = self._elt_text_from_attr(
            "term", function, "name", parent=function_elt
        )
        if term_elt is not None and function.equivalent_concept:
            term_elt.attrib["vocabularySource"] = self.cwuri_url(
                function.equivalent_concept[0]
            )
        return function_elt

    @add_descriptive_note
    @add_citation
    def legal_status_element(self, legal_status):
        legal_status_elt = self.element("legalStatus")
        self._elt_text_from_attr("term", legal_status, "term", parent=legal_status_elt)
        return legal_status_elt

    @add_descriptive_note
    @add_citation
    def occupation_element(self, occupation):
        occupation_elt = self.element("occupation")
        term_elt = self._elt_text_from_attr(
            "term", occupation, "term", parent=occupation_elt
        )
        if term_elt is not None and occupation.equivalent_concept:
            term_elt.attrib["vocabularySource"] = self.cwuri_url(
                occupation.equivalent_concept[0]
            )
        self._eac_date_range_xml_elt(
            occupation.start_date, occupation.end_date, parent=occupation_elt
        )
        return occupation_elt

    @add_descriptive_note
    @add_citation
    def mandate_element(self, mandate):
        mandate_elt = self.element("mandate")
        term_elt = self._elt_text_from_attr("term", mandate, "term", parent=mandate_elt)
        if term_elt is not None and mandate.equivalent_concept:
            term_elt.attrib["vocabularySource"] = self.cwuri_url(
                mandate.equivalent_concept[0]
            )
        return mandate_elt

    def structure_element(self, structure):
        structure_elt = self.element("structureOrGenealogy")
        if structure.description:
            structure_elt.extend(
                self._eac_richstring_paragraph_elements(structure, "description")
            )
        return structure_elt

    @add_citation
    def generalcontext_element(self, context):
        context_elt = self.element("generalContext")
        if context.content:
            context_elt.extend(
                self._eac_richstring_paragraph_elements(context, "content")
            )
        return context_elt

    @add_citation
    def bioghist_element(self, history):
        bioghist_elt = self.element("biogHist")
        if history.text:
            bioghist_elt.extend(
                self._eac_richstring_paragraph_elements(history, "text")
            )
        return bioghist_elt

    @add_descriptive_note
    @add_object_xml_wrap
    def cpfrelation_element(self, relation, cw_rtype, eac_rtype):
        related = relation.related(cw_rtype).one()  # exactly one target (schema)
        relation_elt = self.element(
            "cpfRelation",
            attributes={
                "cpfRelationType": eac_rtype,
                "xlink:href": related.cwuri,
                "xlink:type": "simple",
            },
        )
        if relation.entry:
            self.element("relationEntry", parent=relation_elt, text=relation.entry)
        self._eac_date_range_xml_elt(
            getattr(relation, "start_date", None),
            getattr(relation, "end_date", None),
            parent=relation_elt,
        )
        return relation_elt

    @add_object_xml_wrap
    def resource_relation_element(self, resource_relation):
        resource = resource_relation.resource_relation_resource[0]
        attrs = {
            "xlink:href": resource.uri,
            "xlink:type": "simple",
        }
        if resource_relation.resource_role:
            attrs["xlink:role"] = resource_relation.resource_role
        if resource_relation.agent_role:
            attrs["resourceRelationType"] = resource_relation.agent_role
        res_rel_elt = self.element("resourceRelation", attributes=attrs)
        self._eac_date_range_xml_elt(
            resource_relation.start_date, resource_relation.end_date, parent=res_rel_elt
        )
        return res_rel_elt

    def agent_element(self, activity, maintenance_event_elt):
        if activity.agent:
            self.element("agentType", maintenance_event_elt, text="human")
            self.element("agent", maintenance_event_elt, text=activity.agent)
        else:  # These tags must be present, even if name is empty
            agent_type_elt = self.element("agentType", text="machine")
            maintenance_event_elt.append(agent_type_elt)
            maintenance_event_elt.append(self.element("agent"))

    def address_element(self, address, place_elt):
        address_elt = self.element("address", parent=place_elt)
        for eac_name, attr in ADDRESS_MAPPING:
            self._elt_text_from_attr(
                "addressLine",
                address,
                attr,
                attributes={"localType": eac_name},
                parent=address_elt,
            )

    # helper methods for lxml

    def _elt_text_from_attr(
        self, tag_name, entity, attr_name, parent=None, attributes=None
    ):
        """Return an lxml `Element` whose text is the value of the given attribute on the given
        entity.

        If this element is not empty and if ``parent`` is not ``None``, the element will also be
        inserted in the parent XML element.

        If ``attributes`` is not ``None``, these attributes will be added to the returned element.

        Return ``None`` if element is empty.
        """
        value = getattr(entity, attr_name)
        if value is not None:
            elt = self.element(
                tag_name, parent=parent, attributes=attributes, text=value
            )
            return elt

    def _eac_date_range_xml_elt(self, start_date, end_date, parent=None):
        """Return an EAC lxml ``'dateRange'`` ``Element`` with the given boundaries."""
        if not start_date and not end_date:
            return
        date_range = self.element("dateRange", parent=parent)
        for dt, eac_name in [(start_date, "fromDate"), (end_date, "toDate")]:
            if not dt:
                continue
            self.element(
                eac_name,
                parent=date_range,
                attributes={"standardDate": dt.isoformat()},
                text=dt.isoformat(),
            )
        return date_range

    def _eac_richstring_paragraph_elements(self, entity, attr_name):
        fmt = getattr(entity, attr_name + "_format")
        if fmt == "text/plain":
            value = getattr(entity, attr_name)
            if not value:
                return []
            return [self.element("p", text=line) for line in value.splitlines()]
        else:
            value = entity.printable_value(attr_name)
            if not value:
                return []
            return list(etree.fromstring(u"<root>{0}</root>".format(value)))
