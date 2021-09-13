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
from marshmallow import ValidationError
from marshmallow.validate import Length
from marshmallow.validate import OneOf

from .models import Template
from kadi.lib.api.core import check_access_token_scopes
from kadi.lib.conversion import lower
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.schemas import check_duplicate_identifier
from kadi.lib.schemas import KadiSchema
from kadi.lib.schemas import NonEmptyString
from kadi.lib.schemas import validate_identifier
from kadi.lib.web import url_for
from kadi.modules.accounts.schemas import UserSchema
from kadi.modules.records.extras import ExtraSchema
from kadi.modules.records.schemas import RecordSchema


class TemplateSchema(KadiSchema):
    """Schema to represent generic templates.

    See :class:`.Template`.

    :param previous_template: (optional) A template whose identifier should be excluded
        when checking for duplicates while deserializing.
    :param template_type: (optional) The type of the template. Used when deserializing
        the data and it contains no type value.
    """

    id = fields.Integer(dump_only=True)

    identifier = NonEmptyString(
        required=True,
        filters=[lower, strip],
        validate=[
            Length(max=Template.Meta.check_constraints["identifier"]["length"]["max"]),
            validate_identifier,
        ],
    )

    title = NonEmptyString(
        required=True,
        filters=[normalize],
        validate=Length(max=Template.Meta.check_constraints["title"]["length"]["max"]),
    )

    description = fields.String(
        validate=Length(
            max=Template.Meta.check_constraints["description"]["length"]["max"]
        )
    )

    visibility = fields.String(
        validate=OneOf(Template.Meta.check_constraints["visibility"]["values"])
    )

    type = NonEmptyString(
        required=True,
        filters=[lower, strip],
        validate=OneOf(Template.Meta.check_constraints["type"]["values"]),
    )

    data = fields.Raw(required=True)

    plain_description = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    last_modified = fields.DateTime(dump_only=True)

    creator = fields.Nested(UserSchema, dump_only=True)

    _links = fields.Method("_generate_links")

    _actions = fields.Method("_generate_actions")

    def __init__(self, previous_template=None, template_type=None, **kwargs):
        super().__init__(**kwargs)
        self.previous_template = previous_template
        self.template_type = template_type

    @post_dump
    def _post_dump(self, data, **kwargs):
        if "creator" in data and not check_access_token_scopes("user.read"):
            del data["creator"]

        return data

    @post_load
    def _post_load(self, data, **kwargs):
        check_duplicate_identifier(data, Template, exclude=self.previous_template)

        if "data" not in data:
            return data

        current_type = data.get("type") or self.template_type

        try:
            if current_type == "record":
                data["data"] = RecordSchema(
                    check_identifier=False,
                    is_template=True,
                    exclude=["id", "visibility"],
                    partial=True,
                ).load(data["data"])

                # Since the RecordSchema is loaded partially, we fill any missing
                # default values manually.
                defaults = {
                    "title": "",
                    "identifier": "",
                    "type": None,
                    "description": "",
                    "license": None,
                    "tags": [],
                    "extras": [],
                }

                for key, value in defaults.items():
                    if key not in data["data"]:
                        data["data"][key] = value

            elif current_type == "extras":
                data["data"] = ExtraSchema(is_template=True, many=True).load(
                    data["data"]
                )

            else:
                # Will also be triggered when providing an invalid type directly.
                raise ValidationError("Invalid value.", "type")

        except ValidationError as e:
            raise ValidationError(e.messages, "data") from e

        return data

    def _generate_links(self, obj):
        links = {
            "self": url_for("api.get_template", id=obj.id),
            "user_roles": url_for("api.get_template_user_roles", id=obj.id),
            "group_roles": url_for("api.get_template_group_roles", id=obj.id),
        }

        if self._internal:
            links["view"] = url_for("templates.view_template", id=obj.id)

        return links

    def _generate_actions(self, obj):
        return {
            "edit": url_for("api.edit_template", id=obj.id),
            "delete": url_for("api.delete_template", id=obj.id),
            "add_user_role": url_for("api.add_template_user_role", id=obj.id),
            "add_group_role": url_for("api.add_template_group_role", id=obj.id),
        }
