from .version import VERSION
import six
_TRUE_VALUES = ['y', 'Y', 'yes',  'Yes',  'YES', 'true', 'True', 'TRUE', '1', True]


class LoggingConfiguration(object):
    LOGGER_NAME = "rook"
    FILE_NAME = "rookout/python-rook.log"
    LOG_TO_STDERR = False
    LOG_LEVEL = "INFO"
    PROPAGATE_LOGS = False
    LOG_TO_REMOTE = False
    DEBUG = False


class VersionConfiguration(object):
    VERSION = VERSION
    COMMIT = "CommitGoesHere"


class ProtobufConfiguration(object):
    NAMESPACE_SERIALIZER_DUMPING = r""


class ControllerAddress(object):
    HOST = 'wss://control.rookout.com'
    PORT = 443


class AgentComConfiguration(object):
    COMMAND_THREAD_NAME = "rookout_agent_com"
    MAX_MESSAGE_LENGTH = 1024 * 1024
    BACK_OFF = 0.2
    MAX_SLEEP = 60
    TIMEOUT = 3
    REQUEST_TIMEOUT_SECS = 30
    PING_TIMEOUT = 30
    PING_INTERVAL = 10
    RESET_BACKOFF_TIMEOUT = 3*60.0
    FLUSH_TIMEOUT = 3
    MAX_QUEUED_MESSAGES = 100


class OutputWsConfiguration(object):
    MAX_STATUS_UPDATES = 200
    MAX_LOG_ITEMS = 200
    MAX_AUG_MESSAGES = 100
    BUCKET_REFRESH_RATE = 10


class RateLimiter(object):
    MIN_RATE_LIMIT_VALUE_NS = 1000


class InstrumentationConfig(object):
    ENGINE = "auto"
    MIN_TIME_BETWEEN_HITS_MS = 100
    MAX_AUG_TIME_MS = 400


class ImportServiceConfig(object):
    USE_IMPORT_HOOK = True
    SYS_MODULES_QUERY_INTERVAL = 0.25
    THREAD_NAME = "rookout_import_service_thread"


class HttpServerServiceConfig(object):
    SERVICES_NAMES = ""


class GitConfig(object):
    GIT_COMMIT = None
    GIT_ORIGIN = None


class ShutdownConfig(object):
    IS_SHUTTING_DOWN = False


class DumpConfig(object):
    STRING_CACHE_USERMESSAGE = False


def update_config(new_config):
    try:
        for key, val in six.iteritems(new_config):
            if key == 'PYTHON_StringCache_UserMessage':
                DumpConfig.STRING_CACHE_USERMESSAGE = val in _TRUE_VALUES
                continue
    except:
        try:
            from rook.logger import logger
            logger.exception("Failed to update configuration: " + str(new_config))
        except:  # lgtm[py/catch-base-exception]
            pass
