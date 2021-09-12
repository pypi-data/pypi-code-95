# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.catalogue.model.catalogue_edit import CatalogueEdit


class Catalogue:
    def __init__(self):
        self._catalogue_id = None
        self._catalogue_edit = None

    @property
    def catalogue_id(self):
        """
        :return: mixed
        """
        return self._catalogue_id

    @catalogue_id.setter
    def catalogue_id(self, catalogue_id):
        """
        目录ID
        :param catalogue_id:
        :return:
        """
        self._catalogue_id = catalogue_id

    @property
    def catalogue_edit(self):
        """
        :return: mixed
        """
        return self._catalogue_edit

    @catalogue_edit.setter
    def catalogue_edit(self, catalogue_edit: CatalogueEdit):
        """
        目录版本数据
        :param catalogue_edit:
        :return:
        """
        self._catalogue_edit = catalogue_edit
