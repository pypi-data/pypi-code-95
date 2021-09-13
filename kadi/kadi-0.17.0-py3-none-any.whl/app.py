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
import json
import logging
import os
import warnings
from logging.handlers import SMTPHandler

import sentry_sdk
from flask import Flask
from flask.logging import default_handler
from flask_babel import lazy_gettext
from pluggy import PluginManager
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.middleware.proxy_fix import ProxyFix

import kadi.lib.constants as const
from .config import configs
from kadi.ext.babel import babel
from kadi.ext.celery import celery
from kadi.ext.csrf import csrf
from kadi.ext.db import db
from kadi.ext.limiter import limiter
from kadi.ext.login import login
from kadi.ext.migrate import migrate
from kadi.ext.oauth import oauth
from kadi.ext.talisman import talisman
from kadi.lib.api.blueprint import bp as api_bp
from kadi.lib.api.models import AccessToken
from kadi.lib.api.models import AccessTokenScope
from kadi.lib.conversion import truncate
from kadi.lib.db import TimestampMixin
from kadi.lib.format import duration
from kadi.lib.format import filesize
from kadi.lib.format import pretty_type_name
from kadi.lib.format import timestamp
from kadi.lib.forms import json_field
from kadi.lib.licenses.models import License
from kadi.lib.oauth.models import OAuth2Token
from kadi.lib.revisions.core import setup_revisions
from kadi.lib.revisions.models import Revision
from kadi.lib.search.core import SearchableMixin
from kadi.lib.search.elasticsearch import es
from kadi.lib.tags.models import Tag
from kadi.lib.tasks.models import Task
from kadi.lib.utils import compact_json
from kadi.lib.web import get_locale
from kadi.lib.web import IdentifierConverter
from kadi.lib.web import static_url
from kadi.lib.web import url_for
from kadi.modules.accounts.blueprint import bp as accounts_bp
from kadi.modules.accounts.models import Identity
from kadi.modules.accounts.models import LDAPIdentity
from kadi.modules.accounts.models import LocalIdentity
from kadi.modules.accounts.models import ShibIdentity
from kadi.modules.accounts.models import User
from kadi.modules.accounts.providers import LocalProvider
from kadi.modules.accounts.providers.core import init_auth_providers
from kadi.modules.accounts.utils import json_user
from kadi.modules.collections.blueprint import bp as collections_bp
from kadi.modules.collections.models import Collection
from kadi.modules.groups.blueprint import bp as groups_bp
from kadi.modules.groups.models import Group
from kadi.modules.main.blueprint import bp as main_bp
from kadi.modules.main.tasks import _clean_resources_task
from kadi.modules.notifications.blueprint import bp as notifications_bp
from kadi.modules.notifications.models import Notification
from kadi.modules.notifications.tasks import _send_mail_task
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.models import Permission
from kadi.modules.permissions.models import Role
from kadi.modules.permissions.utils import get_object_roles
from kadi.modules.records.blueprint import bp as records_bp
from kadi.modules.records.models import Chunk
from kadi.modules.records.models import File
from kadi.modules.records.models import Record
from kadi.modules.records.models import RecordLink
from kadi.modules.records.models import TemporaryFile
from kadi.modules.records.models import Upload
from kadi.modules.records.tasks import _clean_files_task
from kadi.modules.records.tasks import _merge_chunks_task
from kadi.modules.records.tasks import _package_files_task
from kadi.modules.records.tasks import _publish_record_task
from kadi.modules.records.tasks import _purge_record_task
from kadi.modules.settings.blueprint import bp as settings_bp
from kadi.modules.sysadmin.blueprint import bp as sysadmin_bp
from kadi.modules.templates.blueprint import bp as templates_bp
from kadi.modules.templates.models import Template
from kadi.modules.workflows.blueprint import bp as workflows_bp
from kadi.modules.workflows.models import Workflow
from kadi.plugins import impl
from kadi.plugins import run_hook
from kadi.plugins import spec
from kadi.plugins import template_hook

# This warning can happen when accessing the server the application runs on directly by
# IP address. Werkzeug will just return an invalid match (404) in this case, triggering
# the usual error handling of the application.
warnings.filterwarnings(
    "ignore",
    module="flask.app",
    category=UserWarning,
    message="Current server name '.*' doesn't match configured server name '.*'",
)


