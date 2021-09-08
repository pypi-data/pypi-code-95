import codefast as cf
from flask import request

from dofast.security._hmac import certify_token

from .config import AUTH_KEY


def make_response(code: int, msg: str):
    return {'code': code, 'message': msg}


def authenticate_flask(app):
    @app.before_request
    def _():
        try:
            token = request.args.get('token', '')
            if certify_token(AUTH_KEY, token):
                cf.info('Authentication SUCCESS.')
                return
            cf.error('Authentication failed' + str(request.data) +
                     str(request.json) + str(request.args))
            return make_response(401, 'Authentication failed.')
        except BaseException as e:
            cf.error('Authentication failed', str(e))
            return make_response(401, 'Authentication failed.')
