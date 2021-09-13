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
from marshmallow.fields import DateTime

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_response
from kadi.lib.api.core import scopes_required
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.api.utils import status
from kadi.lib.conversion import normalize
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.collections.models import Collection
from kadi.modules.groups.models import Group
from kadi.modules.records.models import Record


@bp.get("/trash")
@login_required
@scopes_required("misc.manage_trash")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the resources in the trash by their title or"
    " identifier.",
)
@status(
    200,
    "Return a paginated list of deleted resources, sorted by deletion date in"
    " descending order.",
)
def get_trash(page, per_page, qparams):
    """Get all deleted resources.

    Only the basic metadata of deleted resources the current user created are returned.
    Additionally, each resource contains its resource type (``type``), its deletion date
    (``deleted_at``) as well as endpoints to restore (``_actions.restore``) or purge
    (``_actions.purge``) the resource.
    """
    queries = []
    for model in [Record, Collection, Group]:
        resources_query = model.query.filter(
            db.or_(
                model.title.ilike(f"%{qparams['filter']}%"),
                model.identifier.ilike(f"%{qparams['filter']}%"),
            ),
            model.user_id == current_user.id,
            model.state == "deleted",
        ).with_entities(
            model.id,
            model.title,
            model.identifier,
            model.last_modified.label("deleted_at"),
            db.literal(model.__tablename__).label("type"),
        )
        queries.append(resources_query)

    paginated_resources = (
        queries[0]
        .union(*queries[1:])
        .order_by(db.desc("deleted_at"))
        .paginate(page, per_page, False)
    )

    items = []
    for resource in paginated_resources.items:
        item = {
            "id": resource.id,
            "title": resource.title,
            "identifier": resource.identifier,
            "type": resource.type,
            "deleted_at": DateTime().serialize("deleted_at", resource),
            "_actions": {
                "restore": url_for(f"api.restore_{resource.type}", id=resource.id),
                "purge": url_for(f"api.purge_{resource.type}", id=resource.id),
            },
        }

        items.append(item)

    data = {
        "items": items,
        **create_pagination_data(
            paginated_resources.total, page, per_page, "api.get_trash"
        ),
    }

    return json_response(200, data)
