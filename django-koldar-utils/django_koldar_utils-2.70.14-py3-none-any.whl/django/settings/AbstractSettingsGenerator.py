import abc
import os
from typing import List, Dict, Optional, Tuple, Iterable

import environ
from django.conf import settings

from django.core.management.commands.runserver import Command as runserver
from django_koldar_utils.django.Orm import Orm
from django_koldar_utils.django.settings import settings_helper
from django_koldar_utils.functions import modules
from django_koldar_utils.models.AttrDict import AttrDict


class AbstractSettingsGenerator(abc.ABC):
    """
    A class that setup automatically settings.py.
    If you need to edit the file for every app, this is the place to update.

    In your settings.py you need to do only:

    .. :code-block:


    """

    def __init__(self):
        self.env: environ.Env = None
        self.settings_module: any = None
        self.settings_path: str = None
        """
        Absolute path of the settings.py file representing the configuration of the project
        """
        self.base_dir: str = None
        """
        Absolute path of the parent directory of project_dir 
        """
        self.project_dir: str = None
        """
        Absolute path of the directory where settings.py is located
        """
        self.project_dirname: str = None
        """
        directory name of project_dir
        """


    def _get_server_port(self) -> int:
        return self.env("SERVER_PORT")

    def _get_secret_key(self) -> int:
        return self.env("SECRET_KEY")

    @abc.abstractmethod
    def _configure_installed_apps(self, original: List[str]) -> List[str]:
        pass

    @abc.abstractmethod
    def _configure_middlewares(self, original: List[str]) -> List[str]:
        pass

    def _configure_caches(self, original: Dict[str, any]) -> Dict[str, any]:
        return original

    @abc.abstractmethod
    def _configure_authentication_backends(self) -> List[str]:
        pass

    def _get_auth_user_model(self) -> Optional[str]:
        """
        :return: get the AUTH user model. If returns null we wuill not set it at all
        """

    def _get_static_url(self) -> str:
        return '/static/'

    def _get_logging_configuration(self, original: Dict[str, any]) -> Dict[str, any]:
        return original

    def _get_media_root(self) -> str:
        return settings.MEDIA_ROOT

    def _get_media_url(self) -> str:
        return settings.MEDIA_URL

    def _add_other_settings(self, vars_to_set: AttrDict):
        pass

    @abc.abstractmethod
    def _get_apps_to_configure(self) -> Iterable[Tuple[str, str]]:
        """
        This is just a more comfortable way to add elements to the settings.py. You could also use _add_other_settings,
        but this method has been created for this very reason
        :return: an iterable specifying all the apps that you want to customize.
            Each app to customize is a pair.
                - First item is the name of the variable that will be put in the settings.py
                - Second item is the app label name
        """
        pass

    @abc.abstractmethod
    def _configure_app(self, settings_name: str, app_name: str, original_data: any) -> any:
        """
        :param settings_name: first element of an item yielded by _get_apps_to_configure
        :param app_name: second element of an item yielded by _get_apps_to_configure
        :param original_data: some application may have already a configuration established by this settings generator.
            If so this field will be non None
        :return: the object to assign to the new variable called `settings_name inside `settings.py`
        """
        pass

    def _generate_default_graphene_resolver_middlewares(self) -> List[str]:
        """
        When creating the default configuration of GRAPHENE app, you can choose to set in the default configuration
        additional graphql middlewares. Note that if you override the _configure_app of GRAPHENE app with
        your configuration, this modification may be resetted.
        """
        return []

    def _set_settings_var(self, **kwargs):
        """
        set all the variables specified in input inside the settings module. If a key-value already exists,
        it is overwritten
        """
        for k, v in kwargs.items():
            modules.add_variable_in_module(f"{self.project_dirname}.settings", k, v)

    def generate(self, settings_file: str):
        """
        populate the settings.py module. it is **mandatory** to call this function in settings.py file.
        As side effect, we will add variables in the settings.py module.

        :param settings_file: __file__ of settings.py
        """
        self.settings_path, self.base_dir, self.project_dir, self.project_dirname = settings_helper.get_paths(
            settings_file
        )
        self.env = settings_helper.read_env_file(
            ORM_TABLE_NAMING_CONVENTION=(str, "standard"),
            SAVE_GRAPHQL_SCHEMA=(str, None),
            DEBUG=(bool, False),
            SERVER_PORT=(int, 8080),
        )
        self.settings_module = settings
        vars_to_set = AttrDict()
        # add the interesting patthgs to the variables to set
        vars_to_set.SETTINGS_PATH = self.settings_path
        vars_to_set.BASE_DIR = self.base_dir
        vars_to_set.PROJECT_DIR = self.project_dir
        vars_to_set.PROJECT_DIRNAME = self.project_dirname
        vars_to_set = self._generate(vars_to_set)
        self._set_settings_var(**vars_to_set)

    def _generate(self, vars_to_set: AttrDict):
        vars_to_set.SECRET_KEY = self._get_secret_key()

        # #####################################################
        # Debug
        # #####################################################

        # SECURITY WARNING: don't run with debug turned on in production!
        vars_to_set.DEBUG = self.env("DEBUG")

        # #####################################################
        # CORS
        # #####################################################
        vars_to_set.CORS_ALLOW_HEADERS = ['*']
        vars_to_set.CORS_ORIGIN_ALLOW_ALL = True
        vars_to_set.CORS_ALLOW_ALL_ORIGINS = True

        # #####################################################
        # LISTENING IP AND PORT
        # #####################################################

        vars_to_set.ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

        if vars_to_set.DEBUG:
            # used for static live test server
            vars_to_set.ALLOWED_HOSTS.extend(["testserver"])

        # see https://stackoverflow.com/a/48277389/1887602
        runserver.default_port = self._get_server_port()

        # #####################################################
        # INSTALLED_APPS
        # #####################################################
        vars_to_set.INSTALLED_APPS = [
            # standard
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
        ]
        vars_to_set.INSTALLED_APPS = self._configure_installed_apps(vars_to_set.INSTALLED_APPS)

        # #####################################################
        # MIDDLEWARE
        # #####################################################
        vars_to_set.MIDDLEWARE = [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        vars_to_set.MIDDLEWARE = self._configure_middlewares(vars_to_set.MIDDLEWARE)

        vars_to_set.ROOT_URLCONF = f"{self.project_dirname}.urls"

        vars_to_set.TEMPLATES = [
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

        vars_to_set.WSGI_APPLICATION = f"{self.project_dirname}.wsgi.application"

        # #####################################################
        # Database
        # #####################################################
        # https://docs.djangoproject.com/en/3.1/ref/settings/#databases

        # alter the table convention
        Orm.set_table_naming_convention(self.env("ORM_TABLE_NAMING_CONVENTION"))

        vars_to_set.DATABASES = {
            'default': {
                'ENGINE': self.env('DATABASE_ENGINE'),
                'NAME': self.env("DATABASE_NAME"),
                'USER': self.env("DATABASE_USERNAME"),
                'PASSWORD': self.env("DATABASE_PASSWORD"),
                'HOST': self.env("DATABASE_HOSTNAME"),
                'PORT': self.env("DATABASE_PORT"),
            }
            # 'default': {
            #     'ENGINE': 'django.db.backends.mysql',
            #     'HOST': "auth.c0zcaytggc0x.eu-south-1.rds.amazonaws.com",
            #     'PORT': 3306,
            #     'NAME': "researchers-registry-service",
            #     'USER': "user-researcher-registry",
            #     'PASSWORD': "n5AYS*f!jVu&vGS*teHSOfBv666IM0hoI",
            # },
        }

        # #####################################################
        # User and Authentication
        # #####################################################
        # Password validation
        # https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

        vars_to_set.AUTH_PASSWORD_VALIDATORS = [
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

        vars_to_set.AUTHENTICATION_BACKENDS = self._configure_authentication_backends()

        m = self._get_auth_user_model()
        if m is not None:
            vars_to_set.AUTH_USER_MODEL = m

        # #####################################################
        # Internationalization
        # #####################################################s
        # https://docs.djangoproject.com/en/3.1/topics/i18n/

        vars_to_set.LANGUAGE_CODE = 'en-us'

        vars_to_set.TIME_ZONE = 'UTC'

        vars_to_set.USE_I18N = True

        vars_to_set.USE_L10N = True

        vars_to_set.USE_TZ = True

        # Static files (CSS, JavaScript, Images)
        # https://docs.djangoproject.com/en/3.1/howto/static-files/

        # #####################################################
        # STATIC CONTENT
        # #####################################################

        vars_to_set.STATIC_URL = self._get_static_url()
        vars_to_set.MEDIA_ROOT = self._get_media_root()
        vars_to_set.MEDIA_URL = self._get_media_url()

        # ##############################################################################
        # ADDED
        # ##############################################################################

        # CORS

        # see https://github.com/adamchainz/django-cors-headers
        # CORS_ALLOWED_ORIGINS = []
        # for x in ALLOWED_HOSTS:
        #     CORS_ALLOWED_ORIGINS.append(f"http://{x}")
        #     CORS_ALLOWED_ORIGINS.append(f"https://{x}")
        # CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:3000")
        # CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:8000")
        # CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:8001")

        # #####################################################
        # logging
        # #####################################################
        vars_to_set.LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
        vars_to_set.LOGGING = self._get_logging_configuration(vars_to_set.LOGGING)

        # #####################################################
        # CACHE system.
        # #####################################################
        vars_to_set.CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'default',
            }
        }
        vars_to_set.CACHES = self._configure_caches(vars_to_set.CACHES)

        # cbim-general-service

        # #####################################################
        # CONFIGURE ADDITIONAL APPLICATIONS
        # #####################################################

        # django-graphene-authentication
        vars_to_set.GRAPHENE_AUTHENTICATION = {
            "JWT_REFRESH_TOKEN_N_BYTES": 20,
            "JWT_REFRESH_TOKEN_MODEL": "from django_graphene_authentication.refresh_token.models.StandaloneRefreshToken"
        }

        # django-app-graphqls
        vars_to_set.GRAPHENE = {
            "SCHEMA": "django_app_graphql.graphene.schema.SCHEMA",
            'SCHEMA_OUTPUT': 'graphqls-schema.json',
            'SCHEMA_INDENT': 2,
            'MIDDLEWARE': [
                *self._generate_default_graphene_resolver_middlewares(),
                "django_app_graphql.middleware.GraphQLStackTraceInErrorMiddleware",
            ],
        }
        vars_to_set.GRAPHENE_DJANGO_EXTRAS = {
            'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
            'DEFAULT_PAGE_SIZE': 20,
            'MAX_PAGE_SIZE': 50,
            'CACHE_ACTIVE': True,
            'CACHE_TIMEOUT': 300  # seconds
        }
        vars_to_set.DJANGO_APP_GRAPHQL = {
            "BACKEND_TYPE": "graphene",
            "EXPOSE_GRAPHIQL": True,
            "GRAPHQL_SERVER_URL": "",
            "ENABLE_GRAPHQL_FEDERATION": True,
            "SAVE_GRAPHQL_SCHEMA": self.env("SAVE_GRAPHQL_SCHEMA"),
            "ADD_DUMMY_QUERIES_IF_ABSENT": True,
            "ADD_DUMMY_MUTATIONS_IF_ABSENT": True,
        }

        for settings_name, app_name in self._get_apps_to_configure():
            if settings_name in vars_to_set:
                original = vars_to_set[settings_name]
            else:
                original = None
            data = self._configure_app(settings_name, app_name, original)
            vars_to_set[settings_name] = data

        self._add_other_settings(vars_to_set)

        return vars_to_set

        # """
        # Django settings for researchers_registry_service_be_project project.
        #
        # Generated by 'django-admin startproject' using Django 3.1.4.
        #
        # For more information on this file, see
        # https://docs.djangoproject.com/en/3.1/topics/settings/
        #
        # For the full list of settings and their values, see
        # https://docs.djangoproject.com/en/3.1/ref/settings/
        # """
        # import os
        # from datetime import timedelta
        # from pathlib import Path
        #
        # #  Directory to this file
        # from django.core.management.commands.runserver import Command as runserver
        # from django_koldar_utils.django.Orm import Orm
        #
        # SETTING_DIR = Path(__file__).resolve()
        # # Build paths inside the project like this: BASE_DIR / 'subdir'.
        # BASE_DIR = Path(__file__).resolve().parent.parent
        #
        # # ###################################################################################
        # # django-environ setup
        # # ###################################################################################
        # # see https://django-environ.readthedocs.io/en/latest/#settings-py
        # import environ
        # env = environ.Env(
        #     # set casting, default value
        #     DEBUG=(bool, False)
        # )
        # # reading .env file
        # environ.Env.read_env()
        # ####################################################################################
        # # Django settings
        # ####################################################################################
        #
        # # Quick-start development settings - unsuitable for production
        # # See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
        #
        # # SECURITY WARNING: keep the secret key used in production secret!
        # SECRET_KEY = 'o0jv=_qtdg$nd1#8wt22#%c4n$-(v%+%*8x4(e#p*zm6ow10zm'
        #
        # # SECURITY WARNING: don't run with debug turned on in production!
        # DEBUG = True
        #
        # # ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
        # ALLOWED_HOSTS = ["*"]
        #
        # CORS_ALLOW_HEADERS = ['*']
        # CORS_ORIGIN_ALLOW_ALL = True
        # CORS_ALLOW_ALL_ORIGINS = True
        #
        # # PORT
        # # see https://stackoverflow.com/a/48277389/1887602
        # runserver.default_port = 8001
        #
        # # alter the table convention
        # Orm.set_table_naming_convention("standard")
        #
        # # Application definition
        #
        # INSTALLED_APPS = [
        #     # you need to add if you want Authorization header to be included in the request of the wsgi server
        #     'corsheaders',
        #     # standard
        #     'django.contrib.admin',
        #     'django.contrib.auth',
        #     'django.contrib.contenttypes',
        #     'django.contrib.sessions',
        #     'django.contrib.messages',
        #     'django.contrib.staticfiles',
        #     # cbim apps all need this
        #     'django_cbim_commons',
        #     # cbim services using authentication need this
        #     'django_cbim_general_service',
        #     # graphql
        #     'graphene_django',
        #     'django_filters',
        #     'researchers_registry_service_be',
        #     # make sure the django_app_graphql is the last app you add!
        #     'django_app_graphql',
        # ]
        #
        # MIDDLEWARE = [
        #     'corsheaders.middleware.CorsMiddleware',
        #     'django.middleware.common.CommonMiddleware',
        #     'django.middleware.security.SecurityMiddleware',
        #     'django.contrib.sessions.middleware.SessionMiddleware',
        #     'django.middleware.csrf.CsrfViewMiddleware',
        #     'django.contrib.auth.middleware.AuthenticationMiddleware',
        #     'django.contrib.messages.middleware.MessageMiddleware',
        #     #'django.middleware.clickjacking.XFrameOptionsMiddleware',
        # ]
        #
        # ROOT_URLCONF = 'researchers_registry_service_be_project.urls'
        #
        # TEMPLATES = [
        #     {
        #         'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #         'DIRS': [],
        #         'APP_DIRS': True,
        #         'OPTIONS': {
        #             'context_processors': [
        #                 'django.template.context_processors.debug',
        #                 'django.template.context_processors.request',
        #                 'django.contrib.auth.context_processors.auth',
        #                 'django.contrib.messages.context_processors.messages',
        #             ],
        #         },
        #     },
        # ]
        #
        # WSGI_APPLICATION = 'researchers_registry_service_be_project.wsgi.application'
        #
        #
        # # Database
        # # https://docs.djangoproject.com/en/3.1/ref/settings/#databases
        #
        # DATABASES = {
        #     'default': {
        #         'ENGINE': 'django.db.backends.mysql',
        #         'HOST': "auth.c0zcaytggc0x.eu-south-1.rds.amazonaws.com",
        #         'PORT': 3306,
        #         'NAME': "researchers-registry-service",
        #         'USER': "user-researcher-registry",
        #         'PASSWORD': "n5AYS*f!jVu&vGS*teHSOfBv666IM0hoI",
        #     },
        # }
        #
        #
        # # Password validation
        # # https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
        #
        # AUTH_PASSWORD_VALIDATORS = [
        #     {
        #         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        #     },
        #     {
        #         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        #     },
        #     {
        #         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        #     },
        #     {
        #         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        #     },
        # ]
        #
        # AUTHENTICATION_BACKENDS = [
        #     "django_cbim_general_service.backend.GeneralServiceAuthenticationBackend",
        # ]
        #
        #
        # # Internationalization
        # # https://docs.djangoproject.com/en/3.1/topics/i18n/
        #
        # LANGUAGE_CODE = 'en-us'
        #
        # TIME_ZONE = 'UTC'
        #
        # USE_I18N = True
        #
        # USE_L10N = True
        #
        # USE_TZ = True
        #
        #
        # # Static files (CSS, JavaScript, Images)
        # # https://docs.djangoproject.com/en/3.1/howto/static-files/
        #
        # STATIC_URL = '/static/'
        #
        # # ##############################################################################
        # # ADDED
        # # ##############################################################################
        #
        # # CORS
        #
        # # see https://github.com/adamchainz/django-cors-headers
        # # CORS_ALLOWED_ORIGINS = []
        # # for x in ALLOWED_HOSTS:
        # #     CORS_ALLOWED_ORIGINS.append(f"http://{x}")
        # #     CORS_ALLOWED_ORIGINS.append(f"https://{x}")
        # # CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:3000")
        # # CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:8000")
        # # CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:8001")
        #
        # # logging
        #
        # LOGGING = {
        #     'version': 1,
        #     'disable_existing_loggers': False,
        #     'handlers': {
        #         'console': {
        #             'class': 'logging.StreamHandler',
        #         },
        #     },
        #     'root': {
        #         'handlers': ['console'],
        #         'level': 'DEBUG',
        #     },
        # }
        #
        # # CACHE system.
        # # Used to sav user,roles,permissions
        #
        # CACHES = {
        #     'default': {
        #         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        #         'LOCATION': 'default',
        #     },
        #     'users': {
        #         'BACKEND': 'django_cbim_general_service.cache.UserCache',
        #         'LOCATION': 'users',
        #     }
        # }
        #
        # # django-app-graphqls
        #
        # GRAPHENE = {
        #     "SCHEMA": "django_app_graphql.graphene.schema.SCHEMA",
        #     'SCHEMA_OUTPUT': 'graphqls-schema.json',
        #     'SCHEMA_INDENT': 2,
        #     'MIDDLEWARE': [
        #         "graphql_jwt.middleware.JSONWebTokenMiddleware",
        #         "django_app_graphql.middleware.GraphQLStackTraceInErrorMiddleware",
        #     ],
        # }
        #
        # GRAPHENE_DJANGO_EXTRAS = {
        #     'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
        #     'DEFAULT_PAGE_SIZE': 20,
        #     'MAX_PAGE_SIZE': 50,
        #     'CACHE_ACTIVE': True,
        #     'CACHE_TIMEOUT': 300  # seconds
        # }
        #
        # # see https://django-graphql-jwt.domake.io/en/latest/refresh_token.html
        # GRAPHQL_JWT = {
        #     # This configures graphqls-jwt to add "token" input at each request to be authenticated
        #     'JWT_ALLOW_ARGUMENT': True,
        #     'JWT_ARGUMENT_NAME': "token",
        #     'JWT_VERIFY_EXPIRATION': True,
        #     'JWT_EXPIRATION_DELTA': timedelta(days=1),
        #     'JWT_ALGORITHM': "HS256",
        #     'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
        #     'JWT_AUTH_HEADER_PREFIX': "Bearer",
        #     # VERY IMPORTANT TO MAKE PERMISSION FETCHER AUTHENTICATION BACKEND WORK!
        #     'JWT_DECODE_HANDLER': 'django_cbim_general_service.backend.jwt_decoder_handler',
        #     'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'django_cbim_general_service.backend.jwt_payload_get_username',
        #     'JWT_GET_USER_BY_NATURAL_KEY_HANDLER': 'django_cbim_general_service.backend.user_by_natural_key_handler',
        #     "JWT_SECRET_KEY": "#I0MI5Y$y0^y7@nssN#r@F#7lamW1&1cfmT1^cD94aI&x8JucO",
        #     "JWT_PAYLOAD_HANDLER": "django_cbim_general_service.backend.jwt_payload_handler",
        # }
        #
        # ACCESS_TOKEN_SECRET_KEY = "sK00uj3O#6VcbK!HlxmHuWS#G9JQZaL@BVcl7Zf@b0JU09"
        # """
        # Token key used to encode the access token
        # """
        #
        # DJANGO_APP_GRAPHQL = {
        #     "BACKEND_TYPE": "graphene",
        #     "EXPOSE_GRAPHIQL": True,
        #     "GRAPHQL_SERVER_URL": "",
        #     "ENABLE_GRAPHQL_FEDERATION": True,
        #     "SAVE_GRAPHQL_SCHEMA": os.path.join("output", "schema.graphql"),
        #     "ADD_DUMMY_QUERIES_IF_ABSENT": True,
        #     "ADD_DUMMY_MUTATIONS_IF_ABSENT": True,
        # }


class StandardSettingsGenerator(AbstractSettingsGenerator):
    """
    Noop implementation of AbstractSettingsGenerator
    """

    def _configure_authentication_backends(self) -> List[str]:
        return [
            "django.contrib.auth.ModelBackend"
        ]

    def _get_apps_to_configure(self) -> Iterable[Tuple[str, str]]:
        return []

    def _configure_app(self, settings_name: str, app_name: str, original_data: any) -> any:
        pass

    def _configure_installed_apps(self, original: List[str]) -> List[str]:
        return original

    def _configure_middlewares(self, original: List[str]) -> List[str]:
        return original