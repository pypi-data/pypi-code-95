import asyncio
import traceback
import importlib
import json
import datetime
import logging
import uuid
from asgiref.sync import sync_to_async
from async_timeout import timeout as atimeout
from functools import wraps

from django.conf import settings
from django.core.mail import mail_admins
from channels.generic.websocket import AsyncWebsocketConsumer

from . import _version__ as VERSION
from .utils import serializable, get_client_ip
from .exceptions import *


logger = logging.getLogger(__name__)

if settings.DCE_DEBUG_LOGGER:
    dce_logger = logging.getLogger('dce')
else:
    dce_logger = None

ENDPOINTS_MODULES = {}
USER_TASKS_BY_CHANNEL_NAME = {}


class DCEConsumer(AsyncWebsocketConsumer):

    def get_client_ip(self):
        return get_client_ip(self.scope)

    async def connect(self):
        await self.accept()

        user = self.scope["user"]

        if dce_logger:
            dce_logger.info(f'{user.username} {self.get_client_ip()} connected')

        r = Response(None, {'version': VERSION}, msg_type='service')
        await self.send(text_data=r)

    async def disconnect(self, close_code):
        await self.disconnect_modules(close_code)  # call disconnect() coroutines on every loaded module
        self.finish_tasks()  # clear user channel tasks and cancel pending
        if dce_logger:
            dce_logger.info(f'{self.scope["user"].username} {self.get_client_ip()} disconnected')

    async def receive(self, text_data):
        try:
            request = self.get_request(text_data)
            if request.cancel:
                self.cancel_request(request)
            else:
                await self.dispatch_request(request)
        except Exception as e:
            response = Response(None, None, error=e.__repr__(), error_data=getattr(e, 'data', None), msg_type='service')
            await self.send(text_data=response)
            if dce_logger:
                dce_logger.exception(f"DCEConsumer.receive error: ")
            logger.exception(f"[dce] DCEConsumer.receive error: ")
            await self.send_email_admins(f"[dce] receive error: : {e.__repr__()}\ninput data:\n{text_data}\n\n{traceback.format_exc()}")

    def resolve_path(self, data):

        def load_disconnect_coros(module):
            coros = []
            for name, coro in module.__dict__.items():
                if getattr(coro, '_dce_disconnect', None):
                    coros.append(coro)
            return coros

        path = None
        try:
            # get path and endpoint name
            path = data.get('endpoint', None)
            if not path:
                raise Exception('Endpoint path not specified')
            path_list = path.split('.')
            module_path, endpoint_name = path_list[:-1], path_list[-1]

            # get or import module
            module_path = '.'.join(module_path) + '.dce'
            module_dict = ENDPOINTS_MODULES.get(module_path, None)
            module = module_dict.get('module', None) if module_dict else None
            if not module:
                now = datetime.datetime.now()
                module = importlib.import_module(module_path)
                ENDPOINTS_MODULES[module_path] = {'module': module, 'disconnect_coros': load_disconnect_coros(module)}
                elapsed = (datetime.datetime.now() - now).total_seconds()
                if dce_logger:
                    dce_logger.info(f'module loaded: {module_path}, elapsed: {elapsed}')

            return getattr(module, endpoint_name)  # decorated endpoint

        except Exception as e:
            raise ResolvePathError(f'Resolve path "{path}" error {e.__repr__()}')

    def get_request(self, text_data):
        data = json.loads(text_data)  # get received data
        endpoint = self.resolve_path(data)  # get decorated endpoint
        return Request(data, endpoint, self)  # make request

    def cancel_request(self, request):
        """ cancel request task and clearing user tasks from this task """
        for c, tasks in USER_TASKS_BY_CHANNEL_NAME.items():
            if c == self.channel_name:
                task = [t for t in tasks if t['cmd_id'] == request.cmd_id]
                task = task[0] if len(task) else None

                if task and not task['task'].done():
                    try:
                        task['task'].cancel()
                    except Exception:
                        pass
        # clearing user tasks from this task
        self.remove_task(self.channel_name, cmd_id=request.cmd_id)

    async def dispatch_request(self, request):
        """ create and dispatch user task from request """
        async def task(task_id):
            start = datetime.datetime.now()
            error = None
            tb = None
            response = None
            elapsed = None
            rid = f"[{request.cmd_id}]".ljust(6)
            rin = f"<-".ljust(2)
            rout = f"->".ljust(2)

            try:
                if request.logger:
                    request.logger.info(f"{rid} {rin} {request.log} : {request.data}")

                if request.timeout:
                    async with atimeout(request.timeout):
                        # check permissions
                        if request.permissions:
                            for permission in request.permissions:
                                await permission(request).check_perm()
                        response = await request.endpoint
                else:
                    # check permissions
                    if request.permissions:
                        for permission in request.permissions:
                            await permission(request).check_perm()
                    response = await request.endpoint

            except asyncio.CancelledError as e:
                error = e
            except asyncio.TimeoutError as e:
                error = e
                tb = traceback.format_exc()
                elapsed = (datetime.datetime.now() - start).total_seconds()
                response = Response(request, None, error=f"TimeoutError")
                logger.error(f"[dce] -> [{request.cmd_id}] {request.log} : {elapsed} : {error.__repr__()}")
            except AccessForbidden as e:
                error = e
                elapsed = (datetime.datetime.now() - start).total_seconds()
                if e.log_exc:
                    tb = traceback.format_exc()
                    logger.exception(f"[dce] -> [{request.cmd_id}] {request.log} : {elapsed} : {error.__repr__()}")
                response = Response(request, None, error='AccessForbidden')
            except Exception as e:
                error = e
                tb = traceback.format_exc()
                elapsed = (datetime.datetime.now() - start).total_seconds()
                response = Response(request, None, error=e.__repr__(), error_data=getattr(e, 'data', None))
                logger.exception(f"[dce] -> [{request.cmd_id}] {request.log} : {elapsed} : {error.__repr__()}")
            finally:
                if not elapsed:
                    elapsed = (datetime.datetime.now() - start).total_seconds()

                # send response
                if response:
                    await request.consumer.send(text_data=response)

                # clearing user tasks from this task
                self.remove_task(self.channel_name, task_id=task_id)

                # log to endpoint logger
                if request.logger:
                    if error:
                        if error.__class__.__name__ == 'CancelledError':
                            request.logger.warning(f"{rid} {rout} {request.log} : {elapsed} : {error.__repr__()}")
                        else:
                            request.logger.error(f"{rid} {rout} {request.log} : {elapsed} : {error.__repr__()}")
                    else:
                        request.logger.info(f"{rid} {rout} {request.log} : {elapsed}")

                # send email error message to admins
                if error and tb:
                    await self.send_email_admins(f"{request.log} : {elapsed} : {error.__repr__()}\ninput data:\n{request.data}\n\n{tb}")

                # call user defined coroutine
                await self.finish_request(request, response, elapsed, error, tb)

        loop = asyncio.get_event_loop()
        task_id = str(uuid.uuid4())
        task = loop.create_task(task(task_id))
        self.add_task(self.channel_name, request.path, task, task_id, request.cmd_id)

    async def finish_request(self, request, response, elapsed, error, tb):
        """ user defined coroutine, called after task finished """
        pass

    def add_task(self, channel_name, endpoint, task, task_id, cmd_id=None):
        """ add task to user tasks """
        if USER_TASKS_BY_CHANNEL_NAME.get(channel_name, None):
            USER_TASKS_BY_CHANNEL_NAME[channel_name].append({'name': endpoint, 'task': task, 'task_id': task_id, 'cmd_id': cmd_id})
        else:
            USER_TASKS_BY_CHANNEL_NAME[channel_name] = [{'name': endpoint, 'task': task, 'task_id': task_id, 'cmd_id': cmd_id}]

    def remove_task(self, channel_name, task_id=None, cmd_id=None):
        """ clearing user tasks from received task """
        if task_id:
            for c, tasks in USER_TASKS_BY_CHANNEL_NAME.items():
                if c == channel_name:
                    USER_TASKS_BY_CHANNEL_NAME[c] = [t for t in tasks if t['task_id'] != task_id]
        if cmd_id:
            for c, tasks in USER_TASKS_BY_CHANNEL_NAME.items():
                if c == channel_name:
                    USER_TASKS_BY_CHANNEL_NAME[c] = [t for t in tasks if t['cmd_id'] != cmd_id]

    def finish_tasks(self):
        """ clear user tasks and cancel pending """
        user = self.scope["user"]
        pending_tasks = []
        user_have_tasks = False
        for c, tasks in USER_TASKS_BY_CHANNEL_NAME.items():
            if c == self.channel_name:
                user_have_tasks = True
                for t in tasks:
                    if not t['task'].done():
                        pending_tasks.append(t)

        if len(pending_tasks):
            if dce_logger:
                t_names = ', '.join(t['name'] for t in pending_tasks)
                dce_logger.info(f'{user.username} {self.get_client_ip()} cancel pending requests: {t_names}')

            for t in pending_tasks:
                try:
                    t['task'].cancel()
                except Exception:
                    pass

        if user_have_tasks:
            USER_TASKS_BY_CHANNEL_NAME.pop(self.channel_name, None)

    async def disconnect_modules(self, close_code):
        # todo: реализовать таймаут и логгер из декоратора

        for module_path, v in ENDPOINTS_MODULES.items():
            for coro in v['disconnect_coros']:
                c = coro(self, close_code)  # get real coro
                coro_path = f"{module_path.replace('.dce', '')}.{c.__name__}"
                await c  # call real coro
                if dce_logger:
                    dce_logger.info(f'{self.scope["user"].username} {self.get_client_ip()} disconnect in {coro_path}')

    async def send_email_admins(self, error):
        if settings.DCE_MAIL_ADMINS:
            def send_email_admins():
                mail_admins('dce error', error, fail_silently=True)
            await sync_to_async(send_email_admins, thread_sensitive=False)()

    async def broadcast(self, event):
        """
        Broadcast sending type, need for self.send_to_group()
        """
        message = event['message']
        await self.send(text_data=message)

    async def send_to_group(self, group, msg):
        """
        Wrapper for consumer.channel_layer.group_send() with broadcast type sending
        """
        await self.channel_layer.group_send(group, {
            'type': 'broadcast',
            'message': msg
        })

    async def send_channel(self, event):
        """
        Send type to single channel by channel_name
        """
        message = event['message']
        await self.send(text_data=message)

    async def send_to_channel(self, channel_name, msg):
        """
        Wrapper for self.send_channel need for send message to specified channel by channel_name
        """
        await self.channel_layer.send(channel_name, {
            "type": "send.channel",
            "message": msg
        })


