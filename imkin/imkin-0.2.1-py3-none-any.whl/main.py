#!/usr/bin/env python3
import time
from collections import namedtuple
from urllib.parse import urljoin, quote
from .parsers import ImdbSearchParser, KinopoiskSearchParser, \
    KinopoiskParser, ImdbParser, KinopoiskSeriesParser, ImdbSeriesParser
from .utils import isallow, getd, getr, geth, parser_run, titles_human


def new(url):
    if not url.endswith("/"):
        url += "/"
    if not isallow(url):
        return None
    parser_film = ImdbParser
    if "kinopoisk" in url:
        parser_film = KinopoiskParser
    html = geth(url)
    p = parser_run(parser_film(), html)
    Film = namedtuple("Film", "title alternate year time age isfilm url")
    return Film(p.title, p.alternate, p.year, p.time, p.age, p.isfilm, url)


def gettitles(url):
    titles = {}
    if not url.endswith("/"):
        url += "/"
    if not isallow(url):
        return {}
    html = geth(urljoin(url, "episodes/"))
    parser_series = ImdbSeriesParser
    if "kinopoisk" in url:
        parser_series = KinopoiskSeriesParser
    p = parser_run(parser_series(), html)
    titles = titles_human(p.seasons)
    if "imdb" in url:
        uj = urljoin(url, "episodes?season=")
        try:
            season_last = int(p.season)
        except ValueError:
            return titles
        for i in range(1, season_last):
            time.sleep(1)
            html = geth(uj + str(i))
            if not html:
                continue
            ps = parser_run(parser_series(), html)
            titles.update(titles_human(ps.seasons))
    return titles


def search(word):
    if len(word) < 2:
        return []
    key = quote(word.lower())
    result = []
    for url, parser in (("https://www.imdb.com/find?q=", ImdbSearchParser),
      ("https://www.kinopoisk.ru/index.php?kp_query=", KinopoiskSearchParser)):
        r = getr(url + key)
        if not r:
            continue
        data = getd(r.read())
        html = data.decode("utf8", errors="ignore")
        if "kinopoisk" in url and ("film" in r.url or "series" in r.url):
                p = parser_run(KinopoiskParser(), html)
                name = f"{p.title} / {p.alternate} ({p.year})"
                found = [(name, r.url)]
        else:
            found = parser_run(parser(), html).list
            found = [(i, urljoin(url, j)) for i, j in found]
        result += found
    return result
