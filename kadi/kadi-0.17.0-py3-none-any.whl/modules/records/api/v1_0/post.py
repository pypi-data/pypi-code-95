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
from flask_login import current_user
from flask_login import login_required

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.api.core import scopes_required
from kadi.lib.api.utils import reqschema
from kadi.lib.api.utils import status
from kadi.lib.exceptions import KadiPermissionError
from kadi.lib.resources.api import add_link
from kadi.lib.resources.api import add_role
from kadi.modules.accounts.models import User
from kadi.modules.collections.models import Collection
from kadi.modules.collections.schemas import CollectionSchema
from kadi.modules.groups.models import Group
from kadi.modules.permissions.schemas import GroupRoleSchema
from kadi.modules.permissions.schemas import UserRoleSchema
from kadi.modules.permissions.utils import permission_required
from kadi.modules.records.api.utils import check_max_upload_size
from kadi.modules.records.api.utils import check_upload_user_quota
from kadi.modules.records.core import create_record
from kadi.modules.records.core import link_records
from kadi.modules.records.core import restore_record as _restore_record
from kadi.modules.records.models import Chunk
from kadi.modules.records.models import File
from kadi.modules.records.models import Record
from kadi.modules.records.models import Upload
from kadi.modules.records.schemas import FileSchema
from kadi.modules.records.schemas import RecordLinkSchema
from kadi.modules.records.schemas import RecordSchema
from kadi.modules.records.schemas import UploadSchema
from kadi.modules.records.tasks import start_merge_chunks_task
from kadi.modules.records.tasks import start_purge_record_task


@bp.post("/records")
@permission_required("create", "record", None)
@scopes_required("record.create")
@reqschema(RecordSchema(exclude=["id"]), description="The metadata of the new record.")
@status(201, "Return the new record.")
@status(409, "A conflict occured while trying to create the record.")
def new_record(schema):
    """Create a new record."""
    record = create_record(**schema.load_or_400())

    if not record:
        return json_error_response(409, description="Error creating record.")

    return json_response(201, RecordSchema().dump(record))


@bp.post("/records/<int:id>/records")
@permission_required("link", "record", "id")
@scopes_required("record.link")
@reqschema(
    RecordLinkSchema(only=["record_to.id", "name"]),
    description="The metadata of the new record link.",
)
@status(201, "Return the new record link.")
@status(409, "When trying to link the record with itself.")
def add_record_link(id, schema):
    """Create a new record link.

    Will create a new (outgoing) record link from the record specified by the given
    *id*.
    """
    record = Record.query.get_active_or_404(id)
    data = schema.load_or_400()
    linked_record = Record.query.get_active_or_404(data["record_to"]["id"])

    try:
        record_link = link_records(data["name"], record, linked_record)
    except KadiPermissionError as e:
        return json_error_response(403, str(e))

    if record_link is None:
        return json_error_response(409, description="Cannot link record with itself.")

    db.session.commit()
    return json_response(
        201, RecordLinkSchema(exclude=["record_from"]).dump(record_link)
    )


@bp.post("/records/<int:id>/collections")
@permission_required("link", "record", "id")
@scopes_required("record.link")
@reqschema(
    CollectionSchema(only=["id"]), description="The collection to add the record to."
)
@status(201, "Record successfully added to collection.")
@status(409, "The link already exists.")
def add_record_collection(id, schema):
    """Add the record specified by the given *id* to a collection."""
    record = Record.query.get_active_or_404(id)
    collection = Collection.query.get_active_or_404(schema.load_or_400()["id"])

    return add_link(record.collections, collection)


