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

from flask_login import current_user

from .models import Group
from kadi.lib.storage.misc import delete_thumbnail
from kadi.lib.storage.misc import save_as_thumbnail
from kadi.modules.permissions.models import Role


def get_user_groups(user=None):
    """Get all groups a user is a member of.

    Group membership currently works through roles. As long as a user has any role
    inside a group, they are a member of it. Note that inactive groups will be filtered
    out.

    :param user: (optional) The user to get the groups for. Defaults to the current
        user.
    :return: The groups of the given user as query.
    """
    user = user if user is not None else current_user

    group_ids_query = user.roles.filter(Role.object == "group").with_entities(
        Role.object_id
    )
    return Group.query.filter(Group.id.in_(group_ids_query), Group.state == "active")


def save_group_image(group, file_object):
    """Set an image file as a groups's profile image.

    Uses :func:`kadi.lib.storage.local.save_as_thumbnail` to create and save a thumbnail
    of the given image. If the image cannot be saved, :func:`delete_group_image` will be
    called.

    :param group: The group to set the new profile image for.
    :param file_object: See :func:`kadi.lib.storage.local.save_as_thumbnail`.
    """
    group.image_name = uuid4()

    if not save_as_thumbnail(str(group.image_name), file_object):
        delete_group_image(group)


def delete_group_image(group):
    """Delete a groups's profile image if one exists.

    Uses :func:`kadi.lib.storage.local.delete_thumbnail` to delete the actual thumbnail
    file.

    :param group: The group of which the profile image should be deleted.
    """
    if group.image_name:
        delete_thumbnail(str(group.image_name))
        group.image_name = None
