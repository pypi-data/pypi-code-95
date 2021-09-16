import requests
import json


def sharepoint():
    url = 'https://phoneguyapi.herokuapp.com/ssa/sharepoint'
    response = requests.get(url)
    json_data = json.loads(response.text)
    working = json_data['url']
    return working
