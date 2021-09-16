# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
import re


import pandas as pd


from idebug import *
from kiwoomde import *


from kiwoomdsc import stat
from kiwoomdsc.viewer import *


class KWModelBaseAnalyzer(BaseClass):
    # 컬렉션 데이타 모델 기반 베이스 분석클래스

    @funcIdentity
    def count_coluniquevalues(self, datamodel):
        return stat.count_coluniquevalues(datamodel)
