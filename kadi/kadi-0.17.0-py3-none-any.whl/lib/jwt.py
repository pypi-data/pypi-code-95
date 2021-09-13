# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from time import time

from flask import current_app
from jwt import decode
from jwt import encode
from jwt.exceptions import InvalidTokenError


def encode_jwt(payload, expires_in=None):
    """Encode a given payload inside a JSON web token.

    :param payload: The payload to encode as dictionary.
    :param expires_in: (optional) The time in seconds that the token should expire in.
    :return: The encoded JWT as string.
    """
    if expires_in is not None:
        payload["exp"] = time() + expires_in

    return encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_jwt(token):
    """Decode a given JSON web token.

    :param token: The token to decode as string.
    :return: The decoded payload dictionary or ``None`` if the token was invalid.
    """
    try:
        return decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except InvalidTokenError:
        return None
