# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)
import re


import pandas as pd


from idebug import *
import imath
from kiwoomde import *
from kiwoomde.models import RTModel



def f00(model, filter=None):
    cols = model.schema.get_columns()
    termdict = model._termdict()
    print(cols)
    for c in cols:
        values = model.distinct(c, filter)
        name = termdict[c]
        print(f"{c}({name}) | {len(values)}")
        if len(values) < 1000:
            print(values)


def f01():
    # TR데이타 '주식거래원요청'와
    # 실시간데이타 '주식당일거래원' 간의 컬럼 비교
    # TR데이타는 가장 마지막 데이터고, 실시간데이타는 시간별?
    PartGubun('TR-주식거래원요청 --> A')
    model = TRModel('opt10002', 'test').repr()
    model.schema.repr()
    A = sorted(model.schema.get_columns())

    PartGubun('RT-주식당일거래원 --> B')
    model = RTModel('주식당일거래원', collmode='test', name='인터파크').repr()
    model.schema.repr()
    B = sorted(model.schema.get_columns())
    termdict = model._termdict()
    B = [termdict[c] for c in B]

    # print(A)
    # print(B)

    PartGubun('A 교집합 B')
    A_x_B = []
    for c in A:
        if c in B:
            A_x_B.append(c)
    print(f"A: {len(A)} | B: {len(B)} | A_x_B: {len(A_x_B)}")
    pp.pprint(A_x_B)

    PartGubun('A 차집합 B')
    A_cha_B = []
    for c in A:
        if c not in B:
            A_cha_B.append(c)
    print(f"A: {len(A)} | B: {len(B)} | A_cha_B: {len(A_cha_B)}")
    pp.pprint(A_cha_B)

    PartGubun('B 차집합 A')
    B_cha_A = []
    for c in B:
        if c not in A:
            B_cha_A.append(c)
    print(f"A: {len(A)} | B: {len(B)} | B_cha_A: {len(B_cha_A)}")
    pp.pprint(B_cha_A)


def f02():
    # 실시간데이타 '종목프로그램매매'
    # TR데이타 '종목시간별프로그램매매추이요청 ' 간의 컬럼 비교
    # 실시간데이타의 경우 '순매수수량증감(변동량)' 컬럼이 없기 때문에 별도로 계산해줘야함

    PartGubun('TR-종목시간별프로그램매매추이요청 -> A')
    trmodel = TRModel('opt90008', 'test').repr()
    cols1 = sorted(trmodel.schema.get_columns())
    print(cols1)
    print(len(cols1))

    PartGubun('RT-종목프로그램매매 -> B')
    rtmodel = RTModel('종목프로그램매매', collmode='test', name='인터파크').repr()
    cols2 = sorted(rtmodel.schema.get_columns())
    termdict = rtmodel._termdict()
    cols2 = [termdict[c] for c in cols2]
    print(cols2)
    print(len(cols2))

    PartGubun('A - B')
    _cols1 = cols1.copy()
    for c in cols2:
        try:
            _cols1.remove(c)
        except Exception as e:
            pass
    print(_cols1)
    print(len(_cols1))

    PartGubun('B - A')
    _cols2 = cols2.copy()
    for c in cols1:
        try:
            _cols2.remove(c)
        except Exception as e:
            pass
    print(_cols2)
    print(len(_cols2))


def f03():
    # Realtype별 schema 보기
    realtypes = RTList().distinct('realtype')
    for realtype in realtypes:
        SectionGubun(realtype)
        model = RTModel(realtype, 'test', name='인터파크')
        print(model.schema.mdb)


class BaseRTModelAnalyzer(BaseClass):
    # 분석에 필요한 확실한 데이터만 로딩한다

    def __init__(self, realtype, collmode, **cid):
        self.model = RTModel(realtype=realtype, collmode=collmode, **cid)
        self.calc = Calculator()
        self.data =  []

    def load(self):
        data = self.model.load(limit=60, sort=[('dt',DESCENDING)])
        data = self.model.translate(data)
        # realtype별로 로딩하는 데이타를 자동으로 계산
        data = self._realtype_autocalc(data)
        # self.data += data
        return data

    def calc_delta_amt(self, df, cols):
        # 증감량 계산
        for c in cols:
            srs = df[c].rolling(2).apply(self.calc.delta_amt)
            df[f"{c}증감량"] = srs
        return df

    def calc_delta_rate(self, df, cols):
        # 증감률 계산
        for c in cols:
            srs = df[c].rolling(2).apply(self.calc.delta_rate)
            df[f"{c}증감률"] = srs
        return df


class Calculator(BaseClass):

    def __init__(self):
        # 퍼센트로 전환시 소수점이하 2자리까지
        self._pct_digits = 4

    def delta_amt(self, srs):
        # 0행 - 1행, 1행 - 0행 이든 무조건 결과는 1행에 삽입된다
        # 따라서 1행 - 0 행 = 1행 되는 것이 맞다
        li = list(srs)
        x1, x2 = li[0], li[1]
        return x2 - x1

    def delta_rate(self, srs):
        li = list(srs)
        x1, x2 = li[0], li[1]
        return round(imath.relative_change(x1, x2), self._pct_digits)


class ProgramTradingAnalyzer(BaseRTModelAnalyzer):

    def __init__(self, collmode='real', **cid):
        super().__init__('종목프로그램매매', collmode, **cid)

    def _realtype_autocalc(self, data):
        data = self._calc_delta(data)
        return data

    def _calc_delta(self, data):
        # [매수/매도/순매수]수량증감 계산
        # 순매수수량증감 == 순매수-변동(삼성POP-HTS)
        # 매수수량증감, 매도수량증감 도 필요하다 -> 매수와 매도가 동시에 일어날 수도 있기 때문.
        # 근데 어째, 거의 동시에 일어나지 않는것 같다?
        self._delta_cols = ['매수금액','매도금액','순매수금액','매수수량','매도수량','순매수수량','누적거래량']
        df = pd.DataFrame(data)
        df = df.sort_values('체결시간', ascending=True)
        df = self.calc_delta_amt(df, self._delta_cols)
        df = self.calc_delta_rate(df, self._delta_cols)
        # 증감량의 변화율 계산
        cols = [f"{c}증감량" for c in self._delta_cols]
        df = self.calc_delta_rate(df, cols)

        # 뷰어
        df.info()
        _df = df.set_index('체결시간')
        for c in self._delta_cols:
            SectionGubun(c)
            print(_df.loc[:,[c, f"{c}증감량", f"{c}증감률", f"{c}증감량증감률"]])

        return df.to_dict('records')


class TradingSourceAnalyzer(BaseRTModelAnalyzer):

    def __init__(self, collmode='real', **cid):
        super().__init__('주식당일거래원', collmode, **cid)

    def _realtype_autocalc(self, data):
        data = self._calc_delta(data)
        return data

    def _calc_delta(self, data):
        df = pd.DataFrame(data)
        df.info()
        print(df)
        re.compile('^매수거래원.*\d+$')
        return df.to_dict('records')
