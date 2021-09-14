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
"""cubicweb-eac server objects"""

from cubicweb import ValidationError
from cubicweb.predicates import match_user_groups
from cubicweb.server import Service
from cubicweb.dataimport import RQLObjectStore
from cubicweb.dataimport.importer import ExtEntitiesImporter, cwuri2eid

from cubicweb_skos import to_unicode

from cubicweb_eac import dataimport


def init_extid2eid_index(cnx, source):
    """Return the dictionary mapping external id to eid for entities already in the database."""
    # only consider the system source for EAC related entity types
    extid2eid = cwuri2eid(cnx, dataimport.ETYPES_ORDER_HINT, source_eid=source.eid)
    # though concepts may come from any source
    extid2eid.update(cwuri2eid(cnx, ("Concept",)))
    return extid2eid


class EACImportService(Service):
    """Service to import an AuthorityRecord from an EAC XML file."""

    __regid__ = "eac.import"
    __select__ = match_user_groups("managers", "users")

    def call(self, stream, import_log, **kwargs):
        store = RQLObjectStore(self._cw)
        try:
            created, updated, record_eid, not_visited = self.import_eac_stream(
                stream, import_log, store, **kwargs
            )
        except Exception:
            self._cw.rollback()
            raise
        else:
            try:
                self._cw.commit()
            except ValidationError as exc:
                import_log.record_error("validation error: " + to_unicode(exc))
                raise
            else:
                import_log.record_info("%s entities created" % len(created))
                import_log.record_info("%s entities updated" % len(updated))
        msg = self._cw._("element {0} not parsed")
        for tagname, sourceline in not_visited:
            import_log.record_warning(msg.format(tagname, sourceline), line=sourceline)
        return created, updated, record_eid

    def external_entities_generator(self, stream, import_log):
        return dataimport.EACCPFImporter(stream, import_log, self._cw._)

    def import_eac_stream(self, stream, import_log, store, extid2eid=None, **kwargs):
        try:
            return self._import_eac_stream(
                stream, import_log, store, extid2eid=extid2eid, **kwargs
            )
        except Exception as exc:
            import_log.record_fatal(to_unicode(exc))
            raise

    def _import_eac_stream(self, stream, import_log, store, extid2eid=None, **kwargs):
        source = self._cw.repo.system_source
        if extid2eid is None:
            extid2eid = init_extid2eid_index(self._cw, source)
        importer = ExtEntitiesImporter(
            self._cw.vreg.schema,
            store,
            import_log=import_log,
            extid2eid=extid2eid,
            etypes_order_hint=dataimport.ETYPES_ORDER_HINT,
            **kwargs
        )
        generator = self.external_entities_generator(stream, import_log)
        extentities = self.external_entities_stream(
            generator.external_entities(), extid2eid
        )
        importer.import_entities(extentities)
        if generator.record is not None:
            extid = generator.record.extid
            record_eid = importer.extid2eid[extid]
        else:
            record_eid = None
        return importer.created, importer.updated, record_eid, generator.not_visited()

    def external_entities_stream(self, extentities, extid2eid):
        """Extracted method allowing to plug transformation into the external entities generator."""
        extentities = (
            ee
            for ee in extentities
            if not (ee.etype == "ExternalUri" and ee.extid in extid2eid)
        )

        def handle_agent_kind(extentities):
            """Create agent kind when necessary and remove them from the entity stream, allowing to
            set cwuri properly without attempt to update.
            """
            for extentity in extentities:
                if extentity.etype == "AgentKind":
                    assert (
                        extentity.extid in extid2eid
                    ), "unexpected agent kind {}".format(extentity)
                else:
                    yield extentity

        extentities = handle_agent_kind(extentities)
        return extentities
