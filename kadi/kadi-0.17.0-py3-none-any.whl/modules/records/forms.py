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
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from wtforms import FileField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import ValidationError

from .extras import ExtrasField
from .models import Chunk
from .models import File
from .models import Record
from .models import RecordLink
from kadi.ext.db import db
from kadi.lib.conversion import lower
from kadi.lib.conversion import none
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.format import filesize
from kadi.lib.forms import check_duplicate_identifier
from kadi.lib.forms import DynamicMultiSelectField
from kadi.lib.forms import DynamicSelectField
from kadi.lib.forms import KadiForm
from kadi.lib.forms import LFTextAreaField
from kadi.lib.forms import TagsField
from kadi.lib.forms import validate_identifier
from kadi.lib.forms import validate_mimetype
from kadi.lib.licenses.models import License
from kadi.lib.tags.models import Tag
from kadi.modules.collections.models import Collection
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission


class BaseRecordForm(KadiForm):
    """Base form class for use in creating or updating records.

    :param record: (optional) A record used for prefilling the form.
    :param template: (optional) A record or extras template used for prefilling the
        form.
    """

    title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=Record.Meta.check_constraints["title"]["length"]["max"]),
        ],
    )

    identifier = StringField(
        _l("Identifier"),
        filters=[lower, strip],
        validators=[
            DataRequired(),
            Length(max=Record.Meta.check_constraints["identifier"]["length"]["max"]),
            validate_identifier,
        ],
        description=_l("Unique identifier of this record."),
    )

    type = DynamicSelectField(
        _l("Type"),
        filters=[lower, normalize, none],
        validators=[Length(max=Record.Meta.check_constraints["type"]["length"]["max"])],
        description=_l("Optional type of this record, e.g. dataset, device, etc."),
    )

    description = LFTextAreaField(
        _l("Description"),
        validators=[
            Length(max=Record.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    license = DynamicSelectField(
        _l("License"),
        description=_l(
            "Specifying an optional license can determine the conditions for the"
            " correct reuse of data and metadata when the record is published or simply"
            " shared with other users. A license can also be uploaded as a file, in"
            " which case one of the 'Other' licenses can be chosen."
        ),
    )

    visibility = SelectField(
        _l("Visibility"),
        choices=[
            (v, v.capitalize())
            for v in Record.Meta.check_constraints["visibility"]["values"]
        ],
        description=_l(
            "Public visibility automatically grants any logged-in user read permissions"
            " for this record. More fine-grained permissions can be specified"
            " separately."
        ),
    )

    tags = TagsField(
        _l("Tags"),
        max_len=Tag.Meta.check_constraints["name"]["length"]["max"],
        description=_l("An optional list of keywords further describing the record."),
    )

    extras = ExtrasField(_l("Extra metadata"))

    def __init__(self, *args, record=None, template=None, **kwargs):
        data = None

        # Prefill all simple fields using the data attribute.
        if record is not None:
            data = {
                "title": record.title,
                "identifier": record.identifier,
                "description": record.description,
                "visibility": record.visibility,
                "extras": record.extras,
            }
        elif template is not None:
            if template.type == "record":
                data = {
                    "title": template.data.get("title", ""),
                    "identifier": template.data.get("identifier", ""),
                    "description": template.data.get("description", ""),
                    "extras": template.data.get("extras", []),
                }
            elif template.type == "extras":
                data = {"extras": template.data}

        super().__init__(*args, data=data, **kwargs)

        # Prefill all other fields separately, depending on whether the form was
        # submitted or now.
        if self.is_submitted():
            if self.type.data is not None:
                self.type.initial = (self.type.data, self.type.data)

            if self.license.data is not None:
                license = License.query.filter_by(name=self.license.data).first()

                if license is not None:
                    self.license.initial = (license.name, license.title)

            self.tags.initial = [(tag, tag) for tag in sorted(self.tags.data)]

        elif record is not None:
            if record.type is not None:
                self._fields["type"].initial = (record.type, record.type)

            if record.license is not None:
                self._fields["license"].initial = (
                    record.license.name,
                    record.license.title,
                )

            self._fields["tags"].initial = [
                (tag.name, tag.name) for tag in record.tags.order_by("name")
            ]

        elif template is not None and template.type == "record":
            if template.data.get("type") is not None:
                self._fields["type"].initial = (
                    template.data["type"],
                    template.data["type"],
                )

            if template.data.get("license") is not None:
                license = License.query.filter_by(name=template.data["license"]).first()

                if license is not None:
                    self._fields["license"].initial = (license.name, license.title)

            self._fields["tags"].initial = [
                (tag, tag) for tag in sorted(template.data.get("tags", []))
            ]

    def validate_license(self, license):
        # pylint: disable=missing-function-docstring
        if (
            license.data is not None
            and License.query.filter_by(name=license.data).first() is None
        ):
            raise ValidationError(_("Not a valid license."))


class NewRecordForm(BaseRecordForm):
    """A form for use in creating new records.

    :param record: (optional) See :class:`BaseRecordForm`.
    :param template: (optional) See :class:`BaseRecordForm`.
    :param collection: (optional) A collection used for prefilling the linked
        collections.
    :param user: (optional) A user that will be used for checking various permissions
        when prefilling the form. Defaults to the current user.
    """

    linked_collections = DynamicMultiSelectField(
        _l("Linked collections"),
        coerce=int,
        description=_l("Link this record with one or multiple collections."),
    )

    copy_permission = DynamicSelectField(
        _l("Permissions"),
        coerce=int,
        description=_l(
            "Copy the permissions of another record. Note that only group roles of"
            " readable groups are copied."
        ),
    )

    submit = SubmitField(_l("Create record"))

    def __init__(
        self, *args, record=None, template=None, collection=None, user=None, **kwargs
    ):
        user = user if user is not None else current_user

        if record is not None and not has_permission(user, "read", "record", record.id):
            record = None

        if template is not None and not has_permission(
            user, "read", "template", template.id
        ):
            template = None

        super().__init__(*args, record=record, template=template, **kwargs)

        collection_ids_query = (
            get_permitted_objects(user, "read", "collection")
            .intersect(get_permitted_objects(user, "link", "collection"))
            .filter(Collection.state == "active")
            .with_entities(Collection.id)
        )

        if self.is_submitted():
            if self.linked_collections.data:
                collections = Collection.query.filter(
                    db.and_(
                        Collection.id.in_(collection_ids_query),
                        Collection.id.in_(self.linked_collections.data),
                    )
                )
                self.linked_collections.initial = [
                    (c.id, f"@{c.identifier}") for c in collections
                ]

            if self.copy_permission.data:
                record = Record.query.get_active(self.copy_permission.data)

                if record is not None and has_permission(
                    user, "read", "record", record.id
                ):
                    self.copy_permission.initial = (record.id, f"@{record.identifier}")

        else:
            if record is not None:
                collections = record.collections.filter(
                    Collection.id.in_(collection_ids_query)
                )
                self._fields["linked_collections"].initial = [
                    (c.id, f"@{c.identifier}") for c in collections
                ]

                self._fields["copy_permission"].initial = (
                    record.id,
                    f"@{record.identifier}",
                )

            elif collection is not None and collection.id in {
                c.id for c in collection_ids_query
            }:
                self._fields["linked_collections"].initial = [
                    (collection.id, f"@{collection.identifier}")
                ]

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Record)


class EditRecordForm(BaseRecordForm):
    """A form for use in editing existing records.

    :param record: The record to edit, used for prefilling the form.
    """

    submit = SubmitField(_l("Save changes"))

    submit_quit = SubmitField(_l("Save changes and quit"))

    def __init__(self, record, *args, **kwargs):
        self.record = record
        super().__init__(*args, record=record, **kwargs)

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Record, exclude=self.record)


class LinkRecordForm(KadiForm):
    """A form for use in linking records with other records.

    :param user: (optional) A user that will be used for checking various permissions
        when prefilling the form. Defaults to the current user.
    """

    record = DynamicSelectField(_l("Record"), validators=[DataRequired()], coerce=int)

    name = StringField(
        _l("Name"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=RecordLink.Meta.check_constraints["name"]["length"]["max"]),
        ],
        description=_l("The name or type of the link."),
    )

    link_direction = SelectField(
        _l("Link direction"), choices=[("out", _l("Outgoing")), ("in", _l("Incoming"))]
    )

    submit = SubmitField(_l("Link record"))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        user = user if user is not None else current_user

        # Set the initial value of the dynamic selection based on the submitted form
        # data.
        if self.is_submitted() and self.record.data:
            record = Record.query.get_active(self.record.data)

            if record is not None and has_permission(user, "read", "record", record.id):
                self.record.initial = (record.id, f"@{record.identifier}")


class LinkCollectionsForm(KadiForm):
    """A form for use in linking records with collections."""

    collections = DynamicMultiSelectField(
        _l("Collections"), validators=[DataRequired()], coerce=int
    )

    submit = SubmitField(_l("Link collections"))


class AddPermissionsForm(KadiForm):
    """A form for use in adding user or group roles to a record."""

    users = DynamicMultiSelectField(_l("Users"), coerce=int)

    groups = DynamicMultiSelectField(_l("Groups"), coerce=int)

    role = SelectField(
        _l("Role"),
        choices=[(r, r.capitalize()) for r, _ in Record.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Add permissions"))

    def validate(self, extra_validators=None):
        success = super().validate(extra_validators=extra_validators)

        if success and (self.users.data or self.groups.data):
            return True

        return False


class ChunkMetaForm(KadiForm):
    """A form for use in uploading file chunks.

    :param chunk_count: The total amount of chunks that the upload this chunk is part of
        has. Will be used to validate the chunk's index.
    :param chunk_size: The configured chunk size.
    """

    blob = FileField(validators=[DataRequired()])

    index = IntegerField(
        validators=[
            InputRequired("Missing data for required field."),
            NumberRange(
                min=Chunk.Meta.check_constraints["index"]["range"]["min"],
                message="Must be greater than or equal to %(min)s.",
            ),
        ]
    )

    size = IntegerField(
        validators=[
            InputRequired("Missing data for required field."),
            NumberRange(
                min=Chunk.Meta.check_constraints["size"]["range"]["min"],
                message="Must be greater than or equal to %(min)s.",
            ),
        ],
    )

    checksum = StringField(
        filters=[strip],
        validators=[Length(max=File.Meta.check_constraints["name"]["length"]["max"])],
    )

    def __init__(self, chunk_count, chunk_size, *args, **kwargs):
        self.chunk_count = chunk_count
        self.chunk_size = chunk_size
        super().__init__(*args, **kwargs)

    def validate_index(self, index):
        # pylint: disable=missing-function-docstring
        if index.data and index.data >= self.chunk_count:
            raise ValidationError(f"Must be less than {self.chunk_count}.")

    def validate_size(self, size):
        # pylint: disable=missing-function-docstring
        if size.data and size.data > self.chunk_size:
            raise ValidationError(
                f"Maximum size exceeded ({filesize(self.chunk_size)})."
            )


class EditFileForm(KadiForm):
    """A form for use in editing file metadata.

    :param file: A file used for prefilling the form and checking for duplicate file
        names.
    """

    name = StringField(
        _l("Filename"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=File.Meta.check_constraints["name"]["length"]["max"]),
        ],
    )

    mimetype = StringField(
        _l("MIME type"),
        filters=[lower, normalize],
        validators=[
            DataRequired(),
            Length(max=File.Meta.check_constraints["mimetype"]["length"]["max"]),
            validate_mimetype,
        ],
    )

    submit = SubmitField(_l("Save changes"))

    def __init__(self, file, *args, **kwargs):
        self.file = file
        super().__init__(*args, obj=file, **kwargs)

    def validate_name(self, name):
        # pylint: disable=missing-function-docstring
        name = name.data
        if name is not None:
            file = File.query.filter(
                File.record_id == self.file.record_id,
                File.state == "active",
                File.name == name,
            ).first()

            if file is not None and self.file != file:
                raise ValidationError(_("Name is already in use."))
