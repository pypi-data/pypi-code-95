#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class Response:
    def __init__(self):
        self._result = None

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result
