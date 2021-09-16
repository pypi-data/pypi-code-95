# coding=gbk
import requests
import pyttsx3
def lt():
    while True:
        a=input("user:")
        if a == 'q':
            return
        url='https://api.ownthink.com/bot?appid=9ffcb5785ad9617bf4e64178ac64f7b1&spoken=%s'%a
        te=requests.get(url).json()
        data=te['data']['info']['text']
        print(data)
