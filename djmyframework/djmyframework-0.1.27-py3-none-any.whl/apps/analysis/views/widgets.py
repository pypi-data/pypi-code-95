# -*- coding: utf-8 -*-
# @Time    : 2020-07-16 14:44
# @Author  : xzr
# @File    : widgets
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

from django.utils.translation import gettext_lazy as _

import logging
from collections import OrderedDict as SortedDict

from ..models.query_server import QueryServer
from ..admin_resource import QueryServerModelResource


def get_query_servers(request, group_id=0, get_server_list=False):
    return request.user.get_resource(QueryServerModelResource.name).all()
