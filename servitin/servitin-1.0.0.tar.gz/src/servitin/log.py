import logging
import logging.config
import re
import time

from django.conf import settings


class Log:
    def __init__(self, logger, app_name):
        self.logger = logger
        self.app_name = app_name

    def info(self, msg, id=None, name=None):
        log(self.logger, 'info', self.app_name, msg, id_str=id, subsys_name=name)

    def critical(self, msg, tb=None, id=None, name=None):
        log(self.logger, 'critical', self.app_name, msg, id_str=id, traceback=tb, subsys_name=name)

    def error(self, msg, id=None, tb=None, name=None):
        log(self.logger, 'error', self.app_name, msg, id_str=id, traceback=tb, subsys_name=name)


# todo! logstash logger must go from "service.settings"
def configure_logging(services):
    """
    Initialize main and logstash loggers
    :param settings: Kirservice settings
    """

    # add servitin formatter
    settings.LOGGING['formatters'].update(settings.SERVITIN_LOGGING['formatters'])

    for s in services:
        app_log_settings = getattr(settings, f"SERVITIN_{s['app_name'].upper()}_LOGGING", None)

        if app_log_settings:
            for x in settings.LOGGING.items():
                if x[0] == 'formatters':
                    x[1].update(app_log_settings.get('formatters', {}))
                if x[0] == 'handlers':
                    x[1].update(app_log_settings.get('handlers', {}))
                if x[0] == 'loggers':
                    x[1].update(app_log_settings.get('loggers', {}))

        logging.config.dictConfig(settings.LOGGING)
        logging.Formatter.converter = time.gmtime

        # re init main django logger
        # logger = logging.getLogger('')
        # for handler in logger.handlers:
        #     handler.setFormatter(CustomFormatter(handler.formatter._fmt))

        # init service logger
        logger = logging.getLogger(f"servitin_{s['app_name']}_logger")

        # for handler in logger.handlers:
        #     handler.setFormatter(CustomFormatter(handler.formatter._fmt))

        # for l in settings.LOGGING.get('loggers').items():
        #     if 'is_logstash' in l[1] and l[1]['is_logstash']:
        #         logstash_logger = logging.getLogger(l[0])
        #         logstash_formatter = LogstashFormatterV1()
        #         for handler in logstash_logger.handlers:
        #             handler.setFormatter(logstash_formatter)

        s['logger'] = logger
        s['log'] = Log(logger, s["app_name"])


def log(logger, level, service_name, msg, subsys_name=None, id_str=None, traceback=None, additional=None):
    """
    Logs message with main and logstash loggers
    :param logger: Logger instance
    :param level: Logger level
    :param service_name: Service name. exmpl: Kirservice or Collector
    :param msg: Message string
    :param subsys_name: Subsys name. exmpl: SocketServer or Postgres
    :param id_str: Entry id string
    :param traceback: Formatted traceback info
    :param additional: Additional info
    """
    prefix = f'[{service_name}]' if not subsys_name else f'[{service_name}] [{subsys_name}]'
    prefix = prefix if not id_str else f'{prefix} [{id_str}]'
    msg_str = f'{prefix} {msg}' if not traceback else f'{prefix} {msg}\n{traceback}'
    getattr(logger, level)(msg_str)

    # message = {"msg": msg, "service_name": service_name, "subsys_name": subsys_name, "id_str": id_str,
    #            "traceback": traceback}
    # if additional:
    #     message.update(additional)

    # getattr(logstash, level)(message)


def format_name_tokens(s):
    out = s
    
    # list of matches
    matchlist = list(enumerate(re.finditer("(\[[a-zA-Z0-9-: ._&@]+\])\s+", s)))
    if len(matchlist):
        service_name = matchlist[0][1].group()[:-1]  # exmpl: [Ubuntu-1604-xenial-64-minimal] or [Collector]

        # string startswith system project_settings.SERVITIN_NAME e.g [Ubuntu-1604-xenial-64-minimal]
        if service_name == f'[{settings.SERVITIN_NAME}]':
            newsn = service_name.ljust(32)
            out = s.replace(service_name, newsn, 1)
        
        # other strings exmpl: [Collector] or [Pusher]
        else:
            name_tokens = matchlist[:2]
            if len(name_tokens) == 2:
                newsn = service_name.ljust(15)
                out = s.replace(service_name, newsn, 1)
                
                # subsys name. exmpl: [Postgres] or [SocketServer]
                subsysname = name_tokens[1][1].group()
                newsubsysname = subsysname.ljust(17)
                out = out.replace(subsysname, newsubsysname, 1)
    return out


class CustomFormatter(logging.Formatter):
    def format(self, record):
        res = super(CustomFormatter, self).format(record)
        return format_name_tokens(res)


class UTCFormatter(logging.Formatter):
    converter = time.gmtime
