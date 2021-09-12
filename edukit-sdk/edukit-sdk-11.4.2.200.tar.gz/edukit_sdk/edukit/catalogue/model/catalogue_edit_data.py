# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.catalogue.model.catalogue_full_localized_data import \
    CatalogueFullLocalizedData
from edukit_sdk.edukit.catalogue.model.catalogue_full_meta_data import \
    CatalogueFullMetaData
from edukit_sdk.edukit.common.helpers.helpers import Helpers


class CatalogueEditData:
    def __init__(self):
        self._meta_data = None
        self._localized_data = None
        self._delete_language_list = None

    @property
    def meta_data(self):
        """
        :return: mixed
        """
        return self._meta_data

    @meta_data.setter
    def meta_data(self, meta_data: CatalogueFullMetaData):
        """
        目录完整元数据
        :param meta_data:
        :return:
        """
        self._meta_data = meta_data

    @property
    def localized_data(self):
        """
        :return: mixed
        """
        return self._localized_data

    @localized_data.setter
    def localized_data(self, localized_data: CatalogueFullLocalizedData):
        """
        目录完整多语言数据
        :param localized_data:
        :return:
        """
        self._localized_data = localized_data

    @property
    def delete_language_list(self):
        """
        :return: mixed
        """
        return self._delete_language_list

    @delete_language_list.setter
    def delete_language_list(self, delete_language_list):
        """
        需要删除的多语言数据,语言代码，由BCP-47定义
        :param delete_language_list:
        :return:
        """
        self._delete_language_list = delete_language_list

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
