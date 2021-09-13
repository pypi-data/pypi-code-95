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
from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import request
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import logout_user

from .providers import ShibProvider
from kadi.lib.api.core import json_error_response
from kadi.lib.api.utils import is_api_request
from kadi.lib.web import url_for


bp = Blueprint("accounts", __name__, template_folder="templates")


@bp.before_app_request
def _before_app_request():
    if current_user.is_authenticated:
        auth_providers = current_app.config["AUTH_PROVIDERS"]

        if (
            current_user.state != "active"
            or current_user.is_merged
            or current_user.identity is None
            or current_user.identity.type not in auth_providers
        ):
            url = url_for("main.index")

            if (
                current_user.identity is not None
                and current_user.identity.type == "shib"
                and ShibProvider.is_registered()
            ):
                url = ShibProvider.get_logout_initiator(url)

            logout_user()

            if is_api_request():
                return json_error_response(
                    401, description="This account is currently inactive."
                )

            flash(_("This account is currently inactive."), "danger")
            return redirect(url)

        # The listed endpoints should still work even if the current user does require
        # email confirmation.
        excluded_endpoints = [
            "accounts.request_email_confirmation",
            "accounts.confirm_email",
            "accounts.logout",
            "main.about",
            "main.help",
            "static",
        ]

        if (
            current_user.needs_email_confirmation
            and request.endpoint not in excluded_endpoints
        ):
            if is_api_request():
                return json_error_response(
                    401, description="Please confirm your email address."
                )

            return redirect(url_for("accounts.request_email_confirmation"))


from . import views  # pylint: disable=unused-import
