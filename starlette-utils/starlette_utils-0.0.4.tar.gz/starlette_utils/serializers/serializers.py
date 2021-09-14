#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/8/12 9:07 下午
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: serializers.py
# @Software: PyCharm
"""
import abc

from starlette_utils.exception.exceptions import ValidationError


class SerializerBase(abc.ABC):

    # 序列化器是否经过校验
    _valid = False

    def is_valid(self, raise_exception=False) -> bool:
        """
        序列化器校验

        :param raise_exception: 是否立即抛出异常
        :return:
        """
        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self._is_valid(self.initial_data)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)

    @property
    def validated_data(self) -> dict:
        if not hasattr(self, '_validated_data'):
            msg = 'You must call `.is_valid()` before accessing `.validated_data`.'
            raise AssertionError(msg)
        return self._validated_data


    @abc.abstractmethod
    def _is_valid(self) -> bool:
        """
        序列化器校验参数方法

        :return:
        """
        pass
