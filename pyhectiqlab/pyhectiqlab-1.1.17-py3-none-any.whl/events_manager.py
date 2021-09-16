import threading

import pyhectiqlab
import pyhectiqlab.ops as ops
from pyhectiqlab.auth import AuthProvider

from packaging import version
import logging
logger = logging.getLogger('pyhectiqlab')

class EventsManager():
    def __init__(self, mock=False):
        self.auth_provider = AuthProvider()
        self.mock = mock
        events = []

    def is_logged(self):
        return self.auth_provider.is_logged()

    def compare_python_version(self, on_failed = None):
        """Compare the current python version and the
        required python version.
        """
        def threading_method():
            res = ops.fetch_minimum_python_version()
            required_version = res['version']
            if version.parse(pyhectiqlab.__version__) < version.parse(required_version):
                logger.error(f'Your pyhectiqlab version ({pyhectiqlab.__version__}) is obsolete (required: {required_version}).')
                logger.error('Update with:')
                logger.error('`pip install --upgrade pyhectiqlab`')
                logger.error('Some features may break until you upgrade.')
                if on_failed is not None:
                    on_failed()
            return res

        x = threading.Thread(target=threading_method)
        x.start()
        return 

    def add_event(self, task_name, args, auth=True, async_method=True, repeat_if_401=True):
        if self.mock :
            return
        method = getattr(ops, task_name)

        def threading_method(*args, **kwargs):
            res = method(*args, **kwargs)
            return res

        kwargs = {}
        if auth:
            kwargs = {"token": self.auth_provider.secret_api_key}

        if async_method:
            x = threading.Thread(target=threading_method, args=args, kwargs=kwargs)
            x.start()
            return
        else:
            return method(*args, **kwargs)

