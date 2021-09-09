# Boltlight - a LN node wrapper
#
# Copyright (C) 2021 boltlight contributors
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
#
# For a full list of contributors, please see the AUTHORS.md file.
"""The Python implementation of the gRPC boltlight server."""

import sys

from concurrent.futures import TimeoutError as TimeoutFutError, \
    ThreadPoolExecutor
from configparser import Error as ConfigError
from contextlib import suppress
from functools import wraps
from importlib import import_module
from logging import getLogger
from os import environ
from signal import signal, SIGTERM
from threading import active_count, Thread, Lock
from time import sleep, strftime, time

from grpc import server, ServerInterceptor, ssl_server_credentials, \
    StatusCode, unary_unary_rpc_method_handler
from sqlalchemy.exc import SQLAlchemyError

from . import __version__, boltlight_pb2 as pb, \
    boltlight_pb2_grpc as pb_grpc, settings as sett
from .errors import Err
from .macaroons import check_macaroons, get_baker
from .utils.db import detect_impl_secret, get_mac_params_from_db, init_db, \
    is_db_ok, session_scope
from .utils.exceptions import InterruptException
from .utils.misc import die, handle_importerror, handle_keyboardinterrupt, \
    handle_sigterm, init_common
from .utils.network import check_connection, check_req_params, FakeContext
from .utils.security import check_password, Crypter, get_secret, ScryptParams
from .utils.boltlight import RuntimeTerminate

signal(SIGTERM, handle_sigterm)

LOGGER = getLogger(__name__)

environ["GRPC_SSL_CIPHER_SUITES"] = (
    "HIGH+ECDSA:"
    "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384")


def _handle_logs(func):
    """Wrap API methods to log received request and returned response."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Log information about RPC, before and after its execution."""
        start_time = time()
        peer = user_agent = 'unknown'
        req = args[0]
        ctx = args[1]
        if len(args) == 3:
            req = args[1]
            ctx = args[2]
        with suppress(ValueError):
            peer = ctx.peer().split(':', 1)[1]
        for data in ctx.invocation_metadata():
            if data.key == 'user-agent':
                user_agent = data.value
                break
        LOGGER.info('< %-24s %s %s', req.DESCRIPTOR.name, peer, user_agent)
        res = func(*args, **kwargs)
        res_name = res.DESCRIPTOR.name
        stop_time = time()
        call_time = round(stop_time - start_time, 3)
        LOGGER.info('> %-24s %s %2.3fs', res_name, peer, call_time)
        LOGGER.debug('Full response: %s', str(res).replace('\n', ' '))
        return res

    return wrapper


class UnlockerServicer(pb_grpc.UnlockerServicer):
    """Implementation of the Unlocker service defined by protobuf.

    This service does not require macaroons authentication.
    """

    # pylint: disable=too-few-public-methods

    @_handle_logs
    def Unlock(self, request, context):
        """Unlock boltlight.

        If password is correct, unlock boltlight database and stop the
        UnlockerServicer. Otherwise reject request.
        """
        check_req_params(context, request, 'password')
        mod = import_module(f'..light_{sett.IMPLEMENTATION}', __name__)
        plain_secret = None
        with session_scope(context) as session:
            check_password(context, session, request.password)
            if not sett.DISABLE_MACAROONS:
                mac_params = ScryptParams('')
                mac_params.deserialize(get_mac_params_from_db(session))
                sett.MAC_ROOT_KEY = Crypter.gen_derived_key(
                    request.password, mac_params)
                baker = get_baker(sett.MAC_ROOT_KEY, put_ops=True)
                sett.RUNTIME_BAKER = baker
            if sett.IMPLEMENTATION_SECRETS:
                plain_secret = get_secret(context,
                                          session,
                                          request.password,
                                          sett.IMPLEMENTATION,
                                          sett.IMPL_SEC_TYPE,
                                          active_only=True)
        # Calls the implementation specific update method
        mod.update_settings(plain_secret)
        res = pb.UnlockResponse()
        if request.unlock_node:
            with ThreadPoolExecutor(max_workers=1) as executor:
                try:
                    future = executor.submit(mod.unlock_node, FakeContext(),
                                             request.password)
                    future.result(timeout=1)  # max 1 second to unlock node
                except TimeoutFutError:
                    executor.shutdown(wait=False)
                except RuntimeError as err:
                    # don't fail boltlight unlock if node unlock fails
                    LOGGER.info(err)
                else:
                    res.node_unlocked = True
        sett.UNLOCKER_STOP = True
        return res


