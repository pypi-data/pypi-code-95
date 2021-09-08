# -*- coding: utf-8 -*-
import os

from django.conf import settings


def get_easy_ctx():
    """Get the context-class that contains the credentials (secret-key
       and checkout-key) to communicate with Easy.
    """
    if hasattr(settings, 'EASY_CTX'):
        EASY_CTX = settings.EASY_CTX
    else:
        class CTX(Credentials):
            def __init__(self):
                super(CTX, self).__init__(
                    'abc123',
                    '123abc',
                    settings.EASY_ENCRYPTION_KEY
                )

        EASY_CTX = CTX()
    return EASY_CTX


class Credentials(object):
    """Credentials is the superclass defining the variables that should be
       stored securely as environment variables or similar.
    """
    def __init__(self, secret_key, checkout_key, encryption_key):
        self._secret_key = secret_key
        self._checkout_key = checkout_key
        self._encryption_key = encryption_key

    @property
    def secret_key(self):
        return self._secret_key

    @property
    def checkout_key(self):
        return self._checkout_key

    @property
    def encryption_key(self):
        return self._encryption_key


class EnvironmentCredentials(Credentials):
    """This class uses environment variables to store the credentials needed
       by the Easy-integration.
    """
    def __init__(self, secret_key, checkout_key):
        super().__init__(secret_key, checkout_key)

    @property
    def secret_key(self):
        return os.environ[self._secret_key]

    @property
    def checkout_key(self):
        return os.environ[self._checkout_key]

    @property
    def encryption_key(self):
        return os.environ[self._encryption_key]
