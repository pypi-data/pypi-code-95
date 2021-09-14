import requests
import json


HEADER = {'Content-Type': 'application/json'}


def ret(response):
    if isinstance(response, dict):
        return json.dumps(response, sort_keys=True, indent=4)
    else:
        return response


def send(url, params=None, headers=HEADER):
    response = requests.get(url=url, params=params, headers=headers)
    return ret(response)
