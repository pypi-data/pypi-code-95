import jwt
from datetime import datetime
from django.conf import settings


class JwtHelper(object):
    @staticmethod
    def encode(payload:dict)->str:
        data={
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow()+settings.SHA_ACCOUNTS.get('JWT_ACCESS_TOKEN_EXP'),
        }
        for key,value in payload.items():
            data[key]=value
        token=jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
        return token

    @staticmethod
    def decode(token:str)->dict:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
        return payload