import logging
import json

import requests


def hello(endpoint):
    uri = f"http://{endpoint}/hello" # TODO: insecure -> https로 바꿀 것
    message = {"message": "What' your name?"}

    response = requests.get(uri, params=json.dumps(message))
    logging.info(response.json())