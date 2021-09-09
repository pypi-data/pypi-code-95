import json


class Serializer:

    count = 0

    def __init__(self):
        Serializer.count += 1

    @staticmethod
    def get_func_info(data):
        info = Serializer.deserialize(data)
        return info.get("functionName"), info.get("args"), info.get("kwargs"), info.get("instanceID")

    @staticmethod
    def serialize(obj):
        return json.dumps(obj).encode()

    @staticmethod
    def deserialize(data) -> dict:
        info = json.loads(data.decode())
        return info
