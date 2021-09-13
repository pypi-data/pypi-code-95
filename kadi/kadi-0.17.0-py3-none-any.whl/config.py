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
import os
import socket
from collections import OrderedDict

from celery.schedules import crontab

import kadi.lib.constants as const


class BaseConfig:
    """Base configuration."""

    ##########
    # Celery #
    ##########

    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
    }

    CELERY_BROKER_URL = "redis://localhost:6379/0"

    CELERY_WORKER_REDIRECT_STDOUTS = False

    CELERY_BEAT_SCHEDULE = {
        "clean-files-periodically": {
            "task": "kadi.records.clean_files",
            "schedule": crontab(minute="*/15"),
        },
        "clean-resources-periodically": {
            "task": "kadi.main.clean_resources",
            "schedule": crontab(minute="*/15"),
        },
    }

    #########
    # Flask #
    #########

    # Per default, only static files in production environments are cached via headers
    # set by the web server.
    SEND_FILE_MAX_AGE_DEFAULT = 0

    SESSION_COOKIE_DOMAIN = False

    SESSION_COOKIE_NAME = "kadi_session"

    ###########
    # Limiter #
    ###########

    RATELIMIT_HEADERS_ENABLED = True

    RATELIMIT_STORAGE_URL = "redis://localhost:6379/0"

    #########
    # Login #
    #########

    # Makes a stolen cookie much harder to use. Should work without problems as we do
    # not use the remember cookie.
    SESSION_PROTECTION = "strong"

    ##############
    # SQLAlchemy #
    ##############

    SQLALCHEMY_DATABASE_URI = None

    # Pessimistic disconnect handling.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ############
    # Talisman #
    ############

    # Some options are only turned off since they are handled separately already.
    FLASK_TALISMAN_OPTIONS = {
        "content_security_policy": {
            "default-src": "'self'",
            "object-src": "'none'",
            "img-src": ["'self'", "data:"],
            "script-src": ["'self'", "'unsafe-eval'"],
            "style-src": ["'self'", "'unsafe-inline'", "data:"],
        },
        "content_security_policy_nonce_in": "script-src",
        "force_https": False,
        "session_cookie_secure": False,
    }

    ###########
    # WTForms #
    ###########

    WTF_CSRF_TIME_LIMIT = None

    ########
    # Kadi #
    ########

    API_SCOPES = {
        "user": ["read"],
        "misc": ["manage_trash"],
    }

    API_VERSIONS = ["1.0"]

    AUTH_PROVIDERS = [{"type": "local"}]

    AUTH_PROVIDER_TYPES = {
        "local": {
            "provider": "kadi.modules.accounts.providers.LocalProvider",
            "identity": "kadi.modules.accounts.models.LocalIdentity",
            "form": "kadi.modules.accounts.forms.CredentialsLoginForm",
        },
        "ldap": {
            "provider": "kadi.modules.accounts.providers.LDAPProvider",
            "identity": "kadi.modules.accounts.models.LDAPIdentity",
            "form": "kadi.modules.accounts.forms.CredentialsLoginForm",
        },
        "shib": {
            "provider": "kadi.modules.accounts.providers.ShibProvider",
            "identity": "kadi.modules.accounts.models.ShibIdentity",
            "form": "kadi.modules.accounts.forms.ShibLoginForm",
        },
    }

    BACKEND_TRANSLATIONS_PATH = os.path.join("{root_path}", "translations")

    EXPERIMENTAL_FEATURES = True

    # Current export types with corresponding titles for different resources.
    EXPORT_TYPES = {
        "record": OrderedDict([("json", "JSON"), ("pdf", "PDF"), ("qr", "QR Code")]),
        "collection": OrderedDict([("json", "JSON"), ("qr", "QR Code")]),
    }

    # Path for fonts used outside the web browser context.
    FONTS_PATH = os.path.join("{root_path}", "assets", "fonts")

    FOOTER_NAV_ITEMS = []

    FRONTEND_TRANSLATIONS_PATH = os.path.join("{root_path}", "assets", "translations")

    # Valid MIME types for direct image previews and user and group images.
    IMAGE_MIMETYPES = ["image/jpeg", "image/png"]

    INACTIVE_FILES_MAX_AGE = const.ONE_DAY

    # Default URL from which license metadata is retrieved.
    LICENSES_URL = "https://licenses.opendefinition.org/licenses/groups/all.json"

    LOCALES = {
        "de": "Deutsch (beta)",
        "en": "English",
    }

    LOCALE_COOKIE_NAME = "locale"

    LOCALE_COOKIE_SECURE = False

    LOCALE_DEFAULT = "en"

    MAIL_ERROR_LOGS = []

    MAIL_NO_REPLY = f"no-reply@{socket.getfqdn()}"

    MANIFEST_PATH = os.path.join("{static_path}", "manifest.json")

    # Maximum size in bytes for user and group images.
    MAX_IMAGE_SIZE = 10 * const.ONE_MB

    MAX_UPLOAD_SIZE = const.ONE_GB

    MAX_UPLOAD_USER_QUOTA = 10 * const.ONE_GB

    MIGRATIONS_PATH = os.path.join("{root_path}", "migrations")

    MISC_UPLOADS_PATH = None

    # Maximum size in bytes for files sent directly to a client for preview.
    PREVIEW_MAX_SIZE = 25 * const.ONE_MB

    PLUGIN_CONFIG = {}

    PLUGIN_ENTRYPOINT = "kadi_plugins"

    PLUGINS = []

    PROXY_FIX_ENABLE = False

    PROXY_FIX_HEADERS = {
        "x_for": 1,
        "x_proto": 1,
        "x_host": 1,
        "x_port": 0,
        "x_prefix": 0,
    }

    # Global rate limit for anonymous users.
    RATELIMIT_ANONYMOUS_USER = "100/minute;5/second"

    # Global rate limit for authenticated users.
    RATELIMIT_AUTHENTICATED_USER = "500/minute;25/second"

    RATELIMIT_IP_WHITELIST = ["127.0.0.1"]

    # URL from which the latest published Kadi version is retrieved.
    RELEASE_URL = "https://pypi.org/pypi/kadi/json"

    # Global timeout for external requests in seconds.
    REQUESTS_TIMEOUT = 5

    RESOURCES_MAX_AGE = const.ONE_WEEK

    SENTRY_DSN = None

    SMTP_HOST = "localhost"

    SMTP_PASSWORD = ""

    SMTP_PORT = 25

    SMTP_TIMEOUT = 60

    SMTP_USE_TLS = False

    SMTP_USERNAME = ""

    STORAGE_PATH = None

    SYSTEM_ROLES = {
        "admin": {
            "record": ["create", "read", "update", "link", "permissions", "delete"],
            "collection": ["create", "read", "update", "link", "permissions", "delete"],
            "group": ["create", "read", "update", "members", "delete"],
            "template": ["create", "read", "update", "permissions", "delete"],
        },
        "member": {
            "record": ["create"],
            "collection": ["create"],
            "group": ["create"],
            "template": ["create"],
        },
        "guest": {},
    }

    TEMPORARY_FILES_MAX_AGE = 15 * const.ONE_MINUTE

    UPLOAD_CHUNK_SIZE = 10 * const.ONE_MB

    UPLOADS_MAX_AGE = const.ONE_DAY


