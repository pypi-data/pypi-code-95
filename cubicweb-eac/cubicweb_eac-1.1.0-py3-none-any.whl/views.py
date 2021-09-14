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
"""cubicweb-eac views, mostly for import/export of AuthorityRecord from/to EAC.

Using only this cube, UI will be hardly usable to handle the complexity of the EAC model. You'll
find an UI implementation for EAC as part of the `saem_ref`_ cube.

.. _`saem_ref`: https://www.cubicweb.org/project/cubicweb-saem_ref
"""

from functools import partial
import os.path

from cubicweb import tags, _
from cubicweb.view import View
from cubicweb.predicates import (
    is_instance,
    match_user_groups,
    one_line_rset,
    score_entity,
)
from cubicweb.dataimport.importer import HTMLImportLog
from cubicweb.web import (
    action,
    component,
    formfields as ff,
    formwidgets as fw,
    httpcache,
)
from cubicweb.web.views import actions, calendar, cwsources, forms, idownloadable, uicfg

from cubicweb_skos import to_unicode

from cubicweb_eac import dataimport


abaa = uicfg.actionbox_appearsin_addmenu
pvs = uicfg.primaryview_section
pvdc = uicfg.primaryview_display_ctrl
afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs


# Edit / View setup

actions.CopyAction.__select__ &= ~is_instance("AuthorityRecord")

pvdc.tag_subject_of(("AuthorityRecord", "agent_kind", "*"), {"vid": "text"})

for etype, attr in (
    ("AuthorityRecord", "record_id"),
    ("AuthorityRecord", "isni"),
    ("AgentPlace", "name"),
    ("AgentPlace", "role"),
    ("Activity", "type"),
    ("Mandate", "term"),
    ("LegalStatus", "term"),
    ("EACResourceRelation", "agent_role"),
    ("EACResourceRelation", "resource_role"),
    ("EACSource", "title"),
    ("EACSource", "url"),
):
    affk.set_field_kwargs(etype, attr, widget=fw.TextInput({"size": 80}))


affk.set_field_kwargs("NameEntry", "form_variant", value=u"authorized")


for etype, attrs in [
    ("AgentFunction", ("name", "description")),
    ("AgentPlace", ("name", "role")),
    ("Mandate", ("term", "description")),
    ("LegalStatus", ("term", "description")),
    ("Occupation", ("term", "description")),
]:
    affk.set_fields_order(etype, ("vocabulary_source",) + attrs)
    if attrs[-1] == "description":
        affk.tag_attribute(
            (etype, "description"),
            {
                "help": _(
                    "let this unspecified to see the definition of the "
                    "related concept if a vocabulary is specifed"
                )
            },
        )

afs.tag_object_of(("*", "vocabulary_source", "*"), "main", "hidden")
afs.tag_subject_of(("*", "vocabulary_source", "*"), "main", "attributes")
afs.tag_object_of(("*", "equivalent_concept", "*"), "main", "hidden")

pvs.tag_subject_of(("AuthorityRecord", "postal_address", "*"), "hidden")

# Hide relation to the record for these entity types edition form.
for etype, rtype in (
    ("AgentPlace", "place_agent"),
    ("AgentFunction", "function_agent"),
    ("LegalStatus", "legal_status_agent"),
    ("Mandate", "mandate_agent"),
    ("History", "history_agent"),
    ("Structure", "structure_agent"),
    ("Occupation", "occupation_agent"),
    ("GeneralContext", "general_context_of"),
    ("EACSource", "source_agent"),
    ("EACResourceRelation", "resource_relation_agent"),
):
    afs.tag_subject_of((etype, rtype, "*"), "main", "hidden")

# TextArea for all description attributes where <p> is allowed.
for etype in (
    "AgentFunction",
    "Mandate",
    "Occupation",
    "Structure",
):
    affk.set_field_kwargs(etype, "description", widget=fw.TextArea())

# Citation
pvdc.tag_attribute(("Citation", "uri"), {"vid": "urlattr"})
# Generic rules for all entity types having an `has_citation` relationship.
afs.tag_subject_of(("*", "has_citation", "*"), "main", "inlined")
afs.tag_object_of(("*", "has_citation", "*"), "main", "hidden")
pvs.tag_object_of(("*", "has_citation", "Citation"), "hidden")

