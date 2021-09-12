#!/usr/bin/env python
import json
import re
import sys

import codefast as cf
from codefast.utils import sleep

from .pipe import author


class FileDnContent:
    def __init__(self, file_dict, _dir) -> None:
        self._info = file_dict
        self._dir = _dir

    def __repr__(self) -> str:
        if 'size' in self._info:
            self._info['size'] = cf.fp.sizeof_fmt(self._info['size'])
        else:
            self._info['size'] = ''

        del self._info['icon']
        del self._info['urlencodedname']
        del self._info['modified']
        self._info['dir'] = self._dir
        ljustN = lambda e: e.ljust(30)
        return ''.join(map(ljustN, self._info.values()))


class QuickGet:
    def __init__(self) -> None:
        FILEDN_CODE = author.get('FILEDN_CODE')
        self.PREFIX = f'https://filedn.com/{FILEDN_CODE}'
        self.DIRS = {'apps', 'corpus'}
        proxies_file = cf.io.home() + '/.config/proxies.json'
        self.proxies = None
        if cf.io.exists(proxies_file):
            self.proxies = cf.js(proxies_file)
        cf.info('proxies set to', self.proxies)

    def _get_full_url(self, filename: str, dir: str) -> str:
        return f'{self.PREFIX}/{dir}/{filename}'

    def get(self, filename: str, dir: str) -> None:
        full_url = self._get_full_url(filename, dir)
        cf.net.download(full_url, name=filename, proxies=self.proxies)

    @property
    def list(self) -> None:
        from bs4 import BeautifulSoup
        _objects = []
        for _dir in self.DIRS:
            bs = cf.net.get(self.PREFIX + '/' + _dir,
                            proxies=self.proxies).text.replace('\n', '')
            pat = re.compile(r'directLinkData=(.*)\;')
            links = json.loads(pat.findall(bs, re.MULTILINE)[0])
            _objects += [FileDnContent(u, _dir) for u in links['content']]
        return _objects


def entry():
    from codefast.argparser import ArgParser
    ap = ArgParser()
    ap.input('l', 'list', description='Get object list')
    ap.parse()
    client = QuickGet()
    if ap.list:
        for u in client.list:
            print(u)
    elif len(sys.argv) >= 3:
        _item, _dir = sys.argv[1:3]
        client.get(_item, _dir)
