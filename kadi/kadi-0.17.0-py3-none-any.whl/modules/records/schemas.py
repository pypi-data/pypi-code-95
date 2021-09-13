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
from marshmallow import fields
from marshmallow import post_dump
from marshmallow import post_load
from marshmallow.validate import Length
from marshmallow.validate import OneOf
from marshmallow.validate import Range
from marshmallow.validate import ValidationError

from .models import File
from .models import Record
from .models import RecordLink
from .models import Upload
from kadi.lib.api.core import check_access_token_scopes
from kadi.lib.conversion import lower
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.licenses.schemas import LicenseSchema
from kadi.lib.schemas import check_duplicate_identifier
from kadi.lib.schemas import KadiSchema
from kadi.lib.schemas import NonEmptyString
from kadi.lib.schemas import SortedPluck
from kadi.lib.schemas import validate_identifier
from kadi.lib.schemas import validate_mimetype
from kadi.lib.schemas import ValidateUUID
from kadi.lib.tags.schemas import TagSchema
from kadi.lib.web import url_for
from kadi.modules.accounts.schemas import UserSchema
from kadi.modules.records.extras import ExtraSchema


def _validate_record_id(record_id):
    if Record.query.get_active(record_id) is None:
        raise ValidationError("No record with this ID exists.")


