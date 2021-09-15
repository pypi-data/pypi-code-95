import sys
import os

import asyncio
import time
import traceback
import inspect
from abc import abstractmethod as _abstractmethod
from asgiref.sync import sync_to_async as blocking_function

from raya.raya import create_raya_app as _create_raya_app
from raya.exceptions import RayaApplicationException
from raya.logger import LogLevel, create_logger

# from raya.fake_controllers import XXX

log_app_base = create_logger('RayaApp.AppBase')
log_runtime = create_logger('RayaApp.AppRuntime')
log_runtime_plain = create_logger('RayaApp.AppRuntime', plain_cout=True)

from .exceptions import *

class RayaApplicationBase:

    # Constructor and destructor

    def __init__(self, app_id, dev_mode=False, domain_id=0, log_to_file=False, log_folder=''):
        self.__app_id = app_id
        self.__dev_mode = dev_mode
        self.__domain_id = domain_id
        self.__log_to_file = log_to_file
        self.__log_folder = log_folder
        self.__app = _create_raya_app(self.__app_id, self.__dev_mode, self.__domain_id, self.__log_to_file, self.__log_folder)
        # If not exceptions, creation was ok.
        self.__ready = True
        self.__task_listeners = None
        self.__task_fast_listeners = None
        self.__task_loop = None
        self.__enabled_controllers = []
        self.__abort = False
        self.__correctly_finished = False
        self.__log_app = create_logger(f'RayaApp.{self.__app_id}', plain_cout=True)
        self.__test_basic_coroutine('setup')
        self.__test_basic_coroutine('loop')
        self.__test_basic_coroutine('finish')

    def __del__(self):
        pass

    # Public methods

    def log(self, *args):
        if len(args) == 1:
            self.__log_app(LogLevel.INFO, str(args[0]))
        elif len(args) == 2 and isinstance(args[0], int):
            self.__log_app(args[0], str(args[1]))
        else:
            raise RayaApplicationException(f'log() wrong arguments. Candidates: log(<message>) or log(LogLevel.<level>, <message>)')

    def create_logger(self, name):
        this_log = create_logger(f'RayaApp.{self.__app_id}.{name}', plain_cout=False)
        def create_logger_wrapper(*args):
            if len(args) == 1 and isinstance(args[0], str):
                this_log(LogLevel.INFO, args[0])
            elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], str):
                this_log(args[0], args[1])
            else:
                raise RayaApplicationException(f'log() wrong arguments. Candidates: log(<message>) or log(LogLevel.<level>, <message>)')
        return create_logger_wrapper

    def enable_controller(self, ctlr_name_):
        controller = self.__app._enable_controller(ctlr_name_)
        self.__enabled_controllers.append(controller)
        return controller

    async def finish_app(self):
        if self.__task_listeners is not None: 
            self.__task_listeners.cancel()
        if self.__task_fast_listeners is not None: 
            self.__task_fast_listeners.cancel()
        if self.__task_loop is not None: 
            self.__task_loop.cancel()
        self.__ready = False
        self.__correctly_finished = True
    
    async def sleep(self, sleep_time):
        await asyncio.sleep(sleep_time)
        pass

    # Protected methods

    def _is_ready(self):
        return self.__ready
    
    def _run(self):
        if sys.platform == 'win32':
            try:
                asyncio.run(self.__async_run())
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
        else:
            asyncio.run(self.__async_run())
    
    # Private methods

    def __test_basic_coroutine(self, func_name):
        func = getattr(self, func_name, None)
        if callable(func):
            if(inspect.iscoroutinefunction(func)):
                if len(inspect.signature(func).parameters)!=0:
                    raise RayaApplicationException(f'Method "{func_name}" must have only "self" parameter: "async def {func_name}(self)" in class "RayaApplication"')
            else:
                raise RayaApplicationException(f'Method "{func_name}" must be a coroutine: "async def {func_name}(self)" in class "RayaApplication"')
        else:
            raise RayaApplicationException(f'Method "{func_name}" not found: "async def {func_name}(self)" in class "RayaApplication"')

    def __check_dds_connection(self):
        if not self.__app._check_bridge_connection():
            log_app_base(LogLevel.FATAL, 'Connection with DDS-Robot Bridge was lost.')
            self.__abort = True
            self.__cancel_tasks()

    def __print_exception(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tb_list = traceback.extract_tb(exc_tb)
        tb_list = list(filter(lambda tb: __file__ not in tb.filename, tb_list))
        tb_list = list(filter(lambda tb: '__main__.py' not in tb.filename, tb_list))
        tb_list_format = traceback.format_list(tb_list)
        for tb in tb_list_format:
            log_runtime_plain(LogLevel.INFO, tb)
        self.__abort = True
        if type(e) is RayaControllerException:
            log_runtime_plain(LogLevel.INFO, str(exc_obj))
        else:
            log_runtime_plain(LogLevel.INFO, f'{exc_type.__name__}: {exc_obj}')
        return

    async def __call_setup(self):
        try:
            await self.setup()
            await self.sleep(0.5)
        except Exception as e:
            log_runtime(LogLevel.ERROR, 'ERROR in setup() method:')
            self.__print_exception(e)
            return

    async def __call_loop(self):
        while True:
            try:
                await self.loop()
            except Exception as e:
                self.__cancel_tasks()
                log_runtime(LogLevel.ERROR, 'ERROR in loop() method:')
                self.__print_exception(e)
                return
            self.__check_dds_connection()
            await asyncio.sleep(0)
    
    async def __call_finish(self):
        try:
            await self.finish()
        except Exception as e:
            log_runtime(LogLevel.ERROR, 'ERROR in finish() method:')
            self.__print_exception(e)
            return

    async def __check_listeners(self):
        while True:
            for controller in self.__enabled_controllers:
                try:
                    controller._check_listeners()
                except Exception as e:
                    self.__cancel_tasks()
                    log_runtime(LogLevel.ERROR, 'ERROR in listener:')
                    self.__print_exception(e)
                    return
            await asyncio.sleep(0.1)

    async def __check_fast_listeners(self):
        while True:
            for controller in self.__enabled_controllers:
                try:
                    controller._check_fast_listeners()
                except Exception as e:
                    self.__cancel_tasks()
                    log_runtime(LogLevel.ERROR, 'ERROR in listener:')
                    self.__print_exception(e)
                    return
            await asyncio.sleep(0.001)

    def __cancel_tasks(self):
        if self.__task_listeners is not None: 
            self.__task_listeners.cancel()
        if self.__task_fast_listeners is not None: 
            self.__task_fast_listeners.cancel()
        if self.__task_loop is not None: 
            self.__task_loop.cancel()

    def __interrupt_signal_callback(self):
        self.__cancel_tasks()

    async def __async_run(self):
        if sys.platform != 'win32':
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(2, self.__interrupt_signal_callback) # Interrupt Signal
        # Setup
        await self.__call_setup()
        if self.__abort:
            return
        # Loop
        self.__task_listeners = asyncio.create_task(self.__check_listeners())
        self.__task_fast_listeners = asyncio.create_task(self.__check_fast_listeners())
        self.__task_loop = asyncio.create_task(self.__call_loop())
        try:
            await self.__task_listeners
            await self.__task_fast_listeners
            await self.__task_loop
        except KeyboardInterrupt:
            print('SSS')
        except asyncio.exceptions.CancelledError:
            self.__cancel_tasks()
        if self.__abort:
            return
        # Finish
        if self.__correctly_finished:
            await self.__call_finish()
