from flask import current_app
from jsonclasses.jobject import JObject
from jwt import encode


def encode_jwt_token(operator: JObject) -> str:
    key = current_app.config['jsonclasses_encode_key']
    return encode({'operator': operator._id}, key, algorithm='HS256')
