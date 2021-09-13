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
from flask import render_template
from flask_login import current_user
from sqlalchemy.orm.exc import StaleDataError

from .utils import add_link as _add_link
from .utils import remove_link as _remove_link
from kadi.ext.db import db
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.exceptions import KadiPermissionError
from kadi.modules.accounts.models import User
from kadi.modules.accounts.utils import get_filtered_user_ids
from kadi.modules.groups.models import Group
from kadi.modules.permissions.core import add_role as _add_role
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.core import remove_role as _remove_role
from kadi.modules.permissions.models import Role
from kadi.modules.permissions.schemas import GroupRoleSchema
from kadi.modules.permissions.schemas import UserRoleSchema
from kadi.modules.permissions.utils import get_group_roles
from kadi.modules.permissions.utils import get_object_roles
from kadi.modules.permissions.utils import get_user_roles


def add_link(relationship, resource, user=None):
    """Convenience function to link two resources together.

    For ease of use in API endpoints. Uses :func:`kadi.lib.resources.utils.add_link`.

    Note that this function may issue a database commit.

    :param relationship: See :func:`kadi.lib.resources.utils.add_link`.
    :param resource: See :func:`kadi.lib.resources.utils.add_link`.
    :param user: (optional) See :func:`kadi.lib.resources.utils.add_link`.
    :return: A JSON response depending on the success of the operation.
    """
    user = user if user is not None else current_user

    try:
        if _add_link(relationship, resource, user=user):
            db.session.commit()
            return json_response(201)

        return json_error_response(409, description="Link already exists.")

    except KadiPermissionError as e:
        return json_error_response(403, description=str(e))


def remove_link(relationship, resource, user=None):
    """Convenience function to remove the link between two resources.

    For ease of use in API endpoints. Uses :func:`kadi.lib.resources.utils.remove_link`.

    Note that this function may issue a database commit.

    :param relationship: See :func:`kadi.lib.resources.utils.remove_link`.
    :param resource: See :func:`kadi.lib.resources.utils.remove_link`.
    :param user: (optional) See :func:`kadi.lib.resources.utils.remove_link`.
    :return: A JSON response depending on the success of the operation.
    """
    user = user if user is not None else current_user

    try:
        if _remove_link(relationship, resource, user=user):
            db.session.commit()
            return json_response(204)

        return json_error_response(404, description="Link does not exist.")

    except KadiPermissionError as e:
        return json_error_response(403, description=str(e))


def add_role(subject, resource, role_name, user=None):
    """Convenience function to add an existing role to a user or group.

    For ease of use in API endpoints. Uses
    :func:`kadi.modules.permissions.utils.add_role`.

    Note that this function may issue a database commit.

    :param subject: See :func:`kadi.modules.permissions.utils.add_role`.
    :param resource: The resource the role refers to, an instance of :class:`.Record`,
        :class:`.Collection`, :class:`.Group` or :class:`.Template`.
    :param role_name: See :func:`kadi.modules.permissions.utils.add_role`.
    :param user: (optional) The user performing the operation. Defaults to the current
        user.
    :return: A JSON response depending on the success of the operation.
    """
    user = user if user is not None else current_user

    if isinstance(subject, Group) and not has_permission(
        user, "read", "group", subject.id
    ):
        return json_error_response(403, "No permission to add role to group.")

    try:
        if _add_role(subject, resource.__tablename__, resource.id, role_name):
            db.session.commit()
            return json_response(201)

        return json_error_response(
            409, description="A role for that resource already exists."
        )

    except ValueError as e:
        return json_error_response(400, description=str(e))


def remove_role(subject, resource):
    """Convenience function to remove an existing role of a user or group.

    For ease of use in API endpoints. Uses
    :func:`kadi.modules.permissions.utils.remove_role`. If the given subject is the
    creator of the given resource, the role will not be removed.

    Note that this function may issue a database commit.

    :param subject: See :func:`kadi.modules.permissions.utils.remove_role`.
    :param resource: The resource the role refers to, an instance of :class:`.Record`,
        :class:`.Collection`, :class:`.Group` or :class:`.Template`.
    :return: A JSON response depending on the success of the operation.
    """
    if isinstance(subject, User) and subject == resource.creator:
        return json_error_response(409, description="Cannot remove the creator's role.")

    if _remove_role(subject, resource.__tablename__, resource.id):
        db.session.commit()
        return json_response(204)

    return json_error_response(404, description="Role does not exist.")


def change_role(subject, resource, role_name):
    """Convenience function to change an existing role of a user or group.

    For ease of use in API endpoints. If the given subject is the creator of the given
    resource, the role will not be changed. Uses
    :func:`kadi.modules.permissions.utils.remove_role` and
    :func:`kadi.modules.permissions.utils.add_role`.

    Note that this function may issue a database commit or rollback.

    :param subject: The user or group.
    :param resource: The resource the role refers to, an instance of :class:`.Record`,
        :class:`.Collection`, :class:`.Group` or :class:`.Template`.
    :param role_name: The name of the role to change.
    :return: A JSON response depending on the success of the operation.
    """
    if isinstance(subject, User) and subject == resource.creator:
        return json_error_response(409, description="Cannot change the creator's role.")

    if _remove_role(subject, resource.__tablename__, resource.id):
        try:
            _add_role(subject, resource.__tablename__, resource.id, role_name)
            db.session.commit()
            return json_response(204)

        except ValueError as e:
            return json_error_response(400, description=str(e))

        # Gracefully handle potential race conditions.
        except StaleDataError:
            db.session.rollback()
            return json_error_response(409, description="Error changing role.")

    return json_error_response(404, description="Role does not exist.")


