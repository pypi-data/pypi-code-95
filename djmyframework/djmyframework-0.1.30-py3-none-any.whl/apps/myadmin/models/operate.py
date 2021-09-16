# -*- coding: utf-8 -*-
# @Time    : 2019-09-03 11:39
# @Author  : xzr
# @File    : operate
# @Contact : xzregg@gmail.com
# @Desc    :
import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from framework.models import BaseModel
from ..apps import MyadminConfig
from .user import User


class OperateLog(BaseModel):
    """
    操作日志记录
    """
    user = models.ForeignKey(User, verbose_name=_('管理员ID'), on_delete=models.DO_NOTHING,null=True)
    type = models.CharField(_('类型'), max_length=20, db_index=True)
    ip = models.GenericIPAddressField(_('IP'), max_length=10)
    full_path = models.CharField(_('访问路径'), max_length=200, db_index=True)
    post_params = models.TextField(_('提交参数'), default='')
    msg = models.TextField(_('其他消息'), default='')
    user_agent = models.CharField(_('User-Agent'), max_length=200)

    @property
    def user_alias(self):
        return self.user.alias

    class Meta:
        app_label = MyadminConfig.name
        ordering = ['-id']
