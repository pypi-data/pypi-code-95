#coding:gbk
from urllib.request import urlopen
from bs4 import BeautifulSoup as Be
import urllib.parse
import string

def twqh():
    url = ("https://api.iyk0.com/twqh/")
    urls = urllib.parse.quote(url,safe=string.printable)
    html = urlopen(f"{urls}")
    bs = Be(html,features="lxml")

    html_div = bs.findAll("body")
    print(html_div[0].get_text())
