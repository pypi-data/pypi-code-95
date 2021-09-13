# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

from flask import current_app
from flask_login import current_user
from flask_login import login_required

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import check_access_token_scopes
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.api.core import scopes_required
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.api.utils import status
from kadi.lib.conversion import lower
from kadi.lib.conversion import normalize
from kadi.lib.conversion import parse_boolean_string
from kadi.lib.conversion import parse_json_object
from kadi.lib.conversion import strip
from kadi.lib.resources.api import get_resource_group_roles
from kadi.lib.resources.api import get_resource_user_roles
from kadi.lib.resources.utils import get_linked_resources
from kadi.lib.revisions.models import Revision
from kadi.lib.revisions.schemas import ObjectRevisionSchema
from kadi.lib.tasks.models import Task
from kadi.lib.utils import compact_json
from kadi.lib.web import download_stream
from kadi.lib.web import download_string
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.collections.models import Collection
from kadi.modules.collections.schemas import CollectionSchema
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.utils import permission_required
from kadi.modules.records.core import search_records
from kadi.modules.records.export import get_export_data
from kadi.modules.records.files import download_file as _download_file
from kadi.modules.records.models import File
from kadi.modules.records.models import Record
from kadi.modules.records.models import RecordLink
from kadi.modules.records.models import Upload
from kadi.modules.records.schemas import FileSchema
from kadi.modules.records.schemas import RecordLinkSchema
from kadi.modules.records.schemas import RecordSchema
from kadi.modules.records.schemas import UploadSchema


def _parse_extra_search_queries(extras_str):
    try:
        extras = json.loads(extras_str)
        extras = extras if isinstance(extras, list) else []
    except:
        return []

    for extra in extras:
        if not isinstance(extra, dict):
            return []

    return extras


