#!/usr/bin/env python
import random
import re, os, sys, joblib,json
import pandas as pd
import numpy as np
from collections import defaultdict
from functools import reduce
import codefast as cf

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
        ljustN = lambda e: e.ljust(20)
        _values = sorted(list(self._info.values()), key=len)
        return ''.join(map(ljustN, _values))



class SyncFile:
    def __init__(self) -> None:
        self.PREFIX = f'https://filedn.com/lCdtpv3siVybVynPcgXgnPm/snc'
        proxies_file = cf.io.home() + '/.config/proxies.json'
        self.proxies = None
        if cf.io.exists(proxies_file):
            self.proxies = cf.js(proxies_file)
        cf.info('proxies set to', self.proxies)

    def _get_full_url(self, filename: str) -> str:
        return f'{self.PREFIX}/{filename}'

    def sync(self) -> None:
        '''download all files from snc/'''
        for obj in self.list:
            fn = obj._info['name']
            full_url = self._get_full_url(fn)
            cf.info(f'Syncing {fn}')
            cf.net.download(full_url, name=f'/tmp/{fn}', proxies=self.proxies)

    @property
    def list(self) -> None:
        _objects = []
        bs = cf.net.get(self.PREFIX,
                        proxies=self.proxies).text.replace('\n', '')
        pat = re.compile(r'directLinkData=(.*)\;')
        links = json.loads(pat.findall(bs, re.MULTILINE)[0])
        _objects += [FileDnContent(u, 'snc') for u in links['content']]
        return _objects
