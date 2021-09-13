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
from flask import current_app
from flask import render_template
from flask_login import current_user
from flask_login import login_required

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal_endpoint
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.conversion import clamp
from kadi.lib.conversion import normalize
from kadi.lib.conversion import parse_json_object
from kadi.lib.conversion import strip
from kadi.lib.resources.api import get_selected_resources
from kadi.lib.utils import compact_json
from kadi.lib.web import download_stream
from kadi.lib.web import download_string
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.collections.models import Collection
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.utils import permission_required
from kadi.modules.records.export import get_export_data
from kadi.modules.records.files import (
    download_temporary_file as _download_temporary_file,
)
from kadi.modules.records.files import get_permitted_files
from kadi.modules.records.models import File
from kadi.modules.records.models import Record
from kadi.modules.records.models import TemporaryFile
from kadi.modules.records.previews import get_preview_data
from kadi.modules.records.previews import preview_file as _preview_file
from kadi.modules.records.utils import get_record_links_graph as _get_record_links_graph


@bp.get("/records/<int:id>/export/internal/<export_type>", v=None)
@permission_required("read", "record", "id")
@internal_endpoint
@qparam("preview", default=False, parse=bool)
@qparam("download", default=False, parse=bool)
@qparam("filter", default=lambda: {}, parse=parse_json_object)
def get_record_export_internal(id, export_type, qparams):
    """Export a record in a specific format."""
    record = Record.query.get_active_or_404(id)
    export_types = current_app.config["EXPORT_TYPES"]["record"]

    if export_type not in export_types:
        return json_error_response(404)

    export_filter = {**qparams["filter"], "extras_use_indices": True}

    if export_type == "json":
        return download_string(
            get_export_data(record, export_type, export_filter=export_filter),
            f"{record.identifier}.json",
            as_attachment=qparams["download"],
        )

    if qparams["preview"] or qparams["download"]:
        file_ext = "pdf" if export_type == "pdf" else "png"
        return download_stream(
            get_export_data(record, export_type, export_filter=export_filter),
            f"{record.identifier}.{file_ext}",
            as_attachment=qparams["download"],
        )

    return json_response(
        200,
        body=url_for(
            "api.get_record_export_internal",
            id=record.id,
            export_type=export_type,
            preview=True,
            filter=compact_json(qparams["filter"]),
        ),
    )


@bp.get("/records/<int:id>/records/graph", v=None)
@permission_required("read", "record", "id")
@internal_endpoint
@qparam("depth", default=1, parse=int)
def get_record_links_graph(id, qparams):
    """Get all links of a record for visualizing them in a graph."""
    record = Record.query.get_active_or_404(id)
    depth = clamp(qparams["depth"], 1, 3)

    data = _get_record_links_graph(record, depth)
    return json_response(200, data)


@bp.get("/records/<int:record_id>/files/<uuid:file_id>/preview", v=None)
@permission_required("read", "record", "record_id")
@internal_endpoint
def get_file_preview(record_id, file_id):
    """Get the preview data of a file.

    The actual preview data may either consist of a URL or the preview data itself,
    depending on the preview type. In the first case, a browser may be able to directly
    preview the file using the returned URL.
    """
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        return json_error_response(404)

    preview_data = get_preview_data(file)

    if preview_data is None:
        return json_error_response(404)

    return json_response(200, {"type": preview_data[0], "data": preview_data[1]})


@bp.get("/records/<int:record_id>/files/<uuid:file_id>/preview/file", v=None)
@permission_required("read", "record", "record_id")
@internal_endpoint
def preview_file(record_id, file_id):
    """Preview a file directly in the browser."""
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        return json_error_response(404)

    if (
        file.magic_mimetype
        in [*current_app.config["IMAGE_MIMETYPES"], "application/pdf"]
        and file.size <= current_app.config["PREVIEW_MAX_SIZE"]
    ):
        response = _preview_file(file)

        if response is not None:
            return response

    return json_error_response(404)


