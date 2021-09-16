# coding:utf-8
# pip install baidu-aip

from play import playsound
from aip import AipSpeech
import requests

"""  APPID AK SK """
APP_ID = '24751927'
API_KEY = 'HwlctRCfNYLwwmqMMW6aZ3sM'
SECRET_KEY = '7CVbBVac9BRsMEiIIHNy7GcU2sRUnQrE'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

a = True
while a:
    a=input("user:")
    if a == 'q':
        a = False
        break
    url='https://api.ownthink.com/bot?appid=9ffcb5785ad9617bf4e64178ac64f7b1&spoken=%s'%a
    te=requests.get(url).json()
    data=te['data']['info']['text']
    print(data)

    PER = 4
    result = client.synthesis(data, 'zh', 1, {
        'vol': 10,  # 音量
        'spd': 30,  # 语速
        'pit': 40,  # 语调
        'per': PER,  # 0：女 1：男 3：逍遥 4：小萝莉
    })
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open('auido.mp3', 'wb') as f:
            f.write(result)
    
    p = playsound()
    voice_path = r"auido.mp3"
    p.play(voice_path)  # 播放
    p.close()  # 停止
