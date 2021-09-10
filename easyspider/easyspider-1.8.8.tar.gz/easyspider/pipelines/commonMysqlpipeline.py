# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-03-05 19:10:07
# @Last Modified by:   hang.zhang
# @Last Modified time: 2019-03-06 15:58:14
import json
import time
import logging
import hashlib
from DBService import MysqlService
from twisted.internet.threads import deferToThread
from easyspider.pipelines.commonpipeline import commonpipeline
import copy
logger = logging.getLogger(__name__)


def md5_from_dict(item):
    """注意一个严重问题：！！
            Duplicate entry '001071' for key 'hash_check_item'")

            >>> md5_from_dict({"code": "001071"})
            '05e9ab87d2f88fbc29cf070b6241c0ea'
            >>> md5_from_dict({"code": u"001071"})
            '98f46fdaffc7e924e1c565c9f182ee6e'

    带不带u 差距巨大
    """
    sort_list = sorted(item.items(), key=lambda x: x[0])
    # 全部统一成str

    # sort_list = "".join(sort_list)))
    # sort_list = list(map(lambda  k,v: k+":"+v, sort_list))
    sort_str = ""
    for i in sort_list:
        if i[0]:
            sort_str += i[0]
        if i[1]:
            sort_str += i[1]
        # sort_str += i[0]+i[1]
    import pdb
    # pdb.set_trace()
    # return hashlib.md5(str(sort_list)).hexdigest()
    return hashlib.md5(sort_str.encode("utf-8")).hexdigest()

# insert_or_update 为了标志是否进行过操作，一定要加上一个时间的字段，必须要有时间


def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def process_item(server, item, table=None, db=None, hash_check_item=None, unique_key="id", hash_check_enable=True):
    _save_item = item.copy()

    if not _save_item.get("save_mysql", True) or not _save_item.get("easyspider", {}).get("save_mysql", True):
        return item

    pop_key_list = ["crawled_urls_path", "spider", "crawled_server", "crawled_time"]

    for key in pop_key_list:
        if key in _save_item:
            _save_item.pop(key)

    # 用什么校验，来防止重复插入
    hash_check_item = _save_item.pop("hash_check_item", None)

    if _save_item.get("easyspider"):
        easyspider_meta = _save_item.pop("easyspider")
    else:
        easyspider_meta = {}
    mysql_config = easyspider_meta.get("mysql_config") or {}

    table = table or mysql_config.get("table")
    db = db or mysql_config.get("db")
    # 兼容以前的老版写法，以前的写法是，hash_check直接写在最外面
    # 现在是如果没有发现以前的老版本写法的话，那么就使用新版本的写法
    if not hash_check_item:
        hash_check_item = mysql_config.get("hash_check_item")
    unique_key = mysql_config.get("unique_key")
    hash_check_enable = mysql_config.get("hash_check_enable", True)
    # 多处理两种模式：
    # 1. 如果数据存在，是原地更改，还是删除，以前的操作都是原地更改
    # 2. 如果要更新，是先删除再更新，还是原地更改update

    if_exists = mysql_config.get("if_exists") or "update"
    update_type = mysql_config.get("update_type'") or "inplace"

    # 最后
    error_flag = False
    error_limit = 3
    error_count = 1
    while error_count <= error_limit:
        try:
            _insert_or_update(server, _save_item, table, db, hash_check_item, unique_key, hash_check_enable, if_exists, update_type)
            error_flag = False
            break
        except Exception:
            error_flag = True
            logger.exception(u"第[%s / %s]操作数据库失败，下次再尝试" % (error_count, error_limit))
            time.sleep(2)

        error_count += 1

    # 如果最后一次还是错了，那么再来一次，还是不行，就算了
    if error_flag:
        _insert_or_update(server, _save_item, table, db, hash_check_item, unique_key, hash_check_enable)

    return item


