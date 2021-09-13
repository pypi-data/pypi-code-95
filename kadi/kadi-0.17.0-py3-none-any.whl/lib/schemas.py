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
from flask import abort
from flask import request
from marshmallow import fields
from marshmallow import Schema
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

from .validation import validate_identifier as _validate_identifier
from .validation import validate_mimetype as _validate_mimetype
from .validation import validate_uuid
from .validation import validator
from kadi.lib.api.core import json_error_response
from kadi.lib.api.utils import is_internal_api_request


class KadiSchema(Schema):
    """Base class for all schemas.

    :param _internal: (optional) Flag indicating whether additional data that's only
        relevant for internal usage should be included when serializing objects. If not
        set, the value returned by :func:`kadi.lib.api.utils.is_internal_api_request`
        will be taken instead. Note that this flag will generally not get passed
        automatically to any nested schemas.
    """

    def __init__(self, *args, _internal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._internal = _internal

        if self._internal is None:
            self._internal = is_internal_api_request()

    def load_or_400(self, data=None):
        """Try to deserialize the given input.

        Will try to deserialize/load the given input data using the schemas ``load``
        method. If the validation fails, automatically abort the current request with
        status code 400 and the corresponding error response as JSON.

        :param data: (optional) The input to deserialize. Defaults to the JSON body of
            the current request.
        :return: The deserialized input.
        """
        try:
            data = data if data is not None else request.get_json()
        except BadRequest as e:
            abort(json_error_response(400, description=e.description))

        if data is None:
            abort(json_error_response(400, description="Missing JSON body."))

        try:
            data = self.load(data)
        except ValidationError as e:
            abort(json_error_response(400, errors=e.messages))

        return data


class NonEmptyString(fields.String):
    """String field that does not allow empty or whitespace only strings.

    Additionally allows to set custom filter functions that can be used to further
    convert the output for deserialization.

    :param filters: (optional) List of filter/conversion functions.
    """

    def __init__(self, *args, filters=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters = filters if filters is not None else []

    def _deserialize(self, value, attr, data, **kwargs):
        output = super()._deserialize(value, attr, data, **kwargs)

        if not output.strip():
            raise ValidationError("String must not be empty.")

        for _filter in self.filters:
            output = _filter(output)

        return output


class SortedPluck(fields.Pluck):
    """Pluck field that sorts its serialized output in case ``many`` is set."""

    def _serialize(self, nested_obj, attr, obj, **kwargs):
        output = super()._serialize(nested_obj, attr, obj, **kwargs)

        if self.many:
            return sorted(output)

        return output


class ValidateUUID:
    """Validate a UUID of a specific version in a schema field.

    :param version: (optional) The UUID version.
    """

    def __init__(self, version=4):
        self.version = version

    @validator(ValidationError)
    def __call__(self, value):
        validate_uuid(value, version=self.version)


@validator(ValidationError)
def validate_identifier(value):
    """Validate an identifier in a schema field.

    Uses :func:`kadi.lib.validation.validate_identifier`.

    :param value: The field value.
    """
    _validate_identifier(value)


@validator(ValidationError)
def validate_mimetype(value):
    """Validate a MIME type in a schema field.

    Uses :func:`kadi.lib.validation.validate_mimetype`.

    :param value: The field value.
    """
    _validate_mimetype(value)


def check_duplicate_identifier(data, model, exclude=None):
    """Check for a duplicate identifier in a schema.

    Has to be called manually after the usual validation as further arguments are needed
    for this check.

    :param data: The schema's data.
    :param model: The model the check the identifier in.
    :param exclude: (optional) An object that should be excluded in the check.
    """
    identifier = data.get("identifier")
    if identifier is not None:
        obj_to_check = model.query.filter_by(identifier=identifier).first()

        if obj_to_check is not None and (exclude is None or exclude != obj_to_check):
            raise ValidationError("Identifier is already in use.", "identifier")
