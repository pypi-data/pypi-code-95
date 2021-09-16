#coding:utf-8
from urllib.parse import urlencode
import requests
import urllib
import json

def jr_jr():
    url="https://api.iyk0.com/jr/"
    request=url
    re=requests.get(request)
    rep = re.json()
    code = rep.get('code')
    msg = rep.get('msg')
    today = rep.get('today')
    surplus = rep.get('surplus')
    tips = rep.get('tips')
    lis = {'code':code,'msg':msg,'today':today,'surplus':surplus,'tips':tips}
#print(lis)
    print(today)
    print(surplus)
    print(tips)
