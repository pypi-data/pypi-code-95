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
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.api.core import scopes_required
from kadi.lib.api.utils import reqschema
from kadi.lib.api.utils import status
from kadi.lib.resources.api import add_role
from kadi.modules.accounts.models import User
from kadi.modules.groups.models import Group
from kadi.modules.permissions.schemas import GroupRoleSchema
from kadi.modules.permissions.schemas import UserRoleSchema
from kadi.modules.permissions.utils import permission_required
from kadi.modules.templates.core import create_template
from kadi.modules.templates.models import Template
from kadi.modules.templates.schemas import TemplateSchema


@bp.post("/templates")
@permission_required("create", "template", None)
@scopes_required("template.create")
@reqschema(
    TemplateSchema(),
    description="The metadata and data of the new template, depending on its type.",
)
@status(201, "Return the new template.")
def new_template(schema):
    """Create a new template."""
    template = create_template(**schema.load_or_400())

    if not template:
        return json_error_response(409, description="Error creating template.")

    return json_response(201, schema.dump(template))


@bp.post("/templates/<int:id>/roles/users")
@permission_required("permissions", "template", "id")
@scopes_required("template.permissions")
@reqschema(
    UserRoleSchema(only=["user.id", "role.name"]),
    description="The user and corresponding role to add.",
)
@status(201, "User role successfully added to template.")
@status(409, "A role for that user already exists.")
def add_template_user_role(id, schema):
    """Add a user role to the template specified by the given *id*."""
    template = Template.query.get_or_404(id)
    data = schema.load_or_400()
    user = User.query.get_active_or_404(data["user"]["id"])

    return add_role(user, template, data["role"]["name"])


@bp.post("/templates/<int:id>/roles/groups")
@permission_required("permissions", "template", "id")
@scopes_required("template.permissions")
@reqschema(
    GroupRoleSchema(only=["group.id", "role.name"]),
    description="The group and corresponding role to add.",
)
@status(201, "Group role successfully added to template.")
@status(409, "A role for that group already exists.")
def add_template_group_role(id, schema):
    """Add a group role to the template specified by the given *id*."""
    template = Template.query.get_or_404(id)
    data = schema.load_or_400()
    group = Group.query.get_active_or_404(data["group"]["id"])

    return add_role(group, template, data["role"]["name"])
