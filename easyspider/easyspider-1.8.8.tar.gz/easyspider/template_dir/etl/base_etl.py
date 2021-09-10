# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-18 16:11:45
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-08-01 23:34:01
"""
1. 因为比如获取mongo当中结果的操作get_mongo_result不仅仅在mongo_etl到redis中需要被使用
在etl到mysql的时候也需要被使用..这时候要引入一个mongo_etl_redis就不太好，所以在这里就提供
一个基础的etl_base来解决这个问题

2. 同时对于每个etl都有个cmd_parse的函数，实在是太繁杂了，应该是公共的解析要集合在一起才行

3. 同时有时会需要用到某个函数，但是因为函数在类里面，使用必须要初始化，但是初始化又逃不掉
命令行参数的赋予，所以导致很麻烦。这里就干脆除非run的时候去解析命令行参数，其他时候就是可以
单独传参数被调用的。

4. 这个传参数建议不是self的参数，因为是外部调用，只希望使用这个函数，但是不想麻烦的去设置self
的内容
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("../easyspider/utils")
sys.path.append("../easyspider")
#import settings
#from dbConn_for_etl import MongoConnect, BaseRedis
import argparse
import textwrap
#from logger_base import *


class base_etl(object):

    def __init__(self):
        # mongo系
        self.mongo_server = None
        self.mogno_url = None
        self.mongo_db_name = None

        # redis系
        self.redis_server = None

    # 所有etl的命令行解析函数，参数都不强制要求提供，但是在运行时发现参数不够，报错提示
    # 每个etl的功能，在运行了父类这个函数之后，通过加载-h参数提供
    def parse_cmd(self, desc="etl的基础类,在这里将会解析命令行的参数,参数都不强制要求提供,但是在运行时发现参数不够的时候,将会报错提示"):
        parser = argparse.ArgumentParser(description=desc)

        #------------mongo类-------------------
        parser.add_argument("-mongo-url", help="mongodb连接地址, 默认会采用settings中配置的信息",
                            default=settings.MONGO_URL if hasattr(settings, "MONGO_URL") else "mongodb://127.0.0.1:27017/")
        parser.add_argument("-mongo-db-name", help="mongodb连接的库, 默认会采用settings中配置的信息",
                            default=settings.MONGO_DB_NAME if hasattr(settings, "MONGO_DB_NAME") else "easyspider")
        parser.add_argument("-mongo-collection",
                            help="mongodb的集合, 如果有需要，必须要提供")

        #------------redis类-------------------
        parser.add_argument("-redis-url", help="redis连接地址, 默认会采用settings中配置的信息",
                            default=settings.REDIS_URL if hasattr(settings, "REDIS_URL") else "redis://127.0.0.1:6379")
        parser.add_argument(
            "-redis-key", help="操作的redis-key, 如果同时有mongodb的collection，那么将会以collection名字加上etl前缀")

        #------------csv类---------------------
        parser.add_argument(
            "-csv-file", help="写入的csv文件名, 默认会采用result_csv前缀+collection名")
        parser.add_argument("-csv-split-symbol",
                            help="csv文件的分割符号，默认为 $", default="$")

        #------------mysql类---------------------
        parser.add_argument(
            "-mysql-file", help="写入的mysql脚本文件名, 默认会采用result_mysql_前缀+collection名")
        parser.add_argument(
            "-interval", help="写入mysql脚本时候层级的分割符号，默认为___三个下划线", default="____")
        args = parser.parse_args()
        return args

    #--------------------------mongo系---------------------------------

    # 检查是否已经有mongo连接, 在多次调用函数的时候避免每次重新连接mongodb
    # 返回的是直接可以用的mongo server，直接用mongo server去查询
    # 如果有，检查是否连接地址和库是否都一样，都一样，不用操作
    # 如果有，连接地址一样，数据库地址不一样，那么更新self.mongo_server的库就行了
    # 如果都不对，或者压根没有mongo_server，那么就要重新保存mongo_server
    def mongo_server_check(self, mongo_url, mongo_db_name):
        # 如果已经有了mongo的连接
        if self.mongo_server:
            # 如果连接地址和库都一样，那么就可以使用之前的连接
            if mogno_url == self.mogno_url and mongo_db_name == self.mongo_db_name:
                return self.mongo_server
            # 如果只是连接地址不一样，那么还好可以过来，不需要重新连接
            elif mongo_url == self.mongo_url and mongo_db_name != self.mongo_db_name:
                self.mongo_server.select_db(mongo_db_name)
                return self.mongo_server
        # 如果没有连接，或者连接两个都不对都没有进去return
        self.mongo_server = MongoConnect(mongo_url)
        self.mongo_server.select_db(mongo_db_name)
        # 然后保存最新的mongo的连接地址和连接库
        self.mongo_url, self.mongo_db_name = mongo_url, mongo_db_name
        return self.mongo_server

    # 抽取mongodb中指定collections的全部数据
    def get_mongo_all_result(self, mongo_url, mongo_db_name, collection):
        server = self.mongo_server_check(mongo_url, mongo_db_name)
        return server.find_all(collection)

    # 只抽取部分结果，加快速度方便debug
    def get_mongo_result_limit(self, mongo_url, mongo_db_name, collection, limit=50):
        server = self.mongo_server_check(mongo_url, mongo_db_name)
        return server.find_limit(collection, limit)

    # 把多层的dict平铺，去掉层级关系，层级前缀用_^_^_下划线标志
    # 2017年7月18日12:47:15 心情大好~~ 一遍就过~~~
    # 又加新功能...给定一个过滤函数，在是字典类型的时候开始调用，方便指定不添加哪些字段，不然平铺出来的字段会无线扩充
    def _convert_mongo_2_sheet(self, document, interval, prefix=[], result={}, filter_callback=(lambda x: True)):
        if isinstance(document, dict):
            for k, v in document.items():
                if not filter_callback(k):
                    continue
                prefix.append(k)
                self._convert_mongo_2_sheet(v, interval, prefix, result, filter_callback)
                prefix.pop()
        elif isinstance(document, list):
            # 当list里面放的不是单个的str元素，而是dict又是包含了字典的话就有问题...
            # result[interval.join(prefix)] = interval.join(document)
            # 那么尝试对于list来说，也给他增加一个prefix
            for d in document:
                # 对于list类型来说，不需要上面的prefix
                self._convert_mongo_2_sheet(d, interval, prefix, result, filter_callback)
        else:
            result[interval.join(prefix)] = document
        return result


if __name__ == '__main__':
    bast_etl().parse_cmd()
