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
from .models import Permission
from .models import Role
from kadi.ext.db import db
from kadi.lib.cache import memoize_request
from kadi.lib.db import get_class_by_tablename
from kadi.lib.db import TimestampMixin
from kadi.lib.utils import rgetattr
from kadi.modules.accounts.models import User
from kadi.modules.groups.models import Group
from kadi.modules.groups.utils import get_user_groups


def _get_permissions(subject, action, object_name, check_groups=True):
    group_permissions_query = None

    if isinstance(subject, User) and check_groups:
        group_ids_query = get_user_groups(subject).with_entities(Group.id)

        # Fine-grained permissions of the users's groups.
        group_permissions_query = Permission.query.join(Permission.groups).filter(
            Permission.action == action,
            Permission.object == object_name,
            Group.id.in_(group_ids_query),
        )

        # Role permissions of the users's groups.
        group_permissions_query = group_permissions_query.union(
            Permission.query.join(Permission.roles)
            .join(Role.groups)
            .filter(
                Permission.action == action,
                Permission.object == object_name,
                Group.id.in_(group_ids_query),
            )
        )

    # Fine-grained permissions of the subject.
    permissions_query = subject.permissions.filter(
        Permission.action == action, Permission.object == object_name
    )

    # Role permissions of the subject.
    permissions_query = permissions_query.union(
        Permission.query.join(Permission.roles)
        .join(Role.users if isinstance(subject, User) else Role.groups)
        .filter(
            Permission.action == action,
            Permission.object == object_name,
            subject.__class__.id == subject.id,
        )
    )

    if group_permissions_query:
        permissions_query = permissions_query.union(group_permissions_query)

    return permissions_query


@memoize_request
def has_permission(
    subject, action, object_name, object_id, check_groups=True, check_defaults=True
):
    """Check if a user or group has permission to perform a specific action.

    Includes all fine-grained permissions as well as all permissions from the roles of
    the user or group.

    :param subject: The user or group object.
    :param action: The action to check for.
    :param object_name: The type of object.
    :param object_id: The ID of a specific object or ``None`` for a global permission.
    :param check_groups: (optional) Flag indicating whether the groups of a user should
        be checked as well for their permissions.
    :param check_defaults: (optional) Flag indicating whether the default permissions of
        any object should be checked as well.
    :return: ``True`` if permission is granted, ``False`` otherwise or if the object
        instance to check does not exist.
    """

    # Check if the object class exists.
    model = get_class_by_tablename(object_name)
    if not model:
        return False

    permissions_query = _get_permissions(
        subject, action, object_name, check_groups=check_groups
    )

    # Check for any global action.
    if permissions_query.filter(Permission.object_id.is_(None)).first() is not None:
        return True

    if object_id is None:
        return False

    # Check if the object instance exists.
    object_instance = model.query.get(object_id)
    if not object_instance:
        return False

    # Check the default permissions.
    if check_defaults:
        default_permissions = rgetattr(object_instance, "Meta.permissions", {}).get(
            "default_permissions", {}
        )

        if action in default_permissions:
            for attr, val in default_permissions[action].items():
                if getattr(object_instance, attr, None) == val:
                    return True

    # Finally, check the regular permissions.
    return (
        permissions_query.filter(Permission.object_id == object_id).first() is not None
    )


def get_permitted_objects(
    subject, action, object_name, check_groups=True, check_defaults=True
):
    """Get all objects a user or group has a specific permission for.

    Includes all fine-grained permissions as well as all permissions from the roles of
    the user or group.

    :param subject: The user or group object.
    :param action: The action to check for.
    :param object_name: The type of object.
    :param check_groups: (optional) Flag indicating whether the groups of a user should
        be checked as well for their permissions.
    :param check_defaults: (optional) Flag indicating whether the default permissions of
        the objects should be checked as well.
    :return: The permitted objects as query or ``None`` if the object type does not
        exist.
    """

    # Check if the object class exists.
    model = get_class_by_tablename(object_name)
    if not model:
        return None

    permissions_query = _get_permissions(
        subject, action, object_name, check_groups=check_groups
    )

    # Check for any global action.
    if permissions_query.filter(Permission.object_id.is_(None)).first() is not None:
        return model.query

    # Get all objects for the regular permissions.
    objects_query = model.query.filter(
        model.id.in_(permissions_query.with_entities(Permission.object_id))
    )

    # Get all objects for the default permissions.
    if check_defaults:
        default_permissions = rgetattr(model, "Meta.permissions", {}).get(
            "default_permissions", {}
        )

        if action in default_permissions:
            filters = []
            for attr, val in default_permissions[action].items():
                filters.append(getattr(model, attr, None) == val)

            if filters:
                return objects_query.union(model.query.filter(db.or_(*filters)))

    return objects_query


