# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

# pylint: disable=unused-import

""" Utilities for using thrift, including SASl support. """

# Originally copied from the Cloudera thrift-sasl repo
# https://github.com/cloudera/thrift_sasl/tree/master/thrift_sasl

from __future__ import absolute_import

import getpass
from io import BytesIO as BufferIO
import struct

from thriftpy2.thrift import TClient
from thriftpy2.protocol.binary import TBinaryProtocol  # noqa
from thriftpy2.transport import TSocket, TTransportException, TTransportBase # noqa
from thriftpy2.transport.base import readall # noqa
from thriftpy2.transport.buffered import TBufferedTransport  # noqa

from okera._pure_sasl_client import SASLClient
from okera._util import get_logger_and_init_null
from okera._util import to_bytes

PlannerClient = TClient
WorkerClient = TClient

# Message returned by socket layer when it returns zero bytes
SOCKET_READ_ZERO = "TSocket read 0 bytes"
# Message returned by server if client is kerberized but server is not
KERBEROS_NOT_ENABLED_MSG = 'Unsupported mechanism type GSSAPI'

log = get_logger_and_init_null(__name__)

def create_socket(host, port, timeout, use_ssl, ca_cert):
    sock = get_socket(host, port, use_ssl, ca_cert)
    if timeout is not None:
        timeout = timeout * 1000.  # TSocket expects millis
    sock.set_timeout(timeout)
    return sock

def get_socket(host, port, use_ssl, ca_cert):
    log.debug('get_socket: host=%s port=%s use_ssl=%s ca_cert=%s',
              host, port, use_ssl, ca_cert)
    if not use_ssl:
        return TSocket(host, port)

    from thriftpy2.transport.sslsocket import TSSLSocket
    if ca_cert is None:
        return TSSLSocket(host, port, validate=False)
    return TSSLSocket(host, port, validate=True, cafile=ca_cert)

def get_transport(socket, host, auth_mechanism='NOSASL', service_name=None,
                  user=None, password=None, token=None, host_override=None):
    """
    Creates a new Thrift Transport using the specified auth_mechanism.
    Supported auth_mechanisms are:
    -  None or 'NOSASL' - returns simple buffered transport (default)
    - 'PLAIN'  - returns a SASL transport with the PLAIN mechanism
    - 'GSSAPI' - returns a SASL transport with the GSSAPI mechanism
    - 'DIGEST-MD5' - returns a SASL transport with the DIGEST-MD5 mechanism
    """
    log.debug('get_transport: socket=%s host=%s service_name=%s '
              'auth_mechanism=%s user=%s password=fuggetaboutit '
              'host_override=%s', socket, host, service_name,
              auth_mechanism, user, host_override)

    if auth_mechanism == 'NOSASL':
        return TBufferedTransport(socket)

    # Set defaults for PLAIN SASL / LDAP connections.
    if auth_mechanism in ['LDAP', 'PLAIN']:
        if user is None:
            user = getpass.getuser()
            log.debug('get_transport: user=%s', user)
        if password is None:
            if auth_mechanism == 'LDAP':
                password = ''
            else:
                # PLAIN always requires a password for HS2.
                password = 'password'
            log.debug('get_transport: password=%s', password)
    elif auth_mechanism in ['DIGEST-MD5']:
        # The service is always 'cerebro'.
        service_name = 'cerebro'
        token_parts = token.split('.')
        if len(token_parts) == 2:
          # Okera token - need to escape it
          user = token_parts[0].replace('_', '/').replace('$', '=').replace('-', '+')
          password = token_parts[1].replace('_', '/').replace('$', '=').replace('-', '+')
        else:
          # JWT token: password is always 'cerebro'. The token is the credential.
          user = token
          password = 'cerebro'
    if host_override:
        host = host_override

    def sasl_factory():
        return SASLClient(host, username=user, password=password, service=service_name)

    return TSaslClientTransport(sasl_factory, auth_mechanism, socket)

