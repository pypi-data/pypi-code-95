# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-03-05 20:20:45
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-04-03 14:13:41

# 历史负担真是重啊....为什么说 unexcept argument...原来是引用错包了
# from easyspider.utils.DBService import MongoService
from DBService import MongoService
from easyspider.pipelines.commonpipeline import commonpipeline
import logging
import time
logger = logging.getLogger(__name__)

# 存入mongo的collection的key名
item_result_table_key = "result_table"
# 存入的操作是update还是直接insert
item_update_key = "update_record"
item_update_query_key = "update_query_key"
# 存入的时候是否需要新建一个collections来保存历史记录
item_keep_history = "keep_history"
# 存入库的名字，如果没有指定库，那么就以spider名字来命名
item_save_db = "save_db"

default_mongo_url = "mongodb://localhost:27017"
default_mongo_db_name = "spider"

mongo_url_key = "MONGO_URL"
mongo_db_name = "MONGO_DB_NAME"

# ----------------------------------------
# 上面这一段，是历史原因保留
# ----------------------------------------


class commonMongopipeline(commonpipeline):

    def __init__(self, mongoUrl, mongoDbName):
        self.server = MongoService(mongoUrl)
        self.server.select_db(mongoDbName)

    @classmethod
    def from_settings(cls, settings):
        mongoUrl = settings.get(mongo_url_key, default_mongo_url)
        mongoDbName = settings.get(mongo_db_name, default_mongo_db_name)
        return cls(mongoUrl, mongoDbName)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def _process_item(self, item, spider, response, db=None, collection=None, update=False, hash_check_item=None, hash_check_item_dict_type=False):

        # 解析返回结果里面的控制状态,注意是有两层
        easyspider_meta = item.get("easyspider", {}).get("mongo_config", {})
        if not easyspider_meta:
            # 兼容以前的老的写法
            easyspider_meta = item.get("easyspider", {}).get("save_mongo", {})
        # print "\n\n\n", easyspider_meta, "\n\n"

        # 解析控制状态
        db = easyspider_meta.get("db")
        collection = easyspider_meta.get("collection")
        # 是否打开insert_or_update
        update = easyspider_meta.get("update")
        hash_check_item = easyspider_meta.get("hash_check_item")
        hash_check_item_dict_type = easyspider_meta.get("hash_check_item_dict_type")
        force_replace = easyspider_meta.get("force_replace")

        error_flag = False
        error_limit = 3
        error_count = 1
        while error_count <= error_limit:
            try:
                self._insert_or_update(item, spider, db, collection, update, hash_check_item, hash_check_item_dict_type, force_replace)
                error_flag = False
                break
            except Exception:
                error_flag = True
                logger.exception(u"第[%s / %s]操作数据库失败，下次再尝试" % (error_count, error_limit))
                time.sleep(2)

            error_count += 1

        # 如果最后一次还是错了，那么再来一次，还是不行，就算了
        if error_flag:
            self._insert_or_update(item, spider, db, collection, update, hash_check_item, hash_check_item_dict_type, force_replace)

        return item

    def _insert_or_update(self, item, spider, db=None, collection=None, update=False, hash_check_item=None, hash_check_item_dict_type=False, force_replace=None):
        # 避免改变原值
        _save_item = item.copy()

        # 选择指定的库
        if not db:
            self.server.select_db(_save_item.get(item_save_db, spider.name))
        else:
            self.server.select_db(db)

        # print "sleect db %s" % db

        # 选择指定的集合
        if not collection:
            collection = _save_item.get(item_result_table_key, spider.name)

        # 如果不是更新操作的话，那么很简单的直接插入就可以了
        if not update:
            self.server.insert(collection, _save_item)
            return item

        # 更新有两种，第一种是全盘更新，全盘覆盖，也就是 replace
        # 另外一种就是指定列的update 不影响其他的列
        # 默认为部分更新
        if not force_replace:
            # 如果没有指定，或者force_repalce为False
            force_replace = False
        else:
            force_replace = True

        # 如果是更新操作，那么就比较麻烦了

        if hash_check_item_dict_type:
            # 如果更新操作，是给定了一个特定的值，也就是替换的，不是现有的item的特定值
            last_result = hash_check_item
        else:
            # 如果是根据现在给出的结果，进行搜索替换的话
            last_result = {}
            for k in hash_check_item:
                last_result[k] = _save_item.get(k)
        # print "last_result %s , _save_item %s" % (last_result, _save_item)
        # upsert = True 控制没有就是新增

        # 这里要判断，到底是替换，还是部分更新
        if force_replace:
            self.server.replace_one(collection, last_result, _save_item, upsert=True)
        else:
            self.server.update_one(collection, last_result, {"$set": _save_item}, upsert=True)

        # 最后替换操作完成了之后再来返回
        return item
