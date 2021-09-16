# -*- coding: utf-8 -*-
import pprint
pp = pprint.PrettyPrinter(indent=2)


class BaseClass(object):

    def repr(self):
        print(f"\n{self}")
        pp.pprint(self.__dict__)
        return self

    def attr(self, dic):
        for k, v in dic.items():
            setattr(self, k, v)
        return self


class BaseDataClass(BaseClass):
    # 데이타-타입 파싱은 직접한 후에, 데이타-클래스로 만들어라. 여기서 파싱 안한다.

    def __init__(self, name=None, **doc):
        self.__dataclsname__ = self if name is None else f"{self} of {name}"
        self._setup(**doc)

    def _setup(self, **doc):
        for k,v in doc.items():
            setattr(self, k, v)

    def get_doc(self):
        d = self.__dict__.copy()
        del d['__dataclsname__']
        return d

    def repr(self):
        print(f"\n{self.__dataclsname__}")
        pp.pprint(self.get_doc())

    def get(self, k):
        return getattr(self, k)