class Endpoint:
    """
    Decorator class for endpoint() coroutine
    """

    def __init__(self, coro, permissions=None, timeout=settings.DCE_ENDPOINT_TIMEOUT, logger=None):
        self.coro = coro
        coro._dce_endpoint = {'permissions': permissions, 'timeout': timeout, 'logger': logger}
        wraps(coro)(self)

    def __call__(self, request):
        return self.coro(request)


def endpoint(coro=None, permissions=None, timeout=settings.DCE_ENDPOINT_TIMEOUT, logger=None):
    """
    Wrapper for Endpoint decorator, need to get decorator arguments
    :param coro: endpoint() coroutine
    :param permissions: List of permissions classes
    :param timeout: Timeout in seconds
    :param logger: Custom logger for this endpoint
    :return: wrapped endpoint() coroutine
    """
    if coro:
        return Endpoint(coro)
    else:
        def wrapper(coro):
            return Endpoint(coro, permissions=permissions, timeout=timeout, logger=logger)
        return wrapper


class Disconnect:
    """
    Decorator class for disconnect() coroutine
    """

    def __init__(self, coro, timeout=60, logger=None):
        self.coro = coro
        coro._dce_disconnect = {'timeout': timeout, 'logger': logger}
        wraps(coro)(self)

    def __call__(self, consumer, close_code):
        return self.coro(consumer, close_code)


