# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re
import pprint
pp = pprint.PrettyPrinter(indent=2)


import pandas as pd


from idebug import *


from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.engineer.database import *
from kiwoomde.utils.viewer import *
from kiwoomde.engineer.models import *



class TRInputSelector(SelectorModel):
    # id-value 초기값을 설정하는 경우의 수:
    # STEP1: 변동의 여지가 전혀 없어서 컬렉션 레벨에서 미리 정해놓은 경우.
    # STEP2: 시간과 관련된 id 라서 매번 초기값을 계산해야 하는 경우.
    # STEP3: 반드시 KiwoomOpenAPI 를 통해서 초기값을 가져와야하는 경우.
    # 이 클래스는 STEP2 를 수행한다.

    def __init__(self, trcode, id):
        super().__init__('TRInput')
        self.select(tr=trcode, id=id)

        # 초기값이 없다면, 유저에게 알려준다.
        if not hasattr(self, 'value'):
            # self._autoset_dt_id()
            self.value = None
            print(f"'{self.id}'에 대한 값을 입력하시오.")
            self.show()

        # datetime 관련 id 일 경우, 동적으로 할당한다
        if self.value == 'datetime': self._autoset_dt_id()

    def _autoset_dt_id(self):
        edt = datetime.today().astimezone()
        sdt = edt - timedelta(days=+90)

        def _YYYYMMDD_type():
            if re.search('시작', self.id) is not None:
                self.value = sdt.strftime('%Y%m%d')
            else:
                self.value = edt.strftime('%Y%m%d')

        # 단계1: id 로 결정
        if re.search('일자$|시작일$|종료일$|조회일', self.id) is not None:
            _YYYYMMDD_type()
        else:
            # 단계2: value_info 로 결정
            if isinstance(self.value_info, str):
                if re.search('Y{4}M{2}D{2}|Y{3}M{2}D{2}', self.value_info) is not None:
                    _YYYYMMDD_type()
                elif re.search('Y{4}M{2}(?!D)', self.value_info) is not None:
                    self.value = edt.strftime('%Y%m')
                elif re.search("조회시간\s*4자리", self.value_info) is not None:
                    self.value = edt.strftime('%H%M')

        return self

    def show(self):
        print(f"{self.tr} | {self.id} = {self.value} | {self.value_info}")
        return self

    def show_options(self):
        if len(self.values) > 0:
            pretty_title(f"{self.tr}-{self.id} Options")
            for i, v in enumerate(self.values):
                print(f"[{i}]", v['value'], ':', v['desc'])
        else:
            logger.info('옵션값들을 보유하고 있지 않다.')

    def select_option(self, i):
        if isinstance(self.values, list):
            v = self.values[i]
            self.value = v['value']
        else:
            logger.info('선택할 옵션정보가 없다.')
        return self


class TRInputHandler(BaseClass):

    @funcIdentity
    def __init__(self, trcode):
        self.TRList = TRList().select({'trcode':trcode})
        self.trcode = self.TRList.selected.trcode
        self.trname = self.TRList.selected.trname
        cursor = db.TRInput.find({'tr':self.trcode}, {'_id':0, 'tr':1, 'id':1})
        inputs = list(cursor)
        if len(inputs) == 0:
            logger.critical(f"입력TRcode({trcode})는 'TRInput'컬렉션에 존재하지 않는다.")
        else:
            self.ids = []
            for d in inputs:
                self.ids.append(d['id'])
                selector = TRInputSelector(d['tr'], d['id'])
                setattr(self, selector.id, selector)

    def selector(self, id):
        return getattr(self, id)

    def show_state(self):
        pretty_title(f"{self.trname} 의 현재 INPUT 셋업 상태")
        for id in self.ids:
            self.selector(id).show()


class TRItemMDB(BaseClass):
    # DataBase IO 초단위로 계속 수행하면 속도가 느려지므로,
    # 객체화된 클래스에 메모리로 저장해서 사용하기 위한 핸들러

    def __init__(self):
        cursor = db.TRList.find({'outputs':{'$ne':None}}, {'_id':0, 'trcode':1, 'outputs':1})
        p = re.compile('[,\n]')
        for d in list(cursor):
            items = [e.strip() for e in d['outputs'] if len(e.strip()) > 0]
            setattr(self, d['trcode'], items)

    def get_items(self, trcode):
        return getattr(self, trcode)


class FIDHandler(BaseClass):
    # pat: 프로그램|거래원|주식체결|주식시세|VI
    # len: 104

    def __init__(self):
        cursor = db.RTList.find(None, {'realtype':1, 'fid_data':1})
        for d in list(cursor):
            df = pd.DataFrame(d['fid_data'])
            setattr(self, d['realtype'], list(df.fid))

    def get_fids(self, realtypes=None):
        if realtypes is None:
            realtypes = ['종목프로그램매매', '주식당일거래원', '주식시세', '주식체결','VI발동/해제']

        fids = []
        for type in realtypes:
            fids += getattr(self, type)
        return list(set(fids))

    def get_fidList(self, realtypes=None):
        fids = self.get_fids(realtypes)
        return ";".join(fids)

    def get_allfids(self):
        realtypes = db.RTList.distinct('realtype')
        return self.get_fids(realtypes)

    def get_allfidList(self):
        fids = self.get_allfids()
        return ";".join(fids)

    def splitted_allfidList(self):
        fids = self.get_allfids()
        group = []
        for i in range(0, len(fids), 100):
            group.append(";".join(fids[i:i+100]))
        return group


class TargetIssueHandler(BaseClass):
    # DataIO-Connection-Thread 를 계속 물고 있을 것인가???

    def __init__(self):
        self.reset()

    def show_target(self):
        filter = {'code':{'$in':self.codes}}
        projection = {'_id':0}
        cursor = db.TargetIssue.find(filter, projection).sort('code',ASCENDING)
        df = pd.DataFrame(list(cursor))
        logger.info(self)
        if len(df) == 0: self.repr()
        if len(df) > 0: print(df[:60])
        if len(df) > 60: print(df[60:])

    def repr(self):
        print(f"codeList({self.len}): {self.codeList}")
        return self

    def read(self):
        """Config 로부터 읽어들인다."""
        self.filter = None
        return self

    def _get_codes(self, filter):
        # return db.TargetIssue.distinct('code', filter)
        return db.Company.distinct('code', filter)

    def _build(self, codes):
        """종목코드는 최대 100개 까지만 등록가능."""
        self.codes = codes[-100:]
        self.codeList = ";".join(self.codes)
        self.len = len(self.codes)
        return self

    def reset(self):
        self.read()
        codes = self._get_codes(self.filter)
        return self._build(codes)

    def set(self, codes):
        filter = {'code':{'$in':codes}}
        codes = self._get_codes(filter)
        return self._build(codes)

    def add(self, codes):
        """self.codes 에 추가하고, Collection에 추가한다."""
        filter = {'code':{'$in':codes}}
        codes = self._get_codes(filter)
        codes = list(set(self.codes + codes))
        return self._build(codes)

    def clear(self):
        return self._build([])


# 왜 필요하지
class OptTypeHandler(BaseClass):
    def __init__(self, opttype=0):
        self.opttype = str(opttype)

    def read(self):
        # config.py 사용해서 읽어온다.
        return '1'

    def renewable(self):
        opttype = self.read()
        if self.opttype == opttype:
            return False
        else:
            self.opttype = str(opttype)
            return True
