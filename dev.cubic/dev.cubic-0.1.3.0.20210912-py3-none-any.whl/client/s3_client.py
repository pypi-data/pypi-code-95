from cubic.rest import Rest


class S3Client:
    __rest: Rest
    __server: str
    __user: dict
    __token_key: str

    def __init__(self, server: str, user: dict, token_key: str):
        self.__server = server
        self.__user = user
        self.__token_key = token_key
        self.__rest = Rest(server=self.__server)

    def buckets(self):
        return self.__rest.post("s3/buckets", {
            'user': self.__user,
            'tokenKey': self.__token_key
        })

    def list(self, bucket_name: str, path: str = "", limit: int = 0, next_token: str = ""):
        return self.__rest.post("s3/list", {
            'user': self.__user,
            'tokenKey': self.__token_key,
            'bucketName': bucket_name,
            'path': path,
            'limit': limit,
            'nextToken': next_token
        })
