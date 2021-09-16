# -*- coding: UTF-8 -*-
from urllib.parse import urlencode
#from urllib.parse import parse_qs
import requests
import urllib
import json

def gen():
    message = input("输入要查询的梗：")
    url="https://api.iyk0.com/gzs/?msg={}".format(message)
    #mes = json.dumps(me)
    #mes = json.dumps(me).encode("utf-8")
    #urllib.parse.urlencode(me).encode("utf-8")
    request=url
    # 读取请求结果
    rep=requests.get(request)
    # 请求结果转换成json格式
    repJson = rep.json()
    code = repJson.get('code')
    msg = repJson.get('msg')
    key = repJson.get('key')
    sums = repJson.get('sum')
    data = repJson.get('data')
    for i in data:
        print("查找资料为：")
        print("\n",i['title'])
