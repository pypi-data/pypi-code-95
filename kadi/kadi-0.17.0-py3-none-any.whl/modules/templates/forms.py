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
from copy import deepcopy

from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError

from .models import Template
from kadi.lib.conversion import lower
from kadi.lib.conversion import none
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.forms import check_duplicate_identifier
from kadi.lib.forms import DynamicMultiSelectField
from kadi.lib.forms import DynamicSelectField
from kadi.lib.forms import KadiForm
from kadi.lib.forms import LFTextAreaField
from kadi.lib.forms import SelectField
from kadi.lib.forms import TagsField
from kadi.lib.forms import validate_identifier
from kadi.lib.licenses.models import License
from kadi.lib.tags.models import Tag
from kadi.modules.permissions.core import has_permission
from kadi.modules.records.extras import ExtrasField
from kadi.modules.records.extras import is_nested_type
from kadi.modules.records.models import Record


class BaseTemplateForm(KadiForm):
    """Base form class for use in creating or updating templates.

    :param template: (optional) A template used for prefilling the form.
    """

    title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=Template.Meta.check_constraints["title"]["length"]["max"]),
        ],
    )

    identifier = StringField(
        _l("Identifier"),
        filters=[lower, strip],
        validators=[
            DataRequired(),
            Length(max=Template.Meta.check_constraints["identifier"]["length"]["max"]),
            validate_identifier,
        ],
        description=_l("Unique identifier of this template."),
    )

    description = LFTextAreaField(
        _l("Description"),
        validators=[
            Length(max=Template.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    visibility = SelectField(
        _l("Visibility"),
        choices=[
            (v, v.capitalize())
            for v in Template.Meta.check_constraints["visibility"]["values"]
        ],
        description=_l(
            "Public visibility automatically grants any logged-in user read permissions"
            " for this template. More fine-grained permissions can be specified"
            " separately."
        ),
    )

    def __init__(self, *args, template=None, data=None, **kwargs):
        # Prefill all simple fields using the data attribute, depending on whether any
        # existing data is passed in or not.
        if template is not None:
            new_data = {
                "title": template.title,
                "identifier": template.identifier,
                "description": template.description,
                "visibility": template.visibility,
            }

            if data is not None:
                data.update(new_data)
            else:
                data = new_data

        super().__init__(*args, data=data, **kwargs)


class BaseRecordTemplateForm(BaseTemplateForm):
    """Base form class for use in creating or updating record templates.

    :param template: (optional) See :class:`BaseTemplateForm`.
    """

    record_title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            Length(max=Record.Meta.check_constraints["title"]["length"]["max"])
        ],
    )

    record_identifier = StringField(
        _l("Identifier"),
        filters=[lower, strip],
        validators=[
            Length(max=Record.Meta.check_constraints["identifier"]["length"]["max"])
        ],
        description=_l("Unique identifier of a record."),
    )

    record_type = DynamicSelectField(
        _l("Type"),
        filters=[lower, normalize, none],
        validators=[Length(max=Record.Meta.check_constraints["type"]["length"]["max"])],
        description=_l("Optional type of a record, e.g. dataset, device, etc."),
    )

    record_description = LFTextAreaField(
        _l("Description"),
        validators=[
            Length(max=Record.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    record_license = DynamicSelectField(
        _l("License"),
        description=_l(
            "Specifying an optional license can determine the conditions for the"
            " correct reuse of data and metadata when the record is published or simply"
            " shared with other users. A license can also be uploaded as a file, in"
            " which case one of the 'Other' licenses can be chosen."
        ),
    )

    record_tags = TagsField(
        _l("Tags"),
        max_len=Tag.Meta.check_constraints["name"]["length"]["max"],
        description=_l("An optional list of keywords further describing the record."),
    )

    record_extras = ExtrasField(_l("Extra metadata"), is_template=True)

    def __init__(self, *args, template=None, **kwargs):
        data = None

        # Prefill all simple fields using the data attribute.
        if template is not None:
            data = {
                "record_title": template.data.get("title", ""),
                "record_identifier": template.data.get("identifier", ""),
                "record_description": template.data.get("description", ""),
                "record_extras": template.data.get("extras", []),
            }

        super().__init__(*args, template=template, data=data, **kwargs)

        # Prefill all other fields separately, depending on whether the form was
        # submitted or now.
        if self.is_submitted():
            if self.record_type.data is not None:
                self.record_type.initial = (
                    self.record_type.data,
                    self.record_type.data,
                )

            if self.record_license.data is not None:
                license = License.query.filter_by(name=self.record_license.data).first()

                if license is not None:
                    self.record_license.initial = (license.name, license.title)

            self.record_tags.initial = [
                (tag, tag) for tag in sorted(self.record_tags.data)
            ]

        elif template is not None:
            if template.data.get("type") is not None:
                self._fields["record_type"].initial = (
                    template.data["type"],
                    template.data["type"],
                )

            if template.data.get("license") is not None:
                license = License.query.filter_by(name=template.data["license"]).first()

                if license is not None:
                    self._fields["record_license"].initial = (
                        license.name,
                        license.title,
                    )

            self._fields["record_tags"].initial = [
                (tag, tag) for tag in sorted(template.data.get("tags", []))
            ]

    def validate_record_identifier(self, record_identifier):
        # pylint: disable=missing-function-docstring
        if record_identifier.data:
            validate_identifier(self, record_identifier)

    def validate_record_license(self, record_license):
        # pylint: disable=missing-function-docstring
        if (
            record_license.data is not None
            and License.query.filter_by(name=record_license.data).first() is None
        ):
            raise ValidationError(_("Not a valid license."))


class BaseExtrasTemplateForm(BaseTemplateForm):
    """Base form class for use in creating or updating extras templates.

    :param template: (optional) See :class:`BaseTemplateForm`.
    :param record: (optional) A record used for prefilling the extra metadata. All
        values of this metadata will be removed.
    """

    extras = ExtrasField(_l("Extra metadata"), is_template=True)

    def __init__(self, *args, template=None, record=None, **kwargs):
        data = None

        if template is not None:
            data = {"extras": template.data}
        elif record is not None:
            data = {"extras": self._remove_extra_values(record.extras)}

        super().__init__(*args, template=template, data=data, **kwargs)

    def _remove_extra_values(self, extras):
        new_extras = []

        for extra in extras:
            new_extra = deepcopy(extra)

            if is_nested_type(extra["type"]):
                new_extra["value"] = self._remove_extra_values(extra["value"])
            else:
                new_extra["value"] = None

            new_extras.append(new_extra)

        return new_extras


class NewTemplateFormMixin:
    """Mixin class for forms used in creating new templates."""

    submit = SubmitField(_l("Create template"))

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Template)


class NewRecordTemplateForm(NewTemplateFormMixin, BaseRecordTemplateForm):
    """A form for use in creating new record templates.

    :param template: (optional) See :class:`BaseRecordTemplateForm`.
    :param user: (optional) A user that will be used for checking various permissions
        when prefilling the form. Defaults to the current user.
    """

    def __init__(self, *args, template=None, user=None, **kwargs):
        user = user if user is not None else current_user

        if template is not None and (
            template.type != "record"
            or not has_permission(user, "read", "template", template.id)
        ):
            template = None

        super().__init__(*args, template=template, **kwargs)


class NewExtrasTemplateForm(NewTemplateFormMixin, BaseExtrasTemplateForm):
    """A form for use in creating new extras templates.

    :param template: (optional) See :class:`BaseExtrasTemplateForm`.
    :param record: (optional) See :class:`BaseExtrasTemplateForm`.
    :param user: (optional) A user that will be used for checking various permissions
        when prefilling the form. Defaults to the current user.
    """

    def __init__(self, *args, template=None, record=None, user=None, **kwargs):
        user = user if user is not None else current_user

        if template is not None and (
            template.type != "extras"
            or not has_permission(user, "read", "template", template.id)
        ):
            template = None

        if record is not None and not has_permission(user, "read", "record", record.id):
            record = None

        super().__init__(*args, template=template, record=record, **kwargs)


class EditTemplateFormMixin:
    """Mixin class for forms used in editing existing templates.

    :param template: The template to edit, used for prefilling the form.
    """

    submit = SubmitField(_l("Save changes"))

    submit_quit = SubmitField(_l("Save changes and quit"))

    def __init__(self, template, *args, **kwargs):
        self.template = template
        super().__init__(*args, template=template, **kwargs)

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Template, exclude=self.template)


class EditRecordTemplateForm(EditTemplateFormMixin, BaseRecordTemplateForm):
    """A form for use in updating record templates."""


class EditExtrasTemplateForm(EditTemplateFormMixin, BaseExtrasTemplateForm):
    """A form for use in updating extras templates."""


class AddPermissionsForm(KadiForm):
    """A form for use in adding user or group roles to a record."""

    users = DynamicMultiSelectField(_l("Users"), coerce=int)

    groups = DynamicMultiSelectField(_l("Groups"), coerce=int)

    role = SelectField(
        _l("Role"),
        choices=[(r, r.capitalize()) for r, _ in Template.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Add permissions"))

    def validate(self, extra_validators=None):
        success = super().validate(extra_validators=extra_validators)

        if success and (self.users.data or self.groups.data):
            return True

        return False
