#coding:utf-8
from urllib.parse import urlencode
#from urllib.parse import parse_qs
import requests
import urllib
import json

def baidu_rs():
    url="https://api.iyk0.com/bdr/"
    request=url
    #print(request)
    # 读取请求结果
    rep=requests.get(request)
    # 请求结果转换成json格式
    repJson = rep.json()
    code = repJson.get('code')
    msg = repJson.get('msg')
    data = repJson.get('data')
    dic={'code':code,'msg':msg,'data':data}
    num = 0
    print("百度热搜榜\n")
    for i in data:
        num += 1
        print(f"\t第{num}热搜",i['title'])
        print("\t链接",i['url'],"\n")

