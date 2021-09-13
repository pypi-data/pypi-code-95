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
import requests
from flask import abort
from flask import current_app
from flask import flash
from flask import render_template
from flask import request
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import login_required

from .blueprint import bp
from kadi.ext.db import db
from kadi.lib.utils import random_alnum
from kadi.modules.accounts.forms import RegistrationForm
from kadi.modules.accounts.models import User
from kadi.modules.accounts.providers import LocalProvider
from kadi.modules.collections.models import Collection
from kadi.modules.groups.models import Group
from kadi.modules.records.models import File
from kadi.modules.records.models import Record
from kadi.modules.templates.models import Template
from kadi.version import __version__


@bp.get("")
@login_required
def information():
    """Page for sysadmins to view general information."""
    if not current_user.is_sysadmin:
        abort(404)

    latest_version = None
    try:
        response = requests.get(
            current_app.config["RELEASE_URL"],
            timeout=current_app.config["REQUESTS_TIMEOUT"],
        )
        latest_version = response.json()["info"]["version"]
    except Exception as e:
        current_app.logger.exception(e)

    active_users = User.query.filter(
        User.new_user_id.is_(None), User.state == "active"
    ).count()
    num_records = Record.query.count()
    files_query = File.query.filter(File.state != "deleted")
    num_files = files_query.count()
    file_size = files_query.with_entities(db.func.sum(File.size)).scalar() or 0
    num_collections = Collection.query.count()
    num_groups = Group.query.count()
    num_templates = Template.query.count()

    return render_template(
        "sysadmin/information.html",
        title=_("Information"),
        current_version=__version__,
        latest_version=latest_version,
        active_users=active_users,
        num_records=num_records,
        num_files=num_files,
        file_size=file_size,
        num_collections=num_collections,
        num_groups=num_groups,
        num_templates=num_templates,
    )


@bp.route("/users", methods=["GET", "POST"])
@login_required
def manage_users():
    """Page for sysadmins to manage users."""
    if not current_user.is_sysadmin:
        abort(404)

    new_username = None
    new_password = None
    local_provider_registered = LocalProvider.is_registered()

    form = RegistrationForm()
    del form.password
    del form.password2

    if request.method == "POST" and local_provider_registered:
        if form.validate():
            new_username = form.username.data
            new_password = random_alnum()

            LocalProvider.register(
                username=new_username,
                email=form.email.data,
                displayname=form.displayname.data,
                password=new_password,
            )

            db.session.commit()
            flash(_("User created successfully."), "success")

            # Manually reset all fields, as redirecting would also clear the generated
            # password value.
            form.username.data = form.email.data = form.displayname.data = ""
        else:
            flash(_("Error creating user."), "danger")

    return render_template(
        "sysadmin/manage_users.html",
        title=_("User management"),
        form=form,
        local_provider_registered=local_provider_registered,
        new_username=new_username,
        new_password=new_password,
    )
