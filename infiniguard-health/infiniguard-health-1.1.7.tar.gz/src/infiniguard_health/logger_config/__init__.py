import logging.handlers
import os
import re
import sys
import warnings
from datetime import datetime
from copy import deepcopy

import requests
import urllib3

LOG_DIR = '/var/log/iba'
LOG_FILE_NAME = 'infiniguard-health.log'
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)
TEST_EXECUTABLES = ('nosetests', '_jb_unittest_runner', '_jb_nosetest_runner', 'pytest')
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGFILE_DATE_SUFFIX_FORMAT = '%Y-%m-%d.%H_%M_%S'
LOG_MAX_SIZE_BYTES = 50 * 1024 * 1024   # 50M
LOG_BACKUP_COUNT = 100  # Total of 5G


# Disable verbose urllib3 warnings suggesting certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()
# Disable 'deprecated' warnings from paramiko < 2.5
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

logging.getLogger('paramiko').setLevel(logging.WARNING)
logging.getLogger('fabric').setLevel(logging.WARNING)
logging.getLogger('invoke').setLevel(logging.WARNING)
logging.getLogger('infi.storagemodel').setLevel(logging.WARNING)
logging.getLogger('infi.multipathtools').setLevel(logging.WARNING)


class TimestampedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, **kwargs):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, **kwargs)

    def _get_first_log_record_date(self):
        with open(self.baseFilename) as logfile:
            first_log_record = logfile.readline()

        match = re.match(r'\[(.*?)\]', first_log_record)
        if match:
            first_log_record_date_str = match.groups()[0]
            first_log_record_date = datetime.strptime(first_log_record_date_str, LOG_DATE_FORMAT)
            return datetime.strftime(first_log_record_date, LOGFILE_DATE_SUFFIX_FORMAT)
        return datetime.strftime(datetime.now(), LOGFILE_DATE_SUFFIX_FORMAT)

    @staticmethod
    def _get_index_suffix(log_name):
        match = re.search(r'\.(\d+)$', log_name)
        if match:
            return int(match.groups()[0])

    def _get_largest_index_suffix(self, log_list):
        logs_suffixes = [self._get_index_suffix(log)
                         for log
                         in log_list
                         if self._get_index_suffix(log)]
        if not logs_suffixes:
            return 1
        return max(logs_suffixes)

    def rotation_filename(self, default_name):
        if not os.path.exists(self.baseFilename):
            return self.baseFilename

        # Generate log_name with timestamp.
        log_dir, log_name = os.path.split(self.baseFilename)
        first_log_record_date = self._get_first_log_record_date()
        log_name = f'{log_name}.{first_log_record_date}'

        # if a log_name with the same timestamp exists, adds a numeric suffix. (log_name.timestamp.index)
        if os.path.exists(os.path.join(log_dir, log_name)):
            logs_with_same_timestamp = [filename
                                        for filename
                                        in os.listdir(log_dir)
                                        if first_log_record_date in filename]

            log_name = f'{log_name}.{self._get_largest_index_suffix(logs_with_same_timestamp) + 1}'

        # return full path
        return os.path.join(log_dir, log_name)

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backupCount > 0:
            for log in self.get_logs_to_delete():
                os.remove(log)

            rotate_to_filename = self.rotation_filename(self.baseFilename)
            self.rotate(self.baseFilename, rotate_to_filename)

        if not self.delay:
            self.stream = self._open()

    def get_logs_to_delete(self):
        """Sort all log filenames by timestamp and then bv index_suffix.
           Returns the oldest logs that exceed self.backupCount"""
        log_dir, log_name = os.path.split(self.baseFilename)
        return sorted([os.path.join(log_dir, filename)
                       for filename
                       in os.listdir(log_dir)
                       if log_name in filename and filename != log_name], reverse=True)[self.backupCount:]


logging.handlers.TimestampedRotatingFileHandler = TimestampedRotatingFileHandler


def get_executable_name():
    return os.path.basename(sys.argv[0])


def is_test():
    exec_name = get_executable_name()
    return any(executable in exec_name for executable in TEST_EXECUTABLES)


_is_test = is_test()
prod_handlers = ['file']
test_handlers = ['console']
loggers_handlers = test_handlers if _is_test else prod_handlers

if os.environ.get('IGUARD_VERBOSE'):
    loggers_handlers += ['console']

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': LOG_DATE_FORMAT,
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.TimestampedRotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'maxBytes': LOG_MAX_SIZE_BYTES, 
            'backupCount': LOG_BACKUP_COUNT
        },
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'infiniguard_health': {
            'handlers': loggers_handlers,
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': loggers_handlers,
            'level': 'DEBUG',
            'propagate': False,
        },
        'paramiko': {
            'handlers': loggers_handlers,
            'level': 'WARNING',
            'propagate': False,
        },
    }
}


if _is_test:
    COPY_OF_LOGGING_CONFIG = deepcopy(LOGGING_CONFIG)
    del LOGGING_CONFIG['handlers']['file']
