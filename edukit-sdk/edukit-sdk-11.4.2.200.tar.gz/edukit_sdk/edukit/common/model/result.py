#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class Result:
    def __init__(self):
        self._result_code = None
        self._result_desc = None

    @property
    def result_code(self):
        return self._result_code

    @result_code.setter
    def result_code(self, result_code):
        self._result_code = result_code

    @property
    def result_desc(self):
        return self._result_desc

    @result_desc.setter
    def result_desc(self, result_desc):
        self._result_desc = result_desc

    def to_string(self):
        result_code = '' if not self._result_code and self._result_code != 0 \
            else str(self._result_code)
        result_desc = '' if not self._result_desc else self._result_desc
        return '{"resultCode":' + result_code + \
               ', "resultDesc":"' + result_desc + '"}'
