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
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask_babel import gettext as _
from flask_login import login_required

from .blueprint import bp
from .core import create_group
from .core import delete_group as _delete_group
from .core import update_group
from .forms import AddMembersForm
from .forms import EditGroupForm
from .forms import NewGroupForm
from .models import Group
from .utils import delete_group_image
from .utils import save_group_image
from kadi.ext.db import db
from kadi.lib.forms import field_to_dict
from kadi.lib.resources.views import add_roles
from kadi.lib.web import url_for
from kadi.modules.accounts.models import User
from kadi.modules.permissions.utils import permission_required


@bp.get("")
@login_required
def groups():
    """Group overview page.

    Allows users to search and filter for groups or create new ones.
    """
    return render_template("groups/groups.html", title=_("Groups"))


@bp.route("/new", methods=["GET", "POST"])
@permission_required("create", "group", None)
def new_group():
    """Page to create a new group."""
    form = NewGroupForm()

    if request.method == "POST":
        if form.validate():
            group = create_group(
                title=form.title.data,
                identifier=form.identifier.data,
                description=form.description.data,
                visibility=form.visibility.data,
            )

            if group:
                if form.image.data:
                    save_group_image(group, request.files[form.image.name])

                db.session.commit()

                flash(_("Group created successfully."), "success")
                return redirect(url_for("groups.view_group", id=group.id))

        flash(_("Error creating group."), "danger")

    return render_template(
        "groups/new_group.html",
        title=_("New group"),
        form=form,
        js_resources={"title_field": field_to_dict(form.title)},
    )


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@permission_required("update", "group", "id")
def edit_group(id):
    """Page to edit an existing group."""
    group = Group.query.get_active_or_404(id)
    form = EditGroupForm(group)

    if request.method == "POST":
        if form.validate():
            if update_group(
                group,
                title=form.title.data,
                identifier=form.identifier.data,
                description=form.description.data,
                visibility=form.visibility.data,
            ):
                if form.remove_image.data:
                    delete_group_image(group)

                elif form.image.data:
                    delete_group_image(group)
                    save_group_image(group, request.files[form.image.name])

                db.session.commit()
                flash(_("Changes saved successfully."), "success")

                if form.submit_quit.data:
                    return redirect(url_for("groups.view_group", id=group.id))

                return redirect(url_for("groups.edit_group", id=group.id))

        flash(_("Error editing group."), "danger")

    return render_template(
        "groups/edit_group.html",
        title=_("Edit"),
        form=form,
        group=group,
        js_resources={"title_field": field_to_dict(form.title)},
    )


@bp.get("/<int:id>")
@permission_required("read", "group", "id")
def view_group(id):
    """Page to view a group."""
    group = Group.query.get_active_or_404(id)
    return render_template("groups/view_group.html", group=group)


@bp.route("/<int:id>/members", methods=["GET", "POST"])
@permission_required("members", "group", "id")
def manage_members(id):
    """Page to manage members of a group."""
    group = Group.query.get_active_or_404(id)

    form = AddMembersForm()
    if form.validate_on_submit():
        add_roles(User, form.users.data, group, form.role.data)
        db.session.commit()

        flash(_("Changes saved successfully."), "success")
        return redirect(url_for("groups.manage_members", id=group.id))

    return render_template(
        "groups/manage_members.html", title=_("Members"), form=form, group=group
    )


@bp.get("/<int:group_id>/revisions/<int:revision_id>")
@permission_required("read", "group", "group_id")
def view_revision(group_id, revision_id):
    """Page to view a specific revision of a group."""
    group = Group.query.get_active_or_404(group_id)
    revision = Group.revision_class.query.get_or_404(revision_id)

    if group.id != revision.group_id:
        abort(404)

    return render_template(
        "groups/view_revision.html", title=_("Revision"), group=group, revision=revision
    )


@bp.post("/<int:id>/delete")
@permission_required("delete", "group", "id")
def delete_group(id):
    """Endpoint to delete an existing group.

    Does basically the same as the corresponding API endpoint.
    """
    group = Group.query.get_active_or_404(id)

    _delete_group(group)
    db.session.commit()

    flash(_("Group deleted successfully."), "success")
    return redirect(url_for("groups.groups"))
