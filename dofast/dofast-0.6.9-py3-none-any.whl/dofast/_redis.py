#!/usr/bin/env python
import os
import random
import re
import sys
from collections import defaultdict
from functools import reduce

import codefast as cf
import joblib
import numpy as np
import pandas as pd
import redis


class MyRedis:
    def __init__(self):
        _host = 'localhost'
        _port = 6379
        _user = 'DOFAST_2021'
        _pwd = 'QroEiC6wyuCuEuN+XxVlIAYxXMM3O/ihQy8VdNgcdz0='
        self.r = redis.StrictRedis(host=_host, port=_port)

    def set(self, key: str, value: str) -> None:
        self.r.set(key, value)

    def get(self, key: str) -> str:
        return self.r.get(key)


redis_cli = MyRedis().r