# pylint: disable=too-many-instance-attributes
class TSaslClientTransport(TTransportBase):
    START = 1
    OK = 2
    BAD = 3
    ERROR = 4
    COMPLETE = 5

    def __init__(self, sasl_client_factory, mechanism, trans):
        """
        @param sasl_client_factory: a callable that returns a new sasl.Client object
        @param mechanism: the SASL mechanism (e.g. "GSSAPI")
        @param trans: the underlying transport over which to communicate.
        """
        self._trans = trans
        self.sasl_client_factory = sasl_client_factory
        self.sasl = None
        self.mechanism = mechanism
        self.__wbuf = BufferIO()
        self.__rbuf = BufferIO()
        self.opened = False
        self.encode = None

    def isOpen(self):
        return self._trans.isOpen()

    def is_open(self):
        return self.isOpen()

    def open(self):
        if not self._trans.is_open():
            self._trans.open()

        if self.sasl is not None:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message="Already open!")
        self.sasl = self.sasl_client_factory()

        self.sasl.choose_mechanism([self.mechanism], allow_anonymous=False)
        initial_response = self.sasl.process()

        # Send initial response
        self._send_message(self.START, self.mechanism)
        if initial_response:
            self._send_message(self.OK, initial_response)

        # SASL negotiation loop
        while True:
            status, payload = self._recv_sasl_message()
            if status not in (self.OK, self.COMPLETE):
                raise TTransportException(
                    type=TTransportException.NOT_OPEN,
                    message=("Bad status: %d (%s)" % (status, payload)))
            if status == self.COMPLETE:
                break
            response = self.sasl.process(payload)
            self._send_message(self.OK, response)

    def _send_message(self, status, body):
        if body:
          body_bytes = to_bytes(body)
          header = struct.pack(">BI", status, len(body_bytes))
          self._trans.write(header + body_bytes)
        else:
          header = struct.pack(">BI", status, 0)
          self._trans.write(header)
        self._trans.flush()

    def _recv_sasl_message(self):
        header = readall(self._trans.read, 5)
        status, length = struct.unpack(">BI", header)
        if length > 0:
            return status, readall(self._trans.read, length)
        return status, ""

    def write(self, data):
        self.__wbuf.write(data)

    def flush(self):
        buffer = self.__wbuf.getvalue()
        self._flushPlain(buffer)
        self._trans.flush()
        self.__wbuf = BufferIO()

    def _flushEncoded(self, buffer):
        # sasl.ecnode() does the encoding and adds the length header, so nothing
        # to do but call it and write the result.
        success, encoded = self.sasl.encode(buffer)
        if not success:
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message=self.sasl.getError())
        self._trans.write(encoded)

    def _flushPlain(self, buffer):
        # When we have QOP of auth, sasl.encode() will pass the input to the output
        # but won't put a length header, so we have to do that.

        # Note stolen from TFramedTransport:
        # N.B.: Doing this string concatenation is WAY cheaper than making
        # two separate calls to the underlying socket object. Socket writes in
        # Python turn out to be REALLY expensive, but it seems to do a pretty
        # good job of managing string buffer operations without excessive copies
        self._trans.write(struct.pack(">I", len(buffer)) + buffer)

    def _read(self, sz):
        ret = self.__rbuf.read(sz)
        if len(ret) == sz:
            return ret

        self._read_frame()
        return ret + self.__rbuf.read(sz - len(ret))

    def _read_frame(self):
        header = readall(self._trans.read, 4)
        (length,) = struct.unpack(">I", header)
        if self.encode:
            # If the frames are encoded (i.e. you're using a QOP of auth-int or
            # auth-conf), then make sure to include the header in the bytes you send to
            # sasl.decode()
            encoded = header + readall(self._trans.read, length)
            success, decoded = self.sasl.decode(encoded)
            if not success:
                raise TTransportException(type=TTransportException.UNKNOWN,
                                          message=self.sasl.getError())
        else:
            # If the frames are not encoded, just pass it through
            decoded = readall(self._trans.read, length)

        if length != len(decoded):
            raise TTransportException(
                type=TTransportException.NOT_OPEN,
                message="Short read. Expecting to read %d byte but only read %d bytes." %
                (length, len(decoded)))

        self.__rbuf = BufferIO(decoded)

    def close(self):
        self._trans.close()
        self.sasl = None

    # Implement the CReadableTransport interface.
    # Stolen shamelessly from TFramedTransport
    @property
    def cstringio_buf(self):
        return self.__rbuf

    def cstringio_refill(self, prefix, reqlen):
        # self.__rbuf will already be empty here because fastbinary doesn't
        # ask for a refill until the previous buffer is empty.  Therefore,
        # we can start reading new frames immediately.
        while len(prefix) < reqlen:
            self._read_frame()
            prefix += self.__rbuf.getvalue()
        self.__rbuf = BufferIO(prefix)
        return self.__rbuf
