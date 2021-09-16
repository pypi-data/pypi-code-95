#coding:gbk
from urllib.request import urlopen
from bs4 import BeautifulSoup as Be
import urllib.parse
import string

def tgrj():
    url = ("https://api.iyk0.com/tiangou/")
    urls = urllib.parse.quote(url,safe=string.printable)
    html = urlopen(f"{urls}")
    bs = Be(html,features="lxml")

    html_div = bs.findAll("body")
    print(html_div[0].get_text())