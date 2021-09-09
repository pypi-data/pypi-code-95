import requests


class Rest:
    __server: str

    def __init__(self, server: str):
        self.__server = server

    def post(self, endpoint: str, payload: dict, **kwargs):
        # print("payload", payload)
        response = requests.post(self.__server + "/" + endpoint, json=payload, **kwargs)
        response.raise_for_status()
        return response.json()
