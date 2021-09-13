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
from copy import deepcopy
from datetime import datetime
from datetime import timezone

from flask_babel import gettext as _
from marshmallow import fields
from marshmallow import validates_schema
from marshmallow import ValidationError
from marshmallow.validate import Length
from sqlalchemy.dialects.postgresql import JSONB
from wtforms import Field

from kadi.ext.db import db
from kadi.lib.conversion import normalize
from kadi.lib.conversion import parse_datetime_string
from kadi.lib.conversion import strip
from kadi.lib.format import pretty_type_name
from kadi.lib.schemas import KadiSchema
from kadi.lib.schemas import NonEmptyString
from kadi.lib.utils import is_iterable
from kadi.lib.utils import is_special_float


# We restrict integer values to values safe for parsing them in JS contexts, as they are
# also used for the extra metadata editor. This is not quite the whole long integer
# range, but hopefully enough for most use cases. As a positive side effect, all integer
# values are indexable by Elasticsearch.
MAX_INTEGER = 2 ** 53 - 1


def is_nested_type(value_type):
    """Check if the type of an extra metadata entry is nested.

    :param value_type: The type of the extra metadata entry.
    :return: ``True`` if the given type is nested, ``False`` otherwise.
    """
    return value_type in ["dict", "list"]


class ExtrasJSONB(db.TypeDecorator):
    """Custom JSON type for values containing extra record metadata.

    Converts float values to float explicitely, as larger float values might otherwise
    be interpreted as integers. This also works with dictionaries that do not contain
    extras directly, but as any nested dictionary value instead. See also
    :attr:`.Record.extras`.
    """

    impl = JSONB

    cache_ok = True

    def _is_extra(self, value):
        # Extras always include a type and value, so this should be good enough to
        # detect them.
        if isinstance(value, dict) and "type" in value and "value" in value:
            return True

        return False

    def process_result_value(self, value, dialect):
        """Convert float values of any extras recursively."""
        if value is None:
            return value

        if isinstance(value, dict):
            for _, val in value.items():
                self.process_result_value(val, dialect)

        elif isinstance(value, list) and len(value) > 0 and self._is_extra(value[0]):
            for extra in value:
                if is_nested_type(extra["type"]):
                    self.process_result_value(extra["value"], dialect)

                elif extra["type"] == "float" and extra["value"]:
                    extra["value"] = float(extra["value"])

        return value


def _validate_value(value, value_type):
    if value_type == "int":
        if type(value).__name__ == value_type and -MAX_INTEGER <= value <= MAX_INTEGER:
            return value

    elif value_type == "float":
        # Allow integer values as well.
        if type(value).__name__ in ["int", "float"]:
            value = float(value)

            if not is_special_float(value):
                return value

    elif value_type == "date":
        # Allow using datetime objects directly.
        if not isinstance(value, datetime):
            value = parse_datetime_string(value)

        if value is not None:
            return value.astimezone(timezone.utc).isoformat()

    elif type(value).__name__ == value_type:
        return value

    raise ValueError(f"Not a valid {pretty_type_name(value_type)}.")


class _ValidationSchema(KadiSchema):
    required = fields.Boolean()

    options = fields.List(fields.Raw, validate=[Length(min=1)])

    def __init__(self, value_type, **kwargs):
        super().__init__(**kwargs)
        self.value_type = value_type

    def _flatten_errors(self, errors):
        flat_messages = []

        for field, error_data in errors.items():
            if isinstance(error_data, dict):
                for messages in error_data.values():
                    for message in messages:
                        flat_messages.append(f"{field}: {message}")
            else:
                for message in error_data:
                    flat_messages.append(f"{field}: {message}")

        return flat_messages

    @validates_schema(skip_on_field_errors=False)
    def _validates_schema(self, data, **kwargs):
        if "options" not in data:
            return

        if self.value_type not in ["str", "int", "float"]:
            raise ValidationError(
                f"Cannot be used together with {pretty_type_name(self.value_type)}.",
                "options",
            )

        options = []

        for option in data["options"]:
            try:
                value = _validate_value(option, self.value_type)
                if value not in options:
                    options.append(value)

            except ValueError as e:
                raise ValidationError(
                    f"Not all values are a valid {pretty_type_name(self.value_type)}.",
                    "options",
                ) from e

        data["options"] = options


