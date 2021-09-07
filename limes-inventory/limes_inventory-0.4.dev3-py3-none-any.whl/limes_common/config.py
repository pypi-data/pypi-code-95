from pytz import timezone

_DEBUG = False

TIME_ZONE = timezone('Canada/Pacific')
ENCODING = 'utf-8'
if _DEBUG:
    HTTP_TIMEOUT = 10
else:
    HTTP_TIMEOUT = 5

CSRF_NAME = 'X-CSRFToken'

# ELAB_URL = 'https://us.elabjournal.com/'
ELAB_URL = 'https://elab.msl.ubc.ca/'
ELAB_API = '%sapi/v1/' % ELAB_URL

SERVER_API_VER = 'd1'
if _DEBUG:
    SERVER_BIND = '127.0.0.1:8001'
else:
    SERVER_BIND = 'sh-lims.microbiology.ubc.ca:8001'
SERVER_URL = 'http://%s/api/%s/' % (SERVER_BIND, SERVER_API_VER)
SERVER_DB_PATH = 'limes_server/db'

# PROVIDER_STATICS_PATH = 'limes_core/example_static_providers.json'
PROVIDER_STATICS_PATH = 'limes_core/static_providers.json'
PROVIDER_DEFAULT_TRANSACTION_TIMEOUT = 5
PROVIDER_DEFAULT_CONNECTION_TIMEOUT = 60

ELAB_CACHE = 'elab_cache.npy'