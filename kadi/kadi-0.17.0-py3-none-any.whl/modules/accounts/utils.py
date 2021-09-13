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
from uuid import uuid4

from flask import current_app
from flask_login import login_user as _login_user

from .schemas import UserSchema
from kadi.ext.db import db
from kadi.lib.storage.misc import delete_thumbnail
from kadi.lib.storage.misc import save_as_thumbnail
from kadi.lib.utils import compact_json


def login_user(identity, **kwargs):
    r"""Login a user by their identity.

    Wraps Flask-Login's ``login_user`` function but also makes sure to update the user's
    current identity.

    :param identity: The identity to log in with.
    :return: ``True`` if the login was successful, ``False`` otherwise.
    """
    user = identity.user
    user.identity = identity

    return _login_user(user, force=True)


def save_user_image(user, file_object):
    """Set an image file as a user's profile image.

    Uses :func:`kadi.lib.storage.local.save_as_thumbnail` to create and save a thumbnail
    of the given image. If the image cannot be saved, :func:`delete_user_image` will be
    called.

    :param user: The user to set the new profile image for.
    :param file_object: See :func:`kadi.lib.storage.local.save_as_thumbnail`.
    """
    user.image_name = uuid4()
    if not save_as_thumbnail(str(user.image_name), file_object):
        delete_user_image(user)


def delete_user_image(user):
    """Delete a user's profile image if one exists.

    Uses :func:`kadi.lib.storage.local.delete_thumbnail` to delete the actual thumbnail
    file.

    :param user: The user whose profile image should be deleted.
    """
    if user.image_name:
        delete_thumbnail(str(user.image_name))
        user.image_name = None


def json_user(user):
    """Convert a user into a JSON representation.

    :param user: The user to convert.
    :return: The converted user.
    """
    schema = UserSchema(_internal=True, exclude=["about"])
    return compact_json(schema.dump(user))


def get_filtered_user_ids(filter_term):
    """Get all IDs of users filtered by the given term.

    Convenience function to filter users based on their identities. Note that users with
    multiple identities are only returned once and merged users are always excluded, as
    they do not have any identities anymore.

    :param filter_term: The term to filter the users with based on the display name and
        username of each user's identities.
    :return: The filtered user IDs as query.
    """
    identity_queries = []

    for provider_config in current_app.config["AUTH_PROVIDERS"].values():
        model = provider_config["identity_class"]
        identities_query = model.query.filter(
            db.or_(
                model.displayname.ilike(f"%{filter_term}%"),
                model.username.ilike(f"%{filter_term}%"),
            ),
        ).with_entities(model.user_id.label("id"))

        identity_queries.append(identities_query)

    return identity_queries[0].union(*identity_queries[1:])
