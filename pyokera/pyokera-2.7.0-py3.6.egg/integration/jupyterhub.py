import requests
import os
import pprint
import json

def get_okera_token():
    headers = {
        'User-Agent': 'okera-token-generator-loopback/jupyter',
        'Authorization': 'token ' + os.environ.get('JUPYTERHUB_API_TOKEN')
    }
    r = requests.get(os.environ.get('OKERA_TOKEN_GENERATOR_ENDPOINT'), headers=headers, verify=False)
    result = json.loads(r.content)
    return result.get('okera_token')