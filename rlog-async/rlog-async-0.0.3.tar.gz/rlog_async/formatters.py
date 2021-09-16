# coding: utf-8
import logging
import getpass
from socket import gethostname

from ._compat import json, text_type


class JSONFormatter(logging.Formatter):

    def format(self, record):
        try:
            data = record.__dict__.copy()
            data.update(
                username=getpass.getuser(),
                host=gethostname(),
                args=tuple(text_type(arg) for arg in record.args)
            )
            if 'exc_info' in data and data['exc_info']:
                data['exc_info'] = self.formatException(data['exc_info'])
            return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            return 'Formatter error: %s' % repr(e)
