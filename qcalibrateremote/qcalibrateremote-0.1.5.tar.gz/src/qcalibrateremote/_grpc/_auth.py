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


from base64 import b64encode, b64decode
from icecream import ic

GRPC_AUTH_HEADER = 'rpc-auth-header'

_ASCII = "ascii"

def split_key_and_secret(keyAndSecret):
    (client_key, client_secret) = b64decode(str.encode(keyAndSecret, _ASCII)).decode(_ASCII).split(':', 2)
    return client_key,client_secret

def combine_key_and_secret(client_key, client_secret):
    return b64encode(f"{client_key}:{client_secret}".encode(_ASCII)).decode(_ASCII)
