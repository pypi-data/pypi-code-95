#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class UpdateMediaLocalizedData:
    def __init__(self):
        self._media_type = None
        self._ordinal = None
        self._meida_id = None
        self._frame_id = None
        self._file_name = None
        self._sha256 = None
        self._media_len = None
        self._size = None
        self._width = None
        self._height = None

    @property
    def media_type(self):
        return self._media_type

    @media_type.setter
    def media_type(self, media_type):
        self._media_type = media_type

    @property
    def ordinal(self):
        return self._ordinal

    @ordinal.setter
    def ordinal(self, ordinal):
        self._ordinal = ordinal

    @property
    def meida_id(self):
        return self._meida_id

    @meida_id.setter
    def meida_id(self, meida_id):
        self._meida_id = meida_id

    @property
    def frame_id(self):
        return self._frame_id

    @frame_id.setter
    def frame_id(self, frame_id):
        self._frame_id = frame_id

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name

    @property
    def sha256(self):
        return self.__sha256

    @sha256.setter
    def sha256(self, sha256):
        self._sha256 = sha256

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def media_len(self):
        return self._media_len

    @media_len.setter
    def media_len(self, media_len):
        self._media_len = media_len

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width