class ProductionConfig(BaseConfig):
    """Production configuration."""

    #########
    # Flask #
    #########

    FLASK_SKIP_DOTENV = True

    PREFERRED_URL_SCHEME = "https"

    SESSION_COOKIE_SECURE = True

    USE_X_SENDFILE = True

    ########
    # Kadi #
    ########

    EXPERIMENTAL_FEATURES = False

    LOCALE_COOKIE_SECURE = True


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    #################
    # Elasticsearch #
    #################

    # Ignore Elasticsearch not running and use a basic search fallback.
    ELASTICSEARCH_ENABLE_FALLBACK = True

    #########
    # Flask #
    #########

    SECRET_KEY = "s3cr3t"

    SERVER_NAME = "localhost:5000"

    ##############
    # SQLAlchemy #
    ##############

    SQLALCHEMY_DATABASE_URI = "postgresql://kadi:kadi@localhost/kadi"

    ########
    # Kadi #
    ########

    AUTH_PROVIDERS = [{"type": "local", "allow_registration": True}]

    MISC_UPLOADS_PATH = os.path.join("{instance_path}", "uploads")

    SMTP_PORT = 8025

    STORAGE_PATH = os.path.join("{instance_path}", "storage")


class TestingConfig(BaseConfig):
    """Testing configuration."""

    ##########
    # Celery #
    ##########

    # Ensure celery is never used.
    CELERY_BROKER_URL = None

    #################
    # Elasticsearch #
    #################

    # Ensure Elasticsearch is never used.
    ELASTICSEARCH_HOSTS = None

    #########
    # Flask #
    #########

    FLASK_SKIP_DOTENV = True

    SECRET_KEY = "s3cr3t"

    SERVER_NAME = "localhost"

    TESTING = True

    ###########
    # Limiter #
    ###########

    RATELIMIT_STORAGE_URL = "memory://"

    ##############
    # SQLAlchemy #
    ##############

    SQLALCHEMY_DATABASE_URI = "postgresql://kadi_test:kadi_test@localhost/kadi_test"

    ###########
    # WTForms #
    ###########

    WTF_CSRF_ENABLED = False

    ########
    # Kadi #
    ########

    AUTH_PROVIDERS = [
        {"type": "local", "allow_registration": True},
        {"type": "ldap"},
        {
            "type": "shib",
            "idps": [{"name": "Test", "entity_id": "https://idp.example.com"}],
        },
    ]


configs = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
