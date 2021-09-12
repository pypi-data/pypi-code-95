#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class EduKitException(Exception):
    def __init__(self, message, code=0):
        self._message = message
        self._code = code

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = code
