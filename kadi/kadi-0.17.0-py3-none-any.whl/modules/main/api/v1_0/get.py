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
from flask_login import login_required

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_response
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.api.utils import status
from kadi.lib.conversion import strip
from kadi.lib.licenses.models import License
from kadi.lib.licenses.schemas import LicenseSchema
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.permissions.utils import get_object_roles
from kadi.version import __version__


@bp.get("")
@login_required
@status(200, "Return the API endpoints.")
def index():
    """Get all base API endpoints."""
    endpoints = {
        "collections": url_for("api.get_collections"),
        "groups": url_for("api.get_groups"),
        "info": url_for("api.get_info"),
        "licenses": url_for("api.get_licenses"),
        "records": url_for("api.get_records"),
        "templates": url_for("api.get_templates"),
        "trash": url_for("api.get_trash"),
        "users": url_for("api.get_users"),
    }
    return json_response(200, endpoints)


@bp.get("/info")
@login_required
@status(200, "Return the information about the Kadi instance.")
def get_info():
    """Get information about the Kadi instance."""
    info = {"version": __version__}
    return json_response(200, info)


@bp.get("/roles")
@login_required
@status(200, "Return the resource roles and permissions.")
def get_resource_roles():
    """Get all possible roles and corresponding permissions of all resources."""
    roles = {}

    for object_name in ["record", "collection", "group", "template"]:
        roles[object_name] = get_object_roles(object_name)

    return json_response(200, roles)


@bp.get("/licenses")
@login_required
@paginated
@qparam(
    "filter",
    parse=strip,
    description="A query to filter the licenses by their name or title.",
)
@status(200, "Return a paginated list of licenses, sorted by name in ascending order.")
def get_licenses(page, per_page, qparams):
    """Get all licenses or search and filter for specific licenses."""
    paginated_licenses = (
        License.query.filter(
            db.or_(
                License.name.ilike(f"%{qparams['filter']}%"),
                License.title.ilike(f"%{qparams['filter']}%"),
            )
        )
        .order_by(License.name)
        .paginate(page, per_page, False)
    )

    data = {
        "items": LicenseSchema(many=True).dump(paginated_licenses.items),
        **create_pagination_data(
            paginated_licenses.total, page, per_page, "api.get_licenses", **qparams
        ),
    }

    return json_response(200, data)
