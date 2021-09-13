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
# pylint: disable=missing-function-docstring
import json
import os

from authlib.common.urls import add_params_to_qs
from flask import Blueprint
from flask import render_template
from flask_babel import gettext as _

import kadi.lib.constants as const
from kadi.ext.db import db
from kadi.lib.conversion import markdown_to_html
from kadi.modules.records.files import open_file
from kadi.modules.records.models import File
from kadi.plugins import get_config
from kadi.plugins import hookimpl


# Also used as the name of the blueprint and the OAuth2/publication providers.
PLUGIN_NAME = "zenodo"


bp = Blueprint(PLUGIN_NAME, __name__, template_folder="templates")


@hookimpl
def kadi_register_blueprints(app):
    app.register_blueprint(bp)


@hookimpl
def kadi_get_translations_paths():
    return os.path.join(os.path.dirname(__file__), "translations")


def _compliance_fix(session):
    def _refresh_token_request(url, headers, body):
        # Zenodo requires sending the client ID and secret each time a token is
        # requested, even for the refresh token grant type.
        config = get_config(PLUGIN_NAME)

        client_id = config.get("client_id")
        client_secret = config.get("client_secret")

        body = add_params_to_qs(
            body, {"client_id": client_id, "client_secret": client_secret}
        )
        return url, headers, body

    session.register_compliance_hook("refresh_token_request", _refresh_token_request)


@hookimpl
def kadi_register_oauth2_providers(registry):
    config = get_config(PLUGIN_NAME)

    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    base_url = config.get("base_url", "https://zenodo.org")

    registry.register(
        name=PLUGIN_NAME,
        client_id=client_id,
        client_secret=client_secret,
        access_token_url=f"{base_url}/oauth/token",
        access_token_params={"client_id": client_id, "client_secret": client_secret},
        authorize_url=f"{base_url}/oauth/authorize",
        api_base_url=f"{base_url}/api/",
        client_kwargs={"scope": "deposit:write"},
        compliance_fix=_compliance_fix,
    )


@hookimpl
def kadi_get_oauth2_providers():
    config = get_config(PLUGIN_NAME)
    base_url = config.get("base_url", "https://zenodo.org")

    return {
        "name": PLUGIN_NAME,
        "title": "Zenodo",
        "website": base_url,
        "description": render_template("zenodo/description_oauth.html"),
    }


@hookimpl
def kadi_get_publication_providers():
    return {
        "name": PLUGIN_NAME,
        "description": render_template("zenodo/description_publication.html"),
    }


def _render_error(message=None, response=None):
    if message is None:
        try:
            message = response.json()["message"]
        except:
            message = _("Unknown error.")

    return render_template(
        "zenodo/upload_error.html", status=response.status_code, message=message
    )


def _delete_deposit(deposit, client, token):
    # If a given task was revoked, we attempt to delete the deposit again and just
    # return an empty result.
    client.delete(deposit, token=token)
    return False, ""


@hookimpl
def kadi_publish_record(record, provider, client, token, task):
    if provider != PLUGIN_NAME:
        return None

    # Zenodo requires at least 4 characters for the description.
    description = (
        record.description if len(record.description) >= 4 else "*No description.*"
    )
    metadata = {
        "metadata": {
            "upload_type": "dataset",
            "title": record.title,
            "creators": [{"name": record.creator.identity.displayname}],
            "description": markdown_to_html(description),
            "license": record.license.name if record.license else "notspecified",
            "keywords": [tag.name for tag in record.tags],
        }
    }

    try:
        response = client.post("deposit/depositions", token=token, json=metadata)
        if response.status_code != 201:
            return False, _render_error(response=response)

        deposit = response.json()

        # Limited to local files at the moment.
        files_query = record.active_files.filter(File.storage_type == "local")
        num_files = files_query.count()

        for index, file in enumerate(files_query):
            if task is not None and task.is_revoked:
                return _delete_deposit(deposit["links"]["self"], client, token)

            # Zenodo supports file uploads up to 50GB.
            if file.size > 50 * const.ONE_GB:
                continue

            with open_file(file) as f:
                response = client.put(
                    f"{deposit['links']['bucket']}/{file.name}", token=token, data=f
                )
                if response.status_code != 200:
                    return False, _render_error(response=response)

            if task is not None:
                task.update_progress((index + 1) / num_files * 100)
                db.session.commit()

        # Upload any extra metadata as JSON file called "_meta.json". If another file
        # with that name exists, it will be overwritten, which we should probably handle
        # better in the future.
        if record.extras:
            response = client.put(
                f"{deposit['links']['bucket']}/_meta.json",
                token=token,
                data=json.dumps(record.extras, ensure_ascii=False),
            )
            if response.status_code != 200:
                return False, _render_error(response=response)

        if task is not None and task.is_revoked:
            return _delete_deposit(deposit["links"]["self"], client, token)

        deposit_url = deposit["links"]["html"]

    except Exception as e:
        return False, _render_error(message=repr(e))

    return True, render_template("zenodo/upload_success.html", deposit_url=deposit_url)