def add_role(subject, object_name, object_id, role_name, update_timestamp=True):
    """Add an existing role to a user or group.

    :param subject: The user or group.
    :param object_name: The type of object the role refers to.
    :param object_id: The ID of the object.
    :param role_name: The name of the role.
    :param update_timestamp: (optional) Flag indicating whether the timestamp of the
        underlying object should be updated or not. The object needs to implement
        :class:`TimestampMixin` in that case.
    :return: ``True`` if the role was added successfully, ``False`` if the subject
        already has a role related to the given object.
    :raises ValueError: If no object or role with the given arguments exists or when
        trying to add a role to the object that is being referred to by that role.
    """
    model = get_class_by_tablename(object_name)
    object_instance = model.query.get(object_id)

    if object_instance is None:
        raise ValueError(f"Object '{object_name}' with ID {object_id} does not exist.")

    if subject.__tablename__ == object_name and subject.id == object_id:
        raise ValueError("Cannot add a role to the object to which the role refers.")

    roles = subject.roles.filter(
        Role.object == object_name, Role.object_id == object_id
    )

    if roles.count() > 0:
        return False

    role = Role.query.filter_by(
        object=object_name, object_id=object_id, name=role_name
    ).first()

    if not role:
        raise ValueError("A role with that name does not exist.")

    subject.roles.append(role)

    if update_timestamp and isinstance(object_instance, TimestampMixin):
        object_instance.update_timestamp()

    return True


def remove_role(subject, object_name, object_id, update_timestamp=True):
    """Remove an existing role of a user or group.

    :param subject: The user or group.
    :param object_name: The type of object the role refers to.
    :param object_id: The ID of the object.
    :param update_timestamp: (optional) Flag indicating whether the timestamp of the
        underlying object should be updated or not. The object needs to implement
        :class:`TimestampMixin` in that case.
    :return: ``True`` if the role was removed successfully, ``False`` if there was no
        role to remove.
    :raises ValueError: If no object with the given arguments exists.
    """
    model = get_class_by_tablename(object_name)
    object_instance = model.query.get(object_id)

    if object_instance is None:
        raise ValueError(f"Object '{object_name}' with ID {object_id} does not exist.")

    roles = subject.roles.filter(
        Role.object == object_name, Role.object_id == object_id
    )

    if roles.count() == 0:
        return False

    # As in certain circumstances (e.g. merging two users) a subject may have different
    # roles, all roles related to the given object will be removed.
    for role in roles:
        subject.roles.remove(role)

    if update_timestamp and isinstance(object_instance, TimestampMixin):
        object_instance.update_timestamp()

    return True


def set_system_role(user, system_role):
    """Set an existing system role for a given user.

    :param user: The user to set the system role for.
    :param system_role: The name of the system role to set.
    :return: ``True`` if the system role was set successfully, ``False`` if the given
        system role does not exist.
    """
    new_role = Role.query.filter_by(
        name=system_role, object=None, object_id=None
    ).first()

    if new_role is None:
        return False

    user_roles = user.roles.filter(Role.object.is_(None), Role.object_id.is_(None))
    # As in certain circumstances (e.g. merging two users) a user may have different
    # system roles, all of them will be removed.
    for role in user_roles:
        user.roles.remove(role)

    user.roles.append(new_role)
    return True


def setup_permissions(object_name, object_id):
    """Setup the default permissions of an object.

    The default actions and roles have to be specified in a ``Meta.permissions``
    attribute in each model.

    **Example:**

    .. code-block:: python3

        class Foo:
            class Meta:
                permissions = {
                    "actions": [
                        ("read", "Read this object."),
                        ("update", "Edit this object."),
                    ],
                    "roles": [("admin", ["read", "update"])],
                }

    :param object_name: The type of object the permissions refer to.
    :param object_id: The ID of the object.
    :return: ``True`` if the permissions were set up successfully, ``False`` otherwise.
    :raises ValueError: If no object with the given arguments exists.
    """
    model = get_class_by_tablename(object_name)
    object_instance = model.query.get(object_id)

    if object_instance is None:
        raise ValueError(f"Object '{object_name}' with ID {object_id} does not exist.")

    permissions = {}
    for action, _ in model.Meta.permissions["actions"]:
        permission = Permission.create(
            action=action, object=object_name, object_id=object_id
        )

        permissions[action] = permission

    for name, actions in model.Meta.permissions["roles"]:
        role = Role.create(name=name, object=object_name, object_id=object_id)

        for action in actions:
            role.permissions.append(permissions[action])

    return True


def delete_permissions(object_name, object_id):
    """Delete all permissions of an object.

    :param object_name: The type of object the permissions refer to.
    :param object_id: The ID of the object.
    """
    roles = Role.query.filter(Role.object == object_name, Role.object_id == object_id)

    for role in roles:
        db.session.delete(role)

    permissions = Permission.query.filter(
        Permission.object == object_name, Permission.object_id == object_id
    )

    for permission in permissions:
        db.session.delete(permission)
