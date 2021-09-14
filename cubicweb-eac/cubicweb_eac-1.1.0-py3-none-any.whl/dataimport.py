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
"""cubicweb-eac dataimport utilities for EAC-CPF (Encoded Archival
Context -- Corporate Bodies, Persons, and Families).
"""

from collections import deque
import copy
import json
import datetime
import re
from functools import wraps, partial
import inspect
import logging
from uuid import uuid4

from dateutil.parser import parse as parse_date
from lxml import etree

from cubicweb.dataimport.importer import ExtEntity

from cubicweb_skos import to_unicode

from cubicweb_eac import TYPE_MAPPING, ADDRESS_MAPPING, MAINTENANCETYPE_MAPPING


TYPE_MAPPING = TYPE_MAPPING.copy()
TYPE_MAPPING["human"] = u"person"

ETYPES_ORDER_HINT = (
    "AgentKind",
    "PhoneNumber",
    "PostalAddress",
    "AuthorityRecord",
    "Convention",
    "AgentPlace",
    "PlaceEntry",
    "Mandate",
    "LegalStatus",
    "History",
    "HistoricalEvent",
    "Structure",
    "AgentFunction",
    "Occupation",
    "GeneralContext",
    "AssociationRelation",
    "ChronologicalRelation",
    "HierarchicalRelation",
    "EACResourceRelation",
    "EACFunctionRelation",
    "ParallelNames",
    "ExternalUri",
    "EACSource",
    "Activity",
    "EACOtherRecordId",
    "NameEntry",
    "IdentityRelation",
    "FamilyRelation",
)


class InvalidEAC(RuntimeError):
    """EAC input is malformed."""


class InvalidXML(RuntimeError):
    """EAC input has an invalid XML format"""


class MissingTag(RuntimeError):
    """Mandatory tag is missing in EAC input"""

    def __init__(self, tag, tag_parent=None):
        super(MissingTag, self).__init__()
        self.tag = tag
        self.tag_parent = tag_parent


def external_uri(uri):
    values = [str(uri)]
    return ExtEntity("ExternalUri", uri, {"uri": set(values), "cwuri": set(values)})


def filter_none(func):
    """Filter None value from a generator function."""

    def wrapped(*args, **kwargs):
        for x in func(*args, **kwargs):
            if x is not None:
                yield x

    return wraps(func)(wrapped)


def filter_empty(func):
    """Filter out empty ExtEntity (i.e. with empty ``values`` attribute)."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for extentity in func(self, *args, **kwargs):
            if extentity.values:
                yield extentity

    return wrapper


def elem_maybe_none(func):
    """Method decorator for external entity builder function handling the case
    of `elem` being None.
    """
    if inspect.isgeneratorfunction(func):

        def wrapped(self, elem, *args, **kwargs):
            if elem is None:
                return
            for extentity in func(self, elem, *args, **kwargs):
                yield extentity

    else:

        def wrapped(self, elem, *args, **kwargs):
            if elem is None:
                return None
            else:
                return func(self, elem, *args, **kwargs)

    return wraps(func)(wrapped)


def add_xml_wrap_for(*etypes):
    """Add an `xml_wrap` attribute in ExtEntity's values dictionnary."""

    def decorator(func):
        def wrapped(self, elem):
            objectXMLWrap = self._elem_find(elem, "eac:objectXMLWrap")
            xmlwrap = None
            if objectXMLWrap is not None:
                nchildren = len(objectXMLWrap)
                if nchildren >= 1:
                    xmlwrap = objectXMLWrap[0]
                if nchildren > 1:
                    msg = self._("multiple children elements found in {0}").format(
                        objectXMLWrap
                    )
                    self.import_log.record_warning(msg, line=objectXMLWrap.sourceline)
            attribute_added = False
            for extentity in func(self, elem):
                if xmlwrap is not None and extentity.etype in etypes:
                    # prevent association of xmlwrap to several extentities.
                    assert not attribute_added, "xml_wrap attribute already added"
                    extentity.values.setdefault("xml_wrap", set([])).add(
                        etree.tostring(xmlwrap, encoding="utf-8")
                    )
                    attribute_added = True
                yield extentity

        return wraps(func)(wrapped)

    return decorator


def add_items_for(etype):
    """Add an `items` attribute in ExtEntity's values dictionnary."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, elem):
            for extentity in func(self, elem):
                if extentity.etype == etype:
                    items = self.parse_items(elem)
                    if items:
                        extentity.values["items"] = set([items])
                        extentity.values["items_format"] = set([u"text/html"])
                yield extentity

        return wrapper

    return decorator


def relate_to_record_through(etype, rtype):
    """Add an ``rtype`` relationship from ``etype`` to the imported record."""

    def decorator(func):
        if inspect.isgeneratorfunction(func):

            def wrapper(self, *args, **kwargs):
                for extentity in func(self, *args, **kwargs):
                    if extentity.etype == etype:
                        extentity.values.setdefault(rtype, set()).add(self.record.extid)
                    yield extentity

        else:

            def wrapper(self, *args, **kwargs):
                extentity = func(self, *args, **kwargs)
                if extentity and extentity.etype == etype:
                    extentity.values.setdefault(rtype, set()).add(self.record.extid)
                return extentity

        return wraps(func)(wrapper)

    return decorator


def add_child_for(etype, relation, builder):
    """Handle import of child generated by `builder` function for `etype` ExtEntity
    that is yielded by decorated method.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, elem):
            build_child = getattr(self, builder)
            for extentity in func(self, elem):
                if extentity.etype == etype:
                    for child in build_child(elem):
                        extentity.values.setdefault(relation, set()).add(child.extid)
                        yield child
                yield extentity

        return wrapper

    return decorator


