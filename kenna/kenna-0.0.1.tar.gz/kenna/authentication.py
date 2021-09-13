from kenna.error import MissingCredentialsError, InvalidCredentialsError

import os

DEFAULT_API_KEY = os.getenv('KENNA_API_KEY')

API_KEY_LENGTH = 64


def validate_api_key(key: str) -> str:
    if not key:
        raise MissingCredentialsError("An API key is required")

    if len(key) != API_KEY_LENGTH:
        raise InvalidCredentialsError("API key must be {} characters in length - not {}".format(API_KEY_LENGTH, len(key)))

    return key
