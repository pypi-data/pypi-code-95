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
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import login_required

from .blueprint import bp
from .core import create_record
from .core import delete_record as _delete_record
from .core import link_records
from .core import update_record
from .files import delete_file as _delete_file
from .files import update_file
from .forms import AddPermissionsForm
from .forms import EditFileForm
from .forms import EditRecordForm
from .forms import LinkCollectionsForm
from .forms import LinkRecordForm
from .forms import NewRecordForm
from .models import File
from .models import Record
from .previews import get_preview_scripts
from .tasks import start_publish_record_task
from kadi.ext.db import db
from kadi.lib.exceptions import KadiPermissionError
from kadi.lib.exceptions import KadiValidationError
from kadi.lib.forms import field_to_dict
from kadi.lib.publications import get_publication_providers
from kadi.lib.resources.views import add_links
from kadi.lib.resources.views import add_roles
from kadi.lib.resources.views import copy_roles
from kadi.lib.tasks.models import Task
from kadi.lib.utils import find_dict_in_list
from kadi.lib.validation import validate_uuid
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.accounts.models import User
from kadi.modules.collections.models import Collection
from kadi.modules.groups.models import Group
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.utils import permission_required
from kadi.modules.templates.models import Template


@bp.get("")
@login_required
@qparam("collection", multiple=True, parse=int)
def records(qparams):
    """Record overview page.

    Allows users to search and filter for records or create new ones.
    """
    collections = []
    if qparams["collection"]:
        collections = (
            get_permitted_objects(current_user, "read", "collection")
            .filter(Collection.id.in_(qparams["collection"]))
            .with_entities(Collection.id, Collection.identifier)
        )

    return render_template(
        "records/records.html",
        title=_("Records"),
        js_resources={
            "new_record_endpoint": url_for("records.new_record"),
            "collections": [(c.id, f"@{c.identifier}") for c in collections],
        },
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("create", "record", None)
@qparam("record", default=None, parse=int)
@qparam("template", default=None, parse=int)
@qparam("collection", default=None, parse=int)
@qparam("redirect", default="files")
def new_record(qparams):
    """Page to create a new record."""
    record = None
    template = None
    collection = None

    if request.method == "GET":
        # Copy a record's metadata.
        if qparams["record"] is not None:
            record = Record.query.get_active(qparams["record"])

        # Use a record or extras template.
        if qparams["template"] is not None:
            template = Template.query.get(qparams["template"])

        # Directly link a record with a collection.
        if qparams["collection"] is not None:
            collection = Collection.query.get_active(qparams["collection"])

    form = NewRecordForm(record=record, template=template, collection=collection)

    if request.method == "POST":
        if form.validate():
            record = create_record(
                title=form.title.data,
                identifier=form.identifier.data,
                type=form.type.data,
                description=form.description.data,
                license=form.license.data,
                visibility=form.visibility.data,
                tags=form.tags.data,
                extras=form.extras.data,
            )

            if record:
                add_links(record.collections, Collection, form.linked_collections.data)
                copy_roles(record, form.copy_permission.data)
                db.session.commit()

                flash(_("Record created successfully."), "success")
                return redirect(
                    url_for("records.add_files", id=record.id, tab=qparams["redirect"])
                )

        flash(_("Error creating record."), "danger")

    return render_template(
        "records/new_record.html",
        title=_("New record"),
        form=form,
        current_template=template if record is None else None,
        show_template_selection=record is None,
        redirect=qparams["redirect"],
        js_resources={"title_field": field_to_dict(form.title)},
    )


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@permission_required("update", "record", "id")
@qparam("key", multiple=True)
def edit_record(id, qparams):
    """Page to edit an existing record."""
    record = Record.query.get_active_or_404(id)
    form = EditRecordForm(record)

    if request.method == "POST":
        if form.validate():
            if update_record(
                record,
                title=form.title.data,
                identifier=form.identifier.data,
                type=form.type.data,
                description=form.description.data,
                license=form.license.data,
                visibility=form.visibility.data,
                tags=form.tags.data,
                extras=form.extras.data,
            ):
                flash(_("Changes saved successfully."), "success")

                if form.submit_quit.data:
                    return redirect(url_for("records.view_record", id=record.id))

                return redirect(url_for("records.edit_record", id=record.id))

        flash(_("Error editing record."), "danger")

    return render_template(
        "records/edit_record.html",
        title=_("Edit"),
        form=form,
        record=record,
        js_resources={
            "title_field": field_to_dict(form.title),
            "edit_extra_keys": qparams["key"],
        },
    )


@bp.get("/<int:id>")
@permission_required("read", "record", "id")
def view_record(id):
    """Page to view a record."""
    record = Record.query.get_active_or_404(id)
    return render_template(
        "records/view_record.html",
        record=record,
        publication_providers=get_publication_providers(),
        js_resources={
            "download_files_endpoint": url_for(
                "api.download_record_files", id=record.id
            )
        },
    )


@bp.get("/<int:id>/export/<export_type>")
@permission_required("read", "record", "id")
def export_record(id, export_type):
    """Page to view the exported data of a record.

    Currently ``"json"`` and ``"qr"`` are supported as export type.
    """
    record = Record.query.get_active_or_404(id)
    export_types = current_app.config["EXPORT_TYPES"]["record"]

    if export_type not in export_types:
        abort(404)

    return render_template(
        "records/export_record.html",
        title=export_types[export_type],
        record=record,
        export_type=export_type,
    )


@bp.route("/<int:id>/publish/<provider>", methods=["GET", "POST"])
@permission_required("read", "record", "id")
def publish_record(id, provider):
    """Page to publish a record using a given provider."""
    record = Record.query.get_active_or_404(id)

    publication_providers = get_publication_providers()
    publication_provider = find_dict_in_list(publication_providers, "name", provider)

    if publication_provider is None:
        abort(404)

    if request.method == "POST":
        endpoint = url_for("records.publish_record", id=record.id, provider=provider)

        if not publication_provider["is_connected"]:
            return redirect(endpoint)

        task = Task.query.filter(
            Task.name == "kadi.records.publish_record",
            Task.state.in_(["pending", "running"]),
            Task.user_id == current_user.id,
        ).first()

        if task:
            flash(_("A publishing task is already in progress."), "info")
            return redirect(endpoint)

        task = start_publish_record_task(record, provider)

        if not task:
            flash(_("Error starting publishing task."), "danger")
        else:
            flash(_("Publishing task started successfully."), "success")

    return render_template(
        "records/publish_record.html",
        title=publication_provider["title"],
        record=record,
        provider=publication_provider,
    )


@bp.route("/<int:id>/links", methods=["GET", "POST"])
@permission_required("link", "record", "id")
@qparam("tab", default="records")
def manage_links(id, qparams):
    """Page to link a record to other records or collections."""
    record = Record.query.get_active_or_404(id)

    record_form = LinkRecordForm(_suffix="record")
    collections_form = LinkCollectionsForm(_suffix="collections")

    if qparams["tab"] == "records" and record_form.validate_on_submit():
        linked_record = Record.query.get_active(record_form.record.data)

        if linked_record is not None:
            link_direction = record_form.link_direction.data
            record_from = record if link_direction == "out" else linked_record
            record_to = linked_record if link_direction == "out" else record

            try:
                if link_records(record_form.name.data, record_from, record_to):
                    db.session.commit()
                    flash(_("Changes saved successfully."), "success")
            except KadiPermissionError:
                pass

        return redirect(url_for("records.manage_links", id=record.id))

    if collections_form.validate_on_submit():
        add_links(record.collections, Collection, collections_form.collections.data)
        db.session.commit()
        flash(_("Changes saved successfully."), "success")

    return render_template(
        "records/manage_links.html",
        title=_("Links"),
        record_form=record_form,
        collections_form=collections_form,
        record=record,
    )


@bp.route("/<int:id>/permissions", methods=["GET", "POST"])
@permission_required("permissions", "record", "id")
def manage_permissions(id):
    """Page to manage access permissions of a record."""
    record = Record.query.get_active_or_404(id)

    form = AddPermissionsForm()
    if form.validate_on_submit():
        add_roles(User, form.users.data, record, form.role.data)
        add_roles(Group, form.groups.data, record, form.role.data)
        db.session.commit()

        flash(_("Changes saved successfully."), "success")
        return redirect(url_for("records.manage_permissions", id=record.id))

    return render_template(
        "records/manage_permissions.html",
        title=_("Permissions"),
        form=form,
        record=record,
    )


@bp.get("/<int:id>/files")
@permission_required("update", "record", "id")
@qparam("file")
def add_files(id, qparams):
    """Page to add files to a record."""
    record = Record.query.get_active_or_404(id)
    current_file_endpoint = None

    try:
        file_id = qparams["file"]
        validate_uuid(file_id)
        file = File.query.get(file_id)

        if file is not None and file.state == "active" and file.record_id == record.id:
            current_file_endpoint = url_for(
                "api.get_file", record_id=record.id, file_id=file.id
            )
    except KadiValidationError:
        pass

    return render_template(
        "records/add_files.html",
        title=_("Files"),
        record=record,
        js_resources={"current_file_endpoint": current_file_endpoint},
    )


@bp.get("/<int:record_id>/revisions/<int:revision_id>")
@permission_required("read", "record", "record_id")
def view_record_revision(record_id, revision_id):
    """Page to view a specific revision of a record."""
    record = Record.query.get_active_or_404(record_id)
    revision = Record.revision_class.query.get_or_404(revision_id)

    if record.id != revision.record_id:
        abort(404)

    return render_template(
        "records/view_revision.html",
        title=_("Revision"),
        record=record,
        revision=revision,
    )


@bp.get("/<int:record_id>/files/revisions/<int:revision_id>")
@permission_required("read", "record", "record_id")
def view_file_revision(record_id, revision_id):
    """Page to view a specific file revision of a record."""
    record = Record.query.get_active_or_404(record_id)
    revision = File.revision_class.query.get_or_404(revision_id)

    if record.id != revision.file.record_id:
        abort(404)

    return render_template(
        "records/view_revision.html",
        title=_("Revision"),
        record=record,
        revision=revision,
    )


@bp.post("/<int:id>/delete")
@permission_required("delete", "record", "id")
def delete_record(id):
    """Endpoint to delete an existing record.

    Does basically the same as the corresponding API endpoint.
    """
    record = Record.query.get_active_or_404(id)

    _delete_record(record)
    db.session.commit()

    flash(_("Record deleted successfully."), "success")
    return redirect(url_for("records.records"))


@bp.get("/<int:record_id>/files/<uuid:file_id>")
@permission_required("read", "record", "record_id")
def view_file(record_id, file_id):
    """Page to view a file of a record."""
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        abort(404)

    return render_template(
        "records/view_file.html",
        record=record,
        file=file,
        preview_scripts=get_preview_scripts(),
        js_resources={
            "get_file_preview_endpoint": url_for(
                "api.get_file_preview", record_id=record.id, file_id=file.id
            )
        },
    )


@bp.route("/<int:record_id>/files/<uuid:file_id>/edit", methods=["GET", "POST"])
@permission_required("update", "record", "record_id")
def edit_file(record_id, file_id):
    """Page to edit the metadata of an an existing file of a record."""
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        abort(404)

    form = EditFileForm(file)
    if form.validate_on_submit():
        if update_file(file, name=form.name.data, mimetype=form.mimetype.data):
            flash(_("Changes saved successfully."), "success")
            return redirect(
                url_for("records.view_file", record_id=record.id, file_id=file.id)
            )

        flash(_("Error editing file."), "danger")

    return render_template(
        "records/edit_file.html", title=_("Edit"), form=form, record=record, file=file
    )


@bp.post("/<int:record_id>/files/<uuid:file_id>/delete")
@permission_required("update", "record", "record_id")
def delete_file(record_id, file_id):
    """Endpoint to delete an existing file.

    Does basically the same as the corresponding API endpoint.
    """
    record = Record.query.get_active_or_404(record_id)
    file = File.query.get_active_or_404(file_id)

    if record.id != file.record_id:
        abort(404)

    _delete_file(file)

    flash(_("File deleted successfully."), "success")
    return redirect(url_for("records.view_record", id=record.id, tab="files"))
