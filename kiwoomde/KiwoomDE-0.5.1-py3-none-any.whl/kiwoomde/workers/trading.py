# -*- coding: utf-8 -*-
import re
import threading
from time import sleep
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *


from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.database import *
from kiwoomde.models import *


class TradingSourceRealDataWorker(BaseClass):
    # Realtype(주식당일거래원)-Data ==> TradingSource-Data 재구조화해서 저장하는 스레드
    # 종목 1개당 하나의 Worker 가 실행된다
    # 그러나, 다수의 거래원을 처리해야한다
    # RealtypeModel 로부터 데이터를 가져와서 재구조화해서 저장하는 함수를 포함
    # 최근 업데이트된 시간 이후의 실시간데이타를 1분마다 읽어와서 재구조화->저장.
    # **cid: RealtimeModel 은 종목기반으로 DB저장되므로, 스레드도 종목하나당 하나씩 생성된다
    # document --> data(d={name:'키움증권'}) 방식으로 변환하라
    # source: SourceName
    # loop_interval: 60초 마다 1-cycle 을 돈다

    @funcIdentity
    def __init__(self, collmode='real', **cid):
        if len(cid) == 0: raise
        self.RealtypeModel = RealtypeModel('주식당일거래원', collmode, **cid)
        self.SecurityInfo = SelectorModel('SecurityInfo')
        self._source_manager = {}
        self._setup_TradingSourceDict()
        self._setup_last_dt()
        self.loop_interval = 60

    def _setup_TradingSourceDict(self):
        sources = sorted(self.SecurityInfo.distinct('name'))
        for source in sources:
            tsrd = TradingSourceRealData(source, self.RealtypeModel.collmode)
            tsrd.switch_issue(name=self.RealtypeModel.name)
            self._source_manager.update({source:{'model':tsrd}})

    def _setup_last_dt(self):
        # TradingSourceRealData 에 저장된 가장 최근 dt 값을 설정
        for source, d in self._source_manager.items():
            tsrd = d['model']
            dts = tsrd.distinct('dt')
            last_dt = dts[-1].astimezone() if len(dts) > 0 else None
            d.update({'last_dt':last_dt})

    def _get_tsrd(self, source):
        return self._source_manager[source]['model']

    def _update_last_dt(self, source, dt):
        self._source_manager[source].update({'last_dt':dt})

    def _load_data(self, source):
        # 가장 최근 시간보다 더 최근의 시간에 해당하는 실시간데이타만 불러온다
        last_dt = self._source_manager[source]['last_dt']
        data = self.RealtypeModel.load({'dt':{'$gt':last_dt}}, sort=[('dt',ASCENDING)])
        return self.RealtypeModel.translate(data)

    def _restructure_realtypedata(self, d):
        # 주식당일거래원(=realtype) 실시간데이타를 재구조화

        # PartGubun('거래원리스트 추출')
        p = re.compile('^(매[수|도])거래원(\d)$')
        srcs = []
        for k,v in d.items():
            m = p.search(k)
            if m is not None:
                type = m.group(1)
                rank = m.group(2)
                srcs.append({'name':v, 'p':re.compile(f"^({type})거래원(.*)({rank})$")})

        df = pd.DataFrame(srcs)

        # PartGubun('재구조화된 data 생성')
        for k,v in d.items():
            for src in srcs:
                m = src['p'].search(k)
                if m is None:
                    pass
                else:
                    type = m.group(1)
                    info = m.group(2)
                    rank = m.group(3)
                    if info in ['수량','별증감']:
                        info = '증감' if info == '별증감' else info
                        src.update({f'{type}{info}':v, 'dt':d['dt']})

        df = pd.DataFrame(srcs).drop(columns=['p'])
        df = df.sort_values('name').reset_index(drop=True)

        # PartGubun('동일 거래원으로 데이타를 병합')
        gs = []
        for n,g in df.groupby('name'):
            g = g.fillna(method='ffill').fillna(method='bfill').drop_duplicates(keep='first')
            gs.append(g)
        df = pd.concat(gs)

        return df.to_dict('records')

    def _one_source_cycle(self, source):
        # 주식당일거래원(=realtype) 실시간데이타 로딩
        data = self._load_data(source)
        # logger.debug(f"len_data: {len(data)} [{source}]")

        for datum in data:
            # RealtypeModel-Data 를 재해석
            newdata = self._restructure_realtypedata(datum)
            # print(pd.DataFrame(newdata))

            # 해당 거래원 컬렉션에 저장
            for d in newdata:
                # SectionGubun(d['name'])
                filter = {'dt':d['dt'], 'cid':self.RealtypeModel.cid}
                d.update(filter)
                del d['name']
                # print(d)
                tsrd = self._get_tsrd(source)
                tsrd.update_one(filter, {'$set':d}, True)

                # 가장 최근 시간을 계속 업데이트
                self._update_last_dt(source, d['dt'])

        logger.info(f'Done. [{source}] len_data: {len(data)}')

    def _thread_work(self):
        while 1:
            for source in self._source_manager:
                self._one_source_cycle(source)

            logger.info(f"{self.loop_interval}초 동안 대기 중~")
            sleep(self.loop_interval)

    @funcIdentity
    def run(self):
        t = threading.Thread(target=self._thread_work)
        t.start()
