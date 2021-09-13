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
from pluggy import HookspecMarker


hookspec = HookspecMarker("kadi")


@hookspec
def kadi_register_blueprints(app):
    """Hook for registering custom Flask blueprints.

    An example Flask blueprint, including a custom static path, could look like the
    following:

    .. code-block:: python3

        from flask import Blueprint

        bp = Blueprint(
            'my_plugin',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/my_plugin/static',
        )

    :param app: The application object, which is used to register the blueprint via
        its ``register_blueprint`` method.
    """


@hookspec
def kadi_get_translations_paths():
    """Hook for collecting translation paths.

    The translations path returned by a plugin must be absolute. Note that currently
    translations of the main application and plugins are simply merged together, where
    translations of the main application will always take precedence.
    """


@hookspec
def kadi_register_oauth2_providers(registry):
    """Hook for registering OAuth2 providers.

    Currently, only the authorization code grant is supported. Each provider needs to
    register itself to the given registry provided by the Authlib library using a unique
    name.

    Needs to be used together with :func:`kadi_get_oauth2_providers`.

    :param registry: The OAuth2 provider registry, which is used to register the
        provider via its ``register`` method.
    """


@hookspec
def kadi_get_oauth2_providers():
    """Hook for collecting OAuth2 providers.

    Each OAuth2 provider has to be returned as a dictionary containing all necessary
    information about the provider. A provider must at least provide the unique name
    that was also used to register it.

    **Example:**

    .. code-block:: python3

        {
            "name": "my_provider",
            "title": "My provider",
            "website": "https://example.com",
            "description": "The (HTML) description of the OAuth2 provider.",
        }

    Needs to be used together with :func:`kadi_register_oauth2_providers`.
    """


@hookspec
def kadi_get_publication_providers():
    """Hook for collecting publication providers.

    Each publication provider has to be returned as a dictionary containing all
    necessary information about the provider. A provider must at least provide the
    unique name that was also used to register the OAuth2 provider that this provider
    should use.

    **Example:**

    .. code-block:: python3

        {
            "name": "my_provider",
            "description": "The (HTML) description of the publication provider.",
        }

    Needs to be used together with :func:`kadi_register_oauth2_providers` and
    :func:`kadi_get_oauth2_providers`.
    """


@hookspec(firstresult=True)
def kadi_publish_record(record, provider, client, token, task):
    """Hook for publishing a record using a given provider.

    Each plugin has to check the given provider and decide whether it should start the
    publishing process, otherwise it has to return ``None``. After performing the
    publishing operation, the plugin has to return a tuple containing the result status
    of the operation and a template further describing the result in a user-readable
    manner, e.g. containing a link to view the published result if the operation was
    successful.

    Needs to be used together with :func:`kadi_get_publication_providers`. Note that the
    hook chain will stop after the first returned result that is not ``None``.

    :param record: The record to publish.
    :param provider: The provider to use for publishing.
    :param client: The OAuth2 client to use for publishing.
    :param token: The OAuth2 token to use for publishing.
    :param task: A :class:`.Task` object that may be provided if this hook is executed
        in a background task. Can be used to check whether the publishing operation was
        cancelled and to update the current progress of the operation via the task.
    """


@hookspec(firstresult=True)
def kadi_get_custom_mimetype(file, base_mimetype):
    """Hook for determining a custom MIME type of a file.

    Each plugin has to check the given base MIME type and decide whether it should try
    determining a custom MIME type or not. Otherwise, it has to return ``None``. The
    returned MIME type should only be based on the content a file actually contains.

    Can be used together with :func:`kadi_get_preview_data`. Note that the hook chain
    will stop after the first returned result that is not ``None``.

    :param file: The :class:`.File` to get the custom MIME type of.
    :param base_mimetype: The base MIME type of the file, based on the actual file
        content, which a plugin can base its decision to return a custom MIME type on.
    """


@hookspec(firstresult=True)
def kadi_get_preview_data(file):
    """Hook for obtaining preview data of a file object to be passed to the frontend.

    Each plugin has to check if preview data should be returned for the given file,
    based on e.g. its storage type, size or MIME types, otherwise it has to return
    ``None``. The preview data must consist of a tuple containing the preview type and
    the actual preview data used for rendering the preview later.

    Should be used together with :func:`kadi_get_preview_templates` and
    :func:`kadi_get_preview_scripts`. Note that the hook chain will stop after the first
    returned result that is not ``None``.

    :param file: The :class:`.File` to get the preview data of.
    """


@hookspec
def kadi_get_preview_templates():
    """Hook for collecting templates for rendering preview data.

    Each template should consist of an HTML snippet containing all necessary markup to
    render the preview data. As currently all previews are rendered using Vue.js
    components, the easiest way to include a custom preview is by using such a
    component, which can automatically receive the preview data from the backend as
    shown in the following example:

    .. code-block:: html

        <!-- Check the preview type first before rendering the component. -->
        <div v-if="previewData.type === 'my_plugin_preview_type'">
            <!-- Pass the preview data from the backend into the component. -->
            <my-plugin-preview :data="previewData.data"></my-plugin-preview>
        </div>

    In order to actually register the custom component via JavaScript,
    :func:`kadi_get_preview_scripts` needs to be used. Should also be used together with
    :func:`kadi_get_preview_data`.
    """


@hookspec
def kadi_get_preview_scripts():
    """Hook for collecting scripts for rendering preview data.

    Each script has to be returned as a string or a list of strings, each string
    representing the full URL where the script can be loaded from. As only internal
    scripts can currently be used, scripts should be loaded via a custom static route,
    which a plugin can define by using :func:`kadi_register_blueprints`.

    The following example shows how a custom (global) Vue.js component can be
    registered, which can be used in combination with a template such as the one shown
    in :func:`kadi_get_preview_templates`:

    .. code-block:: js

        Vue.component('my-plugin-preview', {
            // The type of the passed data prop depends on how the preview data is
            // returned from the backend.
            props: {
                data: String,
            },
            // Note the custom delimiters, which are used so they can coexist with
            // Jinja's templating syntax when not using single file components.
            template: `
                <div>{$ data $}</div>
            `,
        })

    Should also be used together with :func:`kadi_get_preview_data`.
    """


@hookspec
def kadi_post_record_create(record):
    """Hook to run operations after a record was created.

    The hook is not executed until the record is successfully created and the changes
    are persisted in the database. Plugins should not make any changes to the record
    anymore.

    :param record: The newly created record.
    """


@hookspec
def kadi_post_record_update(record):
    """Hook to run operations after a record was updated.

    The hook is not executed until the record is successfully updated and the changes
    are persisted in the database. Plugins should not make any changes to the record
    anymore.

    Note that the hook is only executed if the update triggered the creation of a new
    revision, which in turn can be used to react to updates to specific (revisioned)
    attributes, e.g. the latest revision can be retrieved via
    ``record.ordered_revisions.first()``.

    :param record: The updated record.
    """
