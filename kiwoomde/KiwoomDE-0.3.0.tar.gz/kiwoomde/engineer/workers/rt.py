# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
import re
import threading
from time import sleep


import pandas as pd


from idebug import *
from kiwoomde.engineer.database import *


from kiwoomde.engineer.models import *


class RealtypeTradingSourceWorker(BaseClass):
    # Realtype(주식당일거래원)-Data ==> TradingSource-Data 재구조화해서 저장하는 스레드
    # 종목 1개당 하나의 Worker 가 실행된다
    # 최근 업데이트된 시간 이후의 실시간데이타를 1분마다 읽어와서 재구조화->저장.
    # **cid: RealtimeModel 은 종목기반으로 DB저장되므로, 스레드도 종목하나당 하나씩 생성된다
    # document --> data(d={name:'키움증권'}) 방식으로 변환하라
    # _loop_interval: 60초 마다 1-cycle 을 돈다

    @funcIdentity
    def __init__(self, collmode='real', **cid):
        if len(cid) == 0: raise
        self.srcmodel = RealtypeModel('주식당일거래원', collmode, **cid)
        self.dstmodel = RealtypeTradingSource(collmode, **cid)
        self._last_dt = self.dstmodel.get_last_dt()
        self._loop_interval = 60

    def _load_data(self):
        # 가장 최근 시간보다 더 최근의 시간에 해당하는 실시간데이타만 불러온다
        filter = None if self._last_dt is None else {'dt':{'$gt':self._last_dt}}
        data = self.srcmodel.load(filter, sort=[('dt',ASCENDING)])
        return self.srcmodel.translate(data)

    def _work(self):
        # 주식당일거래원(=realtype) 실시간데이타 로딩
        data = self._load_data()

        for datum in data:
            # RealtypeModel-Data 를 재해석
            newdata = self.dstmodel._restructure_realdata(datum)
            # DB저장
            self.dstmodel.insert_many(newdata)
            # 가장 최근 시간을 계속 업데이트
            self._last_dt = datum['dt']

        logger.info(f'Done. len_data: {len(data)}')

    def _work_thread(self):
        while 1:
            self._work()
            logger.info(f"{self._loop_interval}초 동안 대기 중~")
            sleep(self._loop_interval)

    @funcIdentity
    def run(self):
        t = threading.Thread(target=self._work_thread)
        t.start()
