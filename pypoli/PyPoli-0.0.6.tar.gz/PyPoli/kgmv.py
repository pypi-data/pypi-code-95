#coding:utf-8
from urllib.parse import urlencode
import requests
import urllib
import json

def gn():
    gm = input("歌名：")
    url="https://api.iyk0.com/kgmv/?msg={}&n=1".format(gm)
    request=url
    re=requests.get(request)
    rep = re.json()
    mv = rep.get('mvtitle')
    zz = rep.get('singer')
    img = rep.get('img')
    mv_dz = rep.get('link')
    #print(lis)
    print("\n歌名：",mv)
    print("作者：",zz)
    print("图片：",img)
    print("mv链接：",mv_dz,"\n")
