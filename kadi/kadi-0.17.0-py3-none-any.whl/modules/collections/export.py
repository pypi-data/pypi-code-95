# Copyright 2021 Karlsruhe Institute of Technology
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
from io import BytesIO

import qrcode
from flask_login import current_user

from .schemas import CollectionSchema
from kadi.lib.resources.utils import get_linked_resources
from kadi.lib.web import url_for
from kadi.modules.records.models import File
from kadi.modules.records.models import Record
from kadi.modules.records.schemas import FileSchema
from kadi.modules.records.schemas import RecordSchema


def _get_json_data(collection, export_filter, user):
    # Unnecessary meta attributes to exclude in all resources, also depending on whether
    # user information should be excluded.
    if export_filter.get("user", False):
        exclude_attrs = ["_actions", "_links", "creator"]
    else:
        exclude_attrs = ["_actions", "_links", "creator._actions", "creator._links"]

    # Collect the basic metadata of the collection.
    schema = CollectionSchema(exclude=exclude_attrs)
    data = schema.dump(collection)

    # Include all records the collection contains as "records". Only the basic metadata
    # is included for each record as well as their files as "files".
    records = get_linked_resources(Record, collection.records, user=user).order_by(
        Record.last_modified.desc()
    )
    data["records"] = []

    record_schema = RecordSchema(exclude=exclude_attrs)
    file_schema = FileSchema(many=True, exclude=exclude_attrs)

    for record in records:
        files = record.active_files.order_by(File.last_modified.desc())
        record_data = record_schema.dump(record)
        record_data["files"] = file_schema.dump(files)

        data["records"].append(record_data)

    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def _get_qr_data(collection):
    image = qrcode.make(url_for("collections.view_collection", id=collection.id))

    image_data = BytesIO()
    image.save(image_data, format="PNG")
    image_data.seek(0)

    return image_data


def get_export_data(collection, export_type, export_filter=None, user=None):
    """Export a collection in a given format.

    :param collection: The collection to export.
    :param export_type: The export format, one of ``"json"`` or ``"qr"``.
    :param export_filter: (optional) A dictionary specifying various filters in order to
        exclude certain information from the returned export data. Currently only usable
        in combination with the ``"json"`` export type.

        **Example:**

        .. code-block:: python3

            {
                # Whether user information about the creator of the collection or any
                # linked resource should be excluded.
                "user": False,
            }

    :param user: (optional) The user to check for various access permissions when
        generating the export data. Defaults to the current user.
    :return: The exported collection data, depending on the given export type, or
        ``None`` if an unknown export type was given.
    """
    export_filter = export_filter if export_filter is not None else {}
    user = user if user is not None else current_user

    if export_type == "json":
        return _get_json_data(collection, export_filter, user)

    if export_type == "qr":
        return _get_qr_data(collection)

    return None
