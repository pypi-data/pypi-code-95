# -*- coding = UTF-8 -*-
# Author   :buxiubuzhi
# File     : page.py
# project  : McenterSystem
# time     : 2020/12/3 11:56
# Describe :
# ---------------------------------------

import logging
from lazyTest.file import *
from lazyTest.base import *


class Page(object):
    filePath = r"/resources/element/"

    suffix = ".yaml"

    def __init__(self, driver: WebOption):
        self.driver = driver
        self.lazyLog = logging.getLogger(self.getClassName())
        self.lazyLog.info(
            "元素文件: -> %s" % (
                    self.GetProjectPath() + self.filePath + self.getClassName() + self.suffix
            )
        )
        self.source = GetElementSource(
            self.GetProjectPath() + self.filePath + self.getClassName() + self.suffix
        )

    def GetElement(self, key: str) -> str:
        return self.source.GetElement(key).Element

    def GetProjectPath(self) -> str: ...

    @classmethod
    def getClassName(cls):
        return cls.__name__
