import os

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

# Rabbitmq
RABBIT_HOST = 'localhost'
RABBIT_USER = 'guest'
RABBIT_PASS = 'guest'
RABBIT_HEARTBEAT = 30  # Server default is 60 seconds
RABBIT_QUEUE = 'cacahuate_process'
RABBIT_NOTIFY_EXCHANGE = 'charpe_notify'
RABBIT_CONSUMER_TAG = 'cacahuate_consumer_1'

# Default logging config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] %(message)s - %(name)s:%(lineno)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        # 'charpe': {
        #     'class': 'charpe.CharpeHandler',
        #     'level': 'ERROR',
        #     'host': RABBIT_HOST,
        #     'medium': 'email',
        #     'exchange': RABBIT_NOTIFY_EXCHANGE,
        #     'service_name': 'cacahuate',
        #     'params': {
        #         'recipient': 'support@example.com',
        #         'subject': '[cacahuate] Server Error',
        #         'template': 'server-error',
        #     },
        # },
    },
    'loggers': {
        'cacahuate': {
            'handlers': ['console'],
            'level': 'INFO',
            'filters': [],
        },
    },
}

# Where to store xml files
XML_PATH = os.path.join(base_dir, 'xml')

# Custom path to templates
TEMPLATE_PATH = None

# Mongodb
MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'cacahuate')
MONGO_URI = 'mongodb://{credentials}{host}:{port}/{database}'.format(
    credentials='{username}:{password}@'.format(
        username=MONGO_USERNAME,
        password=MONGO_PASSWORD,
    ) if MONGO_USERNAME or MONGO_PASSWORD else '',
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=MONGO_DBNAME,
)

POINTER_COLLECTION = 'pointer'
EXECUTION_COLLECTION = 'execution'

# Defaults for pagination
PAGINATION_LIMIT = 20
PAGINATION_OFFSET = 0

# Time stuff
TIMEZONE = 'UTC'

# For ephimeral objects, like executions and pointers
REDIS_URL = 'redis://localhost'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# LDAP settings
AUTH_LDAP_SERVER_URI = os.getenv(
    'AUTH_LDAP_SERVER_URI',
    'ldap://ldap.example.com',
)
AUTH_LDAP_USE_SSL = os.getenv(
    'AUTH_LDAP_USE_SSL',
    True,
)
AUTH_LDAP_DOMAIN = os.getenv(
    'AUTH_LDAP_DOMAIN',
    'TAREAS',
)
AUTH_LDAP_SEARCH_BASE = os.getenv(
    'AUTH_LDAP_SEARCH_BASE',
    '',
)
AUTH_LDAP_SEARCH_FILTER = os.getenv(
    'AUTH_LDAP_SEARCH_FILTER',
    '',
)
AUTH_LDAP_USER_ATTR_MAP = {
    'email': 'mail',
    'fullname': 'displayName',
}

# Use SSE
SSE_ENABLED = os.getenv('CACAHUATE_SSE_ENABLED', 'False') == 'True'

# The different providers that can be used for log in
ENABLED_LOGIN_PROVIDERS = [
    'ldap',
]

# Providers enabled for locating people in the system
ENABLED_HIERARCHY_PROVIDERS = [
    'anyone',
    'backref',
]

# custom login providers
CUSTOM_LOGIN_PROVIDERS = {
    # 'name': 'importable.path',
}

# custom hierarchy providers
CUSTOM_HIERARCHY_PROVIDERS = {
    # 'name': 'importable.path',
}

# will be sent to charpe for rendering of emails
GUI_URL = 'http://localhost:8080'

# The 'impersonate' login module, when enabled, uses this to login
IMPERSONATE_PASSWORD = 'set me to passlib.hash.pbkdf2_sha256.hash("something")'

# Invalid filters for query string
INVALID_FILTERS = (
    'limit',
    'offset',
)

PROCESS_ENV = {
    # 'CUSTOM_VAR': 'its value',
}
