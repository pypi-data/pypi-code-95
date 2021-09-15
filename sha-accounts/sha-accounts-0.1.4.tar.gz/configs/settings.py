from pathlib import Path
from os import getenv
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv('DJANGO_SECRET_KEY')

DEBUG = getenv('DJANGO_DEBUG', True)

ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

DJANGO_DEFAULT_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

DEBUG_APPS = [
    'django.contrib.staticfiles',
    'drf_yasg',
]

THIRD_PARTIES = [
    'rest_framework',
]

LOCAL_APPS = [
    'sha_accounts',
    'examples'
]

INSTALLED_APPS = DJANGO_DEFAULT_APPS+THIRD_PARTIES+LOCAL_APPS
if DEBUG:
    INSTALLED_APPS += DEBUG_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'configs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'configs.wsgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'token-cache': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
    }
else:
    # Set a database connection and cache
    pass

# Set your customized REST_FRAMEWORK settings
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'djrest_wrapper.exceptions.handler.exception_handler',
    'DEFAULT_RENDERER_CLASSES': ['djrest_wrapper.renderers.defaultjson.DefaultJsonRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'djrest_wrapper.paginations.default.DefaultPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'sha_accounts.backends.authentications.JwtAuthentication',
         ]}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'sha_accounts.User'

SHA_ACCOUNTS = {
    'DEFAULT_ACTIVATION': True,
    'AUTH_USER_PROFILE_MODEL': 'examples.ExampleProfile',
    'JWT_ACCESS_TOKEN_EXP': timedelta(days=1),
    'JWT_USER_ENCODED_FIELDS': ['id'],
    'JWT_AUTH_RAELM': 'sample_raelm'
}
