#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from nokogiri.which_env import which_env
from pickle import Unpickler

class TQDMBytesReader(object):
    def __init__(self, fd, tqdm, total, desc=''):
        self.fd = fd
        self.tqdm = tqdm(total=total)
        self.tqdm.set_description(desc)
    def read(self, size=-1):
        bytes = self.fd.read(size)
        self.tqdm.update(len(bytes))
        return bytes
    def readline(self):
        bytes = self.fd.readline()
        self.tqdm.update(len(bytes))
        return bytes
    def __enter__(self):
        self.tqdm.__enter__()
        return self
    def __exit__(self, *args, **kwargs):
        return self.tqdm.__exit__(*args, **kwargs)

def tqdm_load(fname, tqdm=None, desc=''):
    if tqdm == None:
        if which_env() == which_env.JUPYTER:
            from tqdm.notebook import tqdm
        else:
            from tqdm import tqdm
    with open(fname, "rb") as fd:
         total = Path(fname).stat().st_size
         with TQDMBytesReader(fd, tqdm=tqdm, total=total, desc=desc) as pbfd:
             up = Unpickler(pbfd)
             obj = up.load()
    return obj