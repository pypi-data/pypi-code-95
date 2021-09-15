import jwt
from django.core.cache import caches
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from djrest_wrapper.exceptions.apis import AuthenticationFailedExp, DoesNotExistsExp
from django.conf import settings
from ..utils.jwt import JwtHelper


class JwtAuthentication(BaseAuthentication):
    def get_authorization_header(self, request):
        RAELM = settings.SHA_ACCOUNTS.get('JWT_AUTH_RAELM')
        auth_header = request.headers.get('Authorization', None)
        if auth_header != None:
            raelm, token = auth_header.split(' ')
            if raelm == RAELM:
                return token
            else:
                raise AuthenticationFailedExp(
                    f'raelm {raelm} is not a valid raelm')
        else:
            return None

    def get_decoded_jwt_token(self, token):
        token_is_valid = caches['token-cache'].get(token)
        if token_is_valid == 0:
            try:
                return JwtHelper.decode(token)
            except jwt.DecodeError as e:
                raise AuthenticationFailedExp(f'not a valid jwt token')
            except jwt.ExpiredSignatureError as e:
                raise AuthenticationFailedExp(f'not a valid jwt token')
        else:
            raise AuthenticationFailedExp(f'try to authenticate')

    def authenticate(self, request):
        token = self.get_authorization_header(request)
        if token != None:
            payload = self.get_decoded_jwt_token(token)
            try:
                user = get_user_model().objects.get(
                    id=payload.get('user').get('id'))
                if user.is_active == True:
                    return (user, None)
                else:
                    raise AuthenticationFailedExp(
                        f'your account is not active')
            except ObjectDoesNotExist as e:
                raise DoesNotExistsExp(
                    f'User {payload.get("user").get("id")} not found')
        else:
            return (AnonymousUser(), None)
