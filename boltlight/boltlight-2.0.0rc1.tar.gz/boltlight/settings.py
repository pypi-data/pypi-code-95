# Copyright (C) 2018 inbitcoin s.r.l.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Settings module for boltlight.

WARNING: only Python's core module imports here, to avoid breaking build system
         and import loops.
"""

from os import path
from pathlib import Path

# Empty variables are set at runtime
# Some variables contain default values, could be overwritten

IMPLEMENTATION = ''

DATA = path.join(str(Path.home()), '.boltlight')
CONFIG = path.join(DATA, 'config')

PKG_NAME = 'boltlight'
PIP_NAME = 'boltlight'

HOST = '0.0.0.0'
PORT = '1708'
LISTEN_ADDR = ''
INSECURE_CONNECTION = 0
SERVER_KEY = './certs/server.key'
SERVER_CRT = './certs/server.crt'
IMPLEMENTATION_SECRETS = False
IMPL_SEC_TYPE = ''

# Macaroons settings
RUNTIME_BAKER = None
DISABLE_MACAROONS = 0
MACAROONS_DIR = './macaroons'
MAC_ADMIN = 'admin.macaroon'
MAC_READONLY = 'readonly.macaroon'
MAC_INVOICES = 'invoices.macaroon'

# Security settings
MAC_ROOT_KEY = None
SALT_LEN = 32
ACCESS_TOKEN = b'boltlight'
PASSWORD_LEN = 12
SCRYPT_PARAMS = {
    'cost_factor': 2**15,
    'block_size_factor': 8,
    'parallelization_factor': 1,
    'key_len': 32
}

# boltlight-secure settings
COLLECTING_INPUT = True
DONE = False
NEW_DB = False
SEARCHING_ENTROPY = True
FIRST_WORK_TIME = None
IDLE_COUNTER = 1
IDLE_MESSAGES = {
    1: {
        'msg': 'please keep generating entropy',
        'delay': 5
    },
    2: {
        'msg': 'more entropy, please',
        'delay': 15
    },
    3: {
        'msg': '...good things come to those who wait...',
        'delay': 30
    }
}

# DB settings
DB_DIR = './db'
DB_NAME = 'boltlight.db'
DB_PATH = ''
ALEMBIC_CFG = path.join(path.dirname(__file__), 'migrations/alembic.ini')

# Server settings
GRPC_WORKERS = 10
GRPC_GRACE_TIME = 40
UNLOCKER_STOP = False
RUNTIME_STOP = False
RUNTIME_SERVER = None
THREADS = []

# blink settings
RPCSERVER = 'localhost:1708'
TLSCERT = './certs/server.crt'
MACAROON = path.join(MACAROONS_DIR, MAC_ADMIN)
INSECURE = 0
NO_MACAROON = 0
CLI_RPCSERVER = None
CLI_TLSCERT = None
CLI_MACAROON = None
CLI_INSECURE = None
CLI_NO_MACAROON = None
CLI_TIMEOUT = 10
CLI_BASE_GRPC_CODE = 64

ENFORCE = True

TEST_HASH = '43497fd7f826957108f4a30fd9cec3aeba79972084e90ead01ea330900000000'
MAIN_HASH = '6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000'

# RPC-based implementations settings
RPC_URL = ''
RPC_TRIES = 5
RPC_SLEEP = .5
RPC_CONN_TIMEOUT = 3.1

# c-lightning specific settings
CL_RPC = 'lightning-rpc'

# eclair specific settings
ECL_HOST = 'localhost'
ECL_PORT = 8080
ECL_PASS = ''
ECL_CONFIRMATIONS = 6

# electrum specific settings
ELE_HOST = 'localhost'
ELE_PORT = 7777
ELE_USER = 'user'
ELE_RELEASED_ADDRESSES = []

# lnd specific settings
LND_HOST = 'localhost'
LND_PORT = 10009
LND_CERT = 'tls.cert'
LND_ADDR = ''
LND_CREDS_SSL = ''
LND_CREDS_FULL = ''
LND_MAC = ''

# Common settings
IMPL_MIN_TIMEOUT = 2
IMPL_MAX_TIMEOUT = 180
RESPONSE_RESERVED_TIME = 0.3
THREAD_TIMEOUT = 3
CLOSE_TIMEOUT_NODE = 15
MAX_INVOICES = 200
INVOICES_TIMES = 3
EXPIRY_TIME = 420
DUST_LIMIT_SAT = 546

# Logging settings
LOGS_DIR = './logs'
LOGS_BOLTLIGHT = 'boltlight.log'
LOGS_MIGRATIONS = 'migrations.log'
LOG_TIMEFMT = '%Y-%m-%d %H:%M:%S %z'
LOG_TIMEFMT_SIMPLE = '%d %b %H:%M:%S'
LOGS_LEVEL = 'INFO'
LOG_LEVEL_FILE = 'DEBUG'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
            "[%(asctime)s] %(levelname).3s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': LOG_TIMEFMT
        },
        'simple': {
            'format': '%(asctime)s %(levelname).3s: %(message)s',
            'datefmt': LOG_TIMEFMT_SIMPLE
        },
    },
    'handlers': {
        'console': {
            'level': LOGS_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    }
}
LOGGING_FILE = {
    'file': {
        'level': LOG_LEVEL_FILE,
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': path.join(LOGS_DIR, LOGS_BOLTLIGHT),
        'maxBytes': 1048576,
        'backupCount': 7,
        'formatter': 'verbose'
    }
}

# Macaroons settings
BOLTLIGHT_PERMS = {
    '/boltlight.Boltlight/GetInfo': {
        'entity': 'info',
        'action': 'read'
    },
    '/boltlight.Boltlight/Lock': {
        'entity': 'lock',
        'action': 'write'
    },
}
LIGHTNING_PERMS = {
    '/boltlight.Lightning/BalanceOffChain': {
        'entity': 'balance',
        'action': 'read'
    },
    '/boltlight.Lightning/CheckInvoice': {
        'entity': 'invoice',
        'action': 'read'
    },
    '/boltlight.Lightning/CloseChannel': {
        'entity': 'channel',
        'action': 'write'
    },
    '/boltlight.Lightning/CreateInvoice': {
        'entity': 'invoice',
        'action': 'write'
    },
    '/boltlight.Lightning/DecodeInvoice': {
        'entity': 'invoice',
        'action': 'read'
    },
    '/boltlight.Lightning/GetNodeInfo': {
        'entity': 'info',
        'action': 'read'
    },
    '/boltlight.Lightning/ListChannels': {
        'entity': 'channel',
        'action': 'read'
    },
    '/boltlight.Lightning/ListInvoices': {
        'entity': 'invoice',
        'action': 'read'
    },
    '/boltlight.Lightning/ListPayments': {
        'entity': 'payment',
        'action': 'read'
    },
    '/boltlight.Lightning/ListPeers': {
        'entity': 'peer',
        'action': 'read'
    },
    '/boltlight.Lightning/ListTransactions': {
        'entity': 'transaction',
        'action': 'read'
    },
    '/boltlight.Lightning/NewAddress': {
        'entity': 'address',
        'action': 'write'
    },
    '/boltlight.Lightning/OpenChannel': {
        'entity': 'channel',
        'action': 'write'
    },
    '/boltlight.Lightning/PayInvoice': {
        'entity': 'payment',
        'action': 'write'
    },
    '/boltlight.Lightning/PayOnChain': {
        'entity': 'transaction',
        'action': 'write'
    },
    '/boltlight.Lightning/UnlockNode': {
        'entity': 'unlock',
        'action': 'write'
    },
    '/boltlight.Lightning/BalanceOnChain': {
        'entity': 'balance',
        'action': 'read'
    },
}
ALL_PERMS = {**BOLTLIGHT_PERMS, **LIGHTNING_PERMS}
READ_PERMS = [
    {
        'entity': 'balance',
        'action': 'read'
    },
    {
        'entity': 'channel',
        'action': 'read'
    },
    {
        'entity': 'info',
        'action': 'read'
    },
    {
        'entity': 'invoice',
        'action': 'read'
    },
    {
        'entity': 'payment',
        'action': 'read'
    },
    {
        'entity': 'peer',
        'action': 'read'
    },
    {
        'entity': 'transaction',
        'action': 'read'
    },
]
INVOICE_PERMS = [
    {
        'entity': 'channel',
        'action': 'read'
    },
    {
        'entity': 'info',
        'action': 'read'
    },
    {
        'entity': 'invoice',
        'action': 'read'
    },
    {
        'entity': 'invoice',
        'action': 'write'
    },
    {
        'entity': 'peer',
        'action': 'read'
    },
]
