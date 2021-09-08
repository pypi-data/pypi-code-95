import codefast as cf
from flask import request

from dofast.security._hmac import certify_token

from .config import AUTH_KEY


def make_response(code: int, msg: str):
    return {'code': code, 'message': msg}


def authenticate_flask(app):
    app._tokenset = set()
    
    @app.before_request
    def _():
        try:
            token = request.args.get('token', '')
            if token in app._tokenset:
                return make_response(401, 'Authentication failed: token already used.')

            if certify_token(AUTH_KEY, token):
                app._tokenset.add(token)
                cf.info('Authentication SUCCESS.')
                return

            cf.error('Authentication failed' + str(request.data) +
                     str(request.json) + str(request.args))
            return make_response(401, 'Authentication failed.')
        except BaseException as e:
            cf.error('Authentication failed', str(e))
            return make_response(401, 'Authentication failed.')
