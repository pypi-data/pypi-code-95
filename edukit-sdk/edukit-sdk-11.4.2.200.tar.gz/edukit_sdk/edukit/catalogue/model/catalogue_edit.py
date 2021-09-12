# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.catalogue.model.catalogue_edit_data import \
    CatalogueEditData
from edukit_sdk.edukit.common.helpers.helpers import Helpers


class CatalogueEdit:
    def __init__(self):
        self._catalogue_edit_id = None
        self._edit = None

    @property
    def catalogue_edit_id(self):
        """
        :return: mixed
        """
        return self._catalogue_edit_id

    @catalogue_edit_id.setter
    def catalogue_edit_id(self, catalogue_edit_id):
        """
        课程版本ID
        :param catalogue_edit_id:
        :return:
        """
        self._catalogue_edit_id = catalogue_edit_id

    @property
    def edit(self):
        """
        :return: mixed
        """
        return self._edit

    @edit.setter
    def edit(self, edit: CatalogueEditData):
        """
        目录版本数据
        :param edit:
        :return:
        """
        self._edit = edit

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
