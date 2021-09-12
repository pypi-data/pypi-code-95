from decouple import config
from cubic.rest import Rest
from cubic.client import *


class Sdk:
    __server: str
    __system_id: str
    __access_key: str
    __user_id: str
    __token: str
    __targets: set

    __rest: Rest

    __user: dict
    __token_key: str

    __file_client = None
    __sqream_client = None
    __s3_client = None

    class SdkException(Exception):
        pass

    def __init__(self, user_id: str, token: str, targets: set):
        self.__server = config('CUBIC_SDK_SERVER')
        self.__system_id = config('CUBIC_SDK_SYSTEM_ID')
        self.__access_key = config('CUBIC_SDK_ACCESS_KEY')
        self.__user_id = user_id
        self.__token = token
        self.__targets = targets

        self.__rest = Rest(server=self.__server)

        # session
        session = self.__get_session(
            system_id=self.__system_id,
            access_key=self.__access_key,
            user_id=self.__user_id,
            token=self.__token,
            targets=self.__targets
        )
        # print(session)
        self.__user = session['user']
        self.__token_key = session['tokenKey']

        if "FILE" in self.__targets:
            self.__file_client = file_client.FileClient(server=self.__server, user=self.__user, token_key=self.__token_key)

        if "SQREAM" in self.__targets:
            self.__sqream_client = sqream_client.SqreamClient(
              server=self.__server,
              user=self.__user,
              token_key=self.__token_key
            )

        # if "S3" in self.__targets:
        #     self.__s3_client = s3_client.S3Client(server=self.__server, user=self.__user, token_key=self.__token_key)

    def info(self):
        print("SERVER:", self.__server)
        print("SYSTEM_ID:", self.__system_id)
        print("ACCESS_KEY:", self.__access_key)
        print("USER:", self.__user)
        print("SESSION_TOKEN_KEY:", self.__token_key)

    def __get_session(self, system_id: str, access_key: str, user_id: str, token: str, targets: set):
        return self.__rest.post("sessions", {
            'systemId': system_id,
            'accessKey': access_key,
            'userId': user_id,
            'token': token,
            'target': ','.join(targets)
        })

    def file(self):
        if self.__file_client is None:
            raise Sdk.SdkException("not init file client")

        return self.__file_client

    def sqream(self):
        if self.__sqream_client is None:
            raise Sdk.SdkException("not init sqream client")

        return self.__sqream_client

    def s3(self):
        if self.__s3_client is None:
            raise Sdk.SdkException("not init s3 client")

        return self.__s3_client
