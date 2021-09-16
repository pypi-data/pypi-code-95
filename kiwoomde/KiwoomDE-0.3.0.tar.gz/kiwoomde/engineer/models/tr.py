# -*- coding: utf-8 -*-
import re


from idebug import *
from kiwoomde.engineer.database import *


from kiwoomde.engineer.models.base import KWModel
from kiwoomde.engineer.models._derived import *


def TRModel(trname, collmode='real', **cid):
    if trname == '계좌평가잔고내역요청':
        return AccountValuationBalance(collmode)
    elif trname == '예수금상세현황요청':
        return Yesugeum(collmode)
    elif trname == '계좌별주문체결내역상세':
        return OrderChegeoulHistory(collmode)
    else:
        return BaseTRModel(trname, collmode, **cid)


class BaseTRModel(KWModel):
    # 존재하지 않는 TR을 입력할 경우는 절대 있을 수 없다. 시스템에러를 발생시킨다.
    # 모든 TR-OUTPUT 을 수동으로 저장할 때까지, schema가 없는 TR이 존재한다.
    # 스키마가 없다면 응답데이터 파싱이 불가능하여 시스템에러가 발생한다.
    # 그래도 일단, 샘플데이터 저장을 위해서 시스템에러를 발생시키지 않는다.
    #
    # KiwoomClient-TR 에서 종목코드-input 이 있는 경우,
    # collection-remodeling 을 다시할 수 있도록 메소드를 제공한다.

    @funcIdentity
    def __init__(self, trname, collmode='real', **cid):
        self.TRList = KWModel('TRList').select({'trname':trname})
        self.trcode = self.TRList.selected.trcode
        self.trname = self.TRList.selected.trname
        # self.TRList = SelectorModel('TRList').select(trname=trname)
        # self.trcode = self.TRList.trcode
        # self.trname = self.TRList.trname
        super().__init__(modelName=self.trcode, collmode=collmode)

        # INPUT(id=종목코드) 를 가진 trcode인 경우, 모델을 확장한다.
        # 단, 몇가지 예외처리해야할 TR이 존재한다
        for input in self.TRList.selected.inputs:
            if input['id'] == '종목코드':
                if isinstance(input['value'], str):
                    if re.search('공백허용', input['value']) is not None:
                        # 예외처리: 공백허용할 경우, 확장하지 않는다
                        pass
                    elif len(re.findall('(\d+):(.+)', input['value'])) > 0:
                        # 예외처리: Value Options 를 갖는 형태일 경우, 확장하지 않는다
                        pass
                    else:
                        self._extend_cidmodel(**cid)
                elif input['value'] is None:
                    self._extend_cidmodel(**cid)

        # 동적스키마 재적용
        # trcode별 schema.mdb 의 'role'컬럼에 'key'를 업데이트
        # 미리 정의하지 않았다면, dt를 제외한 모든 TR데이타를 keycols 로 봐야할 듯
        keycols = db.TRModelSchemaKeyCols.distinct('keycols', {'trcode':self.trcode})
        # if len(keycols) == 0:
        #     keycols = self.schema.get_columns({'extra':False})
        self.schema.create_dynamic(schemaName='TRItem',
                                filter={'trs':{'$in':[self.trcode]}},
                                rename={'item':'column'},
                                extra=[{'column':'dt'}],
                                keycols=keycols)


class AccountValuationBalance(BaseTRModel):

    def __init__(self, collmode='real'):
        super().__init__('계좌평가잔고내역', collmode=collmode)

    def get_last_dt(self):
        # 최근거래일 중에 최근보유일시 dt 가져오기
        dts = self.distinct('dt', {'dt':{'$gte':last_tradeday()}})
        if len(dts) > 0:
            return DatetimeParser(sorted(dts)[-1])
        else:
            logger.info('오늘자 보유종목이 없다')

    def select_one(self, issueName):
        dt = self.get_last_dt()
        filter = {'dt':dt, '종목명':issueName}
        af = AutoFilter(self.schema).search(filter)
        self.select(af.filter)
        return self

    def get_issueNames(self):
        dt = self.get_last_dt()
        return self.distinct('종목명', {'dt':dt})

    def upsert_data(self, data):
        # 데이타-업서트 기준 컬럼
        keycols = self.schema.get_columns({'role':'key'})
        if len(data) > 0:
            # 보유종목이 있다면, 업서트해야한다
            for d in data:
                filter = {k:v for k,v in d.items() if k in keycols}
                if len(filter) > 0:
                    self.update_one(filter, {'$set':d}, True)
        else:
            # 보유종목이 없다면, 'dt'만 있는 데이타를 그냥 저장한다
            d = {'dt':datetime.today().astimezone()}
            self.insert_one(d)


class Yesugeum(BaseTRModel):

    def __init__(self, collmode='real'):
        super().__init__('예수금상세현황요청', collmode=collmode)

    def get_last_saved_dt(self):
        # 최근 업데이트일시 dt 가져오기
        dts = self.distinct('dt')
        return DatetimeParser(sorted(dts)[-1])

    def upsert_data(self, data):
        keycols = self.schema.get_columns({'extra':False})
        last_saved_dt = self.get_last_saved_dt()
        for d in data:
            new_dt = d['dt']
            if new_dt.day == last_saved_dt.day:
                # 최근거래일과 최근업데이트일이 같은날이면, 업서트한다
                # 예수금정보가 오늘 중으로 여러번 똑같다면, 업데이트한다 -> 'dt' 컬럼이 업데이트된다
                # 데이타-업서트 기준 컬럼
                filter = {k:v for k,v in d.items() if k in keycols}
                self.update_one(filter, {'$set':d}, True)
            else:
                # 최근거래일이 최근업데이트일보다 다르다면, 인서트한다
                # 예수금정보가 어제랑 오늘이 똑같더라도 날짜가 다르다면 인서트한다
                self.insert_one(d)

    def get(self, item):
        # 최근업데이트 정보의 특정 item에 대한 값을 반환
        return self.distinct(item, {'dt':self.get_last_saved_dt()})[0]


class OrderChegeoulHistory(BaseTRModel):
    # 원주문번호입니다. 신규주문에는 공백, 정정(취소)주문할 원주문번호를 입력합니다.
    def __init__(self, collmode='real'):
        super().__init__('계좌별주문체결내역상세', collmode=collmode)
