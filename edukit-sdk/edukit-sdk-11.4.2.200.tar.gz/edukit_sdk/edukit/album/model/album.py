# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class Album:
    def __init__(self):
        self._action = None
        self._edit = None

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        """
        创建时的操作，1-提交审核
        :param action:
        """
        self._action = action

    @property
    def edit(self):
        return self._edit

    @edit.setter
    def edit(self, edit):
        """
        专辑详情
        :param edit:
        :return:
        """
        self._edit = edit

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