def create_app(flask_env=None):
    """Create a new application object.

    :param flask_env: (optional) The environment the application should run in. One of
        ``"production"``, ``"development"`` or ``"testing"``. Defaults to the value of
        the ``FLASK_ENV`` environment variable or ``"production"``.
    :return: The new application object.
    """
    app = Flask(__name__)

    if flask_env is None:
        flask_env = os.environ.get("FLASK_ENV", "production")

    _load_config(app, flask_env)
    _load_plugins(app)
    _init_extensions(app)
    _init_i18n(app)
    _init_celery(app)
    _init_app(app)
    _register_blueprints(app)
    _setup_jinja(app)
    _setup_logging(app)
    _setup_shell_context(app)

    return app


def _load_config(app, flask_env):
    app.config.from_object(configs[flask_env])

    if os.environ.get("KADI_CONFIG_FILE"):
        app.config.from_envvar("KADI_CONFIG_FILE")

    # Flask only sets this automatically when using an environment variable.
    app.config["ENV"] = flask_env

    interpolations = {
        "instance_path": app.instance_path,
        "root_path": app.root_path,
        "static_path": app.static_folder,
    }

    for key, value in app.config.items():
        if isinstance(value, str):
            app.config[key] = value.format(**interpolations)

    # Allow for the maximum content length to be at least the configured upload chunk
    # size and maximum image size plus some additional padding of 1 MB.
    max_size = max(app.config["UPLOAD_CHUNK_SIZE"], app.config["MAX_IMAGE_SIZE"])
    app.config["MAX_CONTENT_LENGTH"] = max_size + const.ONE_MB

    # See also: kadi.cli.commands.assets
    app.config["MANIFEST_MAPPING"] = None
    manifest_path = app.config["MANIFEST_PATH"]

    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            app.config["MANIFEST_MAPPING"] = json.load(f)

    # Specify the amount of "X-Forwarded-*" header values to trust.
    if app.config["PROXY_FIX_ENABLE"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, **app.config["PROXY_FIX_HEADERS"])

    # Verify that the most important, required config values have at least been set.
    if not app.testing:
        for key in [
            "MISC_UPLOADS_PATH",
            "SECRET_KEY",
            "SERVER_NAME",
            "SQLALCHEMY_DATABASE_URI",
            "STORAGE_PATH",
        ]:
            if not app.config[key]:
                raise ValueError(f"The '{key}' configuration value has not been set.")


def _load_plugins(app):
    plugin_manager = PluginManager("kadi")
    plugin_manager.add_hookspecs(spec)

    # Load all plugins that registered themselves via the entry point.
    for plugin in app.config["PLUGINS"]:
        plugin_manager.load_setuptools_entrypoints(
            app.config["PLUGIN_ENTRYPOINT"], name=plugin
        )

    # Register all builtin hook implementations.
    plugin_manager.register(impl)

    app.plugin_manager = plugin_manager


def _init_extensions(app):
    babel.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db, directory=app.config["MIGRATIONS_PATH"])
    oauth.init_app(app)
    talisman.init_app(app, **app.config["FLASK_TALISMAN_OPTIONS"])

    sentry_dsn = app.config["SENTRY_DSN"]
    if sentry_dsn:
        # pylint: disable=abstract-class-instantiated
        sentry_sdk.init(
            dsn=sentry_dsn, integrations=[CeleryIntegration(), FlaskIntegration()]
        )


def _init_i18n(app):
    # Done here, since both the extension and the plugins need to be initialized. See
    # also: kadi.cli.commands.i18n
    translations_path = app.config["BACKEND_TRANSLATIONS_PATH"]

    with app.app_context():
        plugin_translations_paths = run_hook("kadi_get_translations_paths")

    if plugin_translations_paths:
        translations_path = f"{';'.join(plugin_translations_paths)};{translations_path}"

    app.config["BABEL_TRANSLATION_DIRECTORIES"] = translations_path


