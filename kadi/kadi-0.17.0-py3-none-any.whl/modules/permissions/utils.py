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
from functools import wraps

from flask import abort
from flask import current_app
from flask_login import current_user
from flask_login import login_required

from .core import has_permission
from .models import Permission
from .models import Role
from kadi.ext.db import db
from kadi.lib.db import get_class_by_tablename
from kadi.lib.utils import rgetattr
from kadi.modules.accounts.models import User
from kadi.modules.groups.models import Group


def permission_required(action, object_name, object_id_identifier, status_code=403):
    """Decorator to add access restrictions to a view function.

    If the current user is not authenticated, the decorator will behave the same as
    Flask-Login's ``login_required`` decorator. If the object or object instance to
    check do not exist, the request will automatically get aborted with a 404 status
    code.

    Uses :func:`kadi.modules.permissions.core.has_permission` to check for access
    permissions.

    :param action: See :func:`kadi.modules.permissions.core.has_permission`.
    :param object_name: See :func:`kadi.modules.permissions.core.has_permission`.
    :param object_id_identifier: The name of the variable to use as ``object_id``, which
        needs to be part of the keyword arguments of the decorated function. May also be
        ``None``.
    :param status_code: (optional) The status code to use if no permission was granted.
    """

    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            object_id = None
            if object_id_identifier is not None:
                object_id = kwargs[object_id_identifier]

            model = get_class_by_tablename(object_name)

            # Always return 404 if the model or object do not exist.
            if model is None or (
                object_id is not None
                and not model.query.filter_by(id=object_id)
                .with_entities(model.id)
                .first()
            ):
                abort(404)

            if not has_permission(
                current_user, action, object_name, object_id=object_id
            ):
                abort(status_code)

            return func(*args, **kwargs)

        return login_required(decorated_view)

    return decorator


def initialize_system_role(role_name):
    """Initialize a system role with corresponding global permissions.

    Will create the given system role as defined in ``SYSTEM_ROLES`` in the
    application's configuration as well as all permissions for the global actions of the
    listed objects, which have to be specified in the ``Meta.permissions`` attribute in
    each corresponding model.

    **Example:**

    .. code-block:: python3

        class Foo:
            class Meta:
                permissions = {
                    "global_actions": [
                        ("create", "Create objects."),
                        ("read", "Read all objects."),
                    ],
                }

    :param role_name: The name of the system role to initialize.
    :return: The created role object or ``None`` if the role already exists.
    :raises ValueError: If the given role is not a configured system role or if any of
        the specified global actions is invalid.
    """
    system_roles = current_app.config["SYSTEM_ROLES"]

    if role_name not in system_roles:
        raise ValueError(f"Role '{role_name}' is not a configured system role.")

    if (
        Role.query.filter_by(name=role_name, object=None, object_id=None).first()
        is not None
    ):
        return None

    role = Role.create(name=role_name)

    for object_name, global_actions in system_roles[role_name].items():
        model = get_class_by_tablename(object_name)

        model_actions = rgetattr(model, "Meta.permissions", {}).get(
            "global_actions", []
        )
        model_actions = [action_description[0] for action_description in model_actions]

        for action in global_actions:
            if action not in model_actions:
                raise ValueError(
                    f"Action '{action}' is not valid for model '{object_name}'."
                )

            permission = Permission.query.filter_by(
                action=action, object=object_name, object_id=None
            ).first()

            if permission is None:
                permission = Permission.create(action=action, object=object_name)

            if permission not in role.permissions:
                role.permissions.append(permission)

    return role


def get_user_roles(object_name, object_id=None):
    """Get all users and roles for a specific object or object type.

    :param object_name: The type of the object.
    :param object_id: (optional) The ID of a specific object.
    :return: The users and corresponding roles of the object(s) as query object.
    """
    user_roles_query = (
        db.session.query(User, Role).join(User.roles).filter(Role.object == object_name)
    )

    if object_id:
        user_roles_query = user_roles_query.filter(Role.object_id == object_id)

    return user_roles_query


def get_group_roles(object_name, object_id=None):
    """Get all groups and roles for a specific object or object type.

    Note that inactive groups will be filtered out.

    :param object_name: The type of the object.
    :param object_id: (optional) The ID of a specific object.
    :return: The groups and corresponding roles of the object(s) as query object.
    """
    group_roles_query = (
        db.session.query(Group, Role)
        .join(Group.roles)
        .filter(Role.object == object_name, Group.state == "active")
    )

    if object_id:
        group_roles_query = group_roles_query.filter(Role.object_id == object_id)

    return group_roles_query


def get_object_roles(object_name):
    """Get all possible roles and corresponding permissions of an object type.

    :param object_name: The type of the object.
    :return: A list of dictionaries in the following form:

        .. code-block:: python3

            [
                {
                    "name": "admin",
                    "permissions": [
                        {
                            "action": "read,
                            "description": "Read this resource.",
                        }
                    ]
                }
            ]
    """
    model = get_class_by_tablename(object_name)
    roles = [
        {
            "name": role,
            "permissions": [
                {
                    "action": action,
                    "description": get_action_description(action, object_name),
                }
                for action in actions
            ],
        }
        for role, actions in rgetattr(model, "Meta.permissions", {}).get("roles", [])
    ]

    return roles


def get_action_description(action, object_name):
    """Get the description of an action corresponding to a specific permission.

    :param action: The name of the action.
    :param object_name: The type of the object the action belongs to.
    :return: The description or ``None`` if no suitable action or no model corresponding
        to the object type could be found.
    """
    model = get_class_by_tablename(object_name)
    actions = rgetattr(model, "Meta.permissions", {}).get("actions", [])

    for object_action, description in actions:
        if object_action == action:
            return description

    return None
