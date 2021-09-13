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
from kadi.ext.db import db
from kadi.lib.db import generate_check_constraints
from kadi.lib.db import TimestampMixin
from kadi.lib.utils import SimpleReprMixin
from kadi.modules.records.extras import ExtrasJSONB


class Template(SimpleReprMixin, TimestampMixin, db.Model):
    """Model to represent generic templates."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "user_id", "identifier", "visibility", "type"]
        """See :class:`.SimpleReprMixin`."""

        permissions = {
            "actions": [
                ("read", "View this template."),
                ("update", "Edit this template."),
                ("permissions", "Manage permissions of this template."),
                ("delete", "Delete this template."),
            ],
            "roles": [
                ("member", ["read"]),
                ("editor", ["read", "update"]),
                ("admin", ["read", "update", "permissions", "delete"]),
            ],
            "global_actions": [
                ("create", "Create templates."),
                ("read", "View any template."),
                ("update", "Edit any template."),
                ("permissions", "Manage permissions of any template."),
                ("delete", "Delete any template."),
            ],
            "default_permissions": {"read": {"visibility": "public"}},
        }
        """Possible permissions and roles for templates.

        See :mod:`kadi.modules.permissions`.
        """

        check_constraints = {
            "identifier": {"length": {"max": 50}},
            "title": {"length": {"max": 150}},
            "description": {"length": {"max": 10000}},
            "visibility": {"values": ["private", "public"]},
            "type": {"values": ["record", "extras"]},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "template"

    __table_args__ = generate_check_constraints(Meta.check_constraints)

    id = db.Column(db.Integer, primary_key=True)
    """The ID of the template, auto incremented."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    """The ID of the user that created the template."""

    identifier = db.Column(db.Text, index=True, unique=True, nullable=False)
    """The unique identifier of the template.

    Restricted to a maximum length of 50 characters.
    """

    title = db.Column(db.Text, nullable=False)
    """The title of the template.

    Restricted to a maximum length of 150 characters.
    """

    description = db.Column(db.Text, nullable=False)
    """The description of the template.

    Restricted to a maximum length of 10000 characters.
    """

    plain_description = db.Column(db.Text, nullable=False)
    """The plain description of the template.

    Equal to the normal description with the difference that most markdown is stripped
    out.
    """

    visibility = db.Column(db.Text, index=True, nullable=False)
    """The default visibility of the template.

    One of ``"private"`` or ``"public"``.
    """

    type = db.Column(db.Text, index=True, nullable=False)
    """The type of the template.

    One of ``"record"`` or ``"extras"``.
    """

    data = db.Column(ExtrasJSONB, nullable=False)
    """The data of the template depending on its type.

    For each of the template types, the data consists of:

    * ``"record"``: A JSON object containing all relevant record properties as keys with
      corresponding values. See also :class:`.Record`.
    * ``"extras"``: An array of JSON objects containing the extra metadata of a record.
      See also :attr:`.Record.extras`.
    """

    creator = db.relationship("User", back_populates="templates")

    @classmethod
    def create(
        cls,
        *,
        creator,
        identifier,
        title,
        type,
        data,
        description="",
        plain_description="",
        visibility="private",
    ):
        """Create a new template and add it to the database session.

        :param creator: The user that created the template.
        :param identifier: The identifier of the template.
        :param title: The title of the template.
        :param type: The type of the template.
        :param data: The data of the template.
        :param description: (optional) The description of the template.
        :param plain_description: (optional) The plain description of the template.
        :param visibility: (optional) The default visibility of the template.
        :return: The new :class:`.Template` object.
        """
        template = cls(
            creator=creator,
            identifier=identifier,
            title=title,
            type=type,
            data=data,
            description=description,
            plain_description=plain_description,
            visibility=visibility,
        )

        db.session.add(template)
        return template