def _init_celery(app):
    # This function will initialize celery for use in both the application and the
    # actual worker processes to start and execute tasks respectively.
    prefix = "CELERY_"

    for key, value in app.config.items():
        if key.startswith(prefix):
            setattr(celery.conf, key[len(prefix) :].lower(), value)

    class ContextTask(celery.Task):
        """Wrapper for tasks to run inside their own application context."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    celery.tasks.register(_clean_resources_task)
    celery.tasks.register(_send_mail_task)
    celery.tasks.register(_clean_files_task)
    celery.tasks.register(_merge_chunks_task)
    celery.tasks.register(_package_files_task)
    celery.tasks.register(_publish_record_task)
    celery.tasks.register(_purge_record_task)


def _init_app(app):
    # Register custom URL converters.
    app.url_map.converters["identifier"] = IdentifierConverter

    # Register miscellaneous plugin hooks.
    with app.app_context():
        run_hook("kadi_register_oauth2_providers", registry=oauth)

    # Other miscellaneous initializations.
    setup_revisions()
    init_auth_providers(app)
    TimestampMixin.register_timestamp_listener()

    es.init_app(app)
    if app.config["ELASTICSEARCH_HOSTS"]:
        SearchableMixin.register_search_listeners()


def _register_blueprints(app):
    if app.config["EXPERIMENTAL_FEATURES"]:
        import kadi.modules.workflows.api  # pylint: disable=unused-import

        app.register_blueprint(workflows_bp, url_prefix="/workflows")

    # Register plugin blueprints.
    with app.app_context():
        run_hook("kadi_register_blueprints", app=app)

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(accounts_bp)
    app.register_blueprint(collections_bp, url_prefix="/collections")
    app.register_blueprint(groups_bp, url_prefix="/groups")
    app.register_blueprint(main_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(records_bp, url_prefix="/records")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(sysadmin_bp, url_prefix="/sysadmin")
    app.register_blueprint(templates_bp, url_prefix="/templates")


def _setup_jinja(app):
    # Provide access to some useful builtins in all templates.
    builtins = [abs, all, any, bool, dict, enumerate, filter, float, getattr, hasattr]
    builtins += [int, isinstance, len, list, max, min, repr, reversed, setattr, sorted]
    builtins += [str, sum, zip]

    for builtin in builtins:
        app.jinja_env.globals[builtin.__name__] = builtin

    app.jinja_env.globals.update(
        {
            "_l": lazy_gettext,
            "get_locale": get_locale,
            "get_object_roles": get_object_roles,
            "has_permission": has_permission,
            "json_field": json_field,
            "json_user": json_user,
            "registration_allowed": LocalProvider.registration_allowed,
            "static_url": static_url,
            "template_hook": template_hook,
            "url_for": url_for,
        }
    )

    app.jinja_env.filters.update(
        {
            "duration": duration,
            "filesize": filesize,
            "escaped_json": compact_json,
            "pretty_type_name": pretty_type_name,
            "timestamp": timestamp,
            "truncate": truncate,
        }
    )

    app.jinja_env.add_extension("kadi.lib.jinja.SnippetExtension")


def _setup_logging(app):
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )

    # Flasks default handler is a StreamHandler writing to the stream specified by the
    # WSGI server or to stderr outside of a request.
    default_handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)

    mail_error_logs = app.config["MAIL_ERROR_LOGS"]
    if mail_error_logs:
        auth = None
        secure = None

        if app.config["SMTP_USERNAME"] and app.config["SMTP_PASSWORD"]:
            auth = (app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])
            if app.config["SMTP_USE_TLS"]:
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config["SMTP_HOST"], app.config["SMTP_PORT"]),
            fromaddr=app.config["MAIL_NO_REPLY"],
            toaddrs=mail_error_logs,
            subject="[Kadi4Mat] Error Log",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setFormatter(formatter)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # Disable non-error messages in the Elasticsearch logger, which otherwise seem to
    # propagate to the celery logger.
    logging.getLogger("elasticsearch").setLevel(logging.ERROR)


def _setup_shell_context(app):
    @app.shell_context_processor
    def _shell_context():
        # The listed names will be imported automatically when running "flask shell" or
        # "kadi shell".
        return {
            "db": db,
            "es": es,
            "AccessToken": AccessToken,
            "AccessTokenScope": AccessTokenScope,
            "Chunk": Chunk,
            "Collection": Collection,
            "File": File,
            "Group": Group,
            "Identity": Identity,
            "LDAPIdentity": LDAPIdentity,
            "License": License,
            "LocalIdentity": LocalIdentity,
            "Template": Template,
            "Notification": Notification,
            "OAuth2Token": OAuth2Token,
            "Permission": Permission,
            "Record": Record,
            "RecordLink": RecordLink,
            "Revision": Revision,
            "Role": Role,
            "ShibIdentity": ShibIdentity,
            "Tag": Tag,
            "Task": Task,
            "TemporaryFile": TemporaryFile,
            "Upload": Upload,
            "User": User,
            "Workflow": Workflow,
        }
