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
from .forms import ChangePasswordForm
from .forms import EditProfileForm
from .forms import NewAccessTokenForm
from kadi.ext.db import db
from kadi.ext.oauth import oauth
from kadi.lib.api.core import create_access_token
from kadi.lib.api.models import AccessToken
from kadi.lib.api.utils import get_access_token_scopes
from kadi.lib.db import update_object
from kadi.lib.oauth.core import create_oauth2_token
from kadi.lib.oauth.utils import get_oauth2_providers
from kadi.lib.oauth.utils import get_oauth2_token
from kadi.lib.utils import find_dict_in_list
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.accounts.providers import LocalProvider
from kadi.modules.accounts.utils import delete_user_image
from kadi.modules.accounts.utils import save_user_image
from kadi.modules.notifications.mails import send_email_confirmation_mail


def _send_email_confirmation_mail(identity):
    token = identity.get_email_confirmation_token()
    if send_email_confirmation_mail(identity.email, identity.displayname, token):
        flash(_("A confirmation email has been sent."), "success")
    else:
        flash(_("Could not send confirmation email."), "danger")


@bp.route("", methods=["GET", "POST"])
@login_required
@qparam("action", default="edit_profile")
def edit_profile(qparams):
    """Page for a user to edit their profile."""
    identity = current_user.identity
    form = EditProfileForm(current_user)

    if request.method == "POST":
        if qparams["action"] == "edit_profile":
            if form.validate():
                # User attributes are always editable.
                update_object(
                    current_user,
                    about=form.about.data,
                    email_is_private=not form.show_email.data,
                )

                if form.remove_image.data:
                    delete_user_image(current_user)

                elif form.image.data:
                    delete_user_image(current_user)
                    save_user_image(current_user, request.files[form.image.name])

                # Currently, we assume the display name is always editable.
                identity.displayname = form.displayname.data

                # Currently, we assume only emails of local accounts are editable and
                # possibly need to be (re-)confirmed after changing them.
                if identity.type == "local" and identity.email != form.email.data:
                    update_object(
                        identity, email=form.email.data, email_confirmed=False
                    )

                    if LocalProvider.email_confirmation_required():
                        _send_email_confirmation_mail(identity)

                db.session.commit()

                flash(_("Changes saved successfully."), "success")
                return redirect(url_for("settings.edit_profile"))

            flash(_("Error updating profile."), "danger")

        elif identity.type == "local" and not identity.email_confirmed:
            _send_email_confirmation_mail(identity)

    return render_template(
        "settings/edit_profile.html", title=_("Profile"), form=form, identity=identity
    )


@bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    """Page for a local user to change their password."""
    identity = current_user.identity
    provider = current_app.config["AUTH_PROVIDERS"][identity.type]["provider_class"]

    if not provider.allow_password_change():
        abort(404)

    form = ChangePasswordForm()
    if request.method == "POST":
        if form.validate() and provider.change_password(
            identity.username, form.password.data, form.new_password.data
        ):
            db.session.commit()
            flash(_("Password changed successfully."), "success")
            return redirect(url_for("settings.change_password"))

        flash(_("Error changing password."), "danger")

    return render_template(
        "settings/change_password.html", title=_("Password"), form=form
    )


@bp.route("/access_tokens", methods=["GET", "POST"])
@login_required
def manage_tokens():
    """Page for a user to manage their personal access tokens."""
    new_token = None
    form = NewAccessTokenForm()
    current_scopes = request.form.getlist("scopes")

    if request.method == "POST":
        if form.validate():
            new_token = AccessToken.new_token()

            create_access_token(
                name=form.name.data,
                expires_at=form.expires_at.data,
                token=new_token,
                scopes=current_scopes,
            )
            db.session.commit()
            flash(_("Access token created successfully."), "success")

            # Manually reset all fields, as redirecting would also clear the new token
            # value.
            form.name.data = form.expires_at.raw_data = ""
            form.expires_at.data = form.expires_at.default()
            current_scopes = []
        else:
            flash(_("Error creating access token."), "danger")

    return render_template(
        "settings/manage_tokens.html",
        title=_("Access tokens"),
        form=form,
        new_token=new_token,
        js_resources={
            "current_scopes": current_scopes,
            "access_token_scopes": get_access_token_scopes(),
        },
    )


@bp.route("/services", methods=["GET", "POST"])
@login_required
@qparam("disconnect")
def manage_services(qparams):
    """Page for a user to manage their connected services."""
    if request.method == "POST":
        oauth2_token = get_oauth2_token(qparams["disconnect"], delete_on_error=True)
        db.session.commit()

        if oauth2_token is not None:
            db.session.delete(oauth2_token)
            db.session.commit()

        flash(_("Service disconnected successfully."), "success")
        return redirect(url_for("settings.manage_services"))

    providers = get_oauth2_providers()

    return render_template(
        "settings/manage_services.html",
        title=_("Connected services"),
        providers=providers,
    )


@bp.get("/services/login/<provider>")
@login_required
def oauth2_login(provider):
    """Endpoint to initiate the OAuth2 flow to connect a service."""
    oauth2_providers = get_oauth2_providers()
    oauth2_provider = find_dict_in_list(oauth2_providers, "name", provider)

    if oauth2_provider is None:
        abort(404)

    if oauth2_provider["is_connected"]:
        return redirect(url_for("settings.manage_services"))

    redirect_uri = url_for("settings.oauth2_authorize", provider=provider)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)


@bp.get("/services/authorize/<provider>")
@login_required
def oauth2_authorize(provider):
    """Redirect endpoint to handle the OAuth2 authorization code."""
    oauth2_providers = get_oauth2_providers()
    oauth2_provider = find_dict_in_list(oauth2_providers, "name", provider)

    if oauth2_provider is None:
        abort(404)

    if oauth2_provider["is_connected"]:
        return redirect(url_for("settings.manage_services"))

    try:
        token = oauth.create_client(provider).authorize_access_token()
    except Exception as e:
        current_app.logger.exception(e)

        flash(_("Error connecting service."), "danger")
        return redirect(url_for("settings.manage_services"))

    create_oauth2_token(
        user=current_user,
        name=provider,
        access_token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        expires_at=token.get("expires_at"),
        expires_in=token.get("expires_in"),
    )
    db.session.commit()

    flash(_("Service connected successfully."), "success")
    return redirect(url_for("settings.manage_services"))


@bp.get("/trash")
@login_required
def manage_trash():
    """Page for a user to manage their deleted resources."""
    return render_template("settings/manage_trash.html", title=_("Trash"))