def disconnect(coro=None, timeout=None, logger=None):
    """
    Wrapper for Disconnect decorator, need to get decorator arguments
    :param coro: disconnect() coroutine
    :param timeout: Timeout in seconds
    :param logger: Custom logger for this coroutine
    :return: wrapped disconnect() coroutine
    """
    if coro:
        return Disconnect(coro)
    else:
        def wrapper(coro):
            return Disconnect(coro, timeout=timeout, logger=logger)
        return wrapper


class Request:
    def __init__(self, data, endpoint, consumer):
        self._raw_data = data
        self._endpoint = endpoint
        self._options = getattr(endpoint, '_dce_endpoint')
        self.consumer = consumer
        self.path = self._raw_data['endpoint']
        self.endpoint = None
        self.cmd_id = None
        self.data = None
        self.cancel = False
        self.timeout = None
        self.client_ip = consumer.get_client_ip()
        self.scope = consumer.scope
        self.user = consumer.scope["user"]
        self.username = self.user.username if not self.user.is_anonymous else 'Anonymous'
        self.logger = None
        self.log = None
        self.set_data_and_options()
        self.set_endpoint(endpoint)

    def set_data_and_options(self):
        # set data and cmd_id from received raw_data
        for name, value in self._raw_data.items():
            if not name == 'endpoint':
                self.__setattr__(name, value)

        # set options defined in @endpoint decorator
        for name, value in self._options.items():
            if name in ['permissions', 'timeout']:
                self.__setattr__(name, value)

        # set logger and log prefix
        self.logger = self._options['logger'] if self._options['logger'] else dce_logger
        self.log = f'{self.username} {self.client_ip} {self.path}'

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint(self)