def _insert_or_update(server, item, table=None, db=None, hash_check_item=None, unique_key="id", hash_check_enable=True, if_exists="update", update_type="inplace"):

    # 适应可以指定表的情况
    # -------------------------------------------------------------
    if not table:
        current_table = ""
    else:
        current_table = table

    if not db:
        current_db = ""
    else:
        current_db = db

    if not hash_check_item:
        # 注意，这里没有copy 因为_hash_check_item不会去改变源数据
        _hash_check_item = item
    else:
        # 有hash_check_item，重新装载
        _hash_check_item = {}
        for check_item in hash_check_item:
            _hash_check_item[check_item] = item.get(check_item)

    # 默认以 id 作为unique key
    if not unique_key:
        unique_key = "id"

    if hash_check_enable:
        # 启用hash_check_enable的话，简单直观就是去检索 hash_code
        hash_code = md5_from_dict(_hash_check_item)
        query_map = 'hash_check="%s"' % hash_code
    else:
        # 不启用，只好一个个的 and 下去
        query_map = MysqlService.join_query_map(_hash_check_item)

    check_sql = "select %s from %s.%s where %s;" % (unique_key, current_db, current_table, query_map)
    # 最终生成的查询，如果是hash_check 形式的话，那么就是原来的
    # hashcode_list = self.server.query('select id from %s.%s where hash_check="%s";' % (current_db, current_table, hash_code))
    # 如果不是 hash_check形式的话，那么就是组合的 key=value
    check_result = server.query(check_sql)
    if check_result:
        # 找到记录，那么后续的操作就是update更新
        unique_key_item = check_result[0].get(unique_key)
        if hash_check_enable:
            item["last_checktime"] = current_time()
        update_sql = server.update_sql_from_map(
            current_table, {unique_key: unique_key_item}, item, current_db)
        logger.debug(
            "already have record, update last_checktime, running sql is %s" % update_sql)
        server.execute(update_sql)
    else:
        # 找不到记录，那么就是直接插入
        if hash_check_enable:
            item["hash_check"] = hash_code
            item["last_checktime"] = current_time()
        sql = server.join_sql_from_map(
            current_table, item, current_db)
        logger.debug("find a new record, insert sql is %s" % sql)
        server.execute(sql)


