"""
Base settings to build other settings files upon.
"""

import environ
import sys
import os

ROOT_DIR = (
    environ.Path(__file__) - 3
)
BACKEND_DIR = ROOT_DIR.path("backend")

# env = environ.Env()  # django-sso-app

# django-sso-app
from django_sso_app.settings import *


READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", True)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")  # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", default="en")  # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = env.int("DJANGO_SITE_ID", default=1)  # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(ROOT_DIR.path("locale"))]


# pai
TESTING_MODE = 'test' in sys.argv or 'setup.py' in sys.argv

# file uploads
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# slashes
APPEND_SLASH = True

# extra
from .extra import EXTRA_APPS, EXTRA_ADMINS

# context_processors
DEPLOYMENT_ENV = env("DEPLOYMENT_ENV", default='dev' if DEBUG else 'production')
REPOSITORY_REV = env("REPOSITORY_REV", default=None)
EMAILS_DOMAIN = env('EMAILS_DOMAIN', default=APP_DOMAIN)  # domain name specified in email templates
EMAILS_SITE_NAME = env('EMAILS_SITE_NAME', default=COOKIE_DOMAIN)  # site name specified in email templates
GOOGLE_API_KEY = env('GOOGLE_API_KEY', default='undefined')
GOOGLE_MAPS_API_VERSION = env('GOOGLE_MAPS_API_VERSION', default='3.34')
GOOGLE_ANALYTICS_TRACKING_ID = env('GOOGLE_ANALYTICS_TRACKING_ID', default='')
RAVEN_JS_DSN = env('RAVEN_JS_DSN',default='')
MAPBOX_ACCESSTOKEN = env('MAPBOX_ACCESSTOKEN',
                         default='pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw')

# languages
from .languages import *

# meta
META_DESCRIPTION = env('META_DESCRIPTION', default='Django SSO app')
META_SITE_PROTOCOL = ACCOUNT_DEFAULT_HTTP_PROTOCOL
META_USE_SITES = True
META_SITE_DOMAIN = APP_DOMAIN
META_SITE_NAME = COOKIE_DOMAIN
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_GOOGLEPLUS_PROPERTIES = False
META_USE_TITLE_TAG = False


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
USE_SQLITE = env.bool("USE_SQLITE", default=TESTING_MODE)  # TESTING_MODE uses sqlite
if USE_SQLITE:  # pai
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(ROOT_DIR, 'db.sqlite3')
        }
    }
    DATABASES["default"]["ATOMIC_REQUESTS"] = True
else:
    DATABASES = {"default": env.db("DATABASE_URL")}

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "django_sso_app.config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "django_sso_app.config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
    "django.contrib.flatpages",

    "django.contrib.sitemaps",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    # "allauth",  # django-sso-app
    # "allauth.account",  # django-sso-app
    # "allauth.socialaccount",  # django-sso-app
    "rest_framework",

    # pai
    "corsheaders",
    "meta",

    "django_filters",
    "django_celery_beat",
    "django_celery_results",

    "rpc4django",

    "drf_yasg",

    "django_project_backup"
]

LOCAL_APPS = [
    "django_sso_app.backend.users.apps.UsersConfig",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + DJANGO_SSO_APP_DJANGO_APPS + EXTRA_APPS  # pai

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
# MIGRATION_MODULES = {"sites": "django_sso_app.backend.contrib.sites.migrations"}  # pai

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    # "allauth.account.auth_backends.AuthenticationBackend",  # django-sso-app
] + DJANGO_SSO_APP_DJANGO_AUTHENTICATION_BACKENDS
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "/"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
# https://docs.djangoproject.com/en/2.2/topics/auth/passwords/#using-argon2-with-django
# Argon2 is the winner of the 2015 Password Hashing Competition,
# a community organized open competition to select a next generation hashing algorithm.
# It’s designed not to be easier to compute on custom hardware than it is to compute on an ordinary CPU.
PASSWORD_HASHERS = env.list('DJANGO_PASSWORD_HASHERS', default=[
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
])

""" pai
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
"""
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]  # pai

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django_sso_app.core.middleware.x_forwarded_for.XForwardedForMiddleware",  # django-sso-app
    # "django_sso_app.core.middleware.same_site.SameSiteMiddleware",  # django-sso-app

    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # pai
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",  # required by django-sso-app
    "django_sso_app.core.authentication.middleware.DjangoSsoAppAuthenticationMiddleware",  # django-sso-app

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",  # pai
]

# STATIC
# ------------------------------------------------------------------------------
# pai
_ENV_PUBLIC_ROOT = env('DJANGO_PUBLIC_ROOT', default=None)
if _ENV_PUBLIC_ROOT is None:
    PUBLIC_ROOT = ROOT_DIR.path("public")
else:
    PUBLIC_ROOT = environ.Path(_ENV_PUBLIC_ROOT)

_ENV_PRIVATE_ROOT = env('DJANGO_PRIVATE_ROOT', default=None)
if _ENV_PRIVATE_ROOT is None:
    PRIVATE_ROOT = ROOT_DIR.path("private")
else:
    PRIVATE_ROOT = environ.Path(_ENV_PRIVATE_ROOT)

# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(PUBLIC_ROOT("static"))  # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(BACKEND_DIR.path("static"))]  # pai

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(PUBLIC_ROOT("media"))  # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates

if DJANGO_SSO_APP_BACKEND_CUSTOM_FRONTEND_APP:
    _TEMPLATE_DIRS = []
else:
    _TEMPLATE_DIRS = [str(BACKEND_DIR.path("templates"))]


TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": _TEMPLATE_DIRS,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",

                # "django_sso_app.backend.utils.context_processors.settings_context",  # pai (dangerous)
                'django_sso_app.backend.utils.context_processors.get_stats_info',  # pai

                # django-sso-app
                'django_sso_app.core.context_processors.django_sso_app_context',

                # extra
                'django_sso_app.backend.context_processors.django_meta',
                'django_sso_app.backend.context_processors.google_api_settings',
                'django_sso_app.backend.context_processors.raven_js_dsn_settings',
            ],
        },
    }
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
# FIXTURE_DIRS = (str(ROOT_DIR.path("fixtures")),)  # prevent external fixtures import error

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = False if DEBUG else True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = False  #!! True breaks treebeard (https://github.com/django-treebeard/django-treebeard/issues/92)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# pai
ENABLE_HTTPS = env.bool("ENABLE_HTTPS", default=not DEBUG)
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env("ACCOUNT_DEFAULT_HTTP_PROTOCOL", default="https" if ENABLE_HTTPS else "http")

# CSRF
if DEBUG:
    CSRF_COOKIE_DOMAIN = None
    CSRF_TRUSTED_ORIGINS = ['*']

# cors
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    # https://github.com/ottoyiu/django-cors-headers
    _CORS_ORIGINS = env("CORS_ORIGINS", default='{0}://{1}'.format(ACCOUNT_DEFAULT_HTTP_PROTOCOL, APP_DOMAIN))
    CORS_ALLOWED_ORIGINS = list(map(lambda x: '{}'.format(x.replace(' ', '')), _CORS_ORIGINS.split(',')))
    CORS_ALLOW_CREDENTIALS = True


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Luca Bertuol""", "paiuolo@gmail.com")]
# extra
if len(EXTRA_ADMINS):
    ADMINS = EXTRA_ADMINS

# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "root": {"level": "DEBUG", "handlers": ["console"]},
        "environ": {"level": "INFO", "handlers": ["console"]},
        "factory": {"level": "INFO", "handlers": ["console"]},
    }
}

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE

# pai
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
#CELERY_BROKER_URL = env("CELERY_BROKER_URL")
## http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
#CELERY_RESULT_BACKEND = CELERY_BROKER_URL

if REDIS_ENABLED:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
    CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
    # CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_BACKEND = 'django-db'  # pai

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_SOFT_TIME_LIMIT = 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# pai
# enable task state monitoring
CELERY_TRACK_STARTED = True

# django-reset-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.SessionAuthentication",  # pai
        "django_sso_app.core.api.authentication.DjangoSsoApiAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),

    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    # "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),

    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",

    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}
# Your stuff...
# ------------------------------------------------------------------------------

# django-project-backup
SERIALIZATION_MODULES = {
    'dpb_couchdb_datastore': 'django_project_backup.utils.couchdb.serializers'
}

DJANGO_PROJECT_BACKUP_MODE = env('DJANGO_PROJECT_BACKUP_MODE', default='incremental')

DJANGO_PROJECT_BACKUP_REALTIME = env.bool('DJANGO_PROJECT_BACKUP_REALTIME', default=False)

DJANGO_PROJECT_BACKUP_EXCLUDED_MODELS = env.list('DJANGO_PROJECT_BACKUP_EXCLUDED_MODELS', default=[
    'sessions.session',
    'admin.logentry',
    'django_sso_app.passepartout',
    'django_sso_app.device'
])

DJANGO_PROJECT_BACKUP_PUBLIC_ASSETS_FOLDERS = env.list('DJANGO_PROJECT_BACKUP_PUBLIC_ASSETS_FOLDERS',
                                                        default=[str(PUBLIC_ROOT)])

DJANGO_PROJECT_BACKUP_PRIVATE_ASSETS_FOLDERS = env.list('DJANGO_PROJECT_BACKUP_PRIVATE_ASSETS_FOLDERS',
                                                        default=[str(PRIVATE_ROOT)])

DJANGO_PROJECT_BACKUP_DESTINATION_FOLDER = env('DJANGO_PROJECT_BACKUP_DESTINATION_FOLDER',
                                               default=os.path.join(ROOT_DIR, 'backups'))

DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_URL = env('DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_URL', default='http://127.0.0.1:5984')
DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_USER = env('DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_USER', default='admin')
DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_PASSWORD = env('DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_PASSWORD', default='couchdb')
# couchdb db index
DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_DATABASE_NAME = env('DJANGO_PROJECT_BACKUP_COUCHDB_DATASTORE_DATABASE_NAME',
                                                            default='django_sso_app')

DJANGO_PROJECT_BACKUP_DO_FAILSAFE_BACKUP = env.bool('DJANGO_PROJECT_BACKUP_DO_FAILSAFE_BACKUP',
                                                    default=True)
DJANGO_PROJECT_BACKUP_FAILSAFE_BACKUP_PATH = env('DJANGO_PROJECT_BACKUP_FAILSAFE_BACKUP_PATH',
                                                 default=os.path.join(DJANGO_PROJECT_BACKUP_DESTINATION_FOLDER, 'failed'))

DJANGO_PROJECT_BACKUP_DO_REALTIME_COUCHDB_BACKUP = env.bool('DJANGO_PROJECT_BACKUP_DO_REALTIME_COUCHDB_BACKUP',
                                                            default=DJANGO_PROJECT_BACKUP_REALTIME)
DJANGO_PROJECT_BACKUP_DO_REALTIME_LOG_BACKUP = env.bool('DJANGO_PROJECT_BACKUP_DO_REALTIME_LOG_BACKUP',
                                                        default=False)


from .extra import *  # pai
