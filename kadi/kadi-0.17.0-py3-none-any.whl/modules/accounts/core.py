# Copyright 2021 Karlsruhe Institute of Technology
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
from .models import User
from kadi.ext.db import db
from kadi.modules.accounts.utils import delete_user_image
from kadi.modules.collections.core import purge_collection
from kadi.modules.groups.core import purge_group
from kadi.modules.permissions.core import set_system_role
from kadi.modules.permissions.models import Role
from kadi.modules.records.core import purge_record
from kadi.modules.templates.core import delete_template


def purge_user(user):
    """Purge an existing user.

    This will completely delete the user and all their resources from the database.

    Note that this function issues one or more database commits.

    :param user: The user to purge.
    """
    delete_user_image(user)

    for record in user.records:
        purge_record(record)

    for collection in user.collections:
        purge_collection(collection)

    for group in user.groups:
        purge_group(group)

    for template in user.templates:
        delete_template(template)

    # We need to remove the reference to the current identity separately because of the
    # cyclic user/identity reference.
    user.identity = None
    db.session.commit()

    # Also delete all users that may have been merged into the user to delete. These
    # users should not be referenced anywhere anymore.
    for merged_user in User.query.filter(User.new_user_id == user.id):
        db.session.delete(merged_user)

    db.session.delete(user)


def merge_users(first_user, second_user):
    """Merge two users together.

    This will migrate the ownership of all identities, resources and permissions from
    the second user to the first user. The first user is then also able to log in using
    both identities.

    :param first_user: The user to merge the second user into.
    :param second_user: The user to merge into the first user.
    """
    delete_user_image(second_user)

    # Relationships to migrate.
    relationships = [
        "identities",
        "records",
        "files",
        "temporary_files",
        "uploads",
        "collections",
        "groups",
        "revisions",
        "templates",
        "workflows",
        "tasks",
        "notifications",
        "access_tokens",
        "oauth2_tokens",
    ]
    for relationship in relationships:
        getattr(second_user, relationship).update({"user_id": first_user.id})

    old_system_role = first_user.roles.filter(
        Role.object.is_(None), Role.object_id.is_(None)
    ).first()

    # Migrate permissions and roles.
    for permission in second_user.permissions:
        if permission not in first_user.permissions:
            first_user.permissions.append(permission)

    second_user.permissions = []

    for role in second_user.roles:
        if role not in first_user.roles:
            first_user.roles.append(role)

    second_user.roles = []

    # In case both users had different system roles and/or resource roles, the new user
    # could have multiple of such roles. Since roles are simply groupings of permissions
    # and only the permissions themselves are checked, this does not really matter. We
    # still set at least the system role to the one of the first user. Other roles would
    # be unified once they are removed or changed (except for the creator's role of a
    # resource, which should always grant all permissions anyways).
    set_system_role(first_user, old_system_role.name)

    # Make sure to remove the reference to the merged user's current identity and to set
    # the ID of the new user, marking the old user as merged.
    second_user.identity = None
    second_user.new_user_id = first_user.id
