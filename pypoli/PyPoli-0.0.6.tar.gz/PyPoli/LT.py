#coding:gbk
from urllib.request import urlopen
from bs4 import BeautifulSoup as Be
import urllib.parse
import string

def LT():
    while True:
        message = input("USER:")
        if message == 'q':
            print("下次再聊！")
            return
        url = ("https://api.iyk0.com/liaotian/?msg={}").format(message)
        urls = urllib.parse.quote(url,safe=string.printable)
        html = urlopen(f"{urls}")
        bs = Be(html,features="lxml")

        html_div = bs.findAll("body")
        print(html_div[0].get_text())