# class commonMysqlpipeline(object):
class commonMysqlpipeline(commonpipeline):

    def __init__(self, settings):
        self.mysql_host = settings.get("MYSQL_HOST")
        self.mysql_user = settings.get("MYSQL_USER")
        self.mysql_password = settings.get("MYSQL_PASSWORD")
        self.mysql_port = settings.get("MYSQL_PORT")
        self.mysql_db = settings.get("MYSQL_DB")
        self.mysql_table = settings.get("MYSQL_TABLE")

        self.server = MysqlService(
            self.mysql_host, self.mysql_user, self.mysql_password, self.mysql_port)
        self.server.select_db(self.mysql_db)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    # def process_item(self, item, spider, response):
    #     d = deferToThread(self._process_item, item, spider, response)

    #     def error_back(err):
    #         # 既然出错，那么就要block_callback记录，重新放回起始队列
    #         r_copy = response.copy()
    #         r_copy.request.meta["easyspider"]["from_retry"] = 9999
    #         # 带上item 方便检查错误在哪
    #         msg = "Error processing %s ; %s" % (json.dumps(item), err.getTraceback())
    #         spider.put_back_2_start_url(response,
    #                                     exc_info=msg,
    #                                     )

    #     d.addErrback(error_back)
    #     return d

    def _process_item(self, item, spider, response):
        _save_item = item.copy()
        # 兼容以前老的写法，老的写法是，save_mysql 直接写在最外层
        # 新的规范，这些东西都会是包裹在 easyspider里面的
        # 默认是存入MySQL，所以默认值为True 来让他存入
        if not _save_item.get("save_mysql", True) or not _save_item.get("easyspider", {}).get("save_mysql", True):
            return item
        _save_item.pop("crawled_urls_path")
        # _save_item.pop("crawled_url")
        _save_item.pop("spider")
        _save_item.pop("crawled_server")
        _save_item.pop("crawled_time")
        _save_item.pop("crawled_url")
        # 用什么校验，来防止重复插入
        hash_check_item = _save_item.pop("hash_check_item", None)

        # # 兼容以前老代码的写法
        # table = None
        # db = None
        # hash_check_item = None
        # unique_key = None
        # hash_check_enable = None
        if _save_item.get("easyspider"):
            easyspider_meta = _save_item.pop("easyspider")
        else:
            easyspider_meta = {}
        mysql_config = easyspider_meta.get("mysql_config") or {}

        table = mysql_config.get("table")
        db = mysql_config.get("db")
        # 兼容以前的老版写法，以前的写法是，hash_check直接写在最外面
        # 现在是如果没有发现以前的老版本写法的话，那么就使用新版本的写法
        if not hash_check_item:
            hash_check_item = mysql_config.get("hash_check_item")
        unique_key = mysql_config.get("unique_key")
        hash_check_enable = mysql_config.get("hash_check_enable", True)
        # 最后

        """下面是为了解决 mysql has gone away 错误
        尝试了好多种办法，想从 DBService 里面解决，但是DBService 解决的话，不阻塞当前任务去循环，就只能开线程
        开线程以后，错误就没办法汇报上来了

        所以这有在这里 sleep 来操作，来尝试
        因为都欧式 deferToThread，所以来使用sleep 也就没关系
        """
        error_flag = False
        error_limit = 3
        error_count = 1
        while error_count <= error_limit:
            try:
                _copy_save_item = copy.deepcopy(_save_item)
                self._insert_or_update(_copy_save_item, spider, table, db, hash_check_item, unique_key, hash_check_enable)
                error_flag = False
                break
            except Exception:
                error_flag = True
                logger.exception(u"第[%s / %s]操作数据库失败，下次再尝试" % (error_count, error_limit))
                time.sleep(2)

            error_count += 1

        # 如果最后一次还是错了，那么再来一次，还是不行，就算了
        if error_flag:
            self._insert_or_update(_save_item, spider, table, db, hash_check_item, unique_key, hash_check_enable)

        return item
    """
    # 以前的老版本，现在更新，能在没有 hash_check 的情况下，也能 insert_or_update
    def _insert_or_update(self, item, spider, table=None, db=None, hash_check_item=None):
        if not hash_check_item:
            _hash_check_item = item
        else:
            _hash_check_item = {}
            for check_item in hash_check_item:
                _hash_check_item[check_item] = item.get(check_item)
        hash_code = md5_from_dict(_hash_check_item)

        if not table:
            # current_table = "%s.%s" % (self.mysql_db, self.mysql_table)
            current_table = self.mysql_table
        else:
            current_table = table
        if not db:
            current_db = self.mysql_db
        else:
            current_db = db
        hashcode_list = self.server.query('select id from %s.%s where hash_check="%s";' % (
            current_db, current_table, hash_code))
        if hashcode_list:
            record_id = hashcode_list[0].get("id")
            item["last_checktime"] = current_time()
            update_sql = self.server.update_sql_from_map(
                current_table, {"id": record_id}, item, current_db).replace("%", "%%")
            logger.debug(
                "already have record, update last_checktime, running sql is %s" % update_sql)
            self.server.execute(update_sql)
        else:
            item["hash_check"] = hash_code
            item["last_checktime"] = current_time()
            sql = self.server.join_sql_from_map(
                current_table, item, current_db).replace("%", "%%")
            logger.debug("find a new record, insert sql is %s" % sql)
            self.server.execute(sql)
    """

    def _insert_or_update(self, item, spider, table=None, db=None, hash_check_item=None, unique_key="id", hash_check_enable=True):

        # 适应可以指定表的情况
        # -------------------------------------------------------------
        if not table:
            current_table = self.mysql_table
        else:
            current_table = table

        if not db:
            current_db = self.mysql_db
        else:
            current_db = db

        if not hash_check_item:
            # 注意，这里没有copy 因为_hash_check_item不会去改变源数据
            _hash_check_item = item
        else:
            # 有hash_check_item，重新装载
            _hash_check_item = {}
            for check_item in hash_check_item:
                _hash_check_item[check_item] = item.get(check_item)

        # 默认以 id 作为unique key
        if not unique_key:
            unique_key = "id"

        if hash_check_enable:
            # 启用hash_check_enable的话，简单直观就是去检索 hash_code
            hash_code = md5_from_dict(_hash_check_item)
            query_map = 'hash_check="%s"' % hash_code
        else:
            # 不启用，只好一个个的 and 下去
            query_map = MysqlService.join_query_map(_hash_check_item)

        check_sql = "select %s from %s.%s where %s;" % (unique_key, current_db, current_table, query_map)
        # 最终生成的查询，如果是hash_check 形式的话，那么就是原来的
        # hashcode_list = self.server.query('select id from %s.%s where hash_check="%s";' % (current_db, current_table, hash_code))
        # 如果不是 hash_check形式的话，那么就是组合的 key=value
        check_result = self.server.query(check_sql)
        if check_result:
            # 找到记录，那么后续的操作就是update更新
            unique_key_item = check_result[0].get(unique_key)
            if hash_check_enable:
                item["last_checktime"] = current_time()
            # update_sql = self.server.update_sql_from_map(
            #     current_table, {unique_key: unique_key_item}, item, current_db).replace("%", "%%")
            update_sql = self.server.update_sql_from_map(
                current_table, {unique_key: unique_key_item}, item, current_db)
            logger.debug(
                "already have record, update last_checktime, running sql is %s" % update_sql)
            self.server.execute(update_sql)
        else:
            # 找不到记录，那么就是直接插入
            if hash_check_enable:
                item["hash_check"] = hash_code
                item["last_checktime"] = current_time()
            sql = self.server.join_sql_from_map(
                current_table, item, current_db)
            logger.debug("find a new record, insert sql is %s" % sql)
            self.server.execute(sql)