@bp.post("/records/<int:id>/roles/users")
@permission_required("permissions", "record", "id")
@scopes_required("record.permissions")
@reqschema(
    UserRoleSchema(only=["user.id", "role.name"]),
    description="The user and corresponding role to add.",
)
@status(201, "User role successfully added to record.")
@status(409, "A role for that user already exists.")
def add_record_user_role(id, schema):
    """Add a user role to the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)
    data = schema.load_or_400()
    user = User.query.get_active_or_404(data["user"]["id"])

    return add_role(user, record, data["role"]["name"])


@bp.post("/records/<int:id>/roles/groups")
@permission_required("permissions", "record", "id")
@scopes_required("record.permissions")
@reqschema(
    GroupRoleSchema(only=["group.id", "role.name"]),
    description="The group and corresponding role to add.",
)
@status(201, "Group role successfully added to record.")
@status(409, "A role for that group already exists.")
def add_record_group_role(id, schema):
    """Add a group role to the record specified by the given *id*."""
    record = Record.query.get_active_or_404(id)
    data = schema.load_or_400()
    group = Group.query.get_active_or_404(data["group"]["id"])

    return add_role(group, record, data["role"]["name"])


@bp.post("/records/<int:id>/uploads")
@permission_required("update", "record", "id")
@scopes_required("record.update")
@reqschema(UploadSchema(), description="The metadata of the new upload.")
@status(
    201,
    "Return the new upload. Additionally, the required size for uploading file chunks"
    " is returned as the ``_meta.chunk_size`` property.",
)
@status(
    409,
    "A file with the name of the upload already exists. The file will be returned as"
    " part of the error response as the ``file`` property.",
)
@status(413, "An upload quota was exceeded.")
def new_upload(id, schema):
    """Initiate a new upload in the record specified by the given *id*.

    Once the new upload is initiated, the actual file chunks can be uploaded by sending
    one or more *PUT* requests to the endpoint specified in the
    ``_actions.upload_chunk`` property of the upload.
    """
    record = Record.query.get_active_or_404(id)
    data = schema.load_or_400()

    file = record.active_files.filter(File.name == data["name"]).first()
    if file is not None:
        return json_error_response(
            409,
            description="A file with that name already exists.",
            file=FileSchema().dump(file),
        )

    response = check_max_upload_size(data["size"])
    if response is not None:
        return response

    response = check_upload_user_quota(additional_size=data["size"])
    if response is not None:
        return response

    upload = Upload.create(creator=current_user, record=record, **data)
    db.session.commit()

    data = {
        **UploadSchema().dump(upload),
        "_meta": {"chunk_size": current_app.config["UPLOAD_CHUNK_SIZE"]},
    }

    return json_response(201, data)


@bp.post("/records/<int:record_id>/uploads/<uuid:upload_id>")
@permission_required("update", "record", "record_id")
@scopes_required("record.update")
@status(202, "The upload processing task was started successfully.")
@status(413, "An upload quota was exceeded.")
@status(
    503,
    "The upload processing task could not be started. The upload will remain active in"
    " this case.",
)
def finish_upload(record_id, upload_id):
    """Finish an upload.

    Will finish the upload specified by the given *upload_id* in the record specified by
    the given *record_id*. A background task will be started, which will process and
    finalize the upload. The status of this task can be queried using the endpoint
    specified in the ``_links.status`` property of the upload. Only uploads owned by the
    current user can be finished.
    """
    record = Record.query.get_active_or_404(record_id)
    upload = Upload.query.get_active_or_404(upload_id)

    if record.id != upload.record_id or upload.creator != current_user:
        return json_error_response(404)

    if upload.active_chunks.count() != upload.chunk_count:
        return json_error_response(
            400, description="Number of chunks does not match expected chunk count."
        )

    size = upload.active_chunks.with_entities(db.func.sum(Chunk.size)).scalar() or 0
    if size != upload.size:
        return json_error_response(
            400, description="Total chunk size does not match upload size."
        )

    upload.state = "processing"
    db.session.commit()

    additional_size = 0
    # If the upload replaces a file the quota check needs to take this into account. The
    # processing upload already counts to the total, so only the size of the replaced
    # file needs to be subtracted.
    if upload.file is not None:
        additional_size = -upload.file.size

    response = check_upload_user_quota(additional_size=additional_size)
    if response is not None:
        upload.state = "active"
        db.session.commit()
        return response

    task = start_merge_chunks_task(upload)

    if not task:
        upload.state = "active"
        db.session.commit()

        return json_error_response(
            503, description="Error starting file upload processing task."
        )

    return json_response(202)


@bp.post("/records/<int:id>/restore")
@login_required
@scopes_required("misc.manage_trash")
@status(200, "Return the restored record.")
def restore_record(id):
    """Restore the deleted record specified by the given *id*.

    Only the creator of a record can restore it.
    """
    record = Record.query.get_or_404(id)

    if record.state != "deleted" or record.creator != current_user:
        return json_error_response(404)

    _restore_record(record)
    db.session.commit()

    return json_response(200, RecordSchema().dump(record))


@bp.post("/records/<int:id>/purge")
@login_required
@scopes_required("misc.manage_trash")
@status(202, "The purge record task was started successfully.")
@status(
    503,
    "The purge record task could not be started. The record will remain deleted in this"
    " case.",
)
def purge_record(id):
    """Purge a deleted record specified by the given *id*.

    Will delete the record permanently, including all of its files. The actual deletion
    process will happen in a background task. Only the creator of a record can
    permanently delete it.
    """
    record = Record.query.get_or_404(id)

    if record.state != "deleted" or record.creator != current_user:
        return json_error_response(404)

    # In case it takes longer to actually purge the record, this way it will not show up
    # as a deleted resource anymore.
    record.state = "purged"

    if not start_purge_record_task(record):
        return json_error_response(503, description="Error starting purge record task.")

    db.session.commit()
    return json_response(202)