# AgentPlace
afs.tag_subject_of(("AgentPlace", "place_address", "PostalAddress"), "main", "inlined")
afs.tag_object_of(("AgentPlace", "place_address", "PostalAddress"), "main", "hidden")

# AgentFunction
affk.set_field_kwargs("AgentFunction", "name", widget=fw.TextInput({"size": 80}))


afs.tag_object_of(("*", "name_entry_for", "AuthorityRecord"), "main", "inlined")
afs.tag_subject_of(("NameEntry", "name_entry_for", "*"), "main", "hidden")

affk.set_fields_order("AuthorityRecord", [("name_entry_for", "object")])
pvdc.set_fields_order("AuthorityRecord", [("name_entry_for", "object")])
affk.set_field_kwargs("NameEntry", "parts", widget=fw.TextInput({"size": 80}))

affk.set_field_kwargs("EACOtherRecordId", "value", widget=fw.TextInput({"size": 80}))
affk.set_field_kwargs(
    "EACOtherRecordId", "local_type", widget=fw.TextInput({"size": 80})
)
afs.tag_subject_of(
    ("EACOtherRecordId", "eac_other_record_id_of", "*"), "main", "hidden"
)

pvdc.tag_attribute(("EACSource", "url"), {"vid": "urlattr"})


def unrelated_authorityrecord(rtype, form, field, **kwargs):
    """Choices function returning AuthorityRecord choices.

    Choices values are unrelated through `rtype` to edited entity thus
    filtering out possible ExternalURI targets. It also account for __linkto
    info to build a restricted choice when needed.
    """
    try:
        linkto = form.linked_to[rtype, "subject"][0]
    except (KeyError, IndexError):
        rset = form.edited_entity.unrelated(rtype, targettype="AuthorityRecord")
        return [(x.dc_title(), str(x.eid)) for x in rset.entities()]
    else:
        entity = form._cw.entity_from_eid(linkto)
        return [(entity.dc_title(), str(entity.eid))]


# Set fields order for authority records relations (autoform and primary view)
for etype, from_rdef, to_rdef in (
    ("AssociationRelation", "association_from", "association_to"),
    ("ChronologicalRelation", "chronological_predecessor", "chronological_successor"),
    ("HierarchicalRelation", "hierarchical_parent", "hierarchical_child"),
):
    affk.set_fields_order(
        etype, ("description", "start_date", "end_date", from_rdef, to_rdef)
    )
    for rtype in (from_rdef, to_rdef):
        affk.tag_subject_of(
            (etype, rtype, "*"), {"choices": partial(unrelated_authorityrecord, rtype)}
        )

    pvdc.set_fields_order(
        etype, ("description", "start_date", "end_date", from_rdef, to_rdef)
    )

# By default don't put anything in the 'add' submenu nor in the generic relation, expecting custom
# views to be implemented as in the saem_ref cube
abaa.tag_object_of(("*", "name_entry_for", "AuthorityRecord"), False)
for rtype in (
    "eac_other_record_id_of",
    "place_agent",
    "function_agent",
    "mandate_agent",
    "occupation_agent",
    "general_context_of",
    "legal_status_agent",
    "history_agent",
    "structure_agent",
    "source_agent",
    "resource_relation_agent",
    "association_from",
    "association_to",
    "chronological_predecessor",
    "chronological_successor",
    "hierarchical_parent",
    "hierarchical_child",
):
    abaa.tag_object_of(("*", rtype, "AuthorityRecord"), False)
    afs.tag_object_of(("*", rtype, "AuthorityRecord"), "main", "hidden")
abaa.tag_subject_of(("*", "has_citation", "*"), False)


class XMLWrapComponent(component.EntityCtxComponent):
    """CtxComponent to display xml_wrap of entities."""

    __select__ = component.EntityCtxComponent.__select__ & score_entity(
        lambda x: getattr(x, "xml_wrap", None)
    )
    __regid__ = "eac.xml_wrap"
    context = "navcontentbottom"
    title = _("xml_wrap")

    def render_body(self, w):
        sourcemt, targetmt = "text/xml", "text/html"
        data = self.entity.xml_wrap
        w(self.entity._cw_mtc_transform(data.getvalue(), sourcemt, targetmt, "utf-8"))


