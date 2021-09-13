#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/5/24 下午5:35
# @Author  : Hubert Shelley
# @Project  : Smart7_ORM
# @FileName: models.py
# @Software: PyCharm
"""
from tortoise.models import Model as BaseModel
from tortoise import fields


class Model(BaseModel):
    # 定义抽象类
    id = fields.BigIntField(pk=True)

    class Meta:
        abstract = True


class LogicDeleteModel(Model):
    # 定义逻辑删除抽象类
    id = fields.UUIDField(pk=True)
    datetime_created = fields.DatetimeField(auto_now_add=True)
    datetime_updated = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        abstract = True