class ExtraSchema(KadiSchema):
    """Schema to represent extra record metadata.

    Also does all necessary conversion and validation when deserializing. See also
    :attr:`.Record.extras`.

    :param is_template: (optional) Flag indicating whether the schema is used inside a
        template, in which case different validation rules may apply.
    """

    type = NonEmptyString(required=True, filters=[strip])

    key = NonEmptyString(required=True, filters=[normalize])

    value = fields.Raw(load_default=None)

    unit = NonEmptyString(load_default=None, filters=[normalize])

    validation = fields.Dict()

    def __init__(self, is_template=False, **kwargs):
        super().__init__(**kwargs)
        self.is_template = is_template

    def _add_validation_error(self, errors, index, field, message):
        if index not in errors:
            errors[index] = {field: [message]}
        elif field not in errors[index]:
            errors[index][field] = [message]
        else:
            errors[index][field].append(message)

    def _apply_validation(self, extra, errors, index):
        value = extra["value"]
        validation = extra["validation"]

        if not self.is_template and validation.get("required") and value is None:
            self._add_validation_error(errors, index, "value", "Value is required.")

        # None values always pass the validation. If that is not desirable, "required"
        # can be used in combination with the "options".
        if (
            "options" in validation
            and value is not None
            and value not in validation["options"]
        ):
            self._add_validation_error(
                errors,
                index,
                "value",
                f"Must be one of: {', '.join(str(v) for v in validation['options'])}.",
            )

    @validates_schema(pass_many=True, skip_on_field_errors=False)
    def _validates_schema(self, data, many, **kwargs):
        data = data if many else [data]
        validation_errors = {}
        prev_keys = set()

        for index, extra in enumerate(data):
            # Strip string values and replace empty string values with None.
            if isinstance(extra["value"], str):
                extra["value"] = extra["value"].strip() or None

            value_type = extra.get("type")
            if value_type in ["str", "int", "float", "bool", "date", "dict", "list"]:
                if is_nested_type(value_type):
                    # Set the value to an empty list if it is missing.
                    if extra["value"] is None:
                        extra["value"] = []

                    if value_type == "list":
                        # List values should have no keys at all.
                        schema = ExtraSchema(
                            is_template=self.is_template, many=True, exclude=["key"]
                        )
                    else:
                        schema = ExtraSchema(is_template=self.is_template, many=True)

                    try:
                        extra["value"] = schema.load(extra["value"])
                    except ValidationError as e:
                        messages = e.messages
                        # The index of the current error will not be included
                        # otherwise.
                        if not is_iterable(extra["value"]):
                            messages = {0: messages}

                        validation_errors[index] = {"value": messages}

                    if "validation" in extra:
                        self._add_validation_error(
                            validation_errors,
                            index,
                            "validation",
                            "Cannot be used together with"
                            f" {pretty_type_name(value_type)}.",
                        )

                else:
                    if extra["value"] is not None:
                        try:
                            extra["value"] = _validate_value(extra["value"], value_type)
                        except ValueError as e:
                            self._add_validation_error(
                                validation_errors, index, "value", str(e)
                            )

                    if "validation" in extra:
                        if extra["validation"]:
                            try:
                                schema = _ValidationSchema(value_type)
                                extra["validation"] = schema.load(extra["validation"])
                                self._apply_validation(extra, validation_errors, index)

                            except ValidationError as e:
                                for message in schema._flatten_errors(e.messages):
                                    self._add_validation_error(
                                        validation_errors,
                                        index,
                                        "validation",
                                        message,
                                    )
                        else:
                            # Do not include empty validation objects.
                            del extra["validation"]

                if value_type not in ["int", "float"]:
                    if extra.get("unit") is not None:
                        self._add_validation_error(
                            validation_errors,
                            index,
                            "unit",
                            "Cannot be used together with"
                            f" {pretty_type_name(value_type)}.",
                        )

                    # Do not include the default unit value if it cannot be given.
                    if "unit" in extra:
                        del extra["unit"]
            else:
                self._add_validation_error(
                    validation_errors, index, "type", "Invalid value."
                )

            key = extra.get("key")
            if key in prev_keys:
                self._add_validation_error(
                    validation_errors, index, "key", "Duplicate value."
                )
            if key:
                prev_keys.add(key)

        if validation_errors:
            raise ValidationError(validation_errors)


class ExtrasField(Field):
    """Custom convenience field to process and validate extra record metadata.

    Uses :class:`ExtraSchema` for the validation of the metadata.

    :param is_template: (optional) See :class:`ExtraSchema`.
    """

    def __init__(self, *args, is_template=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_template = is_template
        self._validation_errors = {}

    def _extras_to_formdata(self, extras, errors):
        formdata = []

        for index, extra in enumerate(extras):
            if not isinstance(extra, dict):
                continue

            extra_formdata = {
                "type": {"value": "str", "errors": []},
                "key": {"value": None, "errors": []},
                "value": {"value": None, "errors": []},
                "unit": {"value": None, "errors": []},
                "validation": {"value": None, "errors": []},
            }

            for key, value in extra_formdata.items():
                if key in extra:
                    value["value"] = deepcopy(extra[key])

            for key, value in errors.get(index, {}).items():
                # Check if we actually have a list of errors for the field itself or a
                # nested errors dictionary, which will get handled via the recursion
                # (except for top level "_schema" errors).
                if isinstance(value, list) and key in extra_formdata:
                    for error in value:
                        extra_formdata[key]["errors"].append(error)

            if is_nested_type(extra.get("type")) and isinstance(
                extra.get("value"), list
            ):
                extra_formdata["value"]["value"] = self._extras_to_formdata(
                    extra["value"], errors.get(index, {}).get("value", {})
                )

            formdata.append(extra_formdata)

        return formdata

    def _value(self):
        if self.raw_data:
            try:
                extras = json.loads(self.raw_data[0])
            except:
                return []

            if not isinstance(extras, list):
                return []

            # Merge the validation errors into the formdata, as far as possible.
            return self._extras_to_formdata(extras, self._validation_errors)

        if self.data:
            return self._extras_to_formdata(self.data, {})

        return []

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                extras = json.loads(valuelist[0])
                schema = ExtraSchema(is_template=self.is_template, many=True)
                self.data = schema.load(extras)

            except ValidationError as e:
                self._validation_errors = e.messages
                raise ValueError(_("Invalid extra metadata.")) from e

            except Exception as e:
                raise ValueError(_("Invalid extra metadata.")) from e
        else:
            self.data = []