class AuthorityRecordICalendarableAdapter(calendar.ICalendarableAdapter):
    """ICalendarable adapter for AuthorityRecord entity type."""

    __select__ = calendar.ICalendarableAdapter.__select__ & is_instance(
        "AuthorityRecord"
    )

    @property
    def start(self):
        return self.entity.start_date

    @property
    def stop(self):
        return self.entity.end_date


# Import


class EACImportMixin(object):
    __regid__ = "eac.import"
    __select__ = match_user_groups("managers", "users")


class EACImportForm(EACImportMixin, forms.FieldsForm):
    """File import form for EAC-CPF"""

    filefield = ff.FileField(name="file", label=_("EAC-CPF file"), required=True)
    form_buttons = [fw.SubmitButton(label=_("do_import"))]

    @property
    def action(self):
        return self._cw.build_url(vid=self.__regid__)


class EACImportView(EACImportMixin, View):
    """EAC-CPF import controller"""

    def call(self):
        self.w(tags.h1(self._cw._("Importing an AuthorityRecord from a EAC-CPF file")))
        form = self._cw.vreg["forms"].select(self.__regid__, self._cw)
        if form.posting:
            posted = form.process_posted()
            stream = posted["file"]
            import_log = HTMLImportLog(os.path.basename(stream.filename))
            try:
                _, _, eid = self._cw.cnx.call_service(
                    self.__regid__,
                    stream=stream,
                    import_log=import_log,
                    **self.service_kwargs(posted)
                )
            except dataimport.InvalidXML as exc:
                msg = self._cw._("Invalid XML file")
                self.exception("error while importing %s", stream.filename)
                mtype = "danger"
                import_log.record_fatal(
                    self._cw._("xml syntax error: ") + to_unicode(exc)
                )
                self._cw.status_out = 400
            except dataimport.MissingTag as exc:
                if exc.tag_parent:
                    err = self._cw._(
                        "Missing tag %(tag)s within element %(parent)s in XML file"
                    )
                    params = {"tag": exc.tag, "parent": exc.tag_parent}
                else:
                    err = self._cw._("Missing tag %(tag)s in XML file")
                    params = {"tag": exc.tag}
                msg = err % params
                self.exception("error while importing %s", stream.filename)
                mtype = "danger"
                import_log.record_fatal(msg)
                self._cw.status_out = 400
            except Exception:  # pylint: disable=broad-except
                msg = self._cw._("EAC import failed")
                self.exception("error while importing %s", stream.filename)
                mtype = "danger"
                self._cw.status_out = 500
            else:
                record = self._cw.find("AuthorityRecord", eid=eid).one()
                msg = self._cw._("EAC-CPF import completed: %s") % record.view(
                    "oneline"
                )
                mtype = "success"
            self.w(tags.div(msg, klass="alert alert-%s" % mtype))
            if import_log.logs:
                self._cw.view(
                    "cw.log.table",
                    pyvalue=cwsources.log_to_table(self._cw, u"".join(import_log.logs)),
                    default_level="Warning",
                    w=self.w,
                )
        else:
            form.render(w=self.w)

    def service_kwargs(self, posted):
        """Subclass access point to provide extra arguments to the service (e.g. saem_ref cube)."""
        return {}


# Export


class EACExportAction(action.Action):
    __regid__ = "eac.export"
    __select__ = (
        action.Action.__select__ & one_line_rset() & is_instance("AuthorityRecord")
    )

    title = _("EAC export")
    category = "moreactions"

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.__regid__)


class EACDownloadView(idownloadable.DownloadView):
    """EAC download view"""

    __regid__ = "eac.export"
    __select__ = one_line_rset() & is_instance("AuthorityRecord")

    http_cache_manager = httpcache.NoHTTPCacheManager
    adapter_id = "EAC-CPF"

    def set_request_content_type(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to(self.adapter_id)
        self._cw.set_content_type(
            adapter.content_type,
            filename=adapter.file_name,
            encoding=adapter.encoding,
            disposition="attachment",
        )

    def call(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to(self.adapter_id)
        self.w(adapter.dump())
