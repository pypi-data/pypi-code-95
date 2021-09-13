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
from flask_login import current_user
from flask_login import login_required

from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal_endpoint
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.modules.accounts.models import User
from kadi.modules.permissions.core import set_system_role
from kadi.modules.permissions.schemas import RoleSchema


@bp.patch("/users/<int:id>/system_role", v=None)
@login_required
@internal_endpoint
def change_system_role(id):
    """Change the system role of a user."""
    user = User.query.get_or_404(id)

    if not current_user.is_sysadmin or user.is_merged:
        return json_error_response(404)

    if set_system_role(user, RoleSchema().load_or_400()["name"]):
        db.session.commit()
        return json_response(204)

    return json_error_response(400, description="A role with that name does not exist.")


@bp.patch("/users/<int:id>/state", v=None)
@login_required
@internal_endpoint
def toggle_user_state(id):
    """Toggle the active state of a user."""
    user = User.query.get_or_404(id)

    if not current_user.is_sysadmin or user.is_merged:
        return json_error_response(404)

    if user.state == "active":
        user.state = "inactive"
    elif user.state == "inactive":
        user.state = "active"

    db.session.commit()
    return json_response(204)


@bp.patch("/users/<int:id>/sysadmin", v=None)
@login_required
@internal_endpoint
def toggle_user_sysadmin(id):
    """Toggle the sysadmin state of a user."""
    user = User.query.get_or_404(id)

    if not current_user.is_sysadmin or user.is_merged:
        return json_error_response(404)

    user.is_sysadmin = not user.is_sysadmin
    db.session.commit()

    return json_response(204)
