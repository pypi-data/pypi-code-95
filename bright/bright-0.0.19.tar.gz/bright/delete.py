import requests
import json


HEADER = {'Content-Type': 'application/json'}


def ret(response):
    if isinstance(response, dict):
        return json.dumps(response, sort_keys=True, indent=4)
    else:
        return response


def send(url, data={}, headers=HEADER):
    response = requests.delete(url=url, json=data, headers=headers)
    return ret(response)
