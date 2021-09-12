# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.course.impl.update_edit_localized_data import \
    UpdateEditLocalizedData


class UpdateLocalizedDataRequest:
    def __init__(self):
        self._localized_data = None
        self._localized_media = None

    @property
    def localized_data(self):
        return self._localized_data

    @localized_data.setter
    def localized_data(self, localized_data: UpdateEditLocalizedData):
        self._localized_data = localized_data

    @property
    def localized_media(self):
        return self._localized_media

    @localized_media.setter
    def localized_media(self, localized_media):
        self._localized_media = localized_media

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
