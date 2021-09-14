# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 18:32 
# @Author  : xzr
# @File    : admin_resource.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :


from framework.translation import _
from myadmin.models.resource import ModelResource, Resource
from .models import QueryServer


class QueryServerModelResource(ModelResource):
    label = _('查询服务器')
    name = 'query_server'
    model_class = QueryServer


Resource.register(QueryServerModelResource())
