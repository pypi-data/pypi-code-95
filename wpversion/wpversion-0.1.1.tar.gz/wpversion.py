#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as Soup

from pathlib import Path
import sys

# This is a simple class to deal with version numbers
class Version:
    def __init__(self, v):
        self._v = []
        if v is not None:
            self._v = v.split('.')
    
    def compare(self, v2):
        i = 0
        while i < len(self._v) and i < len(v2._v):
            l = 0
            r = 0
            if (i < len(self._v)):
                l = int(self._v[i])
            if (i < len(v2._v)):
                r = int(v2._v[i])
            if (l < r):
                return -1
            if (l > r):
                return 1
            i = i + 1
        return 0

    def isdot(self):
        return len(self._v) > 1

    def __lt__(self, other):
        return self.compare(other) < 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __str__(self):
        return '.'.join(self._v)

def gethtml(url, retry = True):
    import urllib3
    urllib3.disable_warnings()
    try:
        html = requests.get(url, verify=False)
        if (html.status_code != 200):
            print('could not retrieve url {} X'.format(sys.argv[1]))
            return None
        html = html.content
    except Exception as e:
        if retry:
            html = gethtml("http://{}".format(url), False)
        else:
            print('could not retrieve url {}'.format(sys.argv[1]))
            return None
    return html

if __name__ == '__main__':
    url = None
    if len(sys.argv) > 1:
        url = sys.argv[1]

    if url is None:
        html = ''.join(sys.stdin.readlines())
    else:
        html = gethtml(sys.argv[1], True)

    if html is None:
        sys.exit(1)

    # First we try the generator tag, although it is usually hidden to enhance security
    soup = Soup(html, "html5lib")
    wpmeta = soup.select('meta[name="generator"]')
    if len(wpmeta) > 0:
        wpmeta = wpmeta[0]
        if wpmeta.has_attr('content'):
            print(wpmeta['content'])
    else:
        # Try another method, like guessing the versioning in the links
        from urllib.parse import urlparse
        links = soup.select('link[href*="?ver="]')
        guessed_version = None

        for link in links:
            href = link['href']
            o = urlparse(href)
            vars = o.query.split('&') 
            for var in vars:
                kv = var.split('=')
                version = None
                if kv[0] == 'ver' and len(kv) == 2:
                    version = kv[1]
                version = Version(version)
                
                if version.isdot():
                    if (guessed_version is None):
                        guessed_version = version
                    if (version > guessed_version):
                        version = guessed_version

        if guessed_version is not None:
            print(guessed_version)
