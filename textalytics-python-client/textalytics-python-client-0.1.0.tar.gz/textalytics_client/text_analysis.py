import json

import requests
from textalytics_core.resources import TextInput


class Client():
    def __init__(self, service_base_url, username, password):
        self.service_base_url = service_base_url
        self.username = username
        self.password = password
        self.token()

    def token(self):
        data = {'username': self.username, 'password': self.password}
        token_response = requests.post(self.service_base_url + '/token', data = json.dumps(data))
        response_json = token_response.json()
        self.access_token = response_json["access_token"]
        self.token_type = response_json["token_type"]
        self.refresh_token = response_json["refresh_token"]

    def extract_entities(self, text_input: TextInput):
        if not self.access_token:
            raise Exception("not authorized!")
        if not text_input:
            raise Exception("input cannot be null or empty")

        headers = {'Authorization': self.token_type + " " + self.access_token}
        entities_response = requests.post(self.service_base_url + '/extract-entities',
                                          data = json.dumps(text_input.dict()),
                                          headers=headers)
        return entities_response
