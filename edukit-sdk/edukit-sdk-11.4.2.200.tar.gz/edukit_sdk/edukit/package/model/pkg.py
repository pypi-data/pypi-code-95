#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class Pkg:
    def __init__(self):
        self._action = None
        self._associate_album_id = None
        self._edit = None

    @property
    def action(self):
        """
        :return:mixed
        """
        return self._action

    @action.setter
    def action(self, action):
        """
        创建时的操作，1-提交审核
        :param action:
        :return:
        """
        self._action = action

    @property
    def associate_album_id(self):
        """
        :return:mixed
        """
        return self._associate_album_id

    @associate_album_id.setter
    def associate_album_id(self, associate_album_id):
        """
        关联的专辑ID
        :param associate_album_id:
        :return:
        """
        self._associate_album_id = associate_album_id

    @property
    def edit(self):
        """
        :return:mixed
        """
        return self._edit

    @edit.setter
    def edit(self, edit):
        """
        会员包版本数据
        :param edit:
        :return:
        """
        self._edit = edit

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
