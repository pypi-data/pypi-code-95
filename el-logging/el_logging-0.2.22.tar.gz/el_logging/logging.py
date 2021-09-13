# -*- coding: utf-8 -*-

import os
import sys
import json
import errno
import datetime
import traceback

import yaml
from loguru import logger
from dotenv import load_dotenv


class Rotator:
    def __init__(self, *, size: int, at: datetime.time):
        _now = datetime.datetime.now()
        self._size_limit = size
        self._time_limit = _now.replace(hour=at.hour, minute=at.minute, second=at.second)

        if self._time_limit <= _now:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=1)

    def should_rotate(self, message, file):
        file.seek(0, 2)
        if self._size_limit < (file.tell() + len(message)):
            return True

        if self._time_limit.timestamp() < message.record["time"].timestamp():
            self._time_limit += datetime.timedelta(days=1)
            return True
        return False


## Filter for adding short level name:
def _add_lvlname(record: dict):
    record['lvlname'] = record['level'].name
    if record['level'].name == 'SUCCESS':
        record['lvlname'] = 'OK'
    elif record['level'].name == 'WARNING':
        record['lvlname'] = 'WARN'
    elif record['level'].name == 'CRITICAL':
        record['lvlname'] = 'CRIT'
    return record


## Printing message based on log level to stdout or stderr:
def _std_sink(message):
    if message.record["level"].no < 40:
        sys.stdout.write(message)
    else:
        sys.stderr.write(message)


## Custom json formatter:
def _custom_json_formatter(record: dict):
    _error = None
    if record['exception']:
        _error = {}
        _error_type, _error_value, _error_traceback = record['exception']
        _error['type'] = _error_type.__name__
        _error['value'] = str(_error_value)
        _error['traceback'] = ''.join(traceback.format_tb(_error_traceback))

    _extra = None
    if record['extra'] and (0 < len(record['extra'])):
        _extra = record['extra']

    _json_format = {
        'timestamp': record['time'].strftime('%Y-%m-%dT%H:%M:%S%z'),
        'level': record['level'].name,
        'level_no': record['level'].no,
        'file': record['file'].name,
        'line': record['line'],
        'name': record['name'],
        'process': {
            'name': record['process'].name,
            'id': record['process'].id
        },
        'thread_name': {
            'name': record['thread'].name,
            'id': record['thread'].id
        },
        'message': record['message'],
        'extra': _extra,
        'error': _error,
        'elapsed': str(record['elapsed']),
    }

    record['custom_json'] = json.dumps(_json_format)
    return '{custom_json}\n'