class BoltlightServicer(pb_grpc.BoltlightServicer):
    """Implementation of the Boltlight service defined by protobuf.

    This service requires macaroons authentication (if not deactivated) and
    is active only after a successful unlock.
    """

    # pylint: disable=too-few-public-methods

    @_handle_logs
    def GetInfo(self, _req, _ctx):
        """Return info about boltlight and the wrapped implementation."""
        mod = import_module(f'..light_{sett.IMPLEMENTATION}', __name__)
        return pb.GetInfoResponse(version=__version__,
                                  node_implementation=sett.IMPLEMENTATION,
                                  node_version=mod.get_node_version())

    @_handle_logs
    def Lock(self, request, context):
        """
        Lock boltlight by deleting secrets from memory and stopping the
        runtime server (LightningServicer + BoltlightServicer).
        """
        sett.MAC_ROOT_KEY = None
        sett.RUNTIME_BAKER = None
        sett.ECL_PASS = None
        sett.LND_MAC = None
        sett.RUNTIME_STOP = True
        return pb.LockResponse()


class LightningServicer():  # pylint: disable=too-few-public-methods
    """Implementation of the Lightning service defined by protobuf.

    This service requires macaroons authentication (if not deactivated) and
    is active only after a successful unlock.

    Allow dynamic dispatching by not deriving from the protobuf generated
    class.
    """
    def __getattr__(self, name):
        """Dispatch the gRPC request dynamically."""
        @_handle_logs
        def dispatcher(req, ctx):
            """Call the requested API method for the configured implementation.

            If an AttributeError error is raised, terminate the RPC with
            a unimplemented_method error.
            """
            # Importing module for specific implementation
            module = import_module(f'..light_{sett.IMPLEMENTATION}', __name__)
            # Searching client requested function in module
            try:
                func = getattr(module, name)
            except AttributeError:
                Err().unimplemented_method(ctx, name)
            # Return requested function if implemented
            return func(req, ctx)

        return dispatcher


def _runtime_terminator(method):
    """Return an RpcMethodHandler if request is not accepted."""
    return unary_unary_rpc_method_handler(method)


def _service_locked_terminator():
    """Return an RpcMethodHandler if service is locked."""
    def terminate(_ignored_request, ctx):
        """Terminates gRPC call."""
        LOGGER.error('- Not an Unlocker operation')
        ctx.abort(StatusCode.UNAVAILABLE, 'Service is locked')

    return unary_unary_rpc_method_handler(terminate)


def _check_request(handler):
    """Check if request is authorized.

    A request is authorized if it's defined in settings.ALL_PERMS and macaroons
    are valid (unless they are disabled).
    Return None if authorization is granted, error handler method otherwise.
    """
    if handler.method not in sett.ALL_PERMS:
        if handler.method == '/boltlight.Unlocker/Unlock':
            LOGGER.error('- Unlock is not a runtime operation')
            return RuntimeTerminate.already_unlocked
        LOGGER.error('- Not a runtime operation')
        return RuntimeTerminate.not_runtime
    if sett.DISABLE_MACAROONS:
        return None
    return check_macaroons(handler.invocation_metadata, handler.method)


class RuntimeInterceptor(ServerInterceptor):
    """gRPC interceptor for the runtime (Boltlight + Lightning) services."""

    # pylint: disable=too-few-public-methods, no-init

    def intercept_service(self, continuation, handler_call_details):
        """Intercept the RPC to decide if request is authorized."""
        error_method = _check_request(handler_call_details)
        if error_method:
            return _runtime_terminator(error_method)
        return continuation(handler_call_details)


class UnlockerInterceptor(ServerInterceptor):
    """gRPC interceptor for the Unlocker service."""

    # pylint: disable=too-few-public-methods

    def __init__(self):  # pylint: disable=super-init-not-called
        self._terminator = _service_locked_terminator()

    def intercept_service(self, continuation, handler_call_details):
        """Intercept the RPC to eventually inform that service is locked."""
        if handler_call_details.method == \
                '/boltlight.Unlocker/Unlock':
            return continuation(handler_call_details)
        return self._terminator


def _create_server(interceptors):
    """Create a gRPC server attaching given interceptors to server.

    Depending on boltlight configuration, server can be created in secure or
    insecure mode (no TLS nor macaroons).
    """
    if sett.INSECURE_CONNECTION:
        grpc_server = server(ThreadPoolExecutor(max_workers=sett.GRPC_WORKERS),
                             interceptors=interceptors)
        grpc_server.add_insecure_port(sett.LISTEN_ADDR)
    else:
        grpc_server = server(ThreadPoolExecutor(max_workers=sett.GRPC_WORKERS),
                             interceptors=interceptors)
        with open(sett.SERVER_KEY, 'rb') as key:
            private_key = key.read()
        with open(sett.SERVER_CRT, 'rb') as cert:
            certificate_chain = cert.read()
        server_credentials = ssl_server_credentials(((
            private_key,
            certificate_chain,
        ), ))
        grpc_server.add_secure_port(sett.LISTEN_ADDR, server_credentials)
    return grpc_server


