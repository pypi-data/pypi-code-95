#coding:utf-8
from urllib.parse import urlencode
#from urllib.parse import parse_qs
import requests
import urllib
import json

def sj_pz():
    message = input("输入手机名称：")
    url="https://api.iyk0.com/sjzx/?msg={}".format(message)
    request=url
    #print(request)
    # 读取请求结果
    rep=requests.get(request) 
    # 请求结果转换成json格式
    repJson = rep.json()
    code = repJson.get('code')
    msg = repJson.get('msg')
    sums = repJson.get('sums')
    data = repJson.get('data')
    dic={'code':code,'msg':msg,'sum':sums,'data':data}
    print("\n",code)
    print("\n",msg)
    #print("\n",sums)
    #datas = data
    #print
    for i in data:
        print(f"\t手机品牌",i['手机品牌'])
        print("\t机型图片",i['机型图片'],"\n")
        print(f"\t上市时间",i['上市时间'],"\n")
        print(f"\t描述价格",i['描述价格'],"\n")
        print(f"\t手机配置",i['手机配置'],"\n")
            #print(i[:])
    return data
    return message