class _Response:
    def __init__(self, request, data, consumers=None, error=None, error_data=None, msg_type='user'):
        self.request = request
        self.data = data if not data == None else None
        self.consumers = consumers
        self.error_data = error_data
        self.error = error
        self.msg_type = msg_type

        if request:
            if self.error:
                if getattr(self.request, 'cmd_id', None):
                    self.message_dict = {
                        'data': None,
                        'msg_type': self.msg_type,
                        'status': 'error',
                        'cmd_id': self.request.cmd_id,
                        'consumers': [],
                        'error': self.error,
                        'error_data': self.error_data
                    }
                else:
                    self.message_dict = {
                        'data': None,
                        'msg_type': self.msg_type,
                        'status': 'error',
                        'cmd_id': None,
                        'consumers': self.consumers,
                        'error': self.error,
                        'error_data': self.error_data
                    }
            else:
                if getattr(self.request, 'cmd_id', None):
                    self.message_dict = {
                        'data': self.data,
                        'msg_type': self.msg_type,
                        'status': 'success',
                        'cmd_id': self.request.cmd_id,
                        'consumers': [],
                        'error': None,
                        'error_data': None
                    }
                else:
                    self.message_dict = {
                        'data': self.data,
                        'msg_type': self.msg_type,
                        'status': 'success',
                        'cmd_id': None,
                        'consumers': self.consumers,
                        'error': None,
                        'error_data': None
                    }
        else:
            if self.error:
                self.message_dict = {
                    'data': None,
                    'msg_type': self.msg_type,
                    'status': 'error',
                    'cmd_id': None,
                    'consumers': self.consumers,
                    'error': self.error,
                    'error_data': self.error_data
                }
            else:
                self.message_dict = {
                    'data': self.data,
                    'msg_type': self.msg_type,
                    'status': 'success',
                    'cmd_id': None,
                    'consumers': self.consumers,
                    'error': None,
                    'error_data': None
                }

        self.message = json.dumps(serializable(self.message_dict))


def Response(*args, **kwargs):
    return _Response(*args, **kwargs).message
