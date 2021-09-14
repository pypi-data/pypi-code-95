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
"""cubicweb-ctl plugin introducing eac-import command."""

from os.path import basename
from time import time

from cubicweb.toolsutils import Command, underline_title
from cubicweb.cwctl import CWCTL
from cubicweb.utils import admincnx
from cubicweb.dataimport.importer import SimpleImportLog
from cubicweb.web.views.cwsources import REVERSE_SEVERITIES

from cubicweb_eac.sobjects import init_extid2eid_index


class ImportEacData(Command):
    """Import some EAC files.

    <instance>
      identifier of the instance into which the scheme will be imported. Should use the eac cube.

    <filepath>
      path to the EAC files to import.

    """

    arguments = "[options] <instance> <filepath>..."
    name = "eac-import"
    min_args = 2

    def run(self, args):
        print(u"\n%s" % underline_title("Importing EAC files"))
        appid = args[0]
        with admincnx(appid) as cnx:
            eac_import_files(cnx, args[1:])
        cnx.repo.shutdown()


CWCTL.register(ImportEacData)


def eac_import_files(cnx, fpaths, store=None, **kwargs):
    """High-level import function, given an connection to a cubicweb repository and a list of files
    to import.
    """
    start_time = time()
    imported = created = updated = 0
    if store is None:
        store = _store(cnx)
    service = cnx.vreg["services"].select("eac.import", cnx, **kwargs)
    extid2eid = init_extid2eid_index(cnx, cnx.repo.system_source)
    try:
        for fpath in fpaths:
            _created, _updated = eac_import_file(service, store, fpath, extid2eid)
            if _created or _updated:
                imported += 1
                created += len(_created)
                updated += len(_updated)
            store.flush()
            store.commit()
    finally:
        store.finish()

    output_str = (
        "\nImported {imported}/{total} files ({created} entities + "
        "{updated} updates) in {time:.1f} seconds using {store}"
    )
    print(
        output_str.format(
            imported=imported,
            created=created,
            updated=updated,
            total=len(fpaths),
            time=time() - start_time,
            store=store.__class__.__name__,
        )
    )


def eac_import_file(service, store, fpath, extid2eid, raise_on_error=False):
    import_log = MyImportLog(basename(fpath))
    with open(fpath) as stream:
        try:
            created, updated, record_eid, not_visited = service.import_eac_stream(
                stream, import_log, extid2eid=extid2eid, store=store
            )
            return created, updated
        except Exception:
            if raise_on_error:
                raise
            return 0, 0


class MyImportLog(SimpleImportLog):
    def _log(self, severity, msg, path, line):
        if isinstance(msg, str):
            msg = msg.encode("utf8")
        print(
            "[{severity}] {path}:{line}: {msg}".format(
                severity=REVERSE_SEVERITIES[severity],
                path=self.filename,
                line=line or 0,
                msg=msg,
            )
        )


def _store(cnx):
    if cnx.repo.system_source.dbdriver == "postgres":
        from cubicweb.dataimport.stores import MetadataGenerator
        from cubicweb.dataimport.massive_store import MassiveObjectStore

        MetadataGenerator.META_RELATIONS = MetadataGenerator.META_RELATIONS - set(
            ["owned_by", "created_by"]
        )
        metagen = MetadataGenerator(cnx)
        return MassiveObjectStore(cnx, metagen=metagen, eids_seq_range=1000)
    else:
        from cubicweb.dataimport.stores import NoHookRQLObjectStore

        return NoHookRQLObjectStore(cnx)