@bp.get("/records")
@login_required
@scopes_required("record.read")
@paginated(page_max=100)
@qparam("query", parse=strip, description="The search query.")
@qparam(
    "extras",
    default=lambda: [],
    parse=_parse_extra_search_queries,
    description="An URL-encoded array of JSON objects to specify the search within the"
    " extra metadata of a record.",
)
@qparam("sort", default="_score", description="The order of the search results.")
@qparam(
    "collection",
    multiple=True,
    parse=int,
    description="Collection IDs to filter the records with.",
)
@qparam(
    "child_collections",
    default=False,
    parse=parse_boolean_string,
    description="Flag indicating whether the children of the filtered collections"
    " should be included.",
)
@qparam(
    "tag",
    multiple=True,
    parse=[lower, normalize],
    description="Tags to filter the records with.",
)
@qparam(
    "type",
    multiple=True,
    parse=[lower, normalize],
    description="Record types to filter the records with.",
)
@qparam(
    "mimetype",
    multiple=True,
    parse=[lower, strip],
    description="MIME types to filter the records with.",
)
@qparam(
    "hide_public",
    default=False,
    parse=parse_boolean_string,
    description="Flag indicating whether public records should be excluded in the"
    " results.",
)
@status(200, "Return a paginated list of records.")
def get_records(page, per_page, qparams):
    """Get all records or search and filter for specific records.

    See :func:`kadi.modules.records.core.search_records` for a more detailed description
    of some of the query parameters (in Python syntax).
    """
    if qparams["collection"]:
        collection_ids_query = (
            get_permitted_objects(current_user, "read", "collection")
            .filter(
                Collection.state == "active", Collection.id.in_(qparams["collection"])
            )
            .with_entities(Collection.id)
        )
        qparams["collection"] = [c.id for c in collection_ids_query]

    records, total_records = search_records(
        qparams["query"],
        extras=qparams["extras"],
        sort=qparams["sort"],
        collections=qparams["collection"],
        child_collections=qparams["child_collections"],
        tags=qparams["tag"],
        record_types=qparams["type"],
        mimetypes=qparams["mimetype"],
        hide_public=qparams["hide_public"],
        page=page,
        per_page=per_page,
    )

    data = {
        "items": RecordSchema(many=True).dump(records),
        "_actions": {"new_record": url_for("api.new_record")},
        **create_pagination_data(
            total_records,
            page,
            per_page,
            "api.get_records",
            **{**qparams, "extras": compact_json(qparams["extras"])},
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:id>")
@permission_required("read", "record", "id")
@scopes_required("record.read")
@status(200, "Return the record.")
def get_record(id):
    """Get the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)
    return json_response(200, RecordSchema().dump(record))


@bp.get("/records/identifier/<identifier:identifier>")
@login_required
@scopes_required("record.read")
@status(200, "Return the record.")
def get_record_by_identifier(identifier):
    """Get the record specified by the given *identifier*."""
    record = Record.query.filter_by(
        identifier=identifier, state="active"
    ).first_or_404()

    if not has_permission(current_user, "read", "record", object_id=record.id):
        return json_error_response(403)

    return json_response(200, RecordSchema().dump(record))


@bp.get("/records/<int:id>/records")
@permission_required("read", "record", "id")
@scopes_required("record.read")
@paginated
@qparam(
    "direction",
    default="to",
    description="The direction of the record links. ``to`` will return (outgoing)"
    " records linked to from the current record, while ``from`` will return (incoming)"
    " records that link to the current record.",
)
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the record links by their link name or the linked"
    " records by their title or identifier.",
)
@qparam(
    "action",
    multiple=True,
    description="Further actions the current user needs permission to perform in the"
    " linked records.",
)
@status(
    200,
    "Return a paginated list of record links, sorted by creation date in descending"
    " order.",
)
def get_record_links(id, page, per_page, qparams):
    """Get the record links of the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)

    record_ids_query = (
        get_permitted_objects(current_user, "read", "record")
        .filter(Record.state == "active")
        .with_entities(Record.id)
    )

    for action in set(qparams["action"]):
        record_ids_query = (
            get_permitted_objects(current_user, action, "record")
            .with_entities(Record.id)
            .intersect(record_ids_query)
        )

    # Records linked to from the current record.
    if qparams["direction"] == "to":
        schema = RecordLinkSchema(many=True, exclude=["record_from"])
        record_links = record.links_to.join(RecordLink.record_to).filter(
            RecordLink.record_to_id.in_(record_ids_query)
        )
    # Records that link to the current record.
    else:
        schema = RecordLinkSchema(many=True, exclude=["record_to"])
        record_links = record.linked_from.join(RecordLink.record_from).filter(
            RecordLink.record_from_id.in_(record_ids_query)
        )

    record_links = (
        record_links.filter(
            db.or_(
                RecordLink.name.ilike(f"%{qparams['filter']}%"),
                Record.title.ilike(f"%{qparams['filter']}%"),
                Record.identifier.ilike(f"%{qparams['filter']}%"),
            ),
        )
        .order_by(RecordLink.created_at.desc())
        .paginate(page, per_page, False)
    )

    data = {
        "items": schema.dump(record_links.items),
        **create_pagination_data(
            record_links.total,
            page,
            per_page,
            "api.get_record_links",
            id=record.id,
            **qparams,
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:record_id>/records/<int:link_id>")
@permission_required("read", "record", "record_id")
@scopes_required("record.read")
@status(200, "Return the record link.")
def get_record_link(record_id, link_id):
    """Get a record link.

    Will return the (outgoing) record link specified by the given *link_id* from the
    record specified by the given *record_id*.
    """
    record = Record.query.get_active_or_404(record_id)
    record_link = RecordLink.query.get_or_404(link_id)

    if record.id != record_link.record_from_id:
        return json_error_response(404)

    if not has_permission(
        current_user, "read", "record", object_id=record_link.record_to_id
    ):
        return json_error_response(403)

    return json_response(
        200, RecordLinkSchema(exclude=["record_from"]).dump(record_link)
    )


@bp.get("/records/<int:id>/collections")
@permission_required("read", "record", "id")
@scopes_required("record.read", "collection.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the collections by their title or identifier.",
)
@qparam(
    "action",
    multiple=True,
    description="Further actions the current user needs permission to perform in the"
    " linked collections.",
)
@status(
    200,
    "Return a paginated list of collections, sorted by last modification date in"
    " descending order.",
)
def get_record_collections(id, page, per_page, qparams):
    """Get the collections the record specified by the given *id* is part of."""
    record = Record.query.get_active_or_404(id)

    paginated_collections = (
        get_linked_resources(Collection, record.collections, actions=qparams["action"])
        .filter(
            db.or_(
                Collection.title.ilike(f"%{qparams['filter']}%"),
                Collection.identifier.ilike(f"%{qparams['filter']}%"),
            ),
        )
        .order_by(Collection.last_modified.desc())
        .paginate(page, per_page, False)
    )
    data = {
        "items": CollectionSchema(many=True, linked_record=record).dump(
            paginated_collections.items
        ),
        **create_pagination_data(
            paginated_collections.total,
            page,
            per_page,
            "api.get_record_collections",
            id=record.id,
            **qparams,
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:id>/roles/users")
@permission_required("read", "record", "id")
@scopes_required("record.read", "user.read")
@paginated
@qparam(
    "filter",
    parse=strip,
    description="A query to filter the users by their username or display name.",
)
@qparam("exclude", multiple=True, parse=int, description="User IDs to exclude.")
@status(
    200,
    "Return a paginated list of user roles, sorted by role name and then by user ID in"
    " ascending order. The creator will always be listed first.",
)
def get_record_user_roles(id, page, per_page, qparams):
    """Get the user roles of the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)

    items, total = get_resource_user_roles(
        record,
        page=page,
        per_page=per_page,
        filter_term=qparams["filter"],
        exclude=qparams["exclude"],
    )
    data = {
        "items": items,
        **create_pagination_data(
            total, page, per_page, "api.get_record_user_roles", id=record.id
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:id>/roles/groups")
@permission_required("read", "record", "id")
@scopes_required("record.read", "group.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the groups by their title or identifier.",
)
@status(
    200,
    "Return a paginated list of group roles, sorted by role name and then by group ID"
    " in ascending order.",
)
def get_record_group_roles(id, page, per_page, qparams):
    """Get the group roles of the record specified by the given *id*.

    If a user can manage permissions in this record, all group roles are returned.
    However, groups that a user can normally not read include only a limited subset of
    attributes.
    """
    record = Record.query.get_active_or_404(id)

    items, total = get_resource_group_roles(
        record, page=page, per_page=per_page, filter_term=qparams["filter"]
    )
    data = {
        "items": items,
        **create_pagination_data(
            total, page, per_page, "api.get_record_group_roles", id=record.id
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:id>/revisions")
@permission_required("read", "record", "id")
@scopes_required("record.read")
@paginated
@status(
    200,
    "Return a paginated list of record revisions, sorted by revision timestamp in"
    " descending order.",
)
def get_record_revisions(id, page, per_page):
    """Get the record revisions of the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)
    paginated_revisions = record.ordered_revisions.paginate(page, per_page, False)

    schema = ObjectRevisionSchema(
        many=True,
        schema=RecordSchema,
        api_endpoint="api.get_record_revision",
        view_endpoint="records.view_record_revision",
        endpoint_args={"record_id": record.id},
    )

    data = {
        "items": schema.dump(paginated_revisions.items),
        **create_pagination_data(
            paginated_revisions.total,
            page,
            per_page,
            "api.get_record_revisions",
            id=record.id,
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:record_id>/revisions/<int:revision_id>")
@permission_required("read", "record", "record_id")
@scopes_required("record.read")
@status(200, "Return the record revision.")
def get_record_revision(record_id, revision_id):
    """Get a record revision.

    Will return the record revision specified by the given *revision_id* of the record
    specified by the given *record_id*.
    """
    record = Record.query.get_active_or_404(record_id)
    revision = Record.revision_class.query.get_or_404(revision_id)

    if record.id != revision.record_id:
        return json_error_response(404)

    schema = ObjectRevisionSchema(
        schema=RecordSchema,
        api_endpoint="api.get_record_revision",
        view_endpoint="records.view_record_revision",
        endpoint_args={"record_id": record.id},
    )

    return json_response(200, schema.dump(revision))


@bp.get("/records/<int:id>/export/<export_type>")
@permission_required("read", "record", "id")
@scopes_required("record.read")
@qparam(
    "filter",
    default=lambda: {},
    parse=parse_json_object,
    description="An URL-encoded JSON object to specify various filters to exclude"
    " certain information from the returned export data. See the ``export_filter``"
    " parameter in :func:`kadi.modules.records.export.get_export_data` for a more"
    " detailed description (in Python syntax).",
)
@status(200, "Return the exported record data.")
def get_record_export(id, export_type, qparams):
    """Export the record specified by the given *id* using a specific *export_type*.

    Currently ``json``, ``pdf`` and ``qr`` are supported as export types.
    """
    record = Record.query.get_active_or_404(id)
    export_types = current_app.config["EXPORT_TYPES"]["record"]

    if export_type not in export_types:
        return json_error_response(404)

    export_filter = qparams["filter"]

    # Always exclude certain information if the access token scopes are insufficient.
    if not check_access_token_scopes("user.read"):
        export_filter["user"] = True
    if not check_access_token_scopes("collection.read"):
        export_filter["collections"] = True

    data = get_export_data(record, export_type, export_filter=export_filter)

    if export_type == "json":
        return download_string(data, f"{record.identifier}.json")

    file_ext = "pdf" if export_type == "pdf" else "png"
    return download_stream(data, f"{record.identifier}.{file_ext}")


@bp.get("/records/<int:id>/files")
@permission_required("read", "record", "id")
@scopes_required("record.read")
@paginated
@qparam("filter", parse=normalize, description="A query to filter the files by name.")
@status(
    200,
    "Return a paginated list of files, sorted by last modification date in descending"
    " order.",
)
def get_files(id, page, per_page, qparams):
    """Get the files of the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)

    paginated_files = (
        record.active_files.filter(File.name.ilike(f"%{qparams['filter']}%"))
        .order_by(File.last_modified.desc())
        .paginate(page, per_page, False)
    )

    data = {
        "items": FileSchema(many=True).dump(paginated_files.items),
        "_actions": {"new_upload": url_for("api.new_upload", id=record.id)},
        **create_pagination_data(
            paginated_files.total,
            page,
            per_page,
            "api.get_files",
            id=record.id,
            **qparams,
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:record_id>/files/<uuid:file_id>")
@permission_required("read", "record", "record_id")
@scopes_required("record.read")
@status(200, "Return the file.")
def get_file(record_id, file_id):
    """Get a file of a record.

    Will return the file specified by the given *file_id* of the record specified by the
    given *record_id*.
    """
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        return json_error_response(404)

    return json_response(200, FileSchema().dump(file))


@bp.get("/records/<int:record_id>/files/name/<path:filename>")
@permission_required("read", "record", "record_id")
@scopes_required("record.read")
@status(200, "Return the file.")
def get_file_by_name(record_id, filename):
    """Get a file of a record by its name.

    Will return the file specified by the given *filename* of the record specified by
    the given *record_id*.
    """
    record = Record.query.get_active_or_404(record_id)
    file = record.files.filter(
        File.name == filename, File.state == "active"
    ).first_or_404()

    return json_response(200, FileSchema().dump(file))


@bp.get("/records/<int:record_id>/files/<uuid:file_id>/download")
@permission_required("read", "record", "record_id")
@scopes_required("record.read")
@status(200, "Return the file as attachment.")
def download_file(record_id, file_id):
    """Download a file.

    Will return the file specified by the given *file_id* of the record specified by the
    given *record_id* as attachment.
    """
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        return json_error_response(404)

    response = _download_file(file)

    if response is not None:
        return response

    return json_error_response(404)


@bp.get("/records/<int:id>/files/revisions")
@permission_required("read", "record", "id")
@scopes_required("record.read")
@paginated
@status(
    200,
    "Return a paginated list of file revisions, sorted by revision timestamp in"
    " descending order.",
)
def get_file_revisions(id, page, per_page):
    """Get the file revisions of the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)

    paginated_revisions = (
        File.revision_class.query.join(File)
        .join(Revision)
        .filter(File.record_id == record.id)
        .order_by(Revision.timestamp.desc())
        .paginate(page, per_page, False)
    )

    schema = ObjectRevisionSchema(
        many=True,
        schema=FileSchema,
        api_endpoint="api.get_file_revision",
        view_endpoint="records.view_file_revision",
        endpoint_args={"record_id": record.id},
    )

    data = {
        "items": schema.dump(paginated_revisions.items),
        **create_pagination_data(
            paginated_revisions.total,
            page,
            per_page,
            "api.get_file_revisions",
            id=record.id,
        ),
    }

    return json_response(200, data)


@bp.get("/records/<int:record_id>/files/revisions/<int:revision_id>")
@permission_required("read", "record", "record_id")
@scopes_required("record.read")
@status(200, "Return the file revision.")
def get_file_revision(record_id, revision_id):
    """Get a file revision.

    Will return the file revision specified by the given *revision_id* of the record
    specified by the given *record_id*.
    """
    record = Record.query.get_active_or_404(record_id)
    revision = File.revision_class.query.get_or_404(revision_id)

    if record.id != revision.file.record_id:
        return json_error_response(404)

    view_file_url = None
    file = File.query.get(revision.file.id)

    if file.state == "active":
        view_file_url = url_for(
            "records.view_file", record_id=record.id, file_id=file.id
        )

    schema = ObjectRevisionSchema(
        schema=FileSchema,
        api_endpoint="api.get_file_revision",
        view_endpoint="records.view_file_revision",
        endpoint_args={"record_id": record.id},
        view_object_url=view_file_url,
    )

    return json_response(200, schema.dump(revision))


@bp.get("/records/<int:id>/uploads")
@permission_required("update", "record", "id")
@scopes_required("record.update")
@status(
    200,
    "Return the uploads, sorted by creation date in ascending order. Additionally, the"
    " required size for uploading file chunks is returned as the ``_meta.chunk_size``"
    " property.",
)
def get_uploads(id):
    """Get all uploads of the record specified by the given *id*.

    Only uploads owned by the current user will be returned.
    """
    record = Record.query.get_active_or_404(id)
    uploads = current_user.uploads.filter(
        Upload.record_id == record.id, Upload.state != "inactive"
    ).order_by(Upload.created_at)

    data = {
        "items": UploadSchema(many=True).dump(uploads),
        "_actions": {"new_upload": url_for("api.new_upload", id=record.id)},
        "_meta": {"chunk_size": current_app.config["UPLOAD_CHUNK_SIZE"]},
    }

    return json_response(200, data)


@bp.get("/records/<int:record_id>/uploads/<uuid:upload_id>")
@permission_required("update", "record", "record_id")
@scopes_required("record.update")
@status(
    200,
    "Return the upload and additional metadata in the ``_meta`` property, depending on"
    " the state of the upload.",
)
def get_upload_status(record_id, upload_id):
    """Get the status of an upload.

    Will return the status of the upload specified by the given *upload_id* of the
    record specified by the given *record_id*. Only the status of uploads owned by the
    current user can be queried.
    """
    record = Record.query.get_active_or_404(record_id)
    upload = Upload.query.get_or_404(upload_id)

    if record.id != upload.record_id or upload.creator != current_user:
        return json_error_response(404)

    data = UploadSchema().dump(upload)

    if upload.state != "active":
        task = Task.query.filter(
            Task.name == "kadi.records.merge_chunks",
            Task.arguments["args"][0].astext == str(upload.id),
            Task.state != "revoked",
        ).first()

        # If no task exists, it was either revoked or the upload never got finished.
        if task is None:
            return json_error_response(404)

        if task.state in ["pending", "running"]:
            data["_meta"] = {"progress": task.progress}
        elif task.state == "failure":
            data["_meta"] = {"error": task.result["error"]}
        elif task.state == "success":
            file = File.query.get(task.result["file"])
            data["_meta"] = {"file": FileSchema().dump(file)}

    return json_response(200, data)
