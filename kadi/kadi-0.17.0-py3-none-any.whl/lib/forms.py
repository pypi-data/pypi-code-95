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
from datetime import timezone

from flask_babel import gettext as _
from flask_babel import ngettext
from flask_wtf import FlaskForm
from wtforms import DateTimeField
from wtforms import FileField
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms.validators import Length
from wtforms.validators import StopValidation

from .conversion import lower
from .conversion import normalize
from .validation import validate_identifier as _validate_identifier
from .validation import validate_mimetype as _validate_mimetype
from .validation import validate_username as _validate_username
from .validation import validate_uuid
from .validation import validator
from kadi.lib.utils import compact_json
from kadi.modules.records.extras import ExtrasField


class KadiForm(FlaskForm):
    """Base class for all forms.

    :param _suffix: (optional) A suffix that will be appended to all field IDs in the
        form of ``"<id>_<suffix>"``. This is especially useful when dealing with
        multiple forms on the same page.
    """

    def __init__(self, *args, _suffix=None, **kwargs):
        super().__init__(*args, **kwargs)

        if _suffix is not None:
            for field in self._fields.values():
                field.id = f"{field.id}_{_suffix}"
                field.label.field_id = field.id


class DynamicSelectField(SelectField):
    """Custom select field for dynamically generated selections.

    The instance variable ``initial`` can be used to set an initial value to prefill the
    selection with.
    """

    def __init__(self, *args, **kwargs):
        self.initial = None

        kwargs["default"] = None
        kwargs["choices"] = None
        kwargs["validate_choice"] = False

        super().__init__(*args, **kwargs)


class DynamicMultiSelectField(SelectMultipleField):
    """Custom multi select field for dynamically generated selections.

    The instance variable ``initial`` can be used to set initial values to prefill the
    selection with.
    """

    def __init__(self, *args, **kwargs):
        self.initial = []

        kwargs["default"] = []
        kwargs["choices"] = None

        super().__init__(*args, **kwargs)

    def pre_validate(self, form):
        """Does nothing since the choices are populated dynamically."""


class TagsField(DynamicMultiSelectField):
    """Custom multi select field with support for "tagging".

    Tagging allows putting in custom values in a multi select field.

    :param max_len: (optional) The maximum length of each tag.
    """

    def __init__(self, *args, max_len=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_len = max_len

    def post_validate(self, form, validation_stopped):
        """Validate each tag.

        Does not allow empty tags and optionally checks their maximum length as well.
        """
        for value in self.data:
            if not value:
                self.errors = [_("Tags must not be empty.")]
                return False

            if self.max_len is not None and len(value) > self.max_len:
                self.errors = [
                    ngettext(
                        "Tags cannot be longer than %(num)d character.",
                        "Tags cannot be longer than %(num)d characters.",
                        num=self.max_len,
                    )
                ]
                return False

        return True

    def process_formdata(self, valuelist):
        """Convert each tag to lowercase and remove/normalize whitespace."""
        super().process_formdata(valuelist)

        data = []
        for value in self.data:
            for converter in [lower, normalize]:
                value = converter(value)

            if value not in data:
                data.append(value)

        self.data = data


class LFTextAreaField(TextAreaField):
    """Custom text area field that converts *CR* *LF* to *LF*."""

    def process_formdata(self, valuelist):
        r"""Convert each occurence of \\r\\n to \\n."""
        super().process_formdata(valuelist)

        if self.data is not None:
            self.data = self.data.replace("\r\n", "\n")


class UTCDateTimeField(DateTimeField):
    """Custom timezone aware DateTimeField using UTC.

    :param date_format: (optional) The date format to use for parsing and serializing.
    """

    def __init__(self, *args, date_format="%Y-%m-%dT%H:%M:%S.%fZ", **kwargs):
        kwargs["format"] = date_format
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        """Replace the missing timezone with UTC."""
        super().process_formdata(valuelist)

        if self.data is not None:
            self.data = self.data.replace(tzinfo=timezone.utc)


class ValidateUUID:
    """Validate a UUID of a specific version in a form field.

    :param version: (optional) The UUID version.
    """

    def __init__(self, version=4):
        self.version = version

    @validator(StopValidation)
    def __call__(self, form, field):
        validate_uuid(field.data, version=self.version)


@validator(StopValidation)
def validate_identifier(form, field):
    """Validate an identifier in a form field.

    Uses :func:`kadi.lib.validation.validate_identifier`.

    :param form: The form object.
    :param field: The field object.
    """
    _validate_identifier(field.data)


@validator(StopValidation)
def validate_mimetype(form, field):
    """Validate a MIME type in a form field.

    Uses :func:`kadi.lib.validation.validate_mimetype`.

    :param form: The form object.
    :param field: The field object.
    """
    _validate_mimetype(field.data)


@validator(StopValidation)
def validate_username(form, field):
    """Validate a local username in a form field.

    Uses :func:`kadi.lib.validation.validate_username`.

    :param form: The form object.
    :param field: The field object.
    """
    _validate_username(field.data)


def check_duplicate_identifier(field, model, exclude=None):
    """Check for a duplicate identifier in a form field.

    Has to be called manually after the usual validation as further arguments are needed
    for this check.

    :param field: The identifier field.
    :param model: The model the check the identifier in.
    :param exclude: (optional) An object that should be excluded in the check.
    """
    identifier = field.data
    if identifier is not None:
        obj_to_check = model.query.filter_by(identifier=identifier).first()

        if obj_to_check is not None and (exclude is None or exclude != obj_to_check):
            raise StopValidation(_("Identifier is already in use."))


def field_to_dict(field):
    """Convert a form field into a dictionary representation.

    :param field: The form field to convert.
    :return: The converted form field.
    """
    data = {
        "id": field.id,
        "name": field.name,
        "label": str(field.label.text),
        "description": str(field.description),
        "errors": field.errors or [],
        "data": field.data,
    }

    if field.data is None:
        data["data"] = ""

    if isinstance(field, FileField):
        data["data"] = None
    elif isinstance(field, (UTCDateTimeField, ExtrasField)):
        data["data"] = field._value()
    elif isinstance(field, (DynamicSelectField, DynamicMultiSelectField)):
        data["data"] = field.initial

    if isinstance(field, SelectField):
        if field.choices is not None:
            data["choices"] = [(val, str(title)) for val, title in field.choices]
        else:
            data["choices"] = None

    validation = {
        "required": field.flags.required,
    }

    for validator in field.validators:
        if isinstance(validator, Length):
            if validator.min != -1:
                validation["min"] = validator.min

            if validator.max != -1:
                validation["max"] = validator.max

    data["validation"] = validation

    return data


def json_field(field):
    """Convert a form field into a JSON representation.

    :param field: The form field to convert.
    :return: The converted form field.
    """
    return compact_json(field_to_dict(field))
