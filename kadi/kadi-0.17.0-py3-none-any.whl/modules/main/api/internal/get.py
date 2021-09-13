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
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import login_required

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal_endpoint
from kadi.lib.api.core import json_response
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.licenses.models import License
from kadi.lib.tags.models import Tag
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.collections.models import Collection
from kadi.modules.groups.models import Group
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.records.models import Record
from kadi.modules.templates.models import Template


@bp.get("/tags/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=normalize)
@qparam("type")
def select_tags(qparams):
    """Search tags in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`. Only the tags of
    resources the current user has read permission for are returned.
    """
    tag_queries = []

    # Restrict the results to a certain resource type.
    if qparams["type"] == "record":
        models = [Record]
    elif qparams["type"] == "collection":
        models = [Collection]
    else:
        models = [Record, Collection]

    for model in models:
        tags_query = Tag.query.join(model.tags).filter(
            model.state == "active",
            model.id.in_(
                get_permitted_objects(
                    current_user, "read", model.__tablename__
                ).with_entities(model.id)
            ),
        )
        tag_queries.append(tags_query)

    paginated_tags = (
        tag_queries[0]
        .union(*tag_queries[1:])
        .filter(Tag.name.ilike(f"%{qparams['term']}%"))
        .distinct()
        .order_by(Tag.name)
        .with_entities(Tag.name)
        .paginate(qparams["page"], 10, False)
    )

    data = {"results": [], "pagination": {"more": paginated_tags.has_next}}
    for tag in paginated_tags.items:
        data["results"].append({"id": tag[0], "text": tag[0]})

    return json_response(200, data)


@bp.get("/licenses/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=strip)
def select_licenses(qparams):
    """Search licenses in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`.
    """
    paginated_licenses = (
        License.query.filter(
            db.or_(
                License.name.ilike(f"%{qparams['term']}%"),
                License.title.ilike(f"%{qparams['term']}%"),
            )
        )
        .order_by(License.title)
        .paginate(qparams["page"], 10, False)
    )

    data = {"results": [], "pagination": {"more": paginated_licenses.has_next}}
    for license in paginated_licenses.items:
        data["results"].append({"id": license.name, "text": license.title})

    return json_response(200, data)


@bp.get("/search", v=None)
@login_required
@internal_endpoint
@qparam("query", parse=normalize)
def search_resources(qparams):
    """Search for different resources.

    Currently used in the base navigation quick search. Supports resources of type
    :class:`.Record`, :class:`.Collection`, :class:`.Group` and :class:`.Template`. The
    attributes that will be searched depend on the model.
    """
    resource_types = {
        "record": _("Record"),
        "collection": _("Collection"),
        "group": _("Group"),
        "template": _("Template"),
    }

    resource_queries = []
    for model, endpoint in [
        (Record, "records.view_record"),
        (Collection, "collections.view_collection"),
        (Group, "groups.view_group"),
        (Template, "templates.view_template"),
    ]:
        resources_query = get_permitted_objects(
            current_user, "read", model.__tablename__
        ).with_entities(
            model.id,
            model.title,
            model.identifier,
            model.last_modified.label("last_modified"),
            db.literal(model.__tablename__).label("type"),
            db.literal(endpoint).label("endpoint"),
        )

        resources_query = resources_query.filter(
            db.or_(
                model.title.ilike(f"%{qparams['query']}%"),
                model.identifier.ilike(f"%{qparams['query']}%"),
            )
        )

        if hasattr(model, "state"):
            resources_query = resources_query.filter(model.state == "active")

        resource_queries.append(resources_query)

    resources = (
        resource_queries[0]
        .union(*resource_queries[1:])
        .order_by(db.desc("last_modified"))
        .limit(5)
    )

    data = []
    for resource in resources:
        data.append(
            {
                "identifier": f"@{resource.identifier}",
                "type": resource_types[resource.type],
                "timestamp": resource.last_modified,
                "endpoint": url_for(resource.endpoint, id=resource.id),
            }
        )

    return json_response(200, data)
