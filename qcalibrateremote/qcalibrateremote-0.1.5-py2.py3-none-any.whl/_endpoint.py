#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from abc import ABC, abstractmethod
from typing import Union

import grpc

from ._auth import GrpcAuth
from ._grpc.qcalibrate_pb2_grpc import QCalibrateStub as ClientStub


def _bytes_or_read_file(bytes_or_file: Union[bytes, str]) -> bytes:
    if type(bytes_or_file) is str:
        with open(bytes_or_file, 'rb') as fh:
            return fh.read()
    elif type(bytes_or_file) is bytes:
        return bytes_or_file
    else:
        raise TypeError(f'Expected bytes or string, got {type(bytes_or_file)}')


class Endpoint(ABC):
    """Defines a service endpoint to connect to"""

    def __init__(
            self,
            host: str,
            port: int
    ) -> None:
        """Constructor

        Parameters
        ----------
        host : str
            endpoint host
        port : int
            enpoint port
        """

        super().__init__()
        self._host = host
        self._port = port

    def _get_target(self):
        return f"{self._host}:{self._port}"

    @abstractmethod
    def create_channel(self) -> grpc.Channel:
        """creates a client proxy to communicate with beckend, for internal use only """
        pass

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port


class EndpointSecureKey(Endpoint):
    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        ca_cert: Union[bytes, str] = None,
        compression: grpc.Compression = grpc.Compression.Deflate
    ) -> None:
        """Defines endpoint secured with TLS and a client key

        Parameters
        ----------
        host : str
            endpoint host
        port : int
            enpoint port
        token : str
            client authentication token
        ca_cert : Union[bytes, str], optional
            server CA certificate file content or certificate file name (.pem)
            used to verify server identity in case it uses a self-signed server certificate
            default None
        compression : grpc.Compression, optional
            selects compression algorithm, by default grpc.Compression.Deflate
        """

        super().__init__(host=host, port=port)

        self._ca_cert = _bytes_or_read_file(ca_cert) if ca_cert else None
        self._call_credentials = grpc.metadata_call_credentials(
            GrpcAuth(token=token)
        )
        self._compression = compression

    def create_channel(self) -> grpc.Channel:
        """Internal function to create a gRPC channle

        Returns
        -------
        grpc.Channel
            the created gRPC channel
        """

        credentials = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(self._ca_cert),
            self._call_credentials
        )

        channel = grpc.secure_channel(
            self._get_target(), credentials,
            compression=self._compression)

        return channel
