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
"""Network utils module."""

from importlib import import_module
from logging import getLogger
from time import sleep

from requests import Session as ReqSession
from requests.exceptions import ConnectionError as ReqConnectionErr, \
    Timeout

from .. import boltlight_pb2 as pb, settings as sett
from ..errors import Err
from .misc import disable_logger

LOGGER = getLogger(__name__)


def check_connection(lock):
    """Check if connection to node is successful by calling GetNodeInfo."""
    try:
        acquired = lock.acquire(blocking=False)
        if not acquired:
            return
        request = pb.GetNodeInfoRequest()
        module = import_module(f'...light_{sett.IMPLEMENTATION}', __name__)
        info = None
        LOGGER.info('Checking connection to %s node...', sett.IMPLEMENTATION)
        attempts = 0
        while not info:
            try:
                with disable_logger():
                    info = getattr(module, 'GetNodeInfo')(request,
                                                          FakeContext())
            except RuntimeError as err:
                LOGGER.error('Connection to LN node failed: %s',
                             str(err).strip())
            attempts += 1
            if not info:
                sleep(min(attempts * 2, 60 * 60))
                continue
            if info.identity_pubkey:
                LOGGER.info('Connection to node "%s" successful',
                            info.identity_pubkey)
            node_ver = module.get_node_version()
            if node_ver:
                LOGGER.info('Using %s version %s', sett.IMPLEMENTATION,
                            node_ver)
            else:
                LOGGER.info('Using %s', sett.IMPLEMENTATION)
    finally:
        if acquired:
            lock.release()


def check_req_params(context, request, *parameters):
    """Raise a missing_parameter error if parameter is missing from request."""
    for param in parameters:
        if not getattr(request, param):
            Err().missing_parameter(context, param)


def get_node_timeout(context, min_time=sett.IMPL_MIN_TIMEOUT):
    """Calculate timeout to use when calling LN node.

    Consider client's gRPC timeout if any.
    """
    node_timeout = min_time
    client_time = context.time_remaining()
    if client_time and client_time > node_timeout:
        node_timeout = client_time - sett.RESPONSE_RESERVED_TIME
    node_timeout = min(sett.IMPL_MAX_TIMEOUT, node_timeout)
    return node_timeout


def get_thread_timeout(context):
    """Calculate timeout for an async thread."""
    wait_time = sett.THREAD_TIMEOUT
    if context.time_remaining():
        # subtracting time to do the request and answer to the client
        wait_time = context.time_remaining() - sett.RESPONSE_RESERVED_TIME
    return max(wait_time, 0)


class FakeContext():  # pylint: disable=too-few-public-methods
    """Simulate a gRPC context.

    This is useful when dealing with methods that require a context but the one
    from the client request isn't available.
    """
    def __init__(self, timeout=None):
        self.timeout = timeout

    @staticmethod
    def abort(scode, msg):
        """Raise a runtime error."""
        assert scode
        raise RuntimeError(msg)

    def time_remaining(self):
        """Return the allowed time remaining for the RPC, in seconds.

        If self.timeout is set to None act as no deadline was specified for the
        RPC.
        """
        return self.timeout


class JSONRPCSession():  # pylint: disable=too-few-public-methods
    """Create and mantain a JSON-RPC session open."""
    def __init__(self, auth=None, headers=None, jsonrpc_ver='2.0'):
        self._session = ReqSession()
        self._auth = auth
        self._headers = {'accept': 'application/json'}
        if isinstance(headers, dict):
            self._headers = {**self._headers, **headers}
        self._jsonrpc_ver = jsonrpc_ver
        self._id_count = 0

    def call(self, context, data=None, url=None, timeout=None):
        """Make an RPC call using the opened session.

        Return the response message and a boolean to signal if the response
        contains an error.
        """
        self._id_count += 1
        if url is None:
            url = sett.RPC_URL
        if timeout is None:
            timeout = get_node_timeout(context)
        tries = sett.RPC_TRIES
        while True:
            try:
                response = self._session.post(url,
                                              data=data,
                                              auth=self._auth,
                                              headers=self._headers,
                                              timeout=(sett.RPC_CONN_TIMEOUT,
                                                       timeout))
                break
            except ReqConnectionErr:
                tries -= 1
                if tries == 0:
                    Err().node_error(context,
                                     'RPC call failed: max retries reached')
                LOGGER.debug(
                    'Connection failed, sleeping for %.1f secs (%d tries '
                    'left)', sett.RPC_SLEEP, tries)
                sleep(sett.RPC_SLEEP)
            except Timeout:
                Err().node_error(context, 'RPC call timed out')
        if response.status_code in (400, 403):
            # when password is wrong return Forbidden, True
            return response.reason, True
        if response.status_code not in (200, 500):
            Err().node_error(
                context,
                f'RPC call failed: {response.status_code} {response.reason}')
        json_response = {}
        try:
            json_response = response.json()
        except Exception:  # pylint: disable=broad-except
            Err().node_error(context, 'RPC response is not encoded in JSON')
        if 'error' in json_response and json_response['error'] is not None:
            err = json_response['error']
            if 'message' in err:
                err = json_response['error']['message']
            LOGGER.debug('RPC err: %s', err)
            return err, True
        if 'result' in json_response:
            LOGGER.debug('RPC res: %s', json_response['result'])
            return json_response['result'], False
        LOGGER.debug('RPC res: %s', json_response)
        return json_response, response.status_code == 500
