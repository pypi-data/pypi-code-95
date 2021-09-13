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
from flask_login import login_required

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.api.core import scopes_required
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.api.utils import status
from kadi.lib.conversion import normalize
from kadi.lib.conversion import parse_boolean_string
from kadi.lib.conversion import strip
from kadi.lib.resources.api import get_resource_user_roles
from kadi.lib.revisions.schemas import ObjectRevisionSchema
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.collections.models import Collection
from kadi.modules.collections.schemas import CollectionSchema
from kadi.modules.groups.core import search_groups
from kadi.modules.groups.models import Group
from kadi.modules.groups.schemas import GroupSchema
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.utils import permission_required
from kadi.modules.records.models import Record
from kadi.modules.records.schemas import RecordSchema
from kadi.modules.templates.models import Template
from kadi.modules.templates.schemas import TemplateSchema


@bp.get("/groups")
@login_required
@scopes_required("group.read")
@paginated(page_max=100)
@qparam("query", parse=strip, description="The search query.")
@qparam("sort", default="_score", description="The order of the search results.")
@qparam(
    "hide_public",
    default=False,
    parse=parse_boolean_string,
    description="Flag indicating whether public groups should be excluded in the"
    " results.",
)
@qparam(
    "member_only",
    default=False,
    parse=parse_boolean_string,
    description="Flag indicating whether groups without membership should be excluded"
    " in the results.",
)
@status(200, "Return a paginated list of groups.")
def get_groups(page, per_page, qparams):
    """Get all groups or search and filter for specific groups.

    See :func:`kadi.modules.groups.core.search_groups` for a more detailed explanation
    of some of the query parameters (in Python syntax).
    """
    groups, total_groups = search_groups(
        qparams["query"],
        sort=qparams["sort"],
        hide_public=qparams["hide_public"],
        member_only=qparams["member_only"],
        page=page,
        per_page=per_page,
    )

    data = {
        "items": GroupSchema(many=True).dump(groups),
        "_actions": {"new_group": url_for("api.new_group")},
        **create_pagination_data(
            total_groups, page, per_page, "api.get_groups", **qparams
        ),
    }

    return json_response(200, data)


@bp.get("/groups/<int:id>")
@permission_required("read", "group", "id")
@scopes_required("group.read")
@status(200, "Return the group.")
def get_group(id):
    """Get the group specified by the given *id*."""
    group = Group.query.get_active_or_404(id)
    return json_response(200, GroupSchema().dump(group))


@bp.get("/groups/identifier/<identifier:identifier>")
@login_required
@scopes_required("group.read")
@status(200, "Return the group.")
def get_group_by_identifier(identifier):
    """Get the group specified by the given *identifier*."""
    group = Group.query.filter_by(identifier=identifier, state="active").first_or_404()

    if not has_permission(current_user, "read", "group", object_id=group.id):
        return json_error_response(403)

    return json_response(200, GroupSchema().dump(group))


@bp.get("/groups/<int:id>/members")
@permission_required("read", "group", "id")
@scopes_required("group.read", "user.read")
@paginated
@qparam(
    "filter",
    parse=strip,
    description="A query to filter the members by their username or display name.",
)
@qparam("exclude", multiple=True, parse=int, description="User IDs to exclude.")
@status(
    200,
    "Return a paginated list of members, sorted by role name and then by user ID in"
    " ascending order. The creator will always be listed first.",
)
def get_group_members(id, page, per_page, qparams):
    """Get the members of the group specified by the given *id*."""
    group = Group.query.get_active_or_404(id)

    items, total = get_resource_user_roles(
        group,
        page=page,
        per_page=per_page,
        filter_term=qparams["filter"],
        exclude=qparams["exclude"],
    )
    data = {
        "items": items,
        **create_pagination_data(
            total, page, per_page, "api.get_group_members", id=group.id
        ),
    }

    return json_response(200, data)


@bp.get("/groups/<int:id>/revisions")
@permission_required("read", "group", "id")
@scopes_required("group.read")
@paginated
@status(
    200,
    "Return a paginated list of revisions, sorted by revision timestamp in descending"
    " order.",
)
def get_group_revisions(id, page, per_page):
    """Get the revisions of the group specified by the given *id*."""
    group = Group.query.get_active_or_404(id)
    paginated_revisions = group.ordered_revisions.paginate(page, per_page, False)

    schema = ObjectRevisionSchema(
        many=True,
        schema=GroupSchema,
        api_endpoint="api.get_group_revision",
        view_endpoint="groups.view_revision",
        endpoint_args={"group_id": group.id},
    )

    data = {
        "items": schema.dump(paginated_revisions.items),
        **create_pagination_data(
            paginated_revisions.total,
            page,
            per_page,
            "api.get_group_revisions",
            id=group.id,
        ),
    }

    return json_response(200, data)


