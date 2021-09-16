# -*- coding: utf-8 -*-
import re


import pandas as pd


from idebug import *
from kiwoomde.database import *


from kiwoomde import config
from kiwoomde.base import BaseClass, BaseDataClass
from kiwoomde.models.base import KWModel
from kiwoomde.models._util import *


def DevGuideModel(modelName):
    if modelName == 'TRList':
        return TRList()
    elif modelName == 'RTList':
        return RTList()
    elif modelName == 'ChejanFID':
        return ChejanFID()


# DevGuideText를 데이타로 생성하는 모델
class BaseDGModel(KWModel):

    def __init__(self, modelName):
        super().__init__(modelName)
        self._read_file()

    def _read_file(self):
        # 파일 읽기
        if self.modelName in dba.DevGuideModels():
            # 텍스트파일 읽어들이기
            fpath = config.clean_path(f'{config.DevGuideTextPath}/{self.modelName}.txt')
            f = open(fpath, mode='r', encoding='utf-8')
            text = f.read()
            f.close()
            return text
        else:
            # 모델명에 해당하는 파일명이 없다면 에러발생
            logger.critical(f'해당 모델({self.modelName})에 대한 텍스트 파일이 존재하지 않는다')
            raise

    def _create(self):
        # 텍스트 파일 읽어들이기
        text = self._read_file()
        # 텍스트를 데이터 구조화 --> 모델에 따라 각각 다르게 함수를 구성하라
        data = self._structure_data(text)
        # DB저장
        self.drop()
        self.insert_many(data)


class TRList(BaseDGModel):
    # KOA StudioSA / TR목록

    @funcIdentity
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        # PartGubun('Phase-1: DevGuideText 를 데이타구조화 및 저장')
        self._create()

        # PartGubun('Phase-2: 컬렉션 데이타를 이용하여 추가컬럼들을 업데이트')
        self._update_markettype()

        logger.info('Done.')

    def _split_whole_text(self, text):
        # Split Whole-Text into Each TR-based Text
        p = re.compile('(/[\*]+/)')
        li = p.split(text)
        li = [e.strip() for e in li if len(e.strip()) > 0]
        # 분할패턴도 결과에 포함되어 리턴되므로 삭제해야 한다 --> 쥰내 이해가 안됨
        return [e for e in li if p.search(e) is None]

    def _structure_data(self, text):
        txt_list = self._split_whole_text(text)
        data = []
        for txt in txt_list:
            # 파싱
            trcode, trname = self._get_trcodename(txt)
            outputs = self._get_outputs(txt)
            inputs = self._get_inputs(txt)
            caution = self._get_caution(txt)
            real_active, test_active = self._get_active(caution)
            data.append({
                'trcode':trcode, 'trname':trname,
                'inputs':inputs, 'outputs':outputs,
                'caution':caution, 'real_active':real_active, 'test_active':test_active
            })
        return data

    def _get_trcodename(self, text):
        m = re.search("\[\s*([a-zA-Z0-9]+)\s*:\s*([가-힝A-Z\s0-9\(\)]+)\s*\]", text)
        return m.group(1).strip(), m.group(2).strip()

    def _get_outputs(self, text):
        m = re.search('OUTPUT=(.+)', text)
        return None if m is None else m.group(1).strip().split(',')

    def _get_inputs(self, text):
        inputs = re.findall('SetInputValue\("(.+)"\s*,', text)
        # print(inputs)
        data = []
        for input in inputs:
            d = {'id':input}
            m = re.search(f'{input}\s*=\s*(.+)\n', text)
            value = None if m is None else m.group(1).strip()
            # print(value)
            d.update({'value':value})
            data.append(d)
        return data

    def _get_caution(self, text):
        p = re.compile('\[\s*주의\s*\]')
        m = p.search(text)
        if m is None:
            return None
        else:
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if p.search(line) is not None:
                    break
            return lines[i+1]

    def _get_active(self, caution):
        if caution is None:
            real, test = True, True
        else:
            m = re.search('(이 TR은)[.\s]+(모의투자)*', caution)
            if m is None:
                real, test = True, True
            else:
                real, test = (False, False) if m.group(2) is None else (True, False)
        return real, test

    @funcIdentity
    def _update_markettype(self):
        self.update_many({}, {'$set':{'markettype':'stock'}})

        filter = {'trname':{'$regex':'선물|옵션|선옵'}}
        update = {'$set':{'markettype':'fo'}}
        self.update_many(filter, update)

        filter = {'trname':{'$regex':'ETF'}}
        update = {'$set':{'markettype':'ETF'}}
        self.update_many(filter, update)

        filter = {'trname':{'$regex':'ELW'}}
        update = {'$set':{'markettype':'ELW'}}
        self.update_many(filter, update)

        pattern = '계좌|예수금|자산|위탁.+거래|비밀번호|잔고현황|인출가능|증거금|신용융자'
        filter = {'trname':{'$regex':pattern}}
        update = {'$set':{'markettype':'acct'}}
        self.update_many(filter, update)

        logger.info("Done.")


