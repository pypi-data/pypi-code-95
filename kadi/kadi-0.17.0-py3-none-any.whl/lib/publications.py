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
from flask import current_app
from flask_babel import gettext as _
from flask_login import current_user
from markupsafe import Markup

from kadi.ext.db import db
from kadi.ext.oauth import oauth
from kadi.lib.oauth.utils import get_oauth2_providers
from kadi.lib.oauth.utils import get_oauth2_token
from kadi.lib.utils import find_dict_in_list
from kadi.plugins import run_hook


def get_publication_providers(user=None):
    """Get a list of registered publication providers.

    Uses the ``"kadi_get_publication_providers"`` plugin hook to collect potential
    publication providers combined with the information from
    :func:`kadi.lib.oauth.utils.get_oauth2_providers`.

    Note that this function may issue one or more database commits.

    :param user: (optional) The user that should be checked for whether they are
        connected with the OAuth2 provider the publication provider uses, in which case
        ``"is_connected"`` will be set to ``True`` for the respective provider. Defaults
        to the current user.
    :return: A list of provider dictionaries in the following form, sorted by name:

        .. code-block:: python3

            [
                {
                    "name": "example",
                    "description": "An example publication provider.",
                    "title": "Example provider",
                    "website": "https://example.com",
                    "is_connected": True,
                },
            ]
    """
    user = user if user is not None else current_user

    try:
        providers = run_hook("kadi_get_publication_providers")
    except Exception as e:
        current_app.logger.exception(e)
        return []

    oauth2_providers = get_oauth2_providers(user=user)

    publication_providers = []
    for provider in providers:
        if not isinstance(provider, dict):
            current_app.logger.error("Invalid publication provider format.")
            continue

        provider_name = provider.get("name")
        oauth2_provider = find_dict_in_list(oauth2_providers, "name", provider_name)

        if provider_name is None or oauth2_provider is None:
            current_app.logger.error("Invalid publication provider.")
            continue

        publication_providers.append(
            {
                "name": provider_name,
                "description": Markup(provider.get("description", "")),
                "title": oauth2_provider["title"],
                "website": oauth2_provider["website"],
                "is_connected": oauth2_provider["is_connected"],
            }
        )

    return sorted(publication_providers, key=lambda provider: provider["name"])


def publish_record(record, provider, user=None, task=None):
    """Publish a record using a given provider.

    Uses the ``"kadi_publish_record"`` plugin hook to select the suitable publication
    provider if possible.

    Note that this function issues one or more database commits.

    :param record: The record to publish.
    :param provider: The provider to use for publishing.
    :param user: (optional) The user that is publishing the record. Defaults to the
        current user.
    :param task: (optional) A :class:`.Task` object that can be provided if this
        function is executed in a task.
    :return: A tuple consisting of a flag indicating whether the operation succeeded and
        an HTML template further describing the result, depending on the provider.
    """
    user = user if user is not None else current_user

    oauth2_token = get_oauth2_token(
        provider, user=user, delete_on_error=True, auto_refresh=True
    )
    db.session.commit()

    if oauth2_token is None:
        return False, _(
            "This provider requires a service that is not yet connected to your"
            " account."
        )

    try:
        result = run_hook(
            "kadi_publish_record",
            record=record,
            provider=provider,
            client=oauth.create_client(provider),
            token=oauth2_token.to_token(),
            task=task,
        )
    except Exception as e:
        current_app.logger.exception(e)
        return False, _("The provider failed with an unexpected error.")

    if result is None or not isinstance(result, tuple) or len(result) < 2:
        return False, _("The provider is configured incorrectly.")

    if task is not None and result[0]:
        # Set the progress to 100, in case the plugin does not do that already.
        task.update_progress(100)
        db.session.commit()

    return result[0], Markup(result[1])
