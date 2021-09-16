# Copyright Okera Inc.

from __future__ import absolute_import

import okera
import datetime
from functools import wraps
import os
import random
import pickle
import pytz
import time

import certifi
import jwt
import prestodb
import urllib3
import xml.dom.minidom

from decimal import Context, Decimal
from collections import OrderedDict
from okera._util import get_logger_and_init_null
from okera import (HAS_NUMPY, HAS_PANDAS, assert_numpy_installed, assert_pandas_installed)
from okera._thrift_api import (
    OkeraRecordServicePlanner, RecordServiceWorker, TAccessPermissionLevel,
    TAssignAttributesParams, TAttribute, TAttributeMatchLevel, TAttributeValue,
    TAuthorizeQueryClient, TAuthorizeQueryParams, TCatalogObjectType, TCrawlerParams,
    TCrawlerOpType, TCreateAttributesParams, TDataRegConnection, TDataRegConnectionParams,
    TDeleteAttributesParams, TDiscoverCrawlerParams, TDiscoverCrawlerResult,
    TExecDDLParams, TExecTaskParams, TFetchParams, TGetAttributeNamespacesParams,
    TGetAttributesParams, TGetDatabasesParams, TGetDatasetsParams, TGetPartitionsParams,
    TGetRegisteredObjectsParams, TGetTablesParams, TInitApplicationParams,
    TListCatalogsParams,
    TListDatabasesParams, TListFilesOp, TListFilesParams, TNetworkAddress, TObjectOpType,
    TPlanRequestParams, TRecordFormat, TRecordServiceException, TRequestType, TTypeId,
    TUnassignAttributesParams)
from okera._thrift_util import (
    create_socket, get_transport, TTransportException, TBinaryProtocol,
    PlannerClient, WorkerClient, KERBEROS_NOT_ENABLED_MSG, SOCKET_READ_ZERO)
from .concurrency import (BaseBackgroundTask,
                          ConcurrencyController,
                          OkeraWorkerException,
                          default_max_client_process_count)

if HAS_NUMPY:
    import numpy

if HAS_PANDAS:
    import pandas

urllib3.disable_warnings()
_log = get_logger_and_init_null(__name__)

def _get_user_from_token(token, user_claims=None):
    if not token:
        return None

    try:
        # We try the two JWT libraries that can be installed, since they
        # both use the same module name. If they both fail, this will
        # return None, as we have no mechanism to parse the JWT.
        try:
          decoded = jwt.JWT().decode(token, do_verify=False)
        except:
          decoded = jwt.decode(token, options={"verify_signature": False})

        # Try loading it from the custom user claims if set,
        # and if not, do one fallback to `sub`, and return
        # None if that doesn't work either
        if not user_claims:
            user_claims = []
        for user_claim in user_claims:
            user = decoded.get(user_claim, None)
            if user:
                return user
        return decoded.get('sub', None)
    except:
        return None

    return None

def _is_picklable(o):
    try:
        pickle.dumps(o)
    except (pickle.PicklingError, AttributeError):
        return False
    return True

def _has_complex_type(schema):
    schema_cols = schema.nested_cols or schema.cols
    for col in schema_cols:
        if col.type.type_id in [TTypeId.ARRAY, TTypeId.MAP, TTypeId.RECORD]:
            return True
    return False

def _convert_presto_type(typeinfo, field, decimal_type):
    # PrestoDB and PrestoSQL differ on the way the types get represented
    if 'literalArguments' in typeinfo or 'typeArguments' in typeinfo:
        return _convert_presto_type_prestodb(typeinfo, field, decimal_type)
    else:
        return _convert_presto_type_prestosql(typeinfo, field, decimal_type)

def _convert_presto_type_prestodb(typeinfo, field, decimal_type):
    if field is None:
        return field

    if typeinfo['rawType'] == 'row':
        new_field = {}
        for idx in range(len(typeinfo['literalArguments'])):
            literal = typeinfo['literalArguments'][idx]
            subtype = typeinfo['typeArguments'][idx]
            subfield = field[idx]
            new_field[literal] = _convert_presto_type_prestodb(subtype, subfield, decimal_type)
        return new_field
    elif typeinfo['rawType'] == 'array':
        subtype = typeinfo['typeArguments'][0]
        return list(map(lambda subfield: _convert_presto_type_prestodb(subtype, subfield, decimal_type), field))
    elif typeinfo['rawType'] == 'map':
        value_subtype = typeinfo['typeArguments'][1]
        new_field = {}
        for subkey in field:
            new_field[subkey] = _convert_presto_type_prestodb(value_subtype, field[subkey], decimal_type)
        return new_field
    elif typeinfo['rawType'] == 'decimal':
        return decimal_type(field)
    else:
        return field

def _convert_presto_type_prestosql(typeinfo, field, decimal_type):
    if field is None:
        return field

    if typeinfo['rawType'] == 'row':
        new_field = {}
        for idx in range(len(typeinfo['arguments'])):
            arg = typeinfo['arguments'][idx]['value']
            literal = arg['fieldName']['name']
            subtype = arg['typeSignature']
            subfield = field[idx]
            new_field[literal] = _convert_presto_type_prestosql(subtype, subfield, decimal_type)
        return new_field
    elif typeinfo['rawType'] == 'array':
        subtype = typeinfo['arguments'][0]['value']
        return list(map(lambda subfield: _convert_presto_type_prestosql(subtype, subfield, decimal_type), field))
    elif typeinfo['rawType'] == 'map':
        value_subtype = typeinfo['arguments'][1]['value']
        new_field = {}
        for subkey in field:
            new_field[subkey] = _convert_presto_type_prestosql(value_subtype, field[subkey], decimal_type)
        return new_field
    elif typeinfo['rawType'] == 'decimal':
        return decimal_type(field)
    else:
        return field