@bp.get("/records/<int:record_id>/temporary_files/<uuid:temporary_file_id>", v=None)
@permission_required("read", "record", "record_id")
@internal_endpoint
def download_temporary_file(record_id, temporary_file_id):
    """Download a temporary file."""
    record = Record.query.get_active_or_404(record_id)
    temporary_file = TemporaryFile.query.get_active_or_404(temporary_file_id)

    if record.id != temporary_file.record_id:
        return json_error_response(404)

    response = _download_temporary_file(temporary_file)

    if response is not None:
        return response

    return json_error_response(404)


@bp.get("/records/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=normalize)
@qparam("exclude", multiple=True, parse=int)
@qparam("action", multiple=True)
@qparam("collection", default=None, parse=int)
def select_records(qparams):
    """Search records in dynamic selections.

    Uses :func:`kadi.lib.resources.api.get_selected_resources`.
    """
    exclude = qparams["exclude"]
    collection_id = qparams["collection"]

    # If applicable, exclude records that are already linked to the collection with the
    # given ID.
    if collection_id is not None:
        collection = Collection.query.get_active(collection_id)

        if collection is not None and has_permission(
            current_user, "read", "collection", collection.id
        ):
            record_ids_query = collection.records.filter(
                Record.state == "active"
            ).with_entities(Record.id)
            exclude += [r.id for r in record_ids_query]

    return get_selected_resources(
        Record,
        page=qparams["page"],
        term=qparams["term"],
        exclude=exclude,
        actions=qparams["action"],
    )


@bp.get("/records/types/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=normalize)
def select_record_types(qparams):
    """Search record types in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`. Only the types of
    records the current user has read permission for are returned.
    """
    paginated_record_types = (
        get_permitted_objects(current_user, "read", "record")
        .filter(
            Record.state == "active",
            Record.type.is_not(None),
            Record.type.ilike(f"%{qparams['term']}%"),
        )
        .distinct()
        .order_by(Record.type)
        .with_entities(Record.type)
        .paginate(qparams["page"], 10, False)
    )

    data = {"results": [], "pagination": {"more": paginated_record_types.has_next}}
    for record_type in paginated_record_types.items:
        data["results"].append({"id": record_type[0], "text": record_type[0]})

    return json_response(200, data)


@bp.get("/records/mimetypes/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=strip)
def select_mimetypes(qparams):
    """Search MIME types of record files in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`. Only the MIME
    types of records the current user has read permission for are returned.
    """
    paginated_mimetypes = (
        get_permitted_objects(current_user, "read", "record")
        .join(Record.files)
        .filter(
            Record.state == "active",
            File.state == "active",
            File.mimetype.ilike(f"%{qparams['term']}%"),
        )
        .distinct()
        .order_by(File.mimetype)
        .with_entities(File.mimetype)
        .paginate(qparams["page"], 10, False)
    )

    data = {"results": [], "pagination": {"more": paginated_mimetypes.has_next}}
    for mimetype in paginated_mimetypes.items:
        data["results"].append({"id": mimetype[0], "text": mimetype[0]})

    return json_response(200, data)


@bp.get("/records/files/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=strip)
@qparam("images", default=False, parse=bool)
def select_files(qparams):
    """Search record files in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`. Only the files of
    records the current user has read permission for are returned.
    """
    files_query = get_permitted_files(term=qparams["term"])

    # Restrict the results to previewable, local image files.
    if qparams["images"]:
        files_query = files_query.filter(
            File.storage_type == "local",
            File.magic_mimetype.in_(current_app.config["IMAGE_MIMETYPES"]),
            File.size <= current_app.config["PREVIEW_MAX_SIZE"],
        )

    paginated_files = files_query.order_by(File.name).paginate(
        qparams["page"], 10, False
    )

    data = {"results": [], "pagination": {"more": paginated_files.has_next}}
    for file in paginated_files.items:
        data["results"].append(
            {
                "id": file.id,
                "text": file.name,
                "body": render_template("records/snippets/select_file.html", file=file),
                "view_endpoint": url_for(
                    "records.view_file", record_id=file.record_id, file_id=file.id
                ),
                "preview_endpoint": url_for(
                    "api.preview_file", record_id=file.record_id, file_id=file.id
                ),
            }
        )

    return json_response(200, data)