@bp.get("/groups/<int:group_id>/revisions/<int:revision_id>")
@permission_required("read", "group", "group_id")
@scopes_required("group.read")
@status(200, "Return the revision.")
def get_group_revision(group_id, revision_id):
    """Get a revision.

    Will return the revision specified by the given *revision_id* of the group specified
    by the given *group_id*.
    """
    group = Group.query.get_active_or_404(group_id)
    revision = Group.revision_class.query.get_or_404(revision_id)

    if group.id != revision.group_id:
        return json_error_response(404)

    schema = ObjectRevisionSchema(
        schema=GroupSchema,
        api_endpoint="api.get_group_revision",
        view_endpoint="groups.view_revision",
        endpoint_args={"group_id": group.id},
    )

    return json_response(200, schema.dump(revision))


def _get_shared_resources(group, model, filter_term):
    object_name = model.__tablename__

    group_object_ids_query = get_permitted_objects(
        group, "read", object_name, check_defaults=False
    ).with_entities(model.id)

    user_object_ids_query = get_permitted_objects(
        current_user, "read", object_name
    ).with_entities(model.id)

    objects_query = model.query.filter(
        model.id.in_(group_object_ids_query),
        model.id.in_(user_object_ids_query),
        db.or_(
            model.title.ilike(f"%{filter_term}%"),
            model.identifier.ilike(f"%{filter_term}%"),
        ),
    )

    if hasattr(model, "state"):
        objects_query = objects_query.filter(model.state == "active")

    return objects_query.order_by(model.last_modified.desc())


@bp.get("/groups/<int:id>/records")
@permission_required("read", "group", "id")
@scopes_required("group.read", "record.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the records by their title or identifier.",
)
def get_group_records(id, page, per_page, qparams):
    """Get all records shared with the group with the given *id*.

    Shared means that the group needs to have at least explicit read permission for a
    record.
    """
    group = Group.query.get_active_or_404(id)

    paginated_records = _get_shared_resources(
        group, Record, qparams["filter"]
    ).paginate(page, per_page, False)

    data = {
        "items": RecordSchema(many=True).dump(paginated_records.items),
        **create_pagination_data(
            paginated_records.total,
            page,
            per_page,
            "api.get_group_records",
            id=group.id,
            **qparams,
        ),
    }

    return json_response(200, data)


@bp.get("/groups/<int:id>/collections")
@permission_required("read", "group", "id")
@scopes_required("group.read", "collection.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the collections by their title or identifier.",
)
def get_group_collections(id, page, per_page, qparams):
    """Get all collections shared with the group with the given *id*.

    Shared means that the group needs to have at least explicit read permission for a
    collection.
    """
    group = Group.query.get_active_or_404(id)

    paginated_collections = _get_shared_resources(
        group, Collection, qparams["filter"]
    ).paginate(page, per_page, False)

    data = {
        "items": CollectionSchema(many=True).dump(paginated_collections.items),
        **create_pagination_data(
            paginated_collections.total,
            page,
            per_page,
            "api.get_group_collections",
            id=group.id,
            **qparams,
        ),
    }

    return json_response(200, data)


@bp.get("/groups/<int:id>/templates")
@permission_required("read", "group", "id")
@scopes_required("group.read", "template.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the templates by their title or identifier.",
)
def get_group_templates(id, page, per_page, qparams):
    """Get all records shared with the group with the given *id*.

    Shared means that the group needs to have at least read permission for a template.
    """
    group = Group.query.get_active_or_404(id)

    paginated_templates = _get_shared_resources(
        group, Template, qparams["filter"]
    ).paginate(page, per_page, False)

    data = {
        "items": TemplateSchema(many=True).dump(paginated_templates.items),
        **create_pagination_data(
            paginated_templates.total,
            page,
            per_page,
            "api.get_group_templates",
            id=group.id,
            **qparams,
        ),
    }

    return json_response(200, data)
