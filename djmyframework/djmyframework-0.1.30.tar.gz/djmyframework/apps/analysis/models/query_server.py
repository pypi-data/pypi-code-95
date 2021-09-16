# -*- coding: utf-8 -*-

import copy
import json
import traceback

import MySQLdb
from django.core.management.color import no_style
from django.db import connection, models

from framework.models import BaseModel
from settings import DATABASES
from framework.utils import datetime_to_str, trace_msg, myenum
from framework.utils.cache import CacheAttribute
from framework.translation import _
from framework.connections import connections


class QueryServer(BaseModel):
    """查询服务器
    """

    class Status(myenum.Enum):
        Deleted = (-1, '已删除')
        Normal = (0, '正常')

    name = models.CharField(u'服务器名', max_length=20, blank=False, null=False, db_index=True, help_text='纯字母')
    alias = models.CharField(u'服务器别名', max_length=20,
                             default='', blank=True, null=False)
    host = models.CharField(_('地址'), max_length=200, blank=False, null=False)
    user = models.CharField(_('用户'), max_length=100, default='root', blank=False, null=False)
    password = models.CharField(_('密码'), max_length=100, blank=False, null=False)
    port = models.IntegerField(_('端口'), default=3306, blank=False, null=False)
    db_name = models.CharField(_('数据库名'), max_length=100, blank=False, null=False)
    charset = models.CharField(_('数据字符集'), max_length=100, default='utf8', blank=False, null=False, help_text='默认 utf8')
    status = models.IntegerField(u'服务器状态', default=0, choices=Status.member_list())
    remark = models.CharField(u'备注', max_length=200, default='', blank=True, null=False)
    order = models.IntegerField(u'排序', default=0)

    __conn = None

    @classmethod
    def get_conn(cls, server_id=0, databases='default', connect_timeout=10):
        try:
            if server_id:
                the_server = cls.objects.using(databases).get(id=server_id)
                the_conn = the_server.mysql_conn(True)
                the_conn.autocommit(1)
            else:
                the_conn = connections[databases]

        except Exception as e:
            raise e
        return the_conn

    def mysql_conn(self, select_db=True, connect_timeout=10, is_new=False):
        """mysql的连接
        """
        if not self.__conn or is_new:
            # try:
            the_conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                                       charset=self.charset,
                                       connect_timeout=connect_timeout)
            the_conn.autocommit(1)
            self.__conn = the_conn
        # except Exception as e:
        #     print(trace_msg())
        if self.__conn:
            if select_db:
                self.__conn.select_db(self.db_name)
        return self.__conn

    def get_json_data(self):
        try:
            json_data = self.json_data if self.json_data.find(
                    '{') == 0 else '{%s}' % self.json_data
            server_config = json.loads(json_data)
            return server_config
        except:
            return {}

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.id)

    def create_time_str(self):
        return datetime_to_str(self.create_datetime) if self.create_datetime else ''

    @classmethod
    def get_server_list(cls):
        return cls.objects.filter(~models.Q(status=cls.Status.DELETED)).order_by('-status')

    class Meta:
        ordering = ('order',)
