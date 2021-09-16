#coding:gbk
from urllib.parse import urlencode
import requests
import urllib
import json

def chp():
    url="https://api.iyk0.com/chp/"
    request=url
    re=requests.get(request)
    rep = re.json()

    code = rep.get('code')
    txt = rep.get('txt')
    maxs = rep.get('max')
    print(f"\n{txt}\n")
    #print(f"{maxs}\n")
