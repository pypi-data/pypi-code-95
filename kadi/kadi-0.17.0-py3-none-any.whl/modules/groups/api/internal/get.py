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
import os

from flask import send_file
from flask_login import current_user
from flask_login import login_required

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal_endpoint
from kadi.lib.api.core import json_error_response
from kadi.lib.conversion import normalize
from kadi.lib.db import get_class_by_tablename
from kadi.lib.resources.api import get_selected_resources
from kadi.lib.storage.misc import create_misc_uploads_path
from kadi.lib.web import qparam
from kadi.modules.groups.models import Group
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.utils import get_group_roles
from kadi.modules.permissions.utils import permission_required


@bp.get("/groups/<int:id>/image", v=None)
@permission_required("read", "group", "id")
@internal_endpoint
def preview_group_image(id):
    """Download a group's image thumbnail for direct preview in the browser."""
    group = Group.query.get_active_or_404(id)

    if group.image_name:
        filepath = create_misc_uploads_path(str(group.image_name))

        if os.path.isfile(filepath):
            return send_file(
                filepath,
                mimetype="image/jpeg",
                download_name=f"{group.identifier}.jpg",
                etag=False,
                max_age=31536000,
            )

    return json_error_response(404)


@bp.get("/groups/select", v=None)
@login_required
@internal_endpoint
@qparam("page", default=1, parse=int)
@qparam("term", parse=normalize)
@qparam("exclude", multiple=True, parse=int)
@qparam("action", multiple=True)
@qparam("resource_type")
@qparam("resource_id", default=None, parse=int)
def select_groups(qparams):
    """Search groups in dynamic selections.

    Uses :func:`kadi.lib.resources.api.get_selected_resources`.
    """
    exclude = qparams["exclude"]
    object_name = qparams["resource_type"]
    object_id = qparams["resource_id"]

    # If applicable, exclude groups that already have any role in the specified
    # resource.
    if object_name in ["record", "collection", "template"] and object_id is not None:
        model = get_class_by_tablename(object_name)
        resource = model.query.get(object_id)

        if (
            resource is not None
            and getattr(resource, "state", "active") == "active"
            and has_permission(current_user, "read", object_name, object_id)
        ):
            group_ids_query = get_group_roles(
                object_name, object_id=object_id
            ).with_entities(Group.id)
            exclude += [g.id for g in group_ids_query]

    return get_selected_resources(
        Group,
        page=qparams["page"],
        term=qparams["term"],
        exclude=exclude,
        actions=qparams["action"],
    )