def _init():
    ## Loading environment variables from .env file, if it's exits:
    _env_filename = '.env'
    _current_dir = os.getcwd()
    _env_file_path = os.path.join(_current_dir, _env_filename)
    if os.path.isfile(_env_file_path):
        load_dotenv(dotenv_path=_env_file_path, override=True)

    ## Options for loggers
    _configs_dict = {
        'use_color': True,
        'use_icon': False,
        'use_backtrace': True,
        'std_format_str': '[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{lvlname:<5}</level> | <w>{file}</w>:<w>{line}</w>]: <level>{message}</level>',
        'use_log_file': False,
        'file_format_str': '[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {lvlname:<5} | {file}:{line}]: {message}',
        'rotate_when':
        {
            'at_hour': 0,
            'at_minute': 0,
            'at_second': 0
        },
        'rotate_file_size': 10000000,
        'backup_file_count': 50,
        'file_encoding': 'utf8',
        'all_log_filename': '{app_name}.std.all.log',
        'err_log_filename': '{app_name}.std.err.log',
        'use_log_json': False,
        'use_custom_json': False,
        'json_all_log_filename': '{app_name}.json.all.log',
        'json_err_log_filename': '{app_name}.json.err.log'
    }

    ## Loading configs from file, if it's exits:
    _yaml_configs_file_path = os.path.join(_current_dir, 'configs', 'logger.yaml')
    if os.path.isfile(_yaml_configs_file_path):
        try:
            with open(_yaml_configs_file_path, 'r') as _yaml_configs_file:
                _configs_dict = yaml.safe_load(_yaml_configs_file)['logger']
        except Exception:
            logger.exception(f"Failed to load '{_yaml_configs_file_path}' configs file.")
            exit(2)

    _configs_dict['is_debug'] = False
    _configs_dict['level'] = 'INFO'
    _configs_dict['use_diagnose'] = False

    ## Checking environment for DEBUG option:
    _ENV = str(os.getenv('ENV')).strip().lower()
    _DEBUG = str(os.getenv('DEBUG')).strip().lower()
    if (_DEBUG == 'true') or ((_ENV == 'development') and ((_DEBUG == 'none') or (_DEBUG == ''))):
        _configs_dict['is_debug'] = True
        os.environ['DEBUG'] = 'true'

    if _configs_dict['is_debug']:
        _configs_dict['level'] = 'DEBUG'
        _configs_dict['use_diagnose'] = True

    if _configs_dict['use_icon']:
        _configs_dict['std_format_str'] = _configs_dict['std_format_str'].replace('lvlname:<5', 'level.icon:<4')

    # if _USE_COLOR:
    #     ## Checking terminal could support xterm colors:
    #     _TERM = str(os.getenv('TERM'))
    #     if (_TERM != 'xterm') and (_TERM != 'xterm-16color') and (_TERM != 'xterm-88color') and (_TERM != 'xterm-256color'):
    #         _USE_COLOR = False

    ## Initializing std stream log handler:
    logger.remove()
    logger.add(_std_sink,
                level=_configs_dict['level'],
                format=_configs_dict['std_format_str'],
                colorize=_configs_dict['use_color'],
                filter=_add_lvlname,
                backtrace=_configs_dict['use_backtrace'],
                diagnose=_configs_dict['use_diagnose'])

    ## Checking log file handlers enabled or not:
    if _configs_dict['use_log_file'] or _configs_dict['use_log_json']:
        ## Setting 'APP_NAME':
        _APP_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        if os.getenv('APP_NAME') and os.getenv('APP_NAME').strip():
            _APP_NAME = os.getenv('APP_NAME').strip().replace(' ', '_').lower()
        else:
            os.environ['APP_NAME'] = _APP_NAME
            logger.debug(f"Not found 'APP_NAME' environment variable, changed app name to '{_APP_NAME}'.")

        ## Checking and creating 'logs_dir':
        if os.getenv('LOGS_DIR') and os.getenv('LOGS_DIR').strip():
            _LOGS_DIR = os.getenv('LOGS_DIR').strip()
        else:
            if ('logs_dir' in _configs_dict) and _configs_dict['logs_dir'].strip():
                _LOGS_DIR = _configs_dict['logs_dir'].strip()
            else:
                _LOGS_DIR = os.path.join(_current_dir, 'logs')
                logger.debug(f"Not found 'LOGS_DIR' environment variable, changed to '{_LOGS_DIR}' local directory.")
            os.environ['LOGS_DIR'] = _LOGS_DIR

        if not os.path.isdir(_LOGS_DIR):
            logger.warning(f"'{_LOGS_DIR}' directory doesn't exist!")
            try:
                os.makedirs(_LOGS_DIR)
            except Exception as err:
                if err.errno == errno.EEXIST:
                    logger.info(f"'{_LOGS_DIR}' directory already exists.")
                else:
                    logger.exception(f"Failed to create '{_LOGS_DIR}' directory.")
                    exit(2)
            logger.success(f"Successfully created '{_LOGS_DIR}' directory!")

        ## Setting up log file handlers:
        _rotate_when = datetime.time(_configs_dict['rotate_when']['at_hour'], _configs_dict['rotate_when']['at_minute'], _configs_dict['rotate_when']['at_second'])
        if _configs_dict['use_log_file']:
            ## Initializing log file handler:
            _out_rotator = Rotator(size=_configs_dict['rotate_file_size'], at=_rotate_when)
            _log_file_path = os.path.join(_LOGS_DIR, _configs_dict['all_log_filename'].format(app_name=_APP_NAME))
            logger.add(_log_file_path,
                        level=_configs_dict['level'],
                        format=_configs_dict['file_format_str'],
                        rotation=_out_rotator.should_rotate,
                        retention=_configs_dict['backup_file_count'],
                        encoding=_configs_dict['file_encoding'],
                        enqueue=True,
                        backtrace=_configs_dict['use_backtrace'],
                        diagnose=_configs_dict['use_diagnose'])

            ## Initializing error log file handler:
            _err_rotator = Rotator(size=_configs_dict['rotate_file_size'], at=_rotate_when)
            _log_file_path = os.path.join(_LOGS_DIR, _configs_dict['err_log_filename'].format(app_name=_APP_NAME))
            logger.add(_log_file_path,
                        level='WARNING',
                        format=_configs_dict['file_format_str'],
                        rotation=_err_rotator.should_rotate,
                        retention=_configs_dict['backup_file_count'],
                        encoding=_configs_dict['file_encoding'],
                        enqueue=True,
                        backtrace=_configs_dict['use_backtrace'],
                        diagnose=_configs_dict['use_diagnose'])

        if _configs_dict['use_log_json']:
            _json_out_rotator = Rotator(size=_configs_dict['rotate_file_size'], at=_rotate_when)
            _json_err_rotator = Rotator(size=_configs_dict['rotate_file_size'], at=_rotate_when)

            if _configs_dict['use_custom_json']:
                ## Initializing json log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _configs_dict['json_all_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level=_configs_dict['level'],
                            format=_custom_json_formatter,
                            rotation=_json_out_rotator.should_rotate,
                            retention=_configs_dict['backup_file_count'],
                            encoding=_configs_dict['file_encoding'],
                            enqueue=True,
                            backtrace=_configs_dict['use_backtrace'],
                            diagnose=_configs_dict['use_diagnose'])

                ## Initializing json error log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _configs_dict['json_err_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level='WARNING',
                            format=_custom_json_formatter,
                            rotation=_json_err_rotator.should_rotate,
                            retention=_configs_dict['backup_file_count'],
                            encoding=_configs_dict['file_encoding'],
                            enqueue=True,
                            backtrace=_configs_dict['use_backtrace'],
                            diagnose=_configs_dict['use_diagnose'])
            else:
                ## Initializing json log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _configs_dict['json_all_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level=_configs_dict['level'],
                            format='',
                            serialize=True,
                            rotation=_json_out_rotator.should_rotate,
                            retention=_configs_dict['backup_file_count'],
                            encoding=_configs_dict['file_encoding'],
                            enqueue=True,
                            backtrace=_configs_dict['use_backtrace'],
                            diagnose=_configs_dict['use_diagnose'])

                ## Initializing json error log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _configs_dict['json_err_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level='WARNING',
                            format='',
                            serialize=True,
                            rotation=_json_err_rotator.should_rotate,
                            retention=_configs_dict['backup_file_count'],
                            encoding=_configs_dict['file_encoding'],
                            enqueue=True,
                            backtrace=_configs_dict['use_backtrace'],
                            diagnose=_configs_dict['use_diagnose'])

_init()