def get_selected_resources(
    model, page=1, term="", exclude=None, actions=None, filters=None, user=None
):
    """Convenience function to search resources for use in dynamic selections.

    For ease of use in API endpoints. Used in conjunction with "Select2" to search
    resources via dyamic selection fields. Only the resources the given user has read
    permission for are returned.

    :param model: The resource model to search, one of :class:`.Record`,
        :class:`.Collection` or :class:`.Group`.
    :param page: (optional) The current page.
    :param term: (optional) The search term. Will be used to search the title and
        identifier of the resource (case insensitive).
    :param exclude: (optional) A list of resource IDs to exclude in the results.
        Defaults to an empty list.
    :param actions: (optional) Further actions to check the access permissions for.
    :param filters: (optional) Additional filter expressions to apply to the respective
        resource query.
    :param user: (optional) The user performing the search. Defaults to the current
        user.
    :return: A JSON response containing the results in the following form, assuming the
        search results consist of a single :class:`.Record`:

        .. code-block:: js

            {
                "results": [
                    {
                        "id": 1,
                        "text": "@sample-record-1",
                        "body": "<optional HTML body>",
                    }
                ],
                "pagination": {"more": false},
            }
    """
    exclude = exclude if exclude is not None else []
    actions = actions if actions is not None else []
    filters = filters if filters is not None else []
    user = user if user is not None else current_user
    object_name = model.__tablename__

    resources_query = get_permitted_objects(user, "read", object_name).filter(
        db.or_(model.title.ilike(f"%{term}%"), model.identifier.ilike(f"%{term}%")),
        model.id.notin_(exclude),
        model.state == "active",
    )

    for action in set(actions):
        resources_query = get_permitted_objects(user, action, object_name).intersect(
            resources_query
        )

    if filters:
        resources_query = resources_query.filter(*filters)

    paginated_resources = resources_query.order_by(model.title).paginate(
        page, 10, False
    )

    data = {"results": [], "pagination": {"more": paginated_resources.has_next}}
    for resource in paginated_resources.items:
        data["results"].append(
            {
                "id": resource.id,
                "text": f"@{resource.identifier}",
                "body": render_template(
                    "snippets/resources/select.html", resource=resource
                ),
            }
        )

    return json_response(200, data)


def get_resource_user_roles(
    resource, page=1, per_page=10, filter_term="", exclude=None
):
    """Get the paginated user roles of a resource.

    :param resource: The resource to get the user roles of. One of :class:`.Record`,
        :class:`.Collection` or :class:`.Template`.
    :param page: (optional) The current page.
     :param per_page: (optional) Items per page.
    :param filter_term: (optional) A query to filter the users by their username or
        display name.
    :param exclude: (optional) A list of user IDs to exclude in the results.
    :return: A tuple containing a list of deserialized user roles and the total amount
        of user roles.
    """
    exclude = exclude if exclude is not None else []
    object_name = resource.__class__.__tablename__

    when = []
    for index, role in enumerate(get_object_roles(object_name)):
        when.append((role["name"], index))

    paginated_user_roles = (
        get_user_roles(object_name, object_id=resource.id)
        .filter(
            User.id.in_(get_filtered_user_ids(filter_term)),
            User.id.notin_(exclude),
        )
        .order_by(
            (User.id == resource.user_id).desc(),
            db.case(when, value=Role.name).desc(),
            User.id,
        )
        .paginate(page, per_page, False)
    )

    items = UserRoleSchema(obj=resource).dump_from_iterable(paginated_user_roles.items)

    return items, paginated_user_roles.total


def get_resource_group_roles(resource, page=1, per_page=10, filter_term="", user=None):
    """Get the paginated group roles of a resource.

    This includes the special case of the given user not having read access to a group
    (any more) but wanting to change/remove permissions of the group, if the permissions
    of the user allow them to. Since such groups should still be listed, we include them
    using a limited subset of group attributes.

    :param resource: The resource to get the group roles of. One of :class:`.Record`,
        :class:`.Collection` or :class:`.Template`.
    :param page: (optional) The current page.
     :param per_page: (optional) Items per page.
    :param filter_term: (optional) A query to filter the groups by their title or
        identifier.
    :param user: (optional) The user to check for any permissions regarding the
        resulting groups. Defaults to the current user.
    :return: A tuple containing a list of deserialized group roles and the total amount
        of user roles.
    """
    user = user if user is not None else current_user
    object_name = resource.__class__.__tablename__

    group_ids_query = get_permitted_objects(user, "read", "group").with_entities(
        Group.id
    )

    # Already filtered for active groups.
    group_roles_query = get_group_roles(object_name, object_id=resource.id).filter(
        db.or_(
            Group.title.ilike(f"%{filter_term}%"),
            Group.identifier.ilike(f"%{filter_term}%"),
        )
    )

    # Check whether we have the special case of including all group roles.
    include_all_groups = False

    if has_permission(user, "permissions", object_name, resource.id):
        include_all_groups = True
    else:
        group_roles_query = group_roles_query.filter(Group.id.in_(group_ids_query))

    when = []
    for index, role in enumerate(get_object_roles(object_name)):
        when.append((role["name"], index))

    paginated_group_roles = group_roles_query.order_by(
        db.case(when, value=Role.name).desc(), Group.id
    ).paginate(page, per_page, False)

    items = GroupRoleSchema(obj=resource).dump_from_iterable(
        paginated_group_roles.items
    )

    if include_all_groups:
        group_ids = {g.id for g in group_ids_query}

        for item in items:
            group = item["group"]

            if group["id"] not in group_ids:
                # Replace the group metadata with a limited subset of group attributes.
                item["group"] = {
                    "id": group["id"],
                    "title": group["title"],
                    "identifier": group["identifier"],
                    "visibility": group["visibility"],
                }

    return items, paginated_group_roles.total