class RecordSchema(KadiSchema):
    """Schema to represent records.

    See :class:`.Record`.

    :param previous_record: (optional) A record whose identifier should be excluded when
        checking for duplicates while deserializing.
    :param linked_collection: (optional) A collection that is linked to each record that
        should be serialized. Will be used to build endpoints for corresponding actions.
    :param check_identifier: (optional) Flag indicating whether the identifier should be
        checked for duplicates.
    :param is_template: (optional) Flag indicating whether the schema is used inside a
        template. Currently, this is only relevant for the extra metadata.
    """

    id = fields.Integer(required=True, validate=_validate_record_id)

    identifier = NonEmptyString(
        required=True,
        filters=[lower, strip],
        validate=[
            Length(max=Record.Meta.check_constraints["identifier"]["length"]["max"]),
            validate_identifier,
        ],
    )

    title = NonEmptyString(
        required=True,
        filters=[normalize],
        validate=Length(max=Record.Meta.check_constraints["title"]["length"]["max"]),
    )

    type = NonEmptyString(
        allow_none=True,
        filters=[lower, normalize],
        validate=Length(max=Record.Meta.check_constraints["type"]["length"]["max"]),
    )

    description = fields.String(
        validate=Length(
            max=Record.Meta.check_constraints["description"]["length"]["max"]
        )
    )

    license = fields.Pluck(LicenseSchema, "name", allow_none=True)

    visibility = fields.String(
        validate=OneOf(Record.Meta.check_constraints["visibility"]["values"])
    )

    extras = fields.Method("_serialize_extras", deserialize="_deserialize_extras")

    tags = SortedPluck(TagSchema, "name", many=True)

    plain_description = fields.String(dump_only=True)

    state = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    last_modified = fields.DateTime(dump_only=True)

    creator = fields.Nested(UserSchema, dump_only=True)

    _links = fields.Method("_generate_links")

    _actions = fields.Method("_generate_actions")

    def __init__(
        self,
        previous_record=None,
        linked_collection=None,
        check_identifier=True,
        is_template=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.previous_record = previous_record
        self.linked_collection = linked_collection
        self.check_identifier = check_identifier
        self.is_template = is_template

    @post_dump
    def _post_dump(self, data, **kwargs):
        if "creator" in data and not check_access_token_scopes("user.read"):
            del data["creator"]

        return data

    @post_load
    def _post_load(self, data, **kwargs):
        if self.check_identifier:
            check_duplicate_identifier(data, Record, exclude=self.previous_record)

        if data.get("license") is not None:
            data["license"] = data["license"]["name"]

        if "tags" in data:
            data["tags"] = list({tag["name"] for tag in data["tags"]})

        return data

    def _serialize_extras(self, obj):
        return obj.extras

    def _deserialize_extras(self, value):
        return ExtraSchema(is_template=self.is_template, many=True).load(value)

    def _generate_links(self, obj):
        links = {
            "self": url_for("api.get_record", id=obj.id),
            "files": url_for("api.get_files", id=obj.id),
            "records_to": url_for("api.get_record_links", id=obj.id, direction="to"),
            "records_from": url_for(
                "api.get_record_links", id=obj.id, direction="from"
            ),
            "collections": url_for("api.get_record_collections", id=obj.id),
            "user_roles": url_for("api.get_record_user_roles", id=obj.id),
            "group_roles": url_for("api.get_record_group_roles", id=obj.id),
            "revisions": url_for("api.get_record_revisions", id=obj.id),
            "file_revisions": url_for("api.get_file_revisions", id=obj.id),
        }

        if self._internal:
            links["view"] = url_for("records.view_record", id=obj.id)

        return links

    def _generate_actions(self, obj):
        actions = {
            "edit": url_for("api.edit_record", id=obj.id),
            "delete": url_for("api.delete_record", id=obj.id),
            "new_upload": url_for("api.new_upload", id=obj.id),
            "link_record": url_for("api.add_record_link", id=obj.id),
            "link_collection": url_for("api.add_record_collection", id=obj.id),
            "add_user_role": url_for("api.add_record_user_role", id=obj.id),
            "add_group_role": url_for("api.add_record_group_role", id=obj.id),
        }

        if self.linked_collection:
            actions["remove_link"] = url_for(
                "api.remove_collection_record",
                collection_id=self.linked_collection.id,
                record_id=obj.id,
            )

        return actions


class RecordLinkSchema(KadiSchema):
    """Schema to represent record links.

    See :class:`.RecordLink`.
    """

    id = fields.Integer(required=True)

    record_from = fields.Nested(RecordSchema, dump_only=True)

    record_to = fields.Nested(RecordSchema, required=True)

    name = NonEmptyString(
        required=True,
        filters=[normalize],
        validate=Length(max=RecordLink.Meta.check_constraints["name"]["length"]["max"]),
    )

    created_at = fields.DateTime(dump_only=True)

    _links = fields.Method("_generate_links")

    _actions = fields.Method("_generate_actions")

    def _generate_links(self, obj):
        return {
            "self": url_for(
                "api.get_record_link", record_id=obj.record_from_id, link_id=obj.id
            )
        }

    def _generate_actions(self, obj):
        return {
            "remove_link": url_for(
                "api.remove_record_link", record_id=obj.record_from_id, link_id=obj.id
            )
        }


class FileSchema(KadiSchema):
    """Schema to represent files.

    See :class:`.File`.

    :param record: (optional) A record the file to be deserialized belongs to. Will be
        used to check for duplicate filenames while deserializing.
    :param previous_file: (optional) A file that will be excluded when checking for
        duplicate filenames while deserializing.
    """

    id = fields.String(required=True, validate=ValidateUUID(version=4))

    name = NonEmptyString(
        required=True,
        filters=[normalize],
        validate=Length(max=File.Meta.check_constraints["name"]["length"]["max"]),
    )

    size = fields.Integer(
        required=True,
        validate=Range(min=File.Meta.check_constraints["size"]["range"]["min"]),
    )

    mimetype = NonEmptyString(
        filters=[lower, normalize],
        validate=[
            Length(max=File.Meta.check_constraints["mimetype"]["length"]["max"]),
            validate_mimetype,
        ],
    )

    checksum = NonEmptyString(
        filters=[strip],
        validate=Length(max=File.Meta.check_constraints["checksum"]["length"]["max"]),
    )

    magic_mimetype = fields.String(dump_only=True)

    state = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    last_modified = fields.DateTime(dump_only=True)

    creator = fields.Nested(UserSchema, dump_only=True)

    _links = fields.Method("_generate_links")

    _actions = fields.Method("_generate_actions")

    def __init__(self, record=None, previous_file=None, **kwargs):
        super().__init__(**kwargs)
        self.record = record
        self.previous_file = previous_file

    @post_dump
    def _post_dump(self, data, **kwargs):
        if "creator" in data and not check_access_token_scopes("user.read"):
            del data["creator"]

        return data

    @post_load
    def _post_load(self, data, **kwargs):
        name = data.get("name")
        if name is not None and self.record is not None:
            file = self.record.files.filter(
                File.state == "active", File.name == name
            ).first()

            if file is not None and (
                self.previous_file is None or self.previous_file != file
            ):
                raise ValidationError("Name is already in use.", "name")

        return data

    def _generate_links(self, obj):
        links = {
            "self": url_for("api.get_file", record_id=obj.record_id, file_id=obj.id),
            "record": url_for("api.get_record", id=obj.record_id),
            "download": url_for(
                "api.download_file", record_id=obj.record_id, file_id=obj.id
            ),
        }

        if self._internal:
            links["view"] = url_for(
                "records.view_file", record_id=obj.record_id, file_id=obj.id
            )
            links["edit_file"] = url_for(
                "records.edit_file", record_id=obj.record_id, file_id=obj.id
            )
            links["update_content"] = url_for(
                "records.add_files", id=obj.record_id, file=obj.id
            )

        return links

    def _generate_actions(self, obj):
        actions = {
            "delete": url_for(
                "api.delete_file", record_id=obj.record_id, file_id=obj.id
            ),
            "edit_metadata": url_for(
                "api.edit_file_metadata", record_id=obj.record_id, file_id=obj.id
            ),
        }

        if obj.storage_type == "local":
            actions["edit_data"] = url_for(
                "api.edit_file_data", record_id=obj.record_id, file_id=obj.id
            )

        return actions


class ChunkSchema(KadiSchema):
    """Schema to represent chunks.

    See :class:`.Chunk`.
    """

    index = fields.Integer(dump_only=True)

    size = fields.Integer(dump_only=True)

    state = fields.String(dump_only=True)


class UploadSchema(KadiSchema):
    """Schema to represent local file uploads.

    See :class:`.Upload`.
    """

    id = fields.String(dump_only=True)

    name = NonEmptyString(
        required=True,
        filters=[normalize],
        validate=Length(max=Upload.Meta.check_constraints["name"]["length"]["max"]),
    )

    size = fields.Integer(
        required=True,
        validate=Range(min=Upload.Meta.check_constraints["size"]["range"]["min"]),
    )

    mimetype = NonEmptyString(
        filters=[lower, normalize],
        validate=[
            Length(max=Upload.Meta.check_constraints["mimetype"]["length"]["max"]),
            validate_mimetype,
        ],
    )

    checksum = NonEmptyString(
        filters=[strip],
        validate=Length(max=Upload.Meta.check_constraints["checksum"]["length"]["max"]),
    )

    chunk_count = fields.Integer(dump_only=True)

    state = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    last_modified = fields.DateTime(dump_only=True)

    creator = fields.Nested(UserSchema, dump_only=True)

    file = fields.Nested(FileSchema, dump_only=True)

    chunks = fields.Nested(ChunkSchema, many=True, dump_only=True)

    _links = fields.Method("_generate_links")

    _actions = fields.Method("_generate_actions")

    @post_dump
    def _post_dump(self, data, **kwargs):
        if "creator" in data and not check_access_token_scopes("user.read"):
            del data["creator"]

        return data

    def _generate_links(self, obj):
        return {
            "status": url_for(
                "api.get_upload_status", record_id=obj.record_id, upload_id=obj.id
            ),
            "record": url_for("api.get_record", id=obj.record_id),
        }

    def _generate_actions(self, obj):
        return {
            "upload_chunk": url_for(
                "api.upload_chunk", record_id=obj.record_id, upload_id=obj.id
            ),
            "finish_upload": url_for(
                "api.finish_upload", record_id=obj.record_id, upload_id=obj.id
            ),
            "delete": url_for(
                "api.delete_upload", record_id=obj.record_id, upload_id=obj.id
            ),
        }
