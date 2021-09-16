#coding:gbk
from urllib.parse import urlencode
import requests
import urllib

def rkl():
    url="https://api.iyk0.com/rkl/"
    request=url
    re=requests.get(request)
    rep = re.json()

    txt = rep.get('txt')
    print(txt)
