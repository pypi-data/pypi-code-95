#coding:utf-8
from urllib.parse import urlencode
import requests
import urllib
import json

def qq_JZ():
    message = int(input("输入你的QQ："))
    url="https://api.iyk0.com/qqgj/?qq={}".format(message)
    request=url
    re=requests.get(request)
    rep = re.json()
    code = rep.get('code')
    qqmm = rep.get('QQ号码')
    qqws = rep.get('QQ位数')
    qqjz = rep.get('QQ价值')
    gxsj = rep.get('更新时间')
    yqts = rep.get('友情提示')

    lis = {'code':code,'QQ号码':qqmm,'QQ位数':qqws,'QQ价值':qqjz,'更新时间':gxsj,'友情提示':yqts}
#print(lis)
    print(code)
    print('\nQQ号码：',qqmm)
    print('QQ位数：',qqws)
    print('QQ价值：',qqjz)
    print('更新时间：',gxsj)
    print('友情提示',yqts,'\n')
