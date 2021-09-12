#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class TeacherUpdateLocalizedDataRequest:
    def __init__(self):
        self._localized_data = None,

    @property
    def localized_data(self):
        return self._localized_data

    @localized_data.setter
    def localized_data(self, localized_data):
        self._localized_data = localized_data

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
