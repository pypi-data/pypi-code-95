import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'c(0&0l4*hsdh+#9xgtb^&a)60wdg4+umxvujrp4c+s3a@n+h(d'
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'livesync',
    'django_brython',
    'django.contrib.staticfiles',

    'kirui_devserver.backend',
    'django_kirui'
    # 'kirui'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'livesync.core.middleware.DjangoLiveSyncMiddleware',
]

ROOT_URLCONF = 'kirui_devserver.server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django_kirui.backend.DjangoSamonTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/xml')],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django_kirui.context_processors.djsamon',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/html')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

from django.template.backends.django import DjangoTemplates

WSGI_APPLICATION = 'kirui_devserver.server.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sq3',
    }
}

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

STATIC_URL = '/static/valami/'
STATIC_ROOT = f'/{BASE_DIR}/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

STATICFILES_FINDERS = [
    # 'django_brython.staticfiles.BrythonStaticGenerator',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

BRYTHON_BUNDLER_MAIN_MODULE = 'kirui'
BRYTHON_BUNDLER_EXCLUDE = [
    'kirui.tests',
    'kirui.apps'
]

DJANGO_LIVESYNC = {
    'EVENT_HANDLER': 'django_brython.livesync.handler.DjangoBrythonEventHandler'
}

#DJANGO_LIVESYNC = {
#    'EVENT_HANDLER': 'livesync.core.handler.LiveReloadRequestHandler'
#}

DJANGO_SAMON_BINDING_CLASS = 'django_kirui.context_processors.DjangoSamonBinding'