def _rpc(func):
    """ Decorator for retries when making RPCs.

        This can be used from a OkeraContext API call, in which case we're just retrying
        establishing a new connection or a Planner/Worker Connection object, in which
        we need to reconnect and retry the RPC.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if isinstance(self, OkeraContext):
            retries = self.get_retries()
            initial_retry_delay_ms = self.get_initial_retry_delay_ms()
        else:
            retries = self.ctx.get_retries()
            initial_retry_delay_ms = self.ctx.get_initial_retry_delay_ms()
        attempt = 0
        cycled_token = False
        while True:
            try:
                if "test_hook_retry" in dir(self):
                    self.test_hook_retry(func.__name__, retries, attempt)
                return func(self, *args, **kwargs)
            except (TTransportException, IOError) as e:
                if retries == 1:
                    raise e

                # Since this may be an auth failure, we're going to cycle the
                # auth token if there is a token_func defined. We only do this
                # once however in a given loop, since if it fails again it
                # is unlikely to be auth related (or we're failing to generate
                # good tokens).
                ctx = self
                if not isinstance(self, OkeraContext):
                    ctx = self.ctx
                if not cycled_token and ctx._has_token_func():
                    _log.debug("Generating new token for retry.")
                    ctx._generate_token()
                    cycled_token = True

                attempt += 1
                if attempt == retries:
                    _log.error("All tries failed, raising exception.")
                    raise e
                else:
                    # Exponential delay with jitter
                    delay_ms = random.randint(
                        1, 2**(attempt - 1) * initial_retry_delay_ms)

                    _log.warning(
                        "Attempt failed. Sleeping %dms and then trying again." % delay_ms)
                    time.sleep(delay_ms / 1000)
                    if not isinstance(self, OkeraContext):
                        self._reconnect()
    return wrapper

def _inject_ctx(t_params, okera_context):
    """ Helper function to add a TRequestContext to a Thrift API call.

        Use this function immediately before making a Thrift API call
        on the params object passed into the API along with an Okera context.
        If the params object can accept a TRequestContext and the OkeraContext
        has a TRequestContext, the params will carry the TRequestContext through
        the call.

        This is helpful for instrumenting call patterns across various integrations.
    """

    # If the t_params doesn't accept a TRequestContext, do nothing.
    if not hasattr(t_params, 'ctx'):
        return
    # If the t_params already has a TRequestContext set, do nothing.
    if t_params.ctx is not None:
        return

    t_params.ctx = okera_context.get_request_context()

DIALECT_PRESTO = "presto"
DIALECT_OKERA = "okera"

""" Context for this user session."""
class OkeraContext():
    def __init__(self, application_name, namespace, tz=pytz.utc, retries=3,
            initial_retry_delay_ms=2000, dialect=None, request_context=None):
        _log.debug('Creating Okera context')
        self.__auth = None
        self.__service_name = None
        self.__token = None
        self.__token_func = None
        self.__user_claims = None
        self.__host_override = None
        self.__user = None
        self.__presto_password = None
        self.__name = application_name
        self.__namespace = namespace
        self.__dialect = dialect
        self.__configure()
        self.__tz = tz
        self.__retries = retries
        self.__initial_retry_delay_ms = initial_retry_delay_ms
        self.__request_context = request_context

    def enable_kerberos(self, service_name, host_override=None):
        """Enable kerberos based authentication.

        Parameters
        ----------
        service_name : str
            Authenticate to a particular `okera` service principal. This is typically
            the first part of the 3-part service principal (SERVICE_NAME/HOST@REALM).

        host_override : str, optional
            If set, the HOST portion of the server's service principal. If not set,
            then this is the resolved DNS name of the service being connected to.

        Returns
        -------
        OkeraContext
            Returns this object.
        """

        if not service_name:
            raise ValueError("Service name must be specified.")
        self.__auth = 'GSSAPI'
        self.__service_name = service_name
        self.__host_override = host_override
        self.__user = None
        _log.debug('Enabled kerberos')
        return self

    def enable_token_auth(self, token_str=None, token_file=None,
                          token_func=None, user=None, user_claims=None,
                          presto_password=None):
        """Enables token based authentication.

        Parameters
        ----------
        token_str : str, optional
            Authentication token to use.
        token_file : str, optional
            File containing token to use.
        token_func : lambda, optional
            Lambda to generate a token
        user : str, optional
            User for this request - will attempt to extract from token if not present
        user_claims : list of str, optional
            A list of possible claims to try and load the username from, with `sub` as
            the default fallback.
        presto_password : str, optional
            Password to use to authenticate to Presto, if distinct from the token.

        Returns
        -------
        OkeraContext
            Returns this object.
        """

        if not token_str and not token_file and not token_func:
            raise ValueError("Must specify token_str or token_file or token_func")
        if token_str and token_file:
            raise ValueError("Cannot specify both token_str token_file")
        if not _is_picklable(token_func):
            raise ValueError("token_func must be a picklable object")

        if token_file:
            with open(os.path.expanduser(token_file), 'r') as t:
                token_str = t.read()
        if token_func and not token_str:
            token_str = token_func()

        token = token_str.strip()
        if not user:
            user = _get_user_from_token(token, user_claims=user_claims)

        self.__presto_password = presto_password

        self.__user_claims = user_claims
        self.__token_func = token_func
        self.__configure_token(token, user)
        _log.debug('Enabled token auth')
        return self

    def disable_auth(self):
        """ Disables authentication.

        Returns
        -------
        OkeraContext
            Returns this object.
        """
        self.__auth = None
        self.__token = None
        self.__service_name = None
        self.__host_override = None
        self.__user = None
        _log.debug('Disabled auth')
        return self

    def get_auth(self):
        """ Returns the configured auth mechanism. None if no auth is enabled."""
        return self.__auth

    def get_token(self):
        """ Returns the token string. Note that logging this should be done with care."""
        return self.__token

    def get_presto_password(self):
        """ Returns the presto password. Note that logging this should be done with care."""
        return self.__presto_password

    def get_name(self):
        """ Returns name of this application. This is recorded for diagnostics on
            the server.
        """
        return self.__name

    def _get_user(self):
        """ Returns the user name. This is ignored if authentication is enabled. """
        return self.__user

    def get_namespace(self):
        return self.__namespace

    def get_dialect(self):
        return self.__dialect

    def get_timezone(self):
        return self.__tz

    def get_retries(self):
        return self.__retries

    def get_initial_retry_delay_ms(self):
        return self.__initial_retry_delay_ms

    def is_signed_url(self):
        # when set, pyokera plan requests ask for s3 pre-signed URLS. For tests.
        return os.getenv('ALLOW_PYOKERA_SIGNED_URL', 'False')=='True'

    def get_request_context(self):
        return self.__request_context

    def set_request_context(self, request_context):
        self.__request_context = request_context

    @_rpc
    def connect(
        self, host='localhost', port=12050, timeout=10,
        ssl=False, ca_cert=None,
        presto_host=None, presto_port=None, namespace=None):
        """Get a connection to an ODAS cluster. This connects to the planner service.

        Parameters
        ----------
        host : str or list of hostnames
            The hostname for the planner. If a list is specified, picks a planner at
            random.
        port : int, optional
            The port number for the planner. The default is 12050.
        timeout : int, optional
            Connection timeout in seconds. Default is 10 seconds.
        ssl : bool, optional
            Connect using SSL if set to True. Default is False.
        ca_cert : string, optional
            Path to a file of concatened PEM CA certificates. When not set,
            SSL certificate verification is disabled. Default is no verification.
        presto_host : str, optional
            The hostname for presto. If not specified and presto_port is specified,
            then the same hostname as the planner will be used. If neither are specified,
            then Presto-dialect queries are disabled.
        presto_port : int, optional
            The port number for Presto.
        namespace : str, optional
            The Presto namespace to use for this connection. If set, this will override
            the value set in the context, if any.

        Returns
        -------
        PlannerConnection
            Handle to a connection. Users should call `close()` when done.
        """
        service = self._connect_planner_internal(
            host, port, timeout, ssl, ca_cert)
        namespace = namespace or self.get_namespace()
        planner = PlannerConnection(
            service, self, host, port, timeout, ssl, ca_cert,
            presto_host, presto_port, namespace)
        planner._set_application_internal(self.__name)
        return planner

    def _connect_planner_internal(
        self, host, port, timeout, ssl=False, ca_cert=None):
        """Underlying function to establish a thrift planner connection.

        This function returns a thrift service object instead of the higher
        PlannerConnection wrapper object. This does not retry.
        """
        host, port = self.__pick_host(host, port)

        # Convert from user names to underlying transport names
        auth_mechanism = self.__get_auth()

        _log.debug('Connecting to planner %s:%s with %s authentication '
                   'mechanism', host, port, auth_mechanism)
        sock = create_socket(host, port, timeout, ssl, ca_cert)
        transport = None
        try:
            transport = get_transport(sock, host, auth_mechanism, self.__service_name,
                                      None, None, self.__token, self.__host_override)
            transport.open()
            # Clear timeout after establishing connection. RPCs can take a long time
            # (vs establishing a connection which should be fast).
            sock.set_timeout(None)
            protocol = TBinaryProtocol(transport)
            return _ThriftService(PlannerClient(OkeraRecordServicePlanner, protocol))
        except (TTransportException, IOError) as e:
            sock.close()
            if transport:
                transport.close()
            self.__handle_transport_exception(e)
            raise e
        except:
            sock.close()
            if transport:
                transport.close()
            raise

    def connect_worker(
        self, host='localhost', port=13050, timeout=10, ssl=False, ca_cert=None):
        """Get a connection to ODAS worker.

        Most users should not need to call this API directly.

        Parameters
        ----------
        host : str or list of hostnames
            The hostname for the worker. If a list is specified, picks a worker at
            random.
        port : int, optional
            The port number for the worker. The default is 13050.
        timeout : int, optional
            Connection timeout in seconds. Default is 10 seconds.
        ssl : bool, optional
            Connect using SSL if set to True. Default is False.
        ca_cert : string, optional
            Path to a file of concatened PEM CA certificates. When not set,
            SSL certificate verification is disabled. Default is no verification.

        Returns
        -------
        WorkerConnection
            Handle to a worker connection. Users must call `close()` when done.
        """
        return self._connect_worker(host, port, timeout=timeout, ssl=ssl, ca_cert=ca_cert)

    @_rpc
    def _connect_worker(
        self, host, port, timeout=10, options=None,
        ssl=False, ca_cert=None):
        service = self._connect_worker_internal(
            host, port, timeout, options, ssl, ca_cert)
        worker = WorkerConnection(
            service, self, host, port, timeout, options, ssl, ca_cert)
        worker._set_application_internal(self.__name)
        return worker

    def _connect_worker_internal(
        self, host, port, timeout, options, ssl=False, ca_cert=None):
        """Underlying function to establish a thrift worker connection.

        This function returns a thrift service object instead of the higher
        WorkerConnection wrapper object. This does not retry.
        """
        host, port = self.__pick_host(host, port, options)

        auth_mechanism = self.__get_auth()
        _log.debug('Connecting to worker %s:%s with %s authentication '
                   'mechanism', host, port, auth_mechanism)

        sock = create_socket(host, port, timeout, ssl, ca_cert)
        transport = None
        try:
            transport = get_transport(sock, host, auth_mechanism, self.__service_name,
                                      None, None, self.__token, self.__host_override)
            transport.open()
            protocol = TBinaryProtocol(transport)
            # Clear timeout after establishing connection. RPCs can take a long time
            # (vs establishing a connection which should be fast).
            sock.set_timeout(None)
            return _ThriftService(WorkerClient(RecordServiceWorker, protocol))
        except (TTransportException, IOError) as e:
            sock.close()
            if transport:
                transport.close()
            self.__handle_transport_exception(e)
            raise e
        except:
            sock.close()
            if transport:
                transport.close()
            raise

    @staticmethod
    def __pick_host(host, port, options=None):
        """
        Returns a host, port from the input. host can be a string or a list of strings.
        If it is a list, a host is picked from the list. If the host string contains the
        port that port is used, otherwise, the port argument is used.
        """
        if not host:
            raise ValueError("host must be specified")

        if isinstance(host, list):
            chosen_host = host[0]
            if isinstance(chosen_host, TNetworkAddress):
                if options and 'PIN_HOST' in options:
                    pinned = options['PIN_HOST']
                    # With this option, we want to pin a host instead of picking a
                    # random one.
                    found = False
                    for h in host:
                        if pinned != h.hostname:
                            continue
                        chosen_host = h
                        found = True
                        break

                    if not found:
                      host.sort(key = lambda v: v.hostname)
                      chosen_host = host[0]
                else:
                    chosen_host = random.choice(host)
                host = chosen_host.hostname
                port = chosen_host.port
            elif isinstance(chosen_host, str):
                if options and 'PIN_HOST' in options:
                    pinned = options['PIN_HOST']
                    if pinned in host:
                        chosen_host = pinned
                    else:
                        host.sort()
                        chosen_host = host[0]
                else:
                    chosen_host = random.choice(host)
                host = chosen_host
            else:
                raise ValueError("host list must be TNetworkAddress objects or strings.")

        if isinstance(host, str):
            parts = host.split(':')
            if len(parts) == 2:
                host = parts[0]
                port = int(parts[1])
            elif len(parts) == 1:
                host = parts[0]
                if port is None:
                    raise ValueError("port must be specified")
            else:
                raise ValueError("Invalid host: %s " % host)
        else:
            raise ValueError("Invalid host: %s" % host)
        return host, port

    def __configure(self):
        """ Configures the context based on system wide settings"""
        home = os.path.expanduser("~")
        token_file = os.path.join(home, '.cerebro', 'token')
        if os.path.exists(token_file):
            # TODO: we could catch this exception and go on but having this file be
            # messed up here is likely something to fix ASAP.
            with open(token_file, 'r') as t:
                self.__configure_token(t.read().strip())
            _log.info("Configured token auth with token in home directory.")

    def _has_token_func(self):
        """ Whether or not this context has a token_func configured """
        return self.__token_func is not None

    def _generate_token(self):
        """ Generates a new token by calling the token_func """
        new_token = self.__token_func()
        new_user = _get_user_from_token(new_token, user_claims=self.__user_claims)
        self.__configure_token(new_token, new_user)

    def __configure_token(self, token, user=None):
        # Valid authentication tokens contain '.' in them, either an Okera token or a JWT
        # token. For API convenience, we use the token value to mean user (plain text)
        # when run against unauthenticated servers.
        if '.' in token:
            self.__token = token
            self.__auth = 'TOKEN'
            self.__service_name = 'cerebro'
            self.__user = user
        else:
            self.__token = None
            self.__auth = None
            self.__user = token
        self.__host_override = None

    def __handle_transport_exception(self, e):
        """ Maps transport layer exceptions to better user facing ones. """
        if self.__auth and e.message == SOCKET_READ_ZERO:
            e.message = "Server did not respond to authentication handshake. " + \
                        "Ensure server has authentication enabled."
        elif not self.__auth and e.message == SOCKET_READ_ZERO:
            e.message = "Client does not have authentication enabled but it appears " + \
                        "the server does. Enable client authentication."
        elif self.__auth == 'GSSAPI' and KERBEROS_NOT_ENABLED_MSG in e.message:
            e.message = "Client is authenticating with kerberos but kerberos is not " + \
                        "enabled on the server."
        raise e

    def __get_auth(self):
        """ Canonicalizes user facing auth names to transport layer ones """
        auth_mechanism = self.__auth
        if not auth_mechanism:
            auth_mechanism = 'NOSASL'
        if auth_mechanism == 'TOKEN':
            auth_mechanism = 'DIGEST-MD5'
        return auth_mechanism

class _ThriftService():
    """ Wrapper around a thrift service client object """
    def __init__(self, thrift_client, retries=3):
        self.client = thrift_client
        self.retries = retries

    def close(self):
        # pylint: disable=protected-access
        _log.debug('close_service: client=%s', self.client)
        self.client._iprot.trans.close()

    def reconnect(self):
        # pylint: disable=protected-access
        _log.debug('reconnect: client=%s', self.client)
        self.client._iprot.trans.close()
        self.client._iprot.trans.open()

class PlannerConnection():
    """A connection to an ODAS planner. """

    def __init__(
        self, thrift_service, ctx, host, port, timeout,
        ssl, ca_cert, presto_host, presto_port, namespace):
        self.service = thrift_service
        self.ctx = ctx
        self.host = host
        self.port = port
        self.timeout = timeout
        self.ssl = ssl
        self.ca_cert = ca_cert
        self.presto_host = presto_host if presto_host else (host if presto_port else None)
        self.presto_port = presto_port
        self.namespace = namespace
        self.http_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                             ca_certs=certifi.where())
        _log.debug('PlannerConnection(service=%s)', self.service)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the session and server connection."""
        _log.debug('Closing Planner connection')
        self.service.close()

    def _reconnect(self):
        _log.debug('Reconnecting to planner...')
        self.close()
        self.service = self.ctx._connect_planner_internal(
            self.host, self.port, self.timeout,
            ssl=self.ssl, ca_cert=self.ca_cert)
        _log.debug('Reconnected to planner')

    def _underlying_client(self):
        """ Returns the underlying thrift client. Exposed for internal use. """
        return self.service.client

    def __choose_dialect(self, dialect):
        is_presto_disabled = not self.presto_host and not self.presto_port

        dialect = dialect or self.ctx.get_dialect()

        if not dialect and is_presto_disabled:
            return DIALECT_OKERA
        if not dialect and not is_presto_disabled:
            return DIALECT_PRESTO

        if dialect == DIALECT_PRESTO and is_presto_disabled:
            raise ValueError(
                "Dialect '%s' was selected, but no Presto host/port were specified" % (
                    DIALECT_PRESTO
                ))

        return dialect

    def __inject_ctx(self, t_params):
        _inject_ctx(t_params, self.ctx)

    @_rpc
    def get_protocol_version(self):
        """Returns the RPC API version of the server."""
        return self.service.client.GetProtocolVersion()

    @_rpc
    def get_server_version(self):
        """Returns the version of the server."""
        return self.service.client.GetServerVersion()

    @_rpc
    def set_application(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self._set_application_internal(name)

    def _set_application_internal(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        init = TInitApplicationParams()
        init.application = name
        self.service.client.InitApplication(init)

    @_rpc
    def ls(self, path):
        """ Lists the files in this directory

        Parameters
        ----------
        path : str
            The path to list.

        Returns
        -------
        list(str)
            List of files located at this path.
        """

        if not path:
            raise ValueError("path must be specified.")

        params = TListFilesParams()
        params.op = TListFilesOp.LIST
        params.object = path
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        self.__inject_ctx(params)
        return self.service.client.ListFiles(params).files

    @_rpc
    def open(self, path, preload_content=True, version=None):
        """ Returns the object at this path as a byte stream

        Parameters
        ----------
        path : str
            The path to the file to open.

        Returns
        -------
        object
            Returns an object that behaves like an opened urllib3 stream.
        """
        if not path:
            raise ValueError("path must be specified.")

        params = TListFilesParams()
        params.op = TListFilesOp.READ
        params.object = path
        params.version_id = version
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        try:
            self.__inject_ctx(params)
            urls = self.service.client.ListFiles(params).files
            if urls and len(urls) != 1:
                raise ValueError(
                    "Unexpected result from server. Expecting at most one url.")
            return self.http_pool.request('GET', urls[0],
                                          preload_content=preload_content)
        except TRecordServiceException as ex:
            if not ex.detail.startswith('AuthorizationException'):
                raise ex
            # This request (for the path) failed with an authorization exception,
            # meaning this user does not have full access to the path. Try to see
            # if this user has access to a table over this path.
            objs = self.get_catalog_objects_at(path, True)
            if not objs or path not in objs:
                raise ex
            for obj in objs[path]:
                if '.' in obj:
                    return OkeraFsStream(self, obj)

            # No object found, raise original exception
            raise ex

    @_rpc
    def cat(self, path, as_utf8=True):
        """ Returns the object at this path as a string

        Parameters
        ----------
        path : str
            The path to the file to read.

        as_utf8 : bool
            If true, convert the returned data as a utf-8 string (instead of binary)

        Returns
        -------
        str
            Returns the contents at the path as a string.
        """

        result = self.open(path)

        if result.status != 200:
            if 'Content-Type' in result.headers:
                if result.headers['Content-Type'] == 'application/xml':
                    msg = result.data.decode('utf-8').replace('\n', '')
                    tree = xml.dom.minidom.parseString(msg).toprettyxml(indent='  ')
                    raise ValueError("Could not read from path: %s\n\n%s" % (path, tree))
            raise ValueError("Could not read from path: %d" % result.status)

        if not result.data:
            if as_utf8:
                return b""
            return ""

        # Check the types to avoid some double serialization
        if isinstance(result.data, str):
            if as_utf8:
                # Both UTF-8
                if result.data.endswith('\n'):
                    return result.data[:-1]
                return result.data
            else:
                if result.data.endswith('\n'):
                    return result.data[:-1].encode('utf-8')
                return result.data.encode('utf-8')

        # Result is binary
        if result.data.endswith(b'\n'):
            if as_utf8:
                return result.data[:-1].decode('utf-8')
            return result.data[:-1]
        if as_utf8:
            return result.data.decode('utf-8')
        else:
            return result.data

    @_rpc
    def get_catalog_objects_at(self, path_prefix, include_views=False):
        """ Returns the objects (databases or datasets) thats registered with this
            prefix path.

        Parameters
        ----------
        path_prefix : str
            The path prefix to look up objects defined with this prefix.

        include_views : bool
            If true, also return views at this path.

        Returns
        -------
        map(str, list(str))
            For each path with a catalog objects, the list of objects located at that
            path. Empty map if there are none.
        """

        if not path_prefix:
            raise ValueError("path_prefix must be specified.")

        params = TGetRegisteredObjectsParams()
        params.prefix_path = path_prefix
        params.include_views = include_views
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        self.__inject_ctx(params)
        return self.service.client.GetRegisteredObjects(params).object_names

    @_rpc
    def create_attribute(self, namespace, key):
        """Creates an attribute

        namespace : str
            The namespace to create the attribute in.

        key : str
            The key of the attribute.

        Returns
        -------
        None
        """

        attribute = TAttribute()
        attribute.key = key
        attribute.attribute_namespace = namespace

        params = TCreateAttributesParams()
        params.attributes = [attribute]
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'

        try:
            self.__inject_ctx(params)
            self.service.client.CreateAttributes(params)
        except TRecordServiceException as ex:
            raise

    @_rpc
    def delete_attribute(self, namespace, key):
        """Deletes an attribute

        namespace : str
            The namespace for the attribute to delete.

        key : str
            The key of the attribute.

        Returns
        -------
        bool
            Returns true if the attribute existed and was deleted.
        """

        attribute = TAttribute()
        attribute.key = key
        attribute.attribute_namespace = namespace

        params = TDeleteAttributesParams()
        params.attributes = [attribute]
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'

        self.__inject_ctx(params)
        result = self.service.client.DeleteAttributes(params)
        if result.delete_count > 1:
            _log.warning(
                ("delete_attribute() deleted multiple (%d) attributes. " +
                "This is unexpected.") % result.delete_count)
        return result.delete_count >= 1

    @_rpc
    def list_attribute_namespaces(self, editable_only=False):
        """List attribute namespaces

        editable_only : bool, optional
            If true, only return attributes namespaces where the user has edit access.

        Returns
        -------
        list(str)
            List of attribute namespace.
        """
        params = TGetAttributeNamespacesParams()
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'
        params.editable_only = editable_only

        self.__inject_ctx(params)
        return self.service.client.GetAttributeNamespaces(params).namespaces

    @_rpc
    def list_attributes(self, namespace=None, editable_only=False):
        """List attributes in this namespace

        namespace : str, optional
            The namespace to list attributes in. If not set, returns attributes in
            all namespaces.

        editable_only : bool, optional
            If true, only return attributes namespaces where the user has edit access.

        Returns
        -------
        list(obj)
            Thrift attribute objects.

        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """
        params = TGetAttributesParams()
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'

        # TODO: We shouldn't have to set this
        params.filter_attribute = TAttribute('')
        params.editable_only = editable_only
        if namespace:
            params.filter_attribute.attribute_namespace = namespace
        self.__inject_ctx(params)
        return self.service.client.GetAttributes(params).attributes

    def __set_attribute(self, is_assign, namespace, key, db, dataset, column,
                        cascade):
        attr = TAttribute()
        attr.attribute_namespace = namespace
        attr.key = key

        val = TAttributeValue()
        val.attribute = attr
        val.value = 'true'
        val.is_active = True
        if db:
            val.database = db
            if dataset:
                val.table = dataset
                if column:
                    val.column = column

        if is_assign:
            params = TAssignAttributesParams()
        else:
            params = TUnassignAttributesParams()

        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'
        if cascade is not None:
            params.cascade = cascade

        params.mappings = [val]

        try:
            if is_assign:
                self.__inject_ctx(params)
                self.service.client.AssignAttributes(params)
            else:
                self.__inject_ctx(params)
                self.service.client.UnassignAttributes(params)
        except TRecordServiceException as ex:
            raise

    @_rpc
    def assign_attribute(self, namespace, key, db, dataset=None, column=None,
                         cascade=None):
        """Assigns this attribute to this catalog object

        namespace : str
            The namespace for this attribute.
        key : str
            The key for this attribute.
        db : str
            The database to apply this attribute for.
        dataset : str, optional
            The dataset to apply this attribute for. If not set, applies to the entire
            database.
        column : str, optional
            The column to apply this attribute for. If not set, applies to the entire
            dataset.
        cascade : bool, optional
            If true, control whether this asssignment cascades to views derived on this
            dataset. If not set, uses the server default.

        Returns
        -------
        None
        """

        self.__set_attribute(True, namespace, key, db, dataset, column, cascade)

    @_rpc
    def unassign_attribute(self, namespace, key, db, dataset=None, column=None,
                           cascade=None):
        """Unassigns this attribute to this catalog object

        namespace : str
            The namespace for this attribute.
        key : str
            The key for this attribute.
        db : str
            The database to apply this attribute for.
        dataset : str, optional
            The dataset to apply this attribute for. If not set, applies to the entire
            database.
        column : str, optional
            The column to apply this attribute for. If not set, applies to the entire
            dataset.
        cascade : bool, optional
            If true, control whether this asssignment cascades to views derived on this
            dataset. If not set, uses the server default.

        Returns
        -------
        None
        """

        self.__set_attribute(False, namespace, key, db, dataset, column, cascade)

    @_rpc
    def manage_data_reg_connection(self,
                                   op_type,
                                   data_reg_connection,
                                   connection_names=None,
                                   connection_pattern=None,
                                   requesting_user=None,
                                   jdbc_driver=None):
        """Creates a data registration connection

        op_type : str
            The operation on the data registration connection
        data_reg_connection: TDataRegConnection
            The data registration connection object
        connection_names : list<str>, optional
            The connection_names for listing connections
        connection_pattern : str, optional
            The connection_pattern for searching the connections
        requesting_user : str, optional
        jdbc_driver : str, optional
            The jdbc_driver to filter connections by

        Returns
        -------
        list(TDataRegConnection)
            List of Data Registration Connections.
        """

        drc_op_type = TObjectOpType.CREATE
        if op_type == 'CREATE':
            drc_op_type = TObjectOpType.CREATE
        elif op_type == 'UPDATE':
            drc_op_type = TObjectOpType.UPDATE
        elif op_type == 'DELETE':
            drc_op_type = TObjectOpType.DELETE
        elif op_type == 'TEST_CREATE':
            drc_op_type = TObjectOpType.TEST_CREATE
        elif op_type == 'TEST_EDIT':
            drc_op_type = TObjectOpType.TEST_EDIT
        elif op_type == 'TEST_EXISTING':
            drc_op_type = TObjectOpType.TEST_EXISTING
        elif op_type == 'GET':
            drc_op_type = TObjectOpType.GET
        elif op_type == 'LIST':
            drc_op_type = TObjectOpType.LIST
        else:
            raise RuntimeError("Unrecognized operation type for " \
                "data registration connection. Option provided " + op_type)

        params = TDataRegConnectionParams()
        params.connection = data_reg_connection
        params.op_type = drc_op_type
        params.connection_names = connection_names
        params.connection_pattern = connection_pattern
        params.jdbc_driver = jdbc_driver
        if requesting_user:
            params.requesting_user = requesting_user
        elif self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'

        result = []
        try:
            self.__inject_ctx(params)
            result = self.service.client.ManageDataRegConnection(params)
        except TRecordServiceException as ex:
            raise

        return result

    @_rpc
    def discover_crawler(self,
                        data_reg_connection,
                        jdbc_catalog=None,
                        jdbc_schema=None):
        """Discovers a crawler for a connection

        data_reg_connection: TDataRegConnection
            The data registration connection object

        jdbc_catalog: str, optional
            The JDBC catalog name if discovering schemas for the catalog.
        jdbc_schema: str, optional
            The JDBC schema name if discovering table schemas for the catalog/schema.

        Returns
        -------
        TDiscoverCrawlerResult
            Crawler discovery results.
        """

        params = TDiscoverCrawlerParams()
        params.connection = data_reg_connection
        params.jdbc_catalog = jdbc_catalog
        params.jdbc_schema = jdbc_schema
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'
        result = []
        try:
            self.__inject_ctx(params)
            result = self.service.client.DiscoverCrawler(params)
        except TRecordServiceException as ex:
            raise

        return result

    @_rpc
    def manage_crawler(self,
                        data_reg_connection):
        """Creates a crawler for a connection

        data_reg_connection: TDataRegConnection
            The data registration connection object

        Returns
        -------
        TCrawlStatus
            Crawler Status.
        """

        params = TCrawlerParams()
        params.op_type = TCrawlerOpType.CRAWL
        params.connection = data_reg_connection
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        else:
            # TODO: the thrift API should not have this as required
            params.requesting_user = 'root'

        result = []
        try:
            self.__inject_ctx(params)
            result = self.service.client.ManageCrawler(params)
        except TRecordServiceException as ex:
            raise

        return result

    @_rpc
    def list_catalogs(self, requesting_user=None):
        """Lists all the catalogs which requesting_user has access to

        Parameters
        ----------
        requesting_user : str, optinoal

        Returns
        -------
        list(TOkeraCatalog)
            List of Catalogs.
        """

        params = TListCatalogsParams()
        if requesting_user:
            params.requesting_user = requesting_user
        elif self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()

        result = []
        self.__inject_ctx(params)
        result = self.service.client.ListCatalogs(params)
        return result

    @_rpc
    def list_databases(self, privilege=None):
        """Lists all the databases in the catalog

        Parameters
        ----------
        privilege : TAccessPermissionLevel or list(TAccessPermissionLevel), optional
            Privilege level (or levels) to check for access.

        Returns
        -------
        list(str)
            List of database names.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     dbs = conn.list_databases()
        ...     'okera_sample' in dbs
        True
        """

        request = TGetDatabasesParams()
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        # Thrift enums have a 0 member that won't be passed into
        # RPC if we don't check explicitly for absent value
        if privilege is not None:
            if isinstance(privilege, list):
                request.access_levels = privilege
            else:
                request.access_levels = [privilege]
        self.__inject_ctx(request)
        result = self.service.client.GetDatabases(request)
        dbs = []
        for db  in result.databases:
            dbs.append(db.name[0])
        return dbs


    @_rpc
    def list_databases_v2(self,
                          requesting_user=None,
                          exact_names_filter=None,
                          name_pattern_filter=None,
                          tags=None,
                          privilege=None,
                          sorting_info=None,
                          ignore_internal_dbs=True,
                          limit=10,
                          page_token=None,
                          tag_match_level=None,
                          is_crawler=False,
                          names_only=False):
        """Lists all the databases in the catalog which requesting_user has access to

        Parameters
        ----------
        requesting_user : str, optional
        exact_names_filter : list<str>, optional
        name_pattern_filter : str, optional
        tags : list<TAttribute>, optional
        privilege : list<TPrivilegeLevel>, optional
        sorting_info : list<TSortColOrder>, optional
        ignore_internal_dbs : boolean, optional
        limit : int, optional
        page_token : str, optional
        tag_match_level : TAttributeMatchLevel, optional
        is_crawler : boolean, optional
        names_only : boolean, optional

        Returns
        -------
        list(TDatabase)
            List of database objects.
        prev_token (str)
            pagination info - token for previous page
        next_token (str)
            pagination info - token for next page
        total_count (int)
            Count of total databases user has access to
        """

        params = TListDatabasesParams()
        if requesting_user:
            params.requesting_user = requesting_user
        elif self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        if exact_names_filter:
            params.db_names = exact_names_filter
        if name_pattern_filter:
            params.db_name_pattern = name_pattern_filter
        if tags:
            params.attributes = tags
        # Thrift enums have a 0 member that won't be passed into
        # RPC if we don't check explicitly for absent value
        if privilege is not None:
            params.access_levels = [privilege]
        params.ignore_internal_dbs = ignore_internal_dbs
        if limit:
            params.limit = limit
        if page_token:
            params.page_token = page_token
        # Thrift enums have a 0 member that won't be passed into
        # RPC if we don't check explicitly for absent value
        if tag_match_level is not None:
            params.attr_match_level = tag_match_level
        params.is_crawler = is_crawler
        params.names_only = names_only

        result = []
        self.__inject_ctx(params)
        result = self.service.client.ListDatabases(params)
        return result

    @_rpc
    def list_dataset_names(self, db, filter=None):
        """ Returns the names of the datasets in this db

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        filter : str, optional
            Substring filter on names to of datasets to return.

        Returns
        -------
        list(str)
            List of dataset names.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     datasets = conn.list_dataset_names('okera_sample')
        ...     datasets
        ['okera_sample.sample', 'okera_sample.users', 'okera_sample.users_ccn_masked', 'okera_sample.whoami']
        """
        request = TGetTablesParams()
        request.database = [db]
        request.filter = filter
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        self.__inject_ctx(request)
        tables = self.service.client.GetTables(request).tables
        result = []
        for t in tables:
            result.append(db + '.' + t.name)
        return result

    @_rpc
    def list_datasets(self, db, filter=None, name=None, privilege=None, tags=None,
                      tag_match_level=None, connection_name=None, requesting_user=None):
        """ Returns the datasets in this db

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        filter : str, optional
            Substring filter on names to of datasets to return.
        name : str, optional
            Name of dataset to return. Cannot be set if filter is set.
        privilege : TAccessPermissionLevel, optional
            Privilege level to check for access.
        tags : list<TAttribute>, optional
            List of attributes (tags) to filter
        tag_match_level : TAttributeMatchLevel, optional
            Param to specify the level of match for attributes filter
        connection_name : str, optional
            Filter to get all the datasets associated with the input connection

        Returns
        -------
        obj
            Thrift dataset objects.

        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        if filter and name:
            raise RuntimeError("Cannot specify both filter and name")

        request = TGetDatasetsParams()

        if name:
            request.dataset_names = ['%s.%s' % (db, name)]
            request.with_schema = True
        else:
            # If the request is not for a specific table, then
            # always set the DB, regardless of whether a filter
            # is set.
            request.databases = [db]
            if filter:
                request.filter = filter

        # Thrift enums have a 0 member that won't be passed into
        # RPC if we don't check explicitly for absent value
        if privilege is not None:
            request.access_levels = [privilege]

        if tags:
            request.attributes = tags

        if tag_match_level:
            request.attr_match_level = tag_match_level

        if connection_name:
            request.connection_name = connection_name

        if requesting_user:
            request.requesting_user = requesting_user
        elif self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        self.__inject_ctx(request)
        return self.service.client.GetDatasets(request).datasets

    @_rpc
    def list_partitions(self, db, dataset):
        """ Lists the partitions in this dataset

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        dataset : str
            Name of dataset.

        Returns
        -------
        obj
            Thrift partition objects.
        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        request = TGetPartitionsParams()
        request.database = [db]
        request.table = dataset
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        self.__inject_ctx(request)
        return self.service.client.GetPartitions(request)

    @_rpc
    def plan(self, request, max_task_count=None, requesting_user=None, client=None,
             min_task_size=None):
        """ Plans the request to read from CDAS

        Parameters
        ----------
        request : str, required
            Name of dataset or SQL statement to plan scan for.
        requesting_user : str, optional
            Name of user to request plan for, if different from
            the current user.
        client: TAuthorizeQueryClient, optional
            The TAuthorizeQueryClient enum value of the client to use for SQL
            rewrite planning.
        min_task_size: int, optional
            Test only flag to control the minimum task size for the TaskCombiner to
            generate tasks.

        Returns
        -------
        object
            Thrift serialized plan object.

        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        if not request:
            raise ValueError("request must be specified.")

        if client:
            params = TAuthorizeQueryParams()
            params.sql = request
            params.cte_rewrite = True
            if requesting_user:
                params.requesting_user = requesting_user
            elif self.ctx._get_user():
                params.requesting_user = self.ctx._get_user()
            params.client = client
            params.plan_request = True
            self.__inject_ctx(params)
            result = self.service.client.AuthorizeQuery(params)
            plan = result.plan
        else:
            params = TPlanRequestParams()
            params.request_type = TRequestType.Sql
            if self.ctx.is_signed_url():
                params.cluster_id="external"
            if max_task_count:
                params.max_tasks = max_task_count
            if min_task_size:
                params.min_task_size = min_task_size
            if requesting_user:
                params.requesting_user = requesting_user
            elif self.ctx._get_user():
                params.requesting_user = self.ctx._get_user()

            request = request.strip()
            if request.lower().startswith('select') or request.lower().startswith('with'):
                _log.debug('Planning request for query: %s', request)
                params.sql_stmt = request
            else:
                _log.debug('Planning request to read dataset: %s', request)
                params.sql_stmt = "SELECT * FROM " + request
            self.__inject_ctx(params)
            plan = self.service.client.PlanRequest(params)
        _log.debug('Plan complete. Number of tasks: %d', len(plan.tasks))
        return plan

    @_rpc
    def execute_ddl(self, sql, requesting_user=None):
        # pylint: disable=line-too-long
        """ Execute a DDL statement against the server.

        Parameters
        ----------
        sql : str
            DDL statement to run
        requesting_user : str, optional
            Name of user to request plan for, if different from
            the current user.

        Returns
        -------
        list(list(str))
            Returns the result as a table.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     result = conn.execute_ddl('describe okera_sample.users')
        ...     result
        [['uid', 'string', 'Unique user id', ''], ['dob', 'string', 'Formatted as DD-month-YY', ''], ['gender', 'string', '', ''], ['ccn', 'string', 'Sensitive data, should not be accessible without masking.', '']]
        """
        # pylint: enable=line-too-long

        if not sql:
            raise ValueError("Must specify sql string to execute_ddl")
        request = TExecDDLParams()
        request.ddl = sql
        if requesting_user:
            request.requesting_user = requesting_user
        elif self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        self.__inject_ctx(request)
        response = self.service.client.ExecuteDDL2(request)
        if response.formatted_result:
            return response.formatted_result
        return response.tabular_result

    @_rpc
    def execute_ddl_table_output(self, sql):
        """ Execute a DDL statement against the server.

        Parameters
        ----------
        sql : str
            DDL statement to run

        Returns
        -------
        PrettyTable
            Returns the result as a table object.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     result = conn.execute_ddl_table_output('describe okera_sample.users')
        ...     print(result)
        +--------+--------+-----------------------------------------------------------+------------+
        |  name  |  type  |                          comment                          | attributes |
        +--------+--------+-----------------------------------------------------------+------------+
        |  uid   | string |                       Unique user id                      |            |
        |  dob   | string |                  Formatted as DD-month-YY                 |            |
        | gender | string |                                                           |            |
        |  ccn   | string | Sensitive data, should not be accessible without masking. |            |
        +--------+--------+-----------------------------------------------------------+------------+
        """
        from prettytable import PrettyTable

        if not sql:
            raise ValueError("Must specify sql string to execute_ddl")
        request = TExecDDLParams()
        request.ddl = sql
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        self.__inject_ctx(request)
        response = self.service.client.ExecuteDDL2(request)
        if not response.col_names:
            return None

        t = PrettyTable(response.col_names)
        for row in response.tabular_result:
            t.add_row(row)
        return t

    def scan_as_pandas(self,
                       request,
                       dialect=None,
                       max_records=None,
                       max_client_process_count=default_max_client_process_count(),
                       max_task_count=None,
                       requesting_user=None,
                       options=None,
                       ignore_errors=False,
                       warnings=None,
                       strings_as_utf8=False,
                       presto_session=None,
                       presto_headers=None,
                       presto_protocol="https",
                       min_task_size=None):
        """Scans data, returning the result for pandas.

        Parameters
        ----------
        request : string, required
            Name of dataset or SQL statement to scan.
        max_records : int, optional
            Maximum number of records to return. Default is unlimited.
        options : dictionary, optional
            Optional key/value configs to specify to the request. Note that these
            options are not guaranteed to be backwards compatible.
        warnings : list(string), optional
            If not None, will be populated with any warnings generated for request.

        Returns
        -------
        pandas DataFrame
            Data returned as a pandas DataFrame object

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     pd = conn.scan_as_pandas('select * from okera_sample.sample')
        ...     print(pd)
                                       record
        0      b'This is a sample test file.'
        1  b'It should consist of two lines.'
        """
        assert_pandas_installed()
        assert_numpy_installed() # Pandas requires numpy -- this should never fail
        chosen_dialect = self.__choose_dialect(dialect)

        res = []
        if chosen_dialect == DIALECT_OKERA:
            plan = self.plan(request,
                            max_task_count=max_task_count,
                            requesting_user=requesting_user,
                            min_task_size=min_task_size)
            self._ensure_serialization_support(plan)

            if _has_complex_type(plan.schema):
                output_format = TRecordFormat.Columnar
            else:
                output_format = TRecordFormat.ColumnarNumPy

            # Return any warnings if the user is interested
            if warnings is not None and plan.warnings:
                for warning in plan.warnings:
                    warnings.append(warning.message)

            concurrency_ctl = self._get_concurrency_controller_for_plan(
                plan, max_client_process_count)

            for task in plan.tasks:
                _log.debug('Executing task %s', str(task.task_id))
                concurrency_ctl.enqueueTask(PandasScanTask(self.ctx,
                                                        plan.hosts,
                                                        task,
                                                        max_records,
                                                        options,
                                                        strings_as_utf8,
                                                        output_format=output_format,
                                                        ssl=self.ssl,
                                                        ca_cert=self.ca_cert))

            result_list = self._start_and_wait_for_results(concurrency_ctl,
                                                        len(plan.tasks),
                                                        limit=max_records,
                                                        is_pandas=True,
                                                        ignore_errors=ignore_errors)
            if not result_list:
                # In the case that we do not have results, we still want
                # the DF to have the column names. To do that, we have to
                # get the query plan and extract them, accounting for any
                # complex types by skipping the inner columns.
                col_names = []
                schema_cols = plan.schema.nested_cols or plan.schema.cols

                col_idx = 0
                while col_idx < len(schema_cols):
                    col_names.append(schema_cols[col_idx].name)
                    skip_count = _get_column_skip(schema_cols, col_idx)
                    col_idx += 1 + skip_count

                return pandas.DataFrame(columns=col_names)
            else:
                return pandas.concat(result_list, ignore_index=True).head(max_records)
        elif chosen_dialect == DIALECT_PRESTO:
            results, colnames = self.__execute_presto_query(
                request, max_records, decimal_type=Decimal, presto_session=presto_session,
                presto_headers=presto_headers, presto_protocol=presto_protocol)
            df = pandas.DataFrame(results, columns=colnames)

            return df

    def scan_as_json(self,
                     request,
                     dialect=None,
                     max_records=None,
                     warnings=None,
                     max_client_process_count=default_max_client_process_count(),
                     max_task_count=None,
                     requesting_user=None,
                     ignore_errors=False,
                     strings_as_utf8=True,
                     decimal_type=str,
                     no_numpy_types=True,
                     presto_session=None,
                     presto_headers=None,
                     presto_protocol="https",
                     client=None,
                     min_task_size=None):
        # pylint: disable=line-too-long
        """Scans data, returning the result in json format.

        Parameters
        ----------
        request : string, required
            Name of dataset or SQL statement to scan.
        max_records : int, optional
            Maximum number of records to return. Default is unlimited.
        warnings : list(string), optional
            If not None, will be populated with any warnings generated for request.

        Returns
        -------
        list(obj)
            Data returned as a list of JSON objects

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     data = conn.scan_as_json('okera_sample.sample')
        ...     data
        [{'record': 'This is a sample test file.'}, {'record': 'It should consist of two lines.'}]
        """
        # pylint: enable=line-too-long
        chosen_dialect = self.__choose_dialect(dialect)

        res = []
        if chosen_dialect == DIALECT_OKERA:
            assert_numpy_installed()
            plan = self.plan(request,
                            max_task_count=max_task_count,
                            requesting_user=requesting_user,
                            client=client,
                            min_task_size=min_task_size)
            self._ensure_serialization_support(plan)

            concurrency_ctl = self._get_concurrency_controller_for_plan(
                plan, max_client_process_count)

            if _has_complex_type(plan.schema):
                output_format = TRecordFormat.Columnar
            else:
                output_format = TRecordFormat.ColumnarNumPy

            # Return any warnings if the user is interested
            if warnings is not None and plan.warnings:
                for warning in plan.warnings:
                    warnings.append(warning.message)

            if len(plan.tasks) <= 0:
                return []

            for task in plan.tasks:
                _log.debug('Executing task %s', str(task.task_id))
                concurrency_ctl.enqueueTask(JsonScanTask(self.ctx,
                                                        plan.hosts,
                                                        task,
                                                        max_records,
                                                        output_format=output_format,
                                                        strings_as_utf8=strings_as_utf8,
                                                        decimal_type=decimal_type,
                                                        no_numpy_types=no_numpy_types,
                                                        ssl=self.ssl,
                                                        ca_cert=self.ca_cert))

            res = self._start_and_wait_for_results(concurrency_ctl,
                                                len(plan.tasks),
                                                limit=max_records,
                                                ignore_errors=ignore_errors)
        elif chosen_dialect == DIALECT_PRESTO:
            results, colnames = self.__execute_presto_query(
                request, max_records, to_dict=True, decimal_type=decimal_type,
                presto_session=presto_session, presto_headers=presto_headers,
                presto_protocol=presto_protocol)
            res = results

        if max_records is not None:
            return res[:max_records]
        return res

    def __execute_presto_query(self, query, max_records,
                               to_dict=False, decimal_type=str, presto_session=None,
                               presto_headers=None, presto_protocol="https"):
        # If there is no token, we set the user as the token, as
        # that is helpful for unauthenticated clusters.
        username = self.ctx._get_user()
        token = self.ctx.get_presto_password() or self.ctx.get_token() or self.ctx._get_user()

        if not token or not username:
            raise RuntimeError('Authentication must be enabled for Presto queries.')

        headers = {}
        if self.ctx.get_timezone():
            tz = self.ctx.get_timezone()
            if hasattr(tz, 'zone'):
                # From the pytz object, we need to get back how many seconds
                # this timezone if offset from UTC (either positive or negative).
                # For example, America/New_York is 5 hours behind UTC, which is
                # equivalent to -18000 seconds.
                # There is no easy way to get this information from the pytz
                # object, so we first construct a current datetime and then
                # extract it from that.
                tz_offset = datetime.datetime.now(tz).utcoffset().total_seconds()
                # Given the number of seconds, we want to construct it into an
                # HH:MM format, with a positive or negative sign as well, e.g.
                # -05:00 -> American/New_York
                # +05:30 -> Asia/Calcutta
                tz_offset_string = "%s%s" % (
                    "-" if tz_offset < 0 else "+",
                    time.strftime("%H:%M", time.gmtime(abs(tz_offset)))
                )
                headers['X-Presto-Time-Zone'] = tz_offset_string
        if presto_headers and isinstance(presto_headers, dict):
            headers.update(presto_headers)

        http_scheme = "https"
        presto_auth = prestodb.auth.BasicAuthentication(username, token)
        if presto_protocol == "http":
            http_scheme = "http"
            presto_auth = None

        session_user = username
        # This is used mostly for testing so we can override the session user
        # separately from the authenticated user. We pass the user we want
        # as the session user in this header (the Presto header). Unfortunatly,
        # the Presto library doesn't let us set this via header (it is a "protectd"
        # header), so we manually extract it and set it.
        if 'X-Presto-User' in headers:
            session_user = headers['X-Presto-User']
            del headers['X-Presto-User']

        cycled_token = False
        conn = None
        cursor = None
        results = []
        colnames = []
        typeinfo = []

        def _close_presto_safely():
            if cursor:
                cursor.cancel()
            if conn:
                conn.close()

        try:
            # We will try to correct token expiration if appropriate
            while True:
                try:
                    conn = prestodb.dbapi.connect(
                        host=self.presto_host,
                        port=self.presto_port,
                        user=session_user,
                        catalog=self.namespace,
                        http_scheme=http_scheme,
                        auth=presto_auth,
                        # Allows us to cancel queries once we've read enough
                        isolation_level=prestodb.transaction.IsolationLevel.READ_UNCOMMITTED,
                        http_headers = headers,
                        session_properties=presto_session,
                    )

                    conn._http_session.verify = False
                    cursor = conn.cursor()
                    cursor.execute(query)

                    results = []
                    if max_records:
                        results.extend(cursor.fetchmany(max_records))
                    else:
                        results = cursor.fetchall()
                    colnames = [part[0] for part in cursor.description]
                    # The Presto Python library doesn't expose the full type information,
                    # which includes the struct field information, so we have to go into
                    # "private" parts to get it.
                    types = cursor._query.columns

                    # If we've succeeded exit out of the retry loop
                    break
                except(prestodb.exceptions.DatabaseError) as e:
                    _close_presto_safely()
                    # The Presto library does not give us a great error for when
                    # an authentication error happened (e.g. token expired), so
                    # we use this string matching.
                    auth_failure = 'failed to start transaction: 401' == str(e)
                    has_auth = presto_auth is not None

                    # If auth is enabled and this is an auth failure and we have a way
                    # to refresh tokens and we haven't already cycled the token once,
                    # we'll try and refresh the token. If we have cycled already and we
                    # still failed with an auth failure, it's unlikely that another
                    # refresh will make it work.
                    if has_auth and auth_failure and self.ctx._has_token_func() and not cycled_token:
                        # Generate a new token and update the auth setting
                        self.ctx._generate_token()

                        new_username = self.ctx._get_user()
                        new_token = self.ctx.get_token() or self.ctx._get_user()
                        presto_auth = prestodb.auth.BasicAuthentication(new_username, new_token)

                        cycled_token = True
                        continue

                    # For any other condition, raise the original error
                    raise
        finally:
            _close_presto_safely()

        # Presto returns structs as arrays of the fields, and the field names
        # are stored in the type signature. We need to reconstruct the full type,
        # so we recursively walk the results and type information together. Since
        # we are already processing the results, we combine it into a dictionary
        # if requested (for scan_as_json), or leave it as an array of arrays (for
        # scan_as_pandas).
        for idx in range(len(results)):
            result = results[idx]
            dict_result = {}
            for typeidx in range(len(types)):
                name = types[typeidx]['name']
                typeinfo = types[typeidx]['typeSignature']
                if to_dict:
                    dict_result[name] = _convert_presto_type(
                            typeinfo, result[typeidx], decimal_type)
                else:
                    result[typeidx] = _convert_presto_type(
                            typeinfo, result[typeidx], decimal_type)
            if to_dict:
                results[idx] = dict_result
            else:
                results[idx] = result

        return results, colnames

    @staticmethod
    def _get_concurrency_controller_for_plan(plan, max_client_process_count):
        worker_count = min(max_client_process_count, len(plan.tasks))
        return ConcurrencyController(worker_count=worker_count)

    @staticmethod
    def _calculate_limit(current_limit, results, is_pandas):
        if current_limit is None:
            return None
        if is_pandas:
            if len(results) == 0:
                return current_limit
            return max(current_limit-len(results[0].index), 0)
        return max(current_limit-len(results), 0)

    @staticmethod
    def _start_and_wait_for_results(concurrency_ctl,
                                    task_count,
                                    limit=None,
                                    is_pandas=False,
                                    ignore_errors=False):
        results = []
        if not task_count:
            return results
        try:
            task_result_count = 0
            is_completed = False
            # We're setting the limit value into a shared dict that is handed
            # to all async tasks.  The main thread (this function) is responsible
            # for updating the value as records are received.  The async tasks
            # will read this `limit` value from the dict and pass it as the
            # `max_records` param to the worker.  As records are received in the
            # main thread, the `limit` value will decrease until it is zero, at
            # which point the remaining async tasks will immediately return
            # with empty results.
            concurrency_ctl.metrics_dict['limit'] = limit

            # All default values need to be set prior to calling start().  This is
            # because there will be a delay when setting any shared value between
            # processes because the values are cached in each process.
            concurrency_ctl.start()

            while not is_completed:
                res = concurrency_ctl.output_queue.get()
                if res is not None:
                    task_result_count += 1
                    limit = PlannerConnection._calculate_limit(limit, res, is_pandas)
                    results.extend(res)
                    if task_result_count == task_count:
                        is_completed = True
                    concurrency_ctl.metrics_dict['limit'] = limit

            if not ignore_errors and concurrency_ctl.errors_queue.qsize():
                print('One or more errors occurred while processing this query:')
                total = concurrency_ctl.errors_queue.qsize()
                count = 1
                err = None
                while concurrency_ctl.errors_queue.qsize():
                    err = concurrency_ctl.errors_queue.get()
                    print('Error {}/{}:'.format(count, total))
                    print('{0}'.format(err.format_exception()))
                    count += 1
                raise err
        finally:
            concurrency_ctl.stop()

        return results

    @staticmethod
    def _ensure_serialization_support(plan):
        assert_numpy_installed()
        if not plan.supported_result_formats or \
                TRecordFormat.ColumnarNumPy not in plan.supported_result_formats:
            raise IOError("PyOkera requires the server to support the " +
                          "`ColumnarNumPy` serialization format. Please upgrade the " +
                          "server to at least 0.8.1.")

class WorkerConnection():
    """A connection to a CDAS worker. """

    def __init__(
        self, thrift_service, ctx, host, port, timeout, options,
        ssl=False, ca_cert=None):
        self.service = thrift_service
        self.ctx = ctx
        self.host = host
        self.port = port
        self.timeout = timeout
        self.options = options
        self.ssl = ssl
        self.ca_cert = ca_cert
        _log.debug('WorkerConnection(service=%s)', self.service)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the session and server connection."""
        _log.debug('Closing Worker connection')
        self.service.close()

    def _reconnect(self):
        _log.debug('Reconnecting to worker...')
        self.close()
        self.service = self.ctx._connect_worker_internal(
            self.host, self.port, self.timeout, self.options,
            self.ssl, self.ca_cert)
        _log.debug('Reconnected to worker')

    def __inject_ctx(self, t_params):
        _inject_ctx(t_params, self.ctx)

    @_rpc
    def get_protocol_version(self):
        """Returns the RPC API version of the server."""
        return self.service.client.GetProtocolVersion()

    @_rpc
    def set_application(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self._set_application_internal(name)

    def _set_application_internal(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self.service.client.SetApplication(name)

    def exec_task(
            self, task,
            max_records=None,
            output_format=TRecordFormat.ColumnarNumPy,
            fetch_size=None):
        """ Executes a task to begin scanning records.

        Parameters
        ----------
        task : obj
            Description of task. This is the result from the planner's plan() call.
        max_records: int, optional
            Maximum number of records to return for this task. Default is unlimited.
        output_format : TRecordFormat, optional
            Wire format to use for result records.
        fetch_size : int, optional
            Batch size to use when processing the request. If not specified, the
            server will be an value based on the query.

        Returns
        -------
        object
            Handle for this task. Used in subsequent API calls.
        object
            Schema for records returned from this task.
        """
        request = TExecTaskParams()
        request.task = task.task
        request.limit = max_records
        if fetch_size:
            request.fetch_size = fetch_size
        request.record_format = output_format
        self.__inject_ctx(request)
        result = self.service.client.ExecTask(request)
        return result.handle, result.schema

    def close_task(self, handle):
        """ Closes the task. """
        self.__inject_ctx(handle)
        self.service.client.CloseTask(handle)

    def fetch(self, handle):
        """ Fetch the next batch of records for this task. """
        request = TFetchParams()
        request.handle = handle
        self.__inject_ctx(request)
        return self.service.client.Fetch(request)

def _prepare_column(col):
    assert_numpy_installed()
    buf = col.data
    if isinstance(buf, str):
        buf = buf.encode()

    is_null = numpy.frombuffer(col.is_null.encode(), dtype=numpy.bool)
    return buf, is_null

if HAS_NUMPY:
    # Convert the column type to the number of bytes to
    # read and a human readable name
    _numpy_ttype_to_info = {
        TTypeId.BOOLEAN: (numpy.bool, 1, "BOOLEAN"),
        TTypeId.TINYINT: (numpy.int8, 1, "TINYINT"),
        TTypeId.SMALLINT: (numpy.int16, 2, "SMALLINT"),
        TTypeId.INT: (numpy.int32, 4, "INT"),
        TTypeId.BIGINT: (numpy.int64, 8, "BIGINT"),
        TTypeId.FLOAT: (numpy.float32, 4, "FLOAT"),
        TTypeId.DOUBLE: (numpy.float64, 8, "DOUBLE"),
    }

# As opposed to the NumPy variant of this, we return
# the is_null values as a native Python boolean array
def _prepare_column_native(schema_col, col):
    assert_numpy_installed()
    buf = col.data
    if isinstance(buf, str):
        buf = buf.encode()

    # Record type columns by definition can not have nulls in them, as
    # they will always be just an empty structure. This is a byproduct
    # of the underlying implementation, where those columns do not have
    # a corresponding data column.
    is_null = numpy.frombuffer(col.is_null.encode(), dtype=numpy.bool)
    if schema_col.type.type_id == TTypeId.RECORD:
        is_null = [False for x in is_null]
    return buf, is_null

def _get_column_skip(cols, idx):
    if not cols[idx].type.num_children:
        return 0
    else:
        skip_count = 0
        for child_idx in range(cols[idx].type.num_children):
            # For each child, we find out how many columns to skip for it
            # It does not account for itself, so we add a +1 to its return
            # skip value, and we always start a +1 offset relative to the current
            # index for the child index.
            skip_count += _get_column_skip(cols, idx + skip_count + 1) + 1
        return skip_count

# Converts a column to a native Python object, including support for
# complex types. Note that we have both a schema column index (col_idx)
# as well as a data column index (data_col_idx) to handle the complex
# type case.
# We also return the number of columns to skip, to handle the
# case where we processed some nested columns. This is accounted
# for differently for schema columns (where we expect the outer
# loop that calls us to do the base case incrementing, so we
# return 0 for primitive types), and the
# data column, which we return the number of columns we processed,
# which is at least 1.
def _convert_col_native(
    schema, cols, col_idx, data_col_idx, num_records,
    as_utf8, buf, is_null, ctx_tz, prefix=""):
    assert_numpy_installed()
    any_nulls = numpy.any(is_null)
    # Converts this column of data into the python objects
    if schema[col_idx].type.type_id == TTypeId.STRING or \
          schema[col_idx].type.type_id == TTypeId.VARCHAR:
        column = [None] * num_records
        offset = 0
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            length = numpy.frombuffer(
                buf[offset:offset+4], dtype=numpy.int32).item()
            offset += 4
            column[idx] = buf[offset:offset + length]
            if as_utf8:
                column[idx] = column[idx].decode('utf-8')
            offset += length
        return column, 1, any_nulls, 0, 1
    elif schema[col_idx].type.type_id == TTypeId.CHAR:
        offset = 0
        column = [None] * num_records
        length = schema[col_idx].type.len
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            column[idx] = buf[offset:offset + length]
            if as_utf8:
                column[idx] = column[idx].decode('utf-8')
            offset += length
        return column, 1, any_nulls, 0, 1
    elif (schema[col_idx].type.type_id == TTypeId.BOOLEAN or
            schema[col_idx].type.type_id == TTypeId.TINYINT or
            schema[col_idx].type.type_id == TTypeId.SMALLINT or
            schema[col_idx].type.type_id == TTypeId.INT or
            schema[col_idx].type.type_id == TTypeId.BIGINT or
            schema[col_idx].type.type_id == TTypeId.FLOAT or
            schema[col_idx].type.type_id == TTypeId.DOUBLE):
        offset = 0
        column = [None] * num_records
        dtype, length, type_name = _numpy_ttype_to_info[schema[col_idx].type.type_id]
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            column[idx] = numpy.frombuffer(
                buf[offset:offset+length], dtype=dtype).item()
            offset += length
        return column, 1, any_nulls, 0, 1
    elif schema[col_idx].type.type_id == TTypeId.DATE:
        column = [None] * num_records
        epoch = datetime.datetime(1970, 1, 1, 0, 0)
        length = 4
        offset = 0
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            days_offset = numpy.frombuffer(
                buf[offset:offset + length], dtype=numpy.int32).item()
            column[idx] = (epoch + datetime.timedelta(days_offset)).date()
            offset += length
        return column, 1, any_nulls, 0, 1
    elif schema[col_idx].type.type_id == TTypeId.TIMESTAMP_NANOS:
        column = [None] * num_records
        epoch = datetime.datetime(1970, 1, 1, 0, 0)
        ms_length = 8
        ns_length = 4
        offset = 0
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            ms_offset = numpy.frombuffer(
                buf[offset:offset + ms_length],
                dtype=numpy.int64).item()
            ns_offset = numpy.frombuffer(
                buf[offset + ms_length:offset + ms_length + ns_length],
                dtype=numpy.int32).item()
            column[idx] = datetime.datetime.fromtimestamp(ms_offset / 1000.0, ctx_tz)
            offset += ms_length + ns_length
        return column, 1, any_nulls, 0, 1
    elif schema[col_idx].type.type_id == TTypeId.DECIMAL:
        scale = -schema[col_idx].type.scale
        column = [None] * num_records
        values = None
        if schema[col_idx].type.precision <= 18:
            if schema[col_idx].type.precision <= 9:
                values = numpy.frombuffer(buf, dtype=numpy.int32).tolist()
            elif schema[col_idx].type.precision <= 18:
                values = numpy.frombuffer(buf, dtype=numpy.int64).tolist()
            value_idx = 0
            for idx in range(len(is_null)):
                if is_null[idx]:
                    continue
                column[idx] = Decimal(int(values[value_idx])).scaleb(scale)
                value_idx += 1
        else:
            # The integer part of the Decimal is stored as two back to back 64bit integers
            ctx = Context(schema[col_idx].type.precision)
            for i in range(0, num_records):
              if is_null[i]:
                continue
              # Parse the buffer in 16 byte increments (128 bit integer)
              start = i * 16
              end = start + 16
              buf_part = buf[start:end]
              intpart = int.from_bytes(buf_part, byteorder='little', signed=True)
              v = Decimal(intpart)
              column[i] = v.scaleb(scale)
        return column, 1, any_nulls, 0, 1
    elif schema[col_idx].type.type_id == TTypeId.ARRAY:
        column_lens = [0] * num_records
        column = [None] * num_records

        # First, we get the list of lengths for each array
        offset = 0
        length = 4
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            column_lens[idx] = numpy.frombuffer(
                buf[offset:offset + length], dtype=numpy.int32).item()
            offset += length

        # Get the column and buffers and null array for the item column
        item_col = cols[data_col_idx + 1]
        item_buf, item_is_nulls = _prepare_column_native(schema[col_idx + 1], item_col)

        # Convert recursively the the item column. Note that for the case
        # of arrays, both the (schema) col_idx and data_col_idx are
        # incremented, and the number of records is the sum of all
        # column lengths.
        values, _, _, skip_cols, skip_data_cols = _convert_col_native(
            schema, cols, col_idx + 1, data_col_idx + 1, sum(column_lens),
            as_utf8, item_buf, item_is_nulls, ctx_tz, prefix=(prefix+"    "))

        # Now that we have the individual array values combined into one
        # big array, we need to put them in columnar format.
        values_offset = 0
        for idx in range(len(column_lens)):
            if is_null[idx]:
                continue
            column_len = column_lens[idx]
            column[idx] = values[values_offset:values_offset + column_len]
            values_offset += column_len

        # For arrays, we skip however many columns we skipped recursively,
        # plus an extra one for the array column. This is true for
        # for both schema and data columns.
        return column, 1, any_nulls, skip_cols + 1, skip_data_cols + 1
    elif schema[col_idx].type.type_id == TTypeId.RECORD:
        # Initialize the final column to empty dictionaries, since structs cannot be
        # null (since they don't have a corresponding data column)
        any_nulls = False
        column = [None] * num_records
        for idx in range(len(column)):
            column[idx] = {}

        num_children = schema[col_idx].type.num_children
        child_idx = 0
        child_col_idx_offset = 0
        child_data_col_idx_offset = 0
        child_values = [None] * num_children
        skip_cols = 0

        # For each child, we need to get:
        #   * It's name, which comes from the schema
        #   * It's data column
        #   * The recursive conversion of values
        # We have to do quite a bit of bookkeeping here, because child column
        # might be incremented in "jumps" due to the recursive nature.
        # For example, if you have STRUCT<STRING,STRING>, then child_idx
        # and child_col_idx will be the same.
        # But if you have STRUCT<ARRAY<STRING>,STRING>, then they will
        # deviate as we have to account for skipping the ARRAY root column.
        #
        # Finally, note that the root STRUCT column does not have a corresponding
        # data column, which is why we index at off by one indices to the schema
        # and data column arrays.
        while child_idx < num_children:
            # Get the name of the child column and the child column itself
            child_col_name = schema[col_idx+child_col_idx_offset+1].name
            child_col = cols[data_col_idx+child_data_col_idx_offset]
            child_buf, child_is_nulls = _prepare_column_native(
                schema[col_idx+child_col_idx_offset+1], child_col)

            # Recursively convert the child column into its value.
            # Note that the number of records is the same as the root
            # struct, and also that we have to offset the col_idx
            # and data_col_idx appropriately.
            values, _, _, skip_cols, skip_data_cols = _convert_col_native(
                schema, cols,
                col_idx+child_col_idx_offset+1,
                data_col_idx+child_data_col_idx_offset,
                num_records,
                as_utf8, child_buf, child_is_nulls, ctx_tz, prefix=(prefix+"    "))

            # Store the resulting value - note that we have to store
            # the name as well so we can put it in the appropriate place
            # in the final dict.
            child_values[child_idx] = (child_col_name, values)

            # Increment the indices and offsets, taking into account
            # how many columns we need to skip. Note that for schema
            # columns we increment by an extra column, since we are
            # guaranteed to have processed at least one child column.
            # But for the data columns, we only skip by exactly what
            # the recursive call returned, since it is the true accounting
            # of how many data columns it processed.
            child_col_idx_offset += 1 + skip_cols
            child_data_col_idx_offset += skip_data_cols
            child_idx += 1

        # Finally, we reconstruct the columnar value.
        # The child values are always of length 1, so we
        # just do a straight iteration over them.
        for idx in range(len(column)):
            for child in child_values:
                name, values = child
                column[idx][name] = values[idx]

        return column, 1, any_nulls, child_col_idx_offset, child_data_col_idx_offset
    elif schema[col_idx].type.type_id == TTypeId.MAP:
        # We first calculate the lengths for each map
        column_lens = [0] * num_records
        offset = 0
        length = 4
        for idx in range(len(is_null)):
            if is_null[idx]:
                continue
            column_lens[idx] = numpy.frombuffer(
                buf[offset:offset + length], dtype=numpy.int32).item()
            offset += length

        # Similar to the array case, we need to get the key and value
        # columns (and their buffers), and then recursively compute them.
        # Note that the key one is always at offset 1 (and we depend on that
        # by not taking into account whether we need to skip any columns),
        # and the value one is always at offset 2, and the value can be complex,
        # so we need to take into account how many columns to skip.
        #
        # Also similar to arrays, the number of records is the sum of the map
        # lengths.
        key_col = cols[data_col_idx + 1]
        key_buf, key_is_nulls = _prepare_column_native(schema[col_idx+1], key_col)
        key_values, _, _, _, _ = _convert_col_native(
            schema, cols, col_idx + 1, data_col_idx + 1, sum(column_lens),
            as_utf8, key_buf, key_is_nulls, ctx_tz, prefix=(prefix+"  "))

        value_col = cols[data_col_idx + 2]
        value_buf, value_is_nulls = _prepare_column_native(schema[col_idx+2], value_col)
        value_values, _, _, skip_cols, skip_data_cols = _convert_col_native(
            schema, cols, col_idx + 2, data_col_idx + 2, sum(column_lens),
            as_utf8, value_buf, value_is_nulls, ctx_tz, prefix=(prefix+"  "))

        # Construct the final columnar map. Since the maps
        # are of variable lengths, we need to maintain where
        # we are in indexing the combined array of maps, so
        # that we can slice just the right piece.
        column = [None] * num_records
        map_offset = 0
        for idx in range(len(column_lens)):
            if is_null[idx]:
                continue
            column_len = column_lens[idx]
            curr_keys = key_values[map_offset:map_offset + column_len]
            curr_values = value_values[map_offset:map_offset + column_len]
            column[idx] = dict(zip(curr_keys, curr_values))
            map_offset += column_len

        # For maps, we skip however many columns we skipped recursively,
        # plus an extra two for the key and value columns. This is true for
        # for both schema and data columns.
        return column, 1, any_nulls, skip_cols + 2, skip_data_cols + 2
    else:
        raise RuntimeError(
            "Unsupported type: %s" % (
                TTypeId._VALUES_TO_NAMES[schema[col_idx].type.type_id]
            ))

def _convert_col(schema, cols, col_idx, num_records, as_utf8, buf, is_null, ctx_tz):
    assert_numpy_installed()
    any_nulls = numpy.any(is_null)
    # Converts this column of data into the python objects
    if schema[col_idx].type.type_id == TTypeId.STRING or \
          schema[col_idx].type.type_id == TTypeId.VARCHAR:
        off = 4 * num_records
        column = [numpy.nan] * num_records
        lens = numpy.frombuffer(buf[0: off], dtype=numpy.int32)
        if any_nulls:
            for i in range(0, num_records):
                if not is_null[i]:
                    length = lens[i]
                    column[i] = buf[off:off + length]
                    if as_utf8:
                        column[i] = column[i].decode('utf-8')
                    off += length
        else:
            for i in range(0, num_records):
                length = lens[i]
                column[i] = buf[off:off + length]
                if as_utf8:
                    column[i] = column[i].decode('utf-8')
                off += length
        if as_utf8:
            return column, 1, any_nulls
        else:
            return numpy.array(column, dtype=object), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.CHAR:
        off = 0
        column = [numpy.nan] * num_records
        length = schema[col_idx].type.len
        # Even if there are nulls, CHAR(n) is special
        # and puts in null bytes for the rows that
        # are null. So we need to skip those properly
        for i in range(0, num_records):
            if not is_null[i]:
                column[i] = buf[off:off + length]
            off += length
        if as_utf8:
            # Convert each individual char value to UTF8
            return [c.decode('utf-8') if isinstance(c, bytes) else c for c in column], 1, any_nulls
        else:
            return numpy.array(column, dtype=object), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.BOOLEAN:
        return numpy.frombuffer(buf, dtype=numpy.bool), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.TINYINT:
        return numpy.frombuffer(buf, dtype=numpy.int8), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.SMALLINT:
        return numpy.frombuffer(buf, dtype=numpy.int16), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.INT:
        return numpy.frombuffer(buf, dtype=numpy.int32), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.BIGINT:
        return numpy.frombuffer(buf, dtype=numpy.int64), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.FLOAT:
        return numpy.frombuffer(buf, dtype=numpy.float32), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.DOUBLE:
        return numpy.frombuffer(buf, dtype=numpy.float64), 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.DATE:
        days = numpy.frombuffer(buf, dtype=numpy.int32)
        column = [numpy.nan] * num_records
        epoch = datetime.datetime(1970, 1, 1, 0, 0)
        for i in range(0, num_records):
            if is_null[i]:
                continue
            column[i] = (epoch + datetime.timedelta(int(days[i]))).date()
        return column, 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.TIMESTAMP_NANOS:
        dt = numpy.dtype([('millis', numpy.int64), ('nanos', numpy.int32)])
        values = numpy.frombuffer(buf, dtype=dt)
        millis = values['millis']
        column = [numpy.nan] * num_records
        for i in range(0, num_records):
            if not is_null[i]:
                # TODO: use nanos?
                column[i] = datetime.datetime.fromtimestamp(millis[i] / 1000.0, ctx_tz)
        return column, 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.DECIMAL:
        column = [numpy.nan] * num_records
        scale = -schema[col_idx].type.scale
        if schema[col_idx].type.precision <= 18:
          if schema[col_idx].type.precision <= 9:
              values = numpy.frombuffer(buf, dtype=numpy.int32)
          elif schema[col_idx].type.precision <= 18:
              values = numpy.frombuffer(buf, dtype=numpy.int64)
          for i in range(0, num_records):
              if not is_null[i]:
                  column[i] = Decimal(int(values[i])).scaleb(scale)
        else:
            # The integer part of the Decimal is stored as two back to back 64bit integers
            ctx = Context(schema[col_idx].type.precision)
            for i in range(0, num_records):
              if is_null[i]:
                continue
              # Parse the buffer in 16 byte increments (128 bit integer)
              start = i * 16
              end = start + 16
              buf_part = buf[start:end]
              intpart = int.from_bytes(buf_part, byteorder='little', signed=True)
              v = Decimal(intpart)
              column[i] = v.scaleb(scale)
        return column, 1, any_nulls
    elif schema[col_idx].type.type_id == TTypeId.ARRAY:
        raise RuntimeError(
            "Unsupported type: " + TTypeId._VALUES_TO_NAMES[schema[col_idx].type.type_id])
    else:
        raise RuntimeError(
            "Unsupported type: " + TTypeId._VALUES_TO_NAMES[schema[col_idx].type.type_id])

def _columnar_batch_to_python(schema, columnar_records, num_records,
                              ctx_tz=pytz.utc, strings_as_utf8=False,
                              output_format=TRecordFormat.ColumnarNumPy):
    assert_numpy_installed()
    # Issues with numpy, thrift and this function being perf optimized
    # pylint: disable=no-member
    # pylint: disable=protected-access
    # pylint: disable=too-many-locals
    cols = columnar_records.cols

    # Things we will return.
    col_names = []

    # Checks if any of the values in this batch are null. Handling NULL can be
    # noticeably slower, so skip it in bulk if possible.
    any_nulls = []
    is_nulls = [None] * len(cols)
    data = [None] * len(cols)

    # For each column seen, the index to append to it. Empty means nothing to append.
    # The planner does not need to generate unique column names in all cases. e.g.
    # 'select c1, c1 from t' will generate two columns called 'c1'. We need to dedup
    # here as we put the columns in a dictionary.
    # In this case we will name the second "c1_2"
    col_names_dedup = {}

    # Go over each column and convert the binary data to python objects. This is very
    # perf sensitive.
    result_idx = 0
    col_idx = 0

    # If the nested_cols are set, we want to use those, as they provide
    # the non-flattened version for structs.
    schema_cols = schema.nested_cols or schema.cols

    data_col_idx = 0
    while col_idx < len(schema_cols):
        name = schema_cols[col_idx].name
        if name not in col_names_dedup:
            col_names_dedup[name] = 2
        else:
            # Keep resolving to dedup
            while name in col_names_dedup:
                idx = col_names_dedup[name]
                col_names_dedup[name] = idx + 1
                name += '_' + str(idx)
        col_names.append(name)

        val, idx, any_null = None, None, None
        if output_format == TRecordFormat.ColumnarNumPy:
            buf, is_null = _prepare_column(cols[col_idx])
            val, idx, any_null = _convert_col(schema_cols, cols, col_idx,
                num_records, strings_as_utf8, buf, is_null, ctx_tz)
        else:
            # In the Columnar format case, we are processing a complex
            # column, and so have to do some more fine-grained accounting
            # of which column we need to process.
            # `skip_cols` represents the number of *extra* schema columns
            # that need to be skipped, which is 0 for primitive types, and
            # zero or more for complex types.
            # `skip_data_cols` represents the total number of data columns
            # processed, and is at least 1 for all types.
            #
            # The outer loop here will do the base-case incrementing of moving
            # to the next schema column, but we have to do our own maintenance
            # of which data column we're on.
            buf, is_null = _prepare_column_native(
                schema_cols[col_idx], cols[data_col_idx])
            val, idx, any_null, skip_cols, skip_data_cols = _convert_col_native(
                schema_cols, cols, col_idx, data_col_idx,
                num_records, strings_as_utf8, buf, is_null, ctx_tz)

            # As part of processing complex types, we may have processed some extra
            # columns, so we need to skip over those.
            col_idx += skip_cols
            data_col_idx += skip_data_cols

        data[result_idx] = val
        is_nulls[result_idx] = is_null
        any_nulls.append(any_null)

        col_idx = col_idx + idx
        result_idx += 1
    return col_names, data, any_nulls, is_nulls

def context(application_name=None, namespace='okera', dialect=None, *args, **kwargs):
    """ Gets the top level context object to use pyokera.

    Parameters
    ----------
    application_name : str, optional
        Name of this application. Used for logging and diagnostics.
    namespace : str, optional
        Name of the Presto namespace to connect to (recordservice in 1.5, 'okera'
        in 2.0+). Default is 'okera'.
    dialect : str, optional
        Query dialect to use. Values are 'okera' or 'presto'.

    Returns
    -------
    OkeraContext
        Context object.

    Examples
    --------
    >>> import okera
    >>> ctx = okera.context()
    >>> ctx                                         # doctest: +ELLIPSIS
    <okera.odas.OkeraContext object at 0x...>
    """
    if not application_name:
        application_name = 'pyokera (%s)' % version()
    return OkeraContext(application_name, namespace, dialect=dialect, *args, **kwargs)

def version():
    """ Returns version string of this library. """
    from . import __version__
    return __version__

class ScanTask(BaseBackgroundTask):
  def __init__(
      self, name, ctx, plan_hosts, task, max_records, options, output_format,
      ssl=False, ca_cert=None):
    BaseBackgroundTask.__init__(self, "ScanTask.{0}".format(name))
    self.ctx = ctx
    self.plan_hosts = plan_hosts
    self.task = task
    self.max_records = max_records
    self.options = options
    self.errors = []
    self.output_format = output_format
    self.ssl = ssl
    self.ca_cert = ca_cert

  def __call__(self):
    results = []
    total = 0
    if self.max_records is not None and self.max_records <= 0:
        return results
    with self.ctx._connect_worker(self.plan_hosts, None, options=self.options,
                                  ssl=self.ssl, ca_cert=self.ca_cert) as worker:
        try:
            handle, schema = worker.exec_task(self.task, self.max_records,
                                              self.output_format)
            while True:
                fetch_result = worker.fetch(handle)
                assert fetch_result.record_format == self.output_format
                if fetch_result.num_records:
                    t_results = self.deserialize(schema,
                                                 fetch_result.columnar_records,
                                                 fetch_result.num_records,
                                                 self.output_format)
                    if t_results:
                        results.extend(t_results)

                    total += fetch_result.num_records

                if fetch_result.done or (self.max_records and total >= self.max_records):
                    break

        # Catch any exceptions that were raised and proxy them to the main process
        # via the errors queue.
        except OkeraWorkerException as owe:
            self.errors.append(owe)
        except Exception as ex:
            self.errors.append(OkeraWorkerException(ex))
        finally:
            try:
                worker.close_task(handle)
            except Exception as ex2:
                _log.warn("Failed to close task: " + str(ex2))
    return results

  def deserialize(self, schema, columnar_records, num_records, output_format):
    '''Abstract definition to deserialize the returned dataset'''
    raise Exception('Invalid invocation of an abstract function: ' +
                    'BaseBackgroundTask::deserialize')

class JsonScanTask(ScanTask):
  def __init__(self, ctx, plan_hosts, task, max_records, strings_as_utf8,
               output_format, decimal_type, no_numpy_types,
               ssl=False, ca_cert=None):
    ScanTask.__init__(
        self,
        "JsonScanTask",
        ctx,
        plan_hosts,
        task,
        max_records,
        None,
        output_format,
        ssl=ssl,
        ca_cert=ca_cert)
    self.__strings_as_utf8 = strings_as_utf8
    self.__decimal_type = decimal_type
    self.__no_numpy_types = no_numpy_types

  def __fixup_datum(self, datum):
    if isinstance(datum, Decimal) and self.__decimal_type:
        return self.__decimal_type(datum)
    if isinstance(datum, numpy.generic) and self.__no_numpy_types:
        # Convert from any numpy dtype to a python primitive.
        return numpy.asscalar(datum)
    if isinstance(datum, datetime.datetime):
        return datum.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    elif isinstance(datum, datetime.date):
        return datum.strftime('%Y-%m-%d')
    elif isinstance(datum, dict):
        for key, value in datum.items():
            datum[key] = self.__fixup_datum(value)
        return datum
    elif isinstance(datum, list):
        return [self.__fixup_datum(child) for child in datum]
    else:
        if isinstance(datum, bytes) and self.__strings_as_utf8:
            return datum.decode('utf-8')
        else:
            return datum

  def deserialize(self, schema, columnar_records, num_records, output_format):
    assert_numpy_installed()
    col_names, data, _, is_nulls = _columnar_batch_to_python(
        schema, columnar_records, num_records, self.ctx.get_timezone(),
        self.__strings_as_utf8, output_format)
    num_cols = len(col_names)
    result = []
    # Go over each row and construct a python array as a row
    for r in range(0, num_records):
        row = [None] * num_cols
        for c in range(0, num_cols):
            if is_nulls[c][r]:
                continue
            datum = data[c][r]
            row[c] = self.__fixup_datum(datum)
        result.append(dict(zip(col_names, row)))
    return result

class PandasScanTask(ScanTask):
  def __init__(
      self, ctx, plan_hosts, task, max_records,
      options, strings_as_utf8, output_format,
      ssl=False, ca_cert=None):
    ScanTask.__init__(
        self, "PandasScanTask", ctx, plan_hosts, task,
        max_records, options, output_format,
        ssl=ssl, ca_cert=ca_cert)
    self.__strings_as_utf8 = strings_as_utf8

  def deserialize(self, schema, columnar_records, num_records, output_format):
    assert_numpy_installed()
    assert_pandas_installed()
    result = []
    col_names, data, any_nulls, is_nulls = _columnar_batch_to_python(
        schema, columnar_records, num_records, self.ctx.get_timezone(),
        self.__strings_as_utf8, output_format)
    df = pandas.DataFrame(OrderedDict(zip(col_names, data)))
    if len(df):
        for c in range(0, len(col_names)):
            if not any_nulls[c] or df[col_names[c]].dtype == 'object':
                # Either no nulls, or objects are already handled.
                continue
            if isinstance(df[col_names[c]][0], str):
                continue
            # Fix up nulls, replace with nan
            # TODO: this is not the cheapest
            df[col_names[c]] = df[col_names[c]].where(~is_nulls[c], other=numpy.nan)
    result.append(df)
    return result

class OkeraFsStream():
    """ Wrapper object which behaves like a stream to send serialized results back
        in a byte stream based API. The API is intended to be compatible with a
        urllib stream object. """

    def __init__(self, planner, tbl, delimiter=',', quote_strings=True):
        assert_numpy_installed()
        assert_pandas_installed()
        # TODO: this needs to stream the result instead of all at once
        self.planner = planner
        self.tbl = tbl
        self.status = 200
        self.headers = {}
        self.data = planner.scan_as_pandas(
            tbl, max_task_count=1, strings_as_utf8=True).to_csv(
                None, header=False, index=False)

    def read(self, amt):
        return self.data.encode('utf-8')

Binary = memoryview
