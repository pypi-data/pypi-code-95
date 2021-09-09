# -*- encoding: utf-8 -*-


class APIError(Exception):
    """ Base YesWeHack API Exception """


class InvalidResponse(APIError):
    """ Non json response"""

    def __init__(self):
        super().__init__("Non json response")


class ObjectNotFound(APIError):
    """ Ressource not found : 404 """

    def __init__(self):
        super().__init__("Ressource not found : 404")


class BadCredentials(APIError):
    """ Bad Credentials """

    def __init__(self):
        super().__init__("Bad Credentials")


class TOTPLoginEnabled(APIError):
    """ Totp login is enable and no totp code was given """

    def __init__(self):
        super().__init__("Totp login is enable and no totp code was given")


class JWTNotFound(APIError):
    """ JWT Token not found"""

    def __init__(self):
        super().__init__("JWT Token not found")


class JWTInvalid(APIError):
    """ Invalid JWT Token """

    def __init__(self):
        super().__init__("Invalid JWT Token")

class AccessDenied(APIError):
    """Access denied"""

    def __init__(self, msg):
        super().__init__(msg)

class OAuth2CodeError(APIError):
    """OAuth2 Authorization failed"""

    def __init__(self):
        super().__init__("OAuth2 Authorization failed")
