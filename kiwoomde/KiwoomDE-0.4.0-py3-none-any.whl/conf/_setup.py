# -*- coding: utf-8 -*-
import json
import os
import sys
from platform import python_version_tuple
from pathlib import PureWindowsPath, PurePosixPath
import re
import pprint
pp = pprint.PrettyPrinter(indent=2)


from kiwoomde.base import BaseClass, BaseDataClass


class Configuration(BaseClass):

    def __init__(self):
        self._dataclsList = []
        self._set_default()
        self._set_basepath()
        self._set_syspath()
        self._set_datapath()
        self._autoset_db_attrs()

    def _get_conf_dir(self):
        return os.path.dirname(__file__)

    def _read_default(self):
        # 기본 설정값(default.json) 읽어들인다
        path = self._get_conf_dir()
        f = open(f'{path}/default.json', mode='r')
        text = f.read()
        f.close()
        return json.loads(text.strip())

    def _write_user_setting(self, json_str):
        path = self._get_conf_dir()
        f = open(f'{path}/user.json', mode='w')
        f.write(json_str)
        f.close()

    def _set_default(self):
        # JSON으로 정의된 기본설정값 셋업
        d = self._read_default()
        for k,v in d.items():
            if isinstance(v, dict):
                setattr(self, k, BaseDataClass(name=k, **v))
                self._dataclsList.append(k)
            else:
                setattr(self, k, v)

    def _set_basepath(self):
        # 운영체제 타입에 따라 "프로젝트들이 모여있는 폴더 경로"를 잡아준다
        self.basepath.BasePath = self.basepath.BasePath if os.name == 'nt' else "/Users/sambong/pjts"
        # "내가 만든 패키지 경로"를 추가한다
        self.basepath.MyLibPath = f"{self.basepath.BasePath}/my-packages"
        self._clean_dataclasspath(self.basepath)

    def _set_syspath(self):
        # "프로젝트 패키지 경로" 추가
        self.syspath.ProjectPath = f"{self.basepath.BasePath}/{self.general.ProjectName}"

        # 운영체제 타입에 따라 "파이썬 패키지 경로"를 잡아준다
        if os.name == 'posix':
            v = python_version_tuple()
            envpath = f"env/lib/python{v[0]}.{v[1]}/site-packages"
        elif os.name == 'nt':
            envpath = "env/Lib/site-packages"
        self.syspath.VenvLibPath = f"{self.syspath.ProjectPath}/{envpath}"

        self._clean_dataclasspath(self.syspath)

    def _set_datapath(self):
        self.datapath.DataPath = f'{self.syspath.ProjectPath}/Data'
        for name in ['SchemaCSV','DevGuideText','ManDataJSON']:
            setattr(self.datapath, f'{name}Path', f'{self.datapath.DataPath}/{name}')
        self._clean_dataclasspath(self.datapath)

    def _autoset_db_attrs(self):
        self.db.BackupDatabaseName = f'{self.db.DatabaseName}Backup'
        # db 관련 값의 데이타-타입을 청소한다
        for k,v in self.db.__dict__.items():
            if isinstance(v, str):
                if v.isnumeric():
                    v = int(v)
                elif v in ['True','False']:
                    v = bool(v)
                elif v == 'None':
                    v = None
                setattr(self.db, k, v)

    def _clean_dataclasspath(self, datacls):
        for name, path in datacls.__dict__.items():
            p = self.clean_path(path)
            setattr(datacls, name, p)

    def clean_path(self, p):
        # 운영체제 타입에 따라 path 를 수정한다
        if os.name == 'posix':
            return str(PurePosixPath(p))
        elif os.name == 'nt':
            return str(PureWindowsPath(p))

    def append_syspath(self, target):
        # syspath-DataClass 에 존재하는 타겟을 경로에 추가한다
        for name, path in self.syspath.__dict__.items():
            if name == target:
                sys.path.append(self.clean_path(path))
        sys.path = list(set(sys.path))

    def save(self):
        # 사용자가 변경한 설정값을 별도로 저장한다
        js = json.dumps(self.__dict__)
        print('json_str:', js)
        self._write_user_setting(js)

    def show(self):
        title, simbol, width = f'Configuration at {__file__}', '*', 100
        space = " " * int((width - len(title)) / 2)
        line = simbol * width
        print(f"\n{line}\n{space}{title}{space}\n{line}")

        self.repr()
        for e in self._dataclsList:
            getattr(self, e).repr()

        # 경로 확인
        print(f"\n{'#'*30} sys.path {'#'*30}")
        pp.pprint(sorted(sys.path))
