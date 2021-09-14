#!/usr/bin/env python3
import re
import gzip
import random
import subprocess
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from .parsers import StopParsing


USERAGENTS = (
    "Dillo/3.0.5",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38",
    "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
    "Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 OPR/66.0.3515.72",
    "Links (2.22; Linux X86_64; GNU C; text)",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.4.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edge/86.0.622.51"
)
HEADERS = {
    "User-Agent": random.choice(USERAGENTS),
    "Accept": "text/html, application/xhtml+xml, image/jxr, */*",
    "Accept-Encoding": "gzip",
    "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7"
}


def isallow(url):
    match = re.search(r"(https://www\.(?:imdb|kinopoisk)\.(?:ru|com)/(?:film|title)/(?:tt)*(?:\d+)/)", url)
    if match:
        return True
    return False


def getd(data):
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return data


def getr(url):
    try:
        r = urlopen(Request(url, headers=HEADERS))
    except:
        return None
    return r


def geth(url):
    data = b""
    ua = HEADERS["User-Agent"]
    if "kinopoisk" in url:
        r = subprocess.run(f'wget -qO- -U "{ua}" {url}', shell=True,
            capture_output=True)
        if r.returncode == 0:
            data = r.stdout
    else:
        r = getr(url)
        if r:
            data = r.read()
    if data:
        data = getd(data)
    return data.decode("utf8", errors="ignore")


def parser_run(parser, data):
    try:
        parser.feed(data)
    except StopParsing:
        pass
    finally:
        parser.reset()
        parser.close()
    return parser


def titles_human(seasons):
    titles = {}
    for i, j in seasons.items():
        t = j[0]
        if len(j) > 1:
            t = "/".join(j)
        titles[i] = t
    return titles