add_citations_for = partial(
    add_child_for, relation="has_citation", builder="build_citation"
)
add_events_for = partial(
    add_child_for, relation="has_event", builder="parse_history_chronitems"
)
add_names_for = partial(
    add_child_for, relation="simple_name_relation", builder="build_name_child"
)
add_dates_for = partial(
    add_child_for, relation="date_relation", builder="build_date_entry"
)
add_place_entries_for = partial(
    add_child_for, relation="place_entry_relation", builder="build_place_entry"
)


def require_tag(tagname):
    """Method decorator handling a mandatory tag within a XML element."""

    def warn(self, elem):
        self.import_log.record_warning(
            self._("expecting a %s tag in element %s, found none")
            % (tagname, elem.tag),
            line=elem.sourceline,
        )

    def decorator(func):
        # pylint: disable=protected-access
        if inspect.isgeneratorfunction(func):

            def wrapped(self, elem, *args, **kwargs):
                if self._elem_find(elem, tagname) is None:
                    warn(self, elem)
                    return
                for extentity in func(self, elem, *args, **kwargs):
                    yield extentity

        else:

            def wrapped(self, elem, *args, **kwargs):
                if self._elem_find(elem, tagname) is None:
                    warn(self, elem)
                    return None
                return func(self, elem, *args, **kwargs)

        return wraps(func)(wrapped)

    return decorator


def trace_extentity(instance):
    """Decorator for `build_` methods tracing ExtEntities built from a given
    XML element.
    """

    def decorator(func):
        if inspect.isgeneratorfunction(func):

            def wrapper(elem, *args, **kwargs):
                for extentity in func(elem, *args, **kwargs):
                    instance.record_visited(elem, extentity)
                    yield extentity

        else:

            def wrapper(elem, *args, **kwargs):
                extentity = func(elem, *args, **kwargs)
                if extentity is not None:
                    instance.record_visited(elem, extentity)
                return extentity

        return wraps(func)(wrapper)

    return decorator


def equivalent_concept(tagname, etype):
    """Method decorator indicating that a sub-tag may have a vocabularySource attribute indicating
    that a relation to some ExternalUri object should be drown from any entity of type `etype` built
    by decorated method.
    """

    def decorator(func):
        @wraps(func)
        def wrapped(self, elem, *args, **kwargs):
            subelem = self._elem_find(elem, tagname)
            if subelem is not None:
                extid = subelem.attrib.get("vocabularySource")
                if extid:
                    yield external_uri(extid)
            else:
                extid = None

            def update_extentity(extentity):
                if extid is not None and extentity.etype == etype:
                    extentity.values["equivalent_concept"] = set([extid])

            if inspect.isgeneratorfunction(func):
                for extentity in func(self, elem, *args, **kwargs):
                    update_extentity(extentity)
                    yield extentity
            else:
                extentity = func(self, elem, *args, **kwargs)
                update_extentity(extentity)
                yield extentity

        return wrapped

    return decorator


class EACCPFImporter(object):
    """Importer for EAC-CPF data.

    The importer will generate `extid`s using the `extid_generator` function
    if specified or use `uuid.uuid4` to generate unique `extid`s.

    During import the `record` attribute is set to the external entity of the
    imported AuthorityRecord.

    Ref: http://eac.staatsbibliothek-berlin.de/fileadmin/user_upload/schema/cpfTagLibrary.html
    """

    def __init__(self, fpath, import_log, _=str, extid_generator=None):
        try:
            tree = etree.parse(fpath)
        except etree.XMLSyntaxError as exc:
            raise InvalidXML(str(exc))
        self._ = _
        self._root = tree.getroot()
        self.namespaces = self._root.nsmap.copy()
        # remove default namespaces, not supported by .xpath method we'll use later
        self.namespaces.pop(None, None)
        self.namespaces["eac"] = "urn:isbn:1-931666-33-4"
        self.namespaces.setdefault("xlink", "http://www.w3.org/1999/xlink")
        self.import_log = import_log
        if extid_generator is None:

            def extid_generator():
                return str(uuid4())

        self._gen_extid = extid_generator
        self.record = ExtEntity("AuthorityRecord", None, {})
        # Store a mapping of XML elements to produced ExtEntities
        self._visited = {}

    def __getattribute__(self, name):
        attr = super(EACCPFImporter, self).__getattribute__(name)
        if name.startswith("build_"):
            return trace_extentity(self)(attr)
        return attr

    def values_from_attrib(self, elem, name_attrib_tuples):
        values = {}
        for var_name, attrib_name in name_attrib_tuples:
            attrib_value = elem.attrib.get(attrib_name)
            if attrib_value:
                values[var_name] = set([str(attrib_value)])
        return values

    def values_from_xpaths(self, elem, name_path_tuples):
        values = {}
        for var_name, var_path in name_path_tuples:
            var = self._elem_find(elem, var_path)
            if var is not None and var.text:
                values[var_name] = set([str(var.text)])
        return values

    def parse_items(self, elem):
        values = []
        new_elem = copy.deepcopy(elem)
        for list_elem in self._elem_findall(new_elem, "eac:list"):
            list_elem.tag = "ul"
            for child in self._elem_findall(list_elem, "eac:item"):
                child.tag = "li"
            values.append(list_elem)
        result = u"\n".join(etree.tostring(item, encoding="unicode") for item in values)
        filtered = [
            e for e in re.split(r"xmlns\S*\"", result) if not e.startswith("xmlns")
        ]
        return u"".join(filtered)

    def record_visited(self, elem, extentity):
        assert extentity.extid, extentity
        self._visited.setdefault(elem, set([])).add(extentity.extid)

    def not_visited(self):
        """Yield (tagname, sourceline) items corresponding to XML elements not
        used to build any ExtEntity.
        """
        visited = self._visited
        ns = self.namespaces["eac"]
        queue = deque(self._root)
        # These elements contain other ones which are known to be handled.
        container_tags = [
            "control",
            "cpfDescription",
            "identity",
            "maintenanceHistory",
            "sources",
            "description",
            "mandates",
            "places",
            "legalStatuses",
            "occupations",
            "relations",
        ]
        containers = ["{{{0}}}{1}".format(ns, tag) for tag in container_tags]
        while queue:
            elem = queue.popleft()
            if not isinstance(elem, etree._Element) or isinstance(elem, etree._Comment):
                continue
            if elem in visited:
                continue
            if elem.tag not in containers:
                yield elem.tag.replace("{" + ns + "}", ""), elem.sourceline
            else:
                queue.extend(elem)

    def _elem_find(self, elem, path, method="find"):
        """Wrapper around lxml.etree.Element find* methods to support
        namespaces also for old lxml versions.
        """
        finder = getattr(elem, method)
        try:
            return finder(path, self.namespaces)
        except TypeError:
            # In old lxml, find() does not accept namespaces argument.
            path = path.split(":", 1)
            try:
                ns, path = path
            except ValueError:
                # path has no namespace
                pass
            else:
                path = "{" + self.namespaces[ns] + "}" + path
            return finder(path)

    def _elem_findall(self, *args):
        return self._elem_find(*args, method="findall")

    @filter_empty
    def external_entities(self):
        """Parse a EAC XML file to and yield external entities."""
        # control element.
        control = self._elem_find(self._root, "eac:control")
        if control is None:
            raise MissingTag("control")
        for extentity in self.parse_control(control):
            yield extentity
        # Records (identity tags) are within cpfDescription tag.
        cpf_desc = self._elem_find(self._root, "eac:cpfDescription")
        if cpf_desc is None:
            raise MissingTag("cpfDescription")
        # identity element.
        identity = self._elem_find(cpf_desc, "eac:identity")
        if identity is None:
            raise MissingTag("identity", "cpfDescription")
        for extentity in self.parse_identity(identity):
            yield extentity
        # description element.
        description = self._elem_find(cpf_desc, "eac:description")
        if description is not None:
            for extentity in self.parse_description(description):
                yield extentity
        # relations element.
        for extentity in self.parse_relations(cpf_desc):
            yield extentity
        # Record is complete.
        self.record_visited(self._root, self.record)
        yield self.record

    def parse_identity(self, identity):
        """Parse the `identity` tag and yield external entities, possibly
        updating record's `values` dict.
        """
        # entityId
        isni = self._elem_find(identity, "eac:entityId")
        if isni is not None and isni.text:
            self.record_visited(isni, self.record)
            self.record.values["isni"] = set([str(isni.text)])
        # entityType
        akind = self._elem_find(identity, "eac:entityType")
        if akind is None:
            raise MissingTag("entityType", "identity")
        agent_kind = self.build_agent_kind(akind)
        yield agent_kind
        self.record.values["agent_kind"] = set([agent_kind.extid])
        name_entry = None
        name_entries = self._elem_findall(identity, "eac:nameEntry")
        if not name_entries:
            raise MissingTag("nameEntry", "identity")
        for name_entry in name_entries:
            for extentity in self.build_name_entry(name_entry):
                yield extentity
        parallel_name_entries = self._elem_findall(identity, "eac:nameEntryParallel")
        for parallel_name_entry in parallel_name_entries:
            for extentity in self.build_parallel(parallel_name_entry):
                yield extentity

    @relate_to_record_through("ParallelNames", "parallel_names_of")
    @add_names_for("ParallelNames")
    @add_dates_for("ParallelNames")
    def build_parallel(self, elem):
        """For each nameEntryParallel build a new object linked to the
        EAC-CPF document and get relations for all childrens"""
        values = self.values_from_xpaths(
            elem,
            (
                ("authorized_form", "eac:authorizedForm"),
                ("alternative_form", "eac:alternativeForm"),
            ),
        )
        yield ExtEntity("ParallelNames", self._gen_extid(), values)

    @filter_empty
    def extract_dates_from(self, elem, tag):
        for date in self.find_nested(elem, "eac:date", tag):
            yield ExtEntity(
                "DateEntity",
                self._gen_extid(),
                {
                    "start_date": set([self.parse_date(date)]),
                    "end_date": set([self.parse_date(date)]),
                },
            )
        for date_range in self.find_nested(elem, "eac:dateRange", tag):
            yield ExtEntity(
                "DateEntity", self._gen_extid(), self.parse_daterange(date_range)
            )

    @filter_empty
    @elem_maybe_none
    def build_date_entry(self, elem):
        """Build DateEntitys linked to a parent entity"""
        for usedates in self._elem_findall(elem, "eac:useDates"):
            for extentity in self.build_date_entry(usedates):
                yield extentity
        if self._elem_find(elem, "eac:dateSet"):
            for date_set in self._elem_findall(elem, "eac:dateSet"):
                for extentity in self.extract_dates_from(date_set, "eac:dateSet"):
                    yield extentity
        for entity in self.extract_dates_from(elem, "eac:test"):
            yield entity

    @filter_empty
    @filter_none
    @elem_maybe_none
    def build_name_child(self, elem):
        """Build NameEntry external entity"""
        for elem in self._elem_findall(elem, "eac:nameEntry"):
            values = self.values_from_attrib(
                elem, (("language", "lang"), ("script_code", "scriptCode"))
            )
            values.update(
                self.values_from_xpaths(
                    elem,
                    (
                        ("preferred_form", "eac:preferredForm"),
                        ("alternative_form", "eac:alternativeForm"),
                        ("authorized_form", "eac:authorizedForm"),
                    ),
                )
            )
            parts = self._elem_findall(elem, "eac:part")
            if not parts:
                raise MissingTag("part", "nameEntry")
            values["parts"] = {u", ".join(str(p.text) for p in parts)}
            yield ExtEntity("NameEntry", self._gen_extid(), values)

    def parse_languages(self, elems):
        """Add a `languages` on AuthorityRecord"""
        languages = []
        for elem in elems:
            language = self._elem_find(elem, "eac:language")
            if language is not None and language.text.strip():
                languages.append(language.text.strip())
        if languages:
            self.record.values["languages"] = set([u", ".join(languages)])

    @filter_none
    def parse_description(self, description):
        """Parse the `description` tag and yield external entities, possibly
        updating record's `values` dict.
        """
        # dates.
        daterange = description.xpath(
            "eac:existDates/eac:dateRange", namespaces=self.namespaces
        )
        if daterange:
            elem = daterange[0]
            self.record_visited(elem, self.record)
            self.record_visited(elem.getparent(), self.record)
            dates = self.parse_daterange(elem)
            if dates:
                self.record.values.update(dates)
        # address.
        for place in self.find_nested(description, "eac:place", "eac:places"):
            for extentity in self.build_place(place):
                yield extentity
        # additional EAC-CPF information.
        for legal_status in self.find_nested(
            description, "eac:legalStatus", "eac:legalStatuses"
        ):
            for extentity in self.build_legal_status(legal_status):
                yield extentity
        # mandate
        for mandate in self.find_nested(description, "eac:mandate", "eac:mandates"):
            for extentity in self.build_mandate(mandate):
                yield extentity
        # languagesUsed
        languages = self.find_nested(
            description, "eac:languageUsed", "eac:languagesUsed"
        )
        if languages:
            self.parse_languages(languages)
        # history
        for history in self._elem_findall(description, "eac:biogHist"):
            for extentity in self.build_history(history):
                yield extentity
        # structure
        for structure in self._elem_findall(description, "eac:structureOrGenealogy"):
            for extentity in self.build_structure(structure):
                yield extentity
        # function
        for function in self.find_nested(description, "eac:function", "eac:functions"):
            for extentity in self.build_function(function):
                yield extentity
        # occupation
        for occupation in self.find_nested(
            description, "eac:occupation", "eac:occupations"
        ):
            for extentity in self.build_occupation(occupation):
                yield extentity
        # general context
        for context in self._elem_findall(description, "eac:generalContext"):
            for extentity in self.build_generalcontext(context):
                yield extentity

    def find_nested(self, elem, tagname, innertag):
        """Return a list of element with `tagname` within `element` possibly
        nested within `innertag`.
        """
        all_elems = self._elem_findall(elem, tagname)
        wrapper = self._elem_find(elem, innertag)
        if wrapper is not None:
            all_elems.extend(self._elem_findall(wrapper, tagname))
        return all_elems

    def parse_tag_description(
        self, elem, tagname="eac:descriptiveNote", attrname="description"
    ):
        """Return a dict with `attrname` and `attrname`_format retrieved from
        a description-like tag.
        """
        elems = self._elem_findall(elem, tagname)
        if len(elems) > 1:
            self.import_log.record_warning(
                self._(
                    "found multiple %s tag within %s element, only one will be " "used."
                )
                % (tagname, elem.tag),
                line=elem.sourceline,
            )
        elem = elems[0] if elems else None
        values = {}
        if elem is not None:
            parsed = self.parse_tag_content(elem)
            values.update(
                zip((attrname, attrname + "_format"), (set([p]) for p in parsed))
            )
        return values

    def parse_tag_content(self, elem):
        """Parse the content of an element be it plain text or HTML and return
        the content along with MIME type.
        """
        assert elem is not None, "unexpected empty element"
        text = elem.text.strip() if elem.text else None
        if text:
            desc, desc_format = str(text), u"text/plain"
        else:
            ptag = "{%(eac)s}p" % self.namespaces
            desc = "\n".join(
                etree.tostring(child, encoding=str, method="html").strip()
                for child in elem.iterchildren(ptag)
                if len(child) != 0 or child.text
            )
            if desc:
                desc_format = u"text/html"
            else:
                self.import_log.record_warning(
                    self._(
                        "element %s has no text nor children, no content " "extracted"
                    )
                    % elem.tag,
                    line=elem.sourceline,
                )
                desc, desc_format = None, None
        return desc, desc_format

    @relate_to_record_through("NameEntry", "name_entry_for")
    @add_dates_for("NameEntry")
    def build_name_entry(self, element):
        """Build a NameEntry external entity."""
        self.record_visited(element, self.record)
        parts = self._elem_findall(element, "eac:part")
        if not parts:
            raise MissingTag("part", "nameEntry")
        # Join all "part" tags into a single "parts" attribute.
        values = {"parts": set([u", ".join(str(p.text) for p in parts)])}
        # Consider first authorizedForm and then alternativeForm, missing
        # possible combinations which cannot be handled until the model is
        # complete.
        if self._elem_find(element, "eac:authorizedForm") is not None:
            values["form_variant"] = set([u"authorized"])
        elif self._elem_find(element, "eac:alternativeForm") is not None:
            values["form_variant"] = set([u"alternative"])
        yield ExtEntity("NameEntry", self._gen_extid(), values)

    @elem_maybe_none
    def build_agent_kind(self, elem):
        """Build a AgentKind external entity"""
        # Map EAC entity types to our terminolgy.
        kind = TYPE_MAPPING.get(elem.text, u"unknown-agent-kind")
        if kind == "unknown-agent-kind":
            msg = self._("unexpected entity type {}").format(elem.text)
            self.import_log.record_warning(msg, line=elem.sourceline)
        agentkind_id = "agentkind/" + kind
        return ExtEntity("AgentKind", agentkind_id, {"name": set([str(kind)])})

    @elem_maybe_none
    @relate_to_record_through("LegalStatus", "legal_status_agent")
    @filter_empty
    @add_citations_for("LegalStatus")
    @add_place_entries_for("LegalStatus")
    @add_items_for("LegalStatus")
    @add_dates_for("LegalStatus")
    @equivalent_concept("eac:term", "LegalStatus")
    def build_legal_status(self, elem, **kwargs):
        """Build a `LegalStatus` external entity.

        Extra `kwargs` are passed to `parse_tag_description`.
        """
        values = self.parse_tag_description(elem, **kwargs)
        term = self._elem_find(elem, "eac:term")
        if term is not None and term.text:
            values["term"] = set([str(term.text)])
        yield ExtEntity("LegalStatus", self._gen_extid(), values)

    @elem_maybe_none
    @relate_to_record_through("Mandate", "mandate_agent")
    @filter_empty
    @add_citations_for("Mandate")
    @add_place_entries_for("Mandate")
    @add_items_for("Mandate")
    @add_dates_for("Mandate")
    @equivalent_concept("eac:term", "Mandate")
    def build_mandate(self, elem, **kwargs):
        """Build a `Mandate` external entity.

        Extra `kwargs` are passed to `parse_tag_description`.
        """
        values = self.parse_tag_description(elem, **kwargs)
        term = self._elem_find(elem, "eac:term")
        if term is not None and term.text:
            values["term"] = set([str(term.text)])
        yield ExtEntity("Mandate", self._gen_extid(), values)

    @elem_maybe_none
    def build_citation(self, elem):
        """Build a `Citation` external entity."""
        for citation_elem in self._elem_findall(elem, "eac:citation"):
            note = citation_elem.text.strip() if citation_elem.text else u""
            uri = citation_elem.attrib.get("{%(xlink)s}href" % self.namespaces)
            if not note and not uri:
                msg = self._("element {0} has no text nor (valid) link").format(
                    etree.tostring(citation_elem)
                )
                self.import_log.record_warning(msg, line=citation_elem.sourceline)
                return
            values = {}
            if uri:
                values["uri"] = set([str(uri)])
            if note:
                values["note"] = set([str(note)])
                if u"<span>" in note:
                    values["note_format"] = set([u"text/html"])
            yield ExtEntity("Citation", self._gen_extid(), values)

    @relate_to_record_through("History", "history_agent")
    @add_citations_for("History")
    @add_items_for("History")
    @elem_maybe_none
    def build_history(self, elem):
        """Build a `History` external entity."""
        abstract = self._elem_find(elem, "eac:abstract")
        desc, desc_format = self.parse_tag_content(elem)
        if desc:
            values = {"text": set([desc]), "text_format": set([desc_format])}
            if abstract is not None and abstract.text:
                values["abstract"] = set([str(abstract.text)])
            history = ExtEntity("History", self._gen_extid(), values)
            for child in self.parse_history_chronitems(elem):
                if child.etype == "HistoricalEvent":
                    history.values.setdefault("has_event", set()).add(child.extid)
                yield child
            yield history

    def parse_history_chronitems(self, elem):
        """Build en `Event` external entity."""
        for citem in self._elem_findall(elem, ".//eac:chronItem"):
            for extentity in self.build_event(citem):
                yield extentity

    @add_dates_for("HistoricalEvent")
    @add_place_entries_for("HistoricalEvent")
    @filter_none
    @filter_empty
    @elem_maybe_none
    def build_event(self, elem):
        """Build a `HistoricalEvent` external entity."""
        values = {}
        event = self._elem_find(elem, "eac:event")
        if event is not None and event.text:
            values["event"] = set([str(event.text)])
        yield ExtEntity("HistoricalEvent", self._gen_extid(), values)

    @elem_maybe_none
    @relate_to_record_through("Structure", "structure_agent")
    @add_citations_for("Structure")
    @add_items_for("Structure")
    def build_structure(self, elem):
        """Build a `Structure` external entity."""
        desc, desc_format = self.parse_tag_content(elem)
        if desc:
            values = {
                "description": set([desc]),
                "description_format": set([desc_format]),
            }
            yield ExtEntity("Structure", self._gen_extid(), values)

    @relate_to_record_through("AgentPlace", "place_agent")
    @filter_empty
    @add_citations_for("AgentPlace")
    @add_dates_for("AgentPlace")
    @add_items_for("AgentPlace")
    def build_place(self, elem):
        """Build a AgentPlace external entity"""
        values = {}
        role = self._elem_find(elem, "eac:placeRole")
        if role is not None:
            values["role"] = set([str(role.text)])
        for address in self._elem_findall(elem, "eac:address"):
            for extentity in self.build_address(address):
                if extentity.values:
                    values["place_address"] = set([extentity.extid])
                    yield extentity
        place = ExtEntity("AgentPlace", self._gen_extid(), values)
        for child in self.build_place_entry(elem):
            if child.etype == "PlaceEntry":
                place.values.setdefault("place_entry_relation", set()).add(child.extid)
            yield child
        yield place

    @filter_empty
    @equivalent_concept("eac:placeEntry", "PlaceEntry")
    def build_place_entry(self, elem):
        for entry in self._elem_findall(elem, "eac:placeEntry"):
            values = {"name": set([str(entry.text)])}
            values.update(
                self.values_from_attrib(
                    entry,
                    (
                        ("local_type", "localType"),
                        ("longitude", "longitude"),
                        ("latitude", "latitude"),
                    ),
                )
            )
            yield ExtEntity("PlaceEntry", self._gen_extid(), values)

    def build_address(self, elem):
        """Build `PostalAddress`s external entity"""
        address_entity = {}
        address_lines = []
        for line in self._elem_findall(elem, "eac:addressLine"):
            address_lines.append(str(line.text))
            if "localType" in line.attrib:
                attr = dict(ADDRESS_MAPPING).get(line.attrib["localType"])
                if attr:
                    address_entity.setdefault(attr, set()).add(str(line.text))
        if address_lines:
            address_entity["raw_address"] = set([u"\n".join(address_lines)])
        yield ExtEntity("PostalAddress", self._gen_extid(), address_entity)

    @relate_to_record_through("AgentFunction", "function_agent")
    @filter_empty
    @add_citations_for("AgentFunction")
    @add_place_entries_for("AgentFunction")
    @add_dates_for("AgentFunction")
    @add_items_for("AgentFunction")
    @equivalent_concept("eac:term", "AgentFunction")
    def build_function(self, elem):
        """Build a `AgentFunction`s external entities"""
        values = self.parse_tag_description(elem)
        term = self._elem_find(elem, "eac:term")
        if term is not None:
            values["name"] = set([str(term.text)])
        yield ExtEntity("AgentFunction", self._gen_extid(), values)

    @relate_to_record_through("Occupation", "occupation_agent")
    @filter_empty
    @add_citations_for("Occupation")
    @add_place_entries_for("Occupation")
    @add_items_for("Occupation")
    @add_dates_for("Occupation")
    @equivalent_concept("eac:term", "Occupation")
    def build_occupation(self, elem):
        """Build a `Occupation`s external entities"""
        values = self.parse_tag_description(elem)
        term = self._elem_find(elem, "eac:term")
        if term is not None:
            values["term"] = set([str(term.text)])
        yield ExtEntity("Occupation", self._gen_extid(), values)

    @relate_to_record_through("GeneralContext", "general_context_of")
    @add_citations_for("GeneralContext")
    @add_items_for("GeneralContext")
    def build_generalcontext(self, elem):
        """Build a `GeneralContext` external entity"""
        content, content_format = self.parse_tag_content(elem)
        if content:
            values = {
                "content": set([content]),
                "content_format": set([content_format]),
            }
            yield ExtEntity("GeneralContext", self._gen_extid(), values)

    @elem_maybe_none
    def parse_daterange(self, elem):
        """Parse a `dateRange` tag and return a dict mapping `start_date` and
        `end_date` to parsed date range.
        """
        values = {}
        for eactag, attrname in zip(
            ("eac:fromDate", "eac:toDate"), ("start_date", "end_date")
        ):
            date = self.parse_date(self._elem_find(elem, eactag))
            if date:
                values[attrname] = set([date])
        return values

    @elem_maybe_none
    def parse_date(self, elem):
        """Parse a date-like element"""

        def record_warning(msg):
            self.import_log.record_warning(
                msg % {"e": etree.tostring(elem)}, line=elem.sourceline
            )

        standard_date = elem.attrib.get("standardDate")
        if standard_date:
            date = standard_date
        else:
            for attr in ("notBefore", "notAfter"):
                if elem.attrib.get(attr):
                    record_warning(
                        self._(
                            "found an unsupported %s attribute in date "
                            "element %%(e)s"
                        )
                        % attr
                    )
            # Using element's text.
            date = elem.text
            if not date:
                record_warning(self._("no date specified"))
                return None
        # Set a default value for month and day; the year should always be
        # given.
        default = datetime.datetime(9999, 1, 1)
        try:
            pdate = parse_date(date, default=default)
        except ValueError:
            record_warning(self._("could not parse date %(e)s"))
            return None
        except Exception as exc:  # pylint: disable=broad-except
            # Usually a bug in dateutil.parser.
            record_warning(
                self._("unexpected error during parsing of date %%(e)s: %s")
                % to_unicode(exc)
            )
            logger = logging.getLogger("cubes.eac")
            logger.exception(self._("unhandled exception while parsing date %r"), date)
            return None
        else:
            if pdate.year == default.year:
                record_warning(self._("could not parse a year from date element %(e)s"))
                return None
            return pdate.date()

    def parse_relations(self, cpf_description):
        """Parse the `relations` tag and yield external entities, possibly
        updating record's `values` dict.
        """
        relations = self._elem_find(cpf_description, "eac:relations")
        if relations is None:
            return
        builders = (
            ("eac:cpfRelation", self.build_relation),
            ("eac:resourceRelation", self.build_resource_relation),
            ("eac:functionRelation", self.build_function_relation),
        )
        for xpath, builder in builders:
            for elem in self._elem_findall(relations, xpath):
                for extentity in builder(elem):
                    yield extentity

    @add_xml_wrap_for(
        "AssociationRelation",
        "ChronologicalRelation",
        "HierarchicalRelation",
        "IdentityRelation",
        "FamilyRelation",
    )
    @add_dates_for("AssociationRelation")
    @add_dates_for("ChronologicalRelation")
    @add_dates_for("HierarchicalRelation")
    @add_dates_for("IdentityRelation")
    @add_dates_for("FamilyRelation")
    @add_place_entries_for("AssociationRelation")
    @add_place_entries_for("ChronologicalRelation")
    @add_place_entries_for("HierarchicalRelation")
    @add_place_entries_for("IdentityRelation")
    @add_place_entries_for("FamilyRelation")
    def build_relation(self, elem):
        """Build a relation between records external entity (with proper type)."""
        relationship = elem.attrib.get("cpfRelationType")
        if relationship is None:
            self.import_log.record_warning(
                self._(
                    "found no cpfRelationType attribute in element %s, defaulting "
                    "to associative"
                )
                % etree.tostring(elem),
                line=elem.sourceline,
            )
            relationship = "associative"
        try:
            # "other_role" (resp. "agent_role") role designates the object of the relation (resp.
            # the agent described in the EAC-CPF instance).
            # See: http://eac.staatsbibliothek-berlin.de/fileadmin/user_upload/schema/cpfTagLibrary.html#cpfRelationType # noqa pylint: disable=line-too-long
            # In case the EAC relation is not qualified, we assume the object is the "parent" (or
            # oldest) in the relation.
            etype, other_role, agent_role = {
                "hierarchical": (
                    "HierarchicalRelation",
                    "hierarchical_parent",
                    "hierarchical_child",
                ),
                "hierarchical-parent": (
                    "HierarchicalRelation",
                    "hierarchical_parent",
                    "hierarchical_child",
                ),
                "hierarchical-child": (
                    "HierarchicalRelation",
                    "hierarchical_child",
                    "hierarchical_parent",
                ),
                "temporal": (
                    "ChronologicalRelation",
                    "chronological_predecessor",
                    "chronological_successor",
                ),
                "temporal-earlier": (
                    "ChronologicalRelation",
                    "chronological_predecessor",
                    "chronological_successor",
                ),
                "temporal-later": (
                    "ChronologicalRelation",
                    "chronological_successor",
                    "chronological_predecessor",
                ),
                "associative": (
                    "AssociationRelation",
                    "association_to",
                    "association_from",
                ),
                "identity": ("IdentityRelation", "identity_to", "identity_from"),
                "family": ("FamilyRelation", "family_to", "family_from"),
            }[relationship]
        except KeyError:
            self.import_log.record_warning(
                self._("unsupported cpfRelationType %s in element %s, skipping")
                % (relationship, etree.tostring(elem)),
                line=elem.sourceline,
            )
            return
        obj_uri = elem.attrib.get("{%(xlink)s}href" % self.namespaces)
        if not obj_uri:
            self.import_log.record_warning(
                self._(
                    "found a cpfRelation without any object (no "
                    "xlink:href attribute), skipping"
                ),
                line=elem.sourceline,
            )
            return
        yield external_uri(obj_uri)
        values = {agent_role: set([self.record.extid]), other_role: set([obj_uri])}
        rentry = self._elem_find(elem, "eac:relationEntry")
        if rentry is not None and rentry.text.strip():
            values["entry"] = set([str(rentry.text)])
        values.update(self.parse_tag_description(elem))
        yield ExtEntity(etype, self._gen_extid(), values)

    @add_place_entries_for("EACFunctionRelation")
    @add_dates_for("EACFunctionRelation")
    @add_xml_wrap_for("EACFunctionRelation")
    def build_function_relation(self, elem):
        """Build a relation between function entities

        yield an ExternalUri object, and an EACFunctionRelation
        object that make the link between the ExternalUri and
        the AuthorityRecord object"""
        values = self.parse_tag_description(elem)
        relationship = elem.attrib.pop("functionRelationType", None)
        obj_uri = elem.attrib.pop("{%(xlink)s}href" % self.namespaces, None)
        # Yield the ExternalUri object
        if obj_uri:
            yield external_uri(obj_uri)
            values.update({"function_relation_function": set([str(obj_uri)])})
        if relationship:
            values.update({"r_type": set([str(relationship)])})
        values.update(
            {
                "function_relation_agent": set([str(self.record.extid)]),
            }
        )
        values.update(
            self.values_from_xpaths(
                elem,
                (
                    ("place_entry", "eac:placeEntry"),
                    ("relation_entry", "eac:relationEntry"),
                ),
            )
        )
        if elem.attrib:
            attributes = json.dumps(dict(elem.attrib), sort_keys=True)
        else:
            attributes = json.dumps({})
        values.update({"xml_attributes": set([str(attributes)])})
        yield ExtEntity("EACFunctionRelation", self._gen_extid(), values)

    @add_place_entries_for("EACResourceRelation")
    @add_dates_for("EACResourceRelation")
    @add_xml_wrap_for("EACResourceRelation")
    def build_resource_relation(self, elem):
        """Build a `EACResourceRelation` external entity (along with
        ExternalUri entities).
        """
        obj_uri = elem.attrib.pop("{%(xlink)s}href" % self.namespaces, None)
        if obj_uri is None:
            self.import_log.record_warning(
                self._(
                    "found a resourceRelation without any object (no xlink:href "
                    "attribute), skipping"
                ),
                line=elem.sourceline,
            )
            return
        yield external_uri(obj_uri)
        values = {
            "resource_relation_resource": set([obj_uri]),
            "resource_relation_agent": set([self.record.extid]),
        }
        relation_entry = self._elem_find(elem, "eac:relationEntry")
        if relation_entry is not None:
            values["relation_entry"] = set([str(relation_entry.text)])
        resource_role = elem.attrib.pop("{%(xlink)s}role" % self.namespaces, None)
        if resource_role:
            values["resource_role"] = set([str(resource_role)])
        agent_role = elem.attrib.pop("resourceRelationType", None)
        if agent_role:
            values["agent_role"] = set([str(agent_role)])
        if elem.attrib:
            attributes = json.dumps(dict(elem.attrib), sort_keys=True)
        else:
            attributes = json.dumps({})
        values.update({"xml_attributes": set([str(attributes)])})
        values.update(self.parse_tag_description(elem))
        yield ExtEntity("EACResourceRelation", self._gen_extid(), values)

    @filter_none
    def parse_control(self, control):
        """Parse the `control` tag."""
        record_id = self._elem_find(control, "eac:recordId")
        if record_id is not None and record_id.text and record_id.text.strip():
            record_id = record_id.text.strip()
            self.record.extid = "authorityrecord-{}".format(record_id)
            self.record.values["record_id"] = set([to_unicode(record_id)])
            self.record_visited(record_id, self.record)
        else:
            raise InvalidEAC("recordId element in control tag is mandatory")
        for other_record_id in self._elem_findall(control, "eac:otherRecordId"):
            other_id = other_record_id.text.strip()
            if other_id:
                values = {
                    "eac_other_record_id_of": set([self.record.extid]),
                    "value": set([str(other_id)]),
                }
                if other_record_id.attrib.get("localType"):
                    values["local_type"] = set(
                        [str(other_record_id.attrib["localType"])]
                    )
                extentity = ExtEntity("EACOtherRecordId", self._gen_extid(), values)
                self.record_visited(other_record_id, extentity)
                yield extentity
        builders = (
            ("eac:sources/eac:source", self.build_source),
            (
                "eac:maintenanceHistory/eac:maintenanceEvent",
                self.build_maintenance_event,
            ),
            ("eac:conventionDeclaration", self.build_convention),
        )
        for xpath_str, builder in builders:
            for elem in control.xpath(xpath_str, namespaces=self.namespaces):
                for extentity in builder(elem):
                    yield extentity

    def build_maintenance_event(self, elem):
        """Parse a `maintenanceEvent` tag, yielding a prov:Activity external
        entity along with necessary Records.
        """
        values = {"generated": set([self.record.extid])}
        event_type = self.parse_event_type(self._elem_find(elem, "eac:eventType"))
        if event_type is not None:
            values["type"] = set([event_type])
        date = self._elem_find(elem, "eac:eventDateTime")
        if date is not None:
            dtattr = date.attrib.get("standardDateTime")
            if dtattr:
                try:
                    event_date = parse_date(dtattr)
                except ValueError:
                    self.import_log.record_warning(
                        self._("could not parse date from %s") % etree.tostring(date),
                        line=date.sourceline,
                    )
                else:
                    values["start"] = set([event_date])
                    values["end"] = set([event_date])
        values.update(self.parse_tag_description(elem, "eac:eventDescription"))
        values.update(self.values_from_xpaths(elem, (("agent", "eac:agent"),)))
        agent_type = self._elem_find(elem, "eac:agentType")
        values["agent_type"] = u"unknown"
        if agent_type.text in {"human", "machine"}:
            values["agent_type"] = set([str(agent_type.text)])
        yield ExtEntity("Activity", self._gen_extid(), values)

    @relate_to_record_through("Convention", "convention_of")
    @add_citations_for("Convention")
    @filter_none
    @filter_empty
    @elem_maybe_none
    def build_convention(self, elem):
        """Build a `Convention` external entity"""
        values = self.parse_tag_description(elem)
        abbrev = self._elem_find(elem, "eac:abbreviation")
        if abbrev is not None and abbrev.text:
            values["abbrev"] = set([str(abbrev.text)])
        yield ExtEntity("Convention", self._gen_extid(), values)

    @elem_maybe_none
    def parse_event_type(self, elem):
        """Parse an `eventType` element and try to match a prov:type to build a
        prov:Activity.
        """
        event_type = elem.text.strip() if elem.text else None
        if event_type:
            type_mapping = MAINTENANCETYPE_MAPPING.copy()
            type_mapping["derived"] = u"create"
            type_mapping["updated"] = u"modify"
            try:
                event_type = type_mapping[event_type.lower()]
            except KeyError:
                self.import_log.record_warning(
                    self._(
                        "eventType %s does not match the PROV-O vocabulary, "
                        "respective Activity will not have a `type` attribute set."
                    )
                    % event_type,
                    line=elem.sourceline,
                )
                return None
            return event_type

    @relate_to_record_through("EACSource", "source_agent")
    @filter_empty
    @add_xml_wrap_for("EACSource")
    def build_source(self, elem):
        """Parse a `source` tag, yielding EACSource external entities."""
        values = self.parse_tag_description(elem)
        url = elem.attrib.get("{%(xlink)s}href" % self.namespaces)
        if url is not None:
            values["url"] = set([str(url)])
        entry = self._elem_find(elem, "eac:sourceEntry")
        if entry is not None and entry.text:
            values["title"] = set([str(entry.text)])
        yield ExtEntity("EACSource", self._gen_extid(), values)