class RTList(BaseDGModel):
    # KOA StudioSA / 실시간목록

    def __init__(self):
        super().__init__(self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        # PartGubun('Phase-1: DevGuideText 를 데이타구조화 및 저장')
        self._create()

        # PartGubun('Phase-2: colName의 dtype을 정의/업데이트')
        assign_dtype(self.collName, 'name')

        logger.info('Done.')

    def _split_by_realtype(self, text):
        # 전체 텍스트를 26개의 Realtype별로 나눈다
        li = re.split('[\*]+', text)
        return [e.strip() for e in li if len(e.strip()) > 0]

    def _structure_data(self, text):
        txt_list = self._split_by_realtype(text)
        data = []
        for txt in txt_list:
            realtype = self._get_realtype(txt)
            fid_data = self._get_fid_data(txt)
            data.append({'realtype':realtype, 'fid_data':fid_data})

        return data

    def _get_realtype(self, text):
        m = re.search("Real Type\s*:\s*([가-힝A-Z\s0-9\(\)]+)", text)
        return m.group(1).strip()

    def _get_fid_data(self, text):
        li = re.findall('\[(\d+)\]\s*=\s*(.+)', text)
        data = []
        for t in li:
            data.append({'fid':t[0], 'name':t[1].strip()})
        return data


class ChejanFID(BaseDGModel):
    # RealtimeFID 랑 겹치는데 굳이 필요한가?

    def __init__(self):
        super().__init__(self.__class__.__name__)

    @funcIdentity
    def create_collection(self):
        # PartGubun('Phase-1: DevGuideText 를 데이타구조화 및 저장')
        self._create()

        # PartGubun('Phase-2: colName의 dtype을 정의/업데이트')
        assign_dtype(self.collName, 'name')

        # PartGubun('Phase-3: DevGuide에는 빠진 FID 정보를 RealtimeFID로부터 추가저장')
        self._insert_omitted_FIDs()

        # PartGubun('Phase-4: 수동으로 잔여 FID 정보를 저장')
        self._insert_newly_found_FIDs()

        logger.info('Done.')

    def _structure_data(self, text):
        # 텍스트를 구조화
        data = []
        pairs = re.findall(pattern='"(\d+)"\s*:\s*"(.+)"', string=text)
        for p in pairs:
            data.append({'fid':p[0].strip(), 'name':p[1].strip()})
        return data

    def _insert_omitted_FIDs(self):
        # 개발 중
        # cursor = self.find(None, {'_id':0, 'fid':1, 'name':1})
        # df = pd.DataFrame(list(cursor))
        #
        # projection = {fid:0 for fid in list(df.fid)}
        # projection.update({'_id':0, 'dt':0})
        # cursor = db['_Test_Chejan'].find(None, projection).limit(10)
        # df = pd.DataFrame(list(cursor))
        #
        # cursor = db.RealtimeFID.find({'fid':{'$in':list(df.columns)}}, {'_id':0, 'fid':1, 'name':1, 'dtype':1})
        # df_ = pd.DataFrame(list(cursor))
        #
        # for d in df_.to_dict('records'):
        #     filter = {'fid':d['fid']}
        #     update = {'$set':d}
        #     self.update_one(filter, update, True)
        return

    def _insert_newly_found_FIDs(self):
        values = []
        for fid in [819,949,969,970,10010]:
            values.append([str(fid),None,'int'])
        data = pd.DataFrame(data=values, columns=self.schema.get_columns()).to_dict('records')
        self.insert_many(data)
