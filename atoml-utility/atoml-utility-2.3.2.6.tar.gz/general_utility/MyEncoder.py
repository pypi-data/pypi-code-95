# -*- coding:utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, pd.DataFrame):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


class MyDecoder(json.JSONDecoder):
    
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, pd.DataFrame):
            return pd.read_json(obj)
        return json.JSONEncoder.default(self, obj)