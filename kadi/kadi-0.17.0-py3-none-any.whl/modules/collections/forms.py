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
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Length

from .models import Collection
from kadi.ext.db import db
from kadi.lib.conversion import lower
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.forms import check_duplicate_identifier
from kadi.lib.forms import DynamicMultiSelectField
from kadi.lib.forms import DynamicSelectField
from kadi.lib.forms import KadiForm
from kadi.lib.forms import LFTextAreaField
from kadi.lib.forms import TagsField
from kadi.lib.forms import validate_identifier
from kadi.lib.tags.models import Tag
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission
from kadi.modules.records.models import Record


class BaseCollectionForm(KadiForm):
    """Base form class for use in creating or updating collections.

    :param collection: (optional) A collection used for prefilling the form.
    """

    title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=Collection.Meta.check_constraints["title"]["length"]["max"]),
        ],
    )

    identifier = StringField(
        _l("Identifier"),
        filters=[strip, lower],
        validators=[
            DataRequired(),
            Length(
                max=Collection.Meta.check_constraints["identifier"]["length"]["max"]
            ),
            validate_identifier,
        ],
        description=_l("Unique identifier of this collection."),
    )

    description = LFTextAreaField(
        _l("Description"),
        validators=[
            Length(
                max=Collection.Meta.check_constraints["description"]["length"]["max"]
            )
        ],
    )

    visibility = SelectField(
        _l("Visibility"),
        choices=[
            (v, v.capitalize())
            for v in Collection.Meta.check_constraints["visibility"]["values"]
        ],
        description=_l(
            "Public visibility automatically grants any logged-in user read permissions"
            " for this collection. More fine-grained permissions can be specified"
            " separately."
        ),
    )

    tags = TagsField(
        _l("Tags"),
        max_len=Tag.Meta.check_constraints["name"]["length"]["max"],
        description=_l(
            "An optional list of keywords further describing the collection."
        ),
    )

    def __init__(self, *args, collection=None, **kwargs):
        data = None

        # Prefill all simple fields using the data attribute.
        if collection is not None:
            data = {
                "title": collection.title,
                "identifier": collection.identifier,
                "description": collection.description,
                "visibility": collection.visibility,
            }

        super().__init__(*args, data=data, **kwargs)

        # Prefill all other fields separately, depending on whether the form was
        # submitted or now.
        if self.is_submitted():
            self.tags.initial = [(tag, tag) for tag in sorted(self.tags.data)]
        elif collection is not None:
            self._fields["tags"].initial = [
                (tag.name, tag.name) for tag in collection.tags.order_by("name")
            ]


class NewCollectionForm(BaseCollectionForm):
    """A form for use in creating new collections.

    :param collection: (optional) See :class:`BaseCollectionForm`.
    :param user: (optional) A user that will be used for checking various permissions
        when prefilling the form. Defaults to the current user.
    """

    linked_records = DynamicMultiSelectField(
        _l("Linked records"),
        coerce=int,
        description=_l("Link this collection with one or multiple records."),
    )

    copy_permission = DynamicSelectField(
        _l("Permissions"),
        coerce=int,
        description=_l(
            "Copy the permissions of another collection. Note that only group roles of"
            " readable groups are copied."
        ),
    )

    submit = SubmitField(_l("Create Collection"))

    def __init__(self, *args, collection=None, user=None, **kwargs):
        user = user if user is not None else current_user

        if collection is not None and not has_permission(
            user, "read", "collection", collection.id
        ):
            collection = None

        super().__init__(*args, collection=collection, **kwargs)

        record_ids_query = (
            get_permitted_objects(user, "read", "record")
            .intersect(get_permitted_objects(user, "link", "record"))
            .filter(Record.state == "active")
            .with_entities(Record.id)
        )

        if self.is_submitted():
            if self.linked_records.data:
                records = Record.query.filter(
                    db.and_(
                        Record.id.in_(record_ids_query),
                        Record.id.in_(self.linked_records.data),
                    )
                )
                self.linked_records.initial = [
                    (r.id, f"@{r.identifier}") for r in records
                ]

            if self.copy_permission.data:
                collection = Collection.query.get_active(self.copy_permission.data)

                if collection is not None and has_permission(
                    user, "read", "collection", collection.id
                ):
                    self.copy_permission.initial = (
                        collection.id,
                        f"@{collection.identifier}",
                    )

        elif collection is not None:
            records = collection.records.filter(Record.id.in_(record_ids_query))
            self._fields["linked_records"].initial = [
                (r.id, f"@{r.identifier}") for r in records
            ]

            self._fields["copy_permission"].initial = (
                collection.id,
                f"@{collection.identifier}",
            )

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Collection)


class EditCollectionForm(BaseCollectionForm):
    """A form for use in editing existing collections.

    :param collection: The collection to edit, used for prefilling the form.
    """

    submit = SubmitField(_l("Save changes"))

    submit_quit = SubmitField(_l("Save changes and quit"))

    def __init__(self, collection, *args, **kwargs):
        self.collection = collection
        super().__init__(*args, collection=collection, **kwargs)

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Collection, exclude=self.collection)


class LinkRecordsForm(KadiForm):
    """A form for use in linking collections with records."""

    records = DynamicMultiSelectField(
        _l("Records"), validators=[DataRequired()], coerce=int
    )

    submit = SubmitField(_l("Link records"))


class LinkCollectionsForm(KadiForm):
    """A form for use in linking collections with other collections."""

    collections = DynamicMultiSelectField(
        _l("Collections"), validators=[DataRequired()], coerce=int
    )

    submit = SubmitField(_l("Link collections"))


class AddPermissionsBaseForm(KadiForm):
    """Base form class for use in adding user or group roles concerning collections."""

    users = DynamicMultiSelectField(_l("Users"), coerce=int)

    groups = DynamicMultiSelectField(_l("Groups"), coerce=int)

    def validate(self, extra_validators=None):
        success = super().validate(extra_validators=extra_validators)

        if success and (self.users.data or self.groups.data):
            return True

        return False


class AddCollectionPermissionsForm(AddPermissionsBaseForm):
    """A form for use in adding user or group roles to a collection."""

    role = SelectField(
        _l("Role"),
        choices=[(r, r.capitalize()) for r, _ in Collection.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Add permissions"))


class AddRecordsPermissionsForm(AddPermissionsBaseForm):
    """A form for use in adding or removing user or group roles of linked records."""

    records = DynamicMultiSelectField(_l("Records"), coerce=int)

    role = SelectField(
        _l("Role"),
        choices=[("", "")]
        + [(r, r.capitalize()) for r, _ in Record.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Apply permissions"))
