#coding:gbk
from urllib.parse import urlencode
import requests
import urllib
import json

def yq():
    message = input("输入城市：")
    url="https://api.iyk0.com/yq/?msg={}".format(message)
    request=url
    re=requests.get(request)
    rep = re.json()

    code = rep.get('code')
    msg = rep.get('msg')
    cxdq = rep.get('查询地区')
    mqqz = rep.get('目前确诊')
    swrs = rep.get('死亡人数')
    zyrs = rep.get('治愈人数')
    xzqz = rep.get('新增确诊')
    xcqz = rep.get('现存确诊')
    xcwzz = rep.get('现存无症状')
    time = rep.get('time')

    print("查询地区：",cxdq)
    print("\t目前确诊：",mqqz)
    print("\t死亡人数：",swrs)
    print("\t治愈人数：",zyrs)
    print("\t新增确诊：",xzqz)
    print("\t现存确诊：",xcqz)
    print("\t现存无症状：",xcwzz)
    print("\t更新时间：",time)
