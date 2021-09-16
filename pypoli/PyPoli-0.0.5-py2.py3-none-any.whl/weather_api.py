#coding:utf-8
from urllib.parse import urlencode
import requests
import urllib
import json

def weather_api():
    message = str(input("要查询的城市："))

    url="https://api.iyk0.com/tq/?city={}".format(message)
    request=url
    re=requests.get(request)
    rep = re.json()

    code = rep.get('code')
    msg = rep.get('msg')
    city = rep.get('city')
    up = rep.get('update_time')
    wea = rep.get('wea')
    wea_img = rep.get('wea_img')
    tem = rep.get('tem')
    tem_day = rep.get('tem_day')
    tem_night = rep.get('tem_night')
    win = rep.get('win')
    win_speed = rep.get('win_speed')
    win_meter = rep.get('win_meter')
    air = rep.get('air')
    time = rep.get('time')
    print('\n城市名字：',city)
    print('更新时间：',up)
    print('天气情况：',wea)
    print('时实温度：',tem)
    print('高温：',tem_day)
    print('低温：',tem_night)
    print('风向：',win)
    print('风力等：',win_speed)
    print('风速：',win_meter)
    print('空气质量：',air)
    print('当天日期，星期：',time,'\n')
    lis = {'code':code,
           'msg':msg,
           'city':city,
           'update_time':up,
           'wea':wea,
           'wea_img':wea_img,
           'tem':tem,
           'tem_day':tem_day,
           'win':win,
           'win_speed':win_speed,
           'win_meter':win_meter,
           'air':air,
           'time':time,
           }
#print(lis)
