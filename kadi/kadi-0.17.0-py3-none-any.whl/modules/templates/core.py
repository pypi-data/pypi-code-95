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
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .models import Template
from kadi.ext.db import db
from kadi.lib.conversion import strip_markdown
from kadi.lib.db import update_object
from kadi.modules.permissions.core import add_role
from kadi.modules.permissions.core import delete_permissions
from kadi.modules.permissions.core import setup_permissions


def create_template(
    *, identifier, title, type, data, creator=None, description="", visibility="private"
):
    """Create a new template.

    This will also create all default permissions of the template.

    Note that this function issues a database commit or rollback.

    :param identifier: See :attr:`.Template.identifier`.
    :param title: See :attr:`.Template.title`.
    :param type: See :attr:`.Template.type`.
    :param data: See :attr:`.Template.data`.
    :param creator: (optional) The user that created the template. Defaults to the
        current user.
    :param description: (optional) See :attr:`.Template.description`.
    :param visibility: (optional) See :attr:`.Template.visibility`.
    :return: The created template or ``None`` if the template could not be created.
    """
    creator = creator if creator is not None else current_user

    # Basic sanity check of the data.
    if (type == "record" and not isinstance(data, dict)) or (
        type == "extras" and not isinstance(data, list)
    ):
        return None

    template = Template.create(
        identifier=identifier,
        title=title,
        type=type,
        data=data,
        creator=creator,
        description=description,
        plain_description=strip_markdown(description),
        visibility=visibility,
    )

    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return None

    setup_permissions("template", template.id)
    add_role(creator, "template", template.id, "admin")

    db.session.commit()
    return template


def update_template(template, **kwargs):
    r"""Update an existing template.

    Note that this function issues a database commit or rollback.

    :param template: The template to update.
    :param \**kwargs: Keyword arguments that will be passed to
        :func:`kadi.lib.db.update_object`.
    :return: ``True`` if the template was updated successfully, ``False`` otherwise.
    """
    if "description" in kwargs:
        kwargs["plain_description"] = strip_markdown(kwargs["description"])

    update_object(template, **kwargs)

    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return False

    db.session.commit()
    return True


def delete_template(template):
    """Delete an existing template.

    This will completely delete the template from the database.

    :param template: The template to delete.
    """
    delete_permissions("template", template.id)
    db.session.delete(template)