def _serve_unlocker():
    """Start the unlocker gRPC server.

    The server must be composed by the Unlocker service.
    """
    grpc_server = _create_server([UnlockerInterceptor()])
    pb_grpc.add_UnlockerServicer_to_server(UnlockerServicer(), grpc_server)
    grpc_server.start()
    _log_listening('Unlocker service')
    LOGGER.info('Waiting for password to unlock Lightning service...')
    _unlocker_wait(grpc_server)


def _serve_runtime():
    """Start the runtime gRPC server.

    The server must be composed by the Boltlight and Lightning services.
    """
    grpc_server = _create_server([RuntimeInterceptor()])
    pb_grpc.add_LightningServicer_to_server(LightningServicer(), grpc_server)
    pb_grpc.add_BoltlightServicer_to_server(BoltlightServicer(), grpc_server)
    sett.RUNTIME_SERVER = grpc_server
    grpc_server.start()
    _log_listening('Lightning service')
    _runtime_wait(grpc_server)


def _log_listening(servicer_name):
    """Log at which host and port the service is listening."""
    if sett.INSECURE_CONNECTION:
        LOGGER.info('%s listening on %s (insecure connection)', servicer_name,
                    sett.LISTEN_ADDR)
    else:
        LOGGER.info('%s listening on %s (secure connection)', servicer_name,
                    sett.LISTEN_ADDR)


def _interrupt_threads():
    """Try to gracefully stop all pending threads of the runtime server."""
    close_event = None
    if sett.RUNTIME_SERVER:
        close_event = sett.RUNTIME_SERVER.stop(sett.GRPC_GRACE_TIME)
    if close_event:
        while not close_event.is_set() or sett.THREADS:
            LOGGER.info('Waiting for %s threads to complete...',
                        active_count())
            sleep(3)
    LOGGER.info('All threads shutdown correctly')


def _unlocker_wait(grpc_server):
    """Wait a signal to stop the unlocker server."""
    while not sett.UNLOCKER_STOP:
        sleep(1)
    grpc_server.stop(0)
    sett.UNLOCKER_STOP = False


def _runtime_wait(grpc_server):
    """Wait a signal to stop the runtime server."""
    while not sett.RUNTIME_STOP:
        sleep(1)
    grpc_server.stop(0)
    sett.RUNTIME_STOP = False


def _log_intro():
    """Print a booting boilerplate to ease run distinction."""
    LOGGER.info(' ' * 72)
    LOGGER.info(' ' * 72)
    LOGGER.info(' ' * 72)
    LOGGER.info('*' * 72)
    LOGGER.info(' ' * 72)
    LOGGER.info('Boltlight')
    LOGGER.info('version %s', __version__)
    LOGGER.info(' ' * 72)
    LOGGER.info('booting up at %s', strftime(sett.LOG_TIMEFMT))
    LOGGER.info(' ' * 72)
    LOGGER.info('*' * 72)


def _log_outro():
    """Print a quitting boilerplate to ease run distinction."""
    LOGGER.info('stopping at %s', strftime(sett.LOG_TIMEFMT))
    LOGGER.info('*' * 37)


def _start_services(lock):
    """Handle the unlocker and the runtime servers start."""
    _serve_unlocker()
    con_thread = Thread(target=check_connection, args=(lock, ))
    con_thread.daemon = True
    con_thread.start()
    _serve_runtime()


@handle_keyboardinterrupt
def _start_boltlight():
    """Start boltlight.

    Check if a module for the requested implementation exists and import it.
    Initialize boltlight and start the Unlocker gRPC service.
    """
    init_common("Start boltlight's gRPC server", runtime=True)
    _log_intro()
    init_db()
    with session_scope(FakeContext()) as session:
        if not is_db_ok(session):
            raise RuntimeError(
                'Your database configuration is incomplete or old. '
                'Update it by running boltlight-secure (and deleting db)')
        sett.IMPLEMENTATION_SECRETS = detect_impl_secret(session)
    lock = Lock()
    while True:
        _start_services(lock)


def start():
    """Boltlight entrypoint.

    Any raised and uncaught exception will be handled here.
    """
    try:
        _start_boltlight()
    except ImportError as err:
        handle_importerror(err)
    except KeyError as err:
        LOGGER.error("The environment variable '%s' needs to be set", err)
        die()
    except RuntimeError as err:
        if str(err):
            LOGGER.error(str(err))
        die()
    except FileNotFoundError as err:
        LOGGER.error(str(err))
        die()
    except ConfigError as err:
        err_msg = ''
        if str(err):
            err_msg = str(err)
        LOGGER.error('Configuration error: %s', err_msg)
        die()
    except SQLAlchemyError as err:
        err_msg = ''
        if str(err):
            err_msg = str(err)
        LOGGER.error('DB error: %s', err_msg)
        die()
    except InterruptException:
        _interrupt_threads()
        _log_outro()
        sys.exit(0)
