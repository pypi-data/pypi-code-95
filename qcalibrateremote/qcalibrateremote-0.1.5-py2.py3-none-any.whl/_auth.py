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

from grpc import AuthMetadataPlugin
from ._grpc import GRPC_AUTH_HEADER


class GrpcAuth(AuthMetadataPlugin):
    """Class implents a metadata plugin adding access token header as call level security

    Parameters
    ----------
    grpc : [type]
        [description]
    """
    def __init__(self, token):
        self._token = token

    def __call__(self, context, callback):
        callback(((GRPC_AUTH_HEADER, self._token),), None)
