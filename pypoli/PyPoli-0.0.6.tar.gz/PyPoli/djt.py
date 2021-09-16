#coding:gbk
from urllib.parse import urlencode
import requests
import urllib
import json
def djt():
    url="https://api.iyk0.com/du/"
    request=url
    re=requests.get(request)
    rep = re.json()

    name = rep.get('name')
    avatar = rep.get('avatar')
    data = rep.get('data')

    print(name)
    print(avatar)
    print(data)
