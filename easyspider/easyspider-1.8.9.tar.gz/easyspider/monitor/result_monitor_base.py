# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-17 11:32:39
# @Last Modified by:   zhangTian
# @Last Modified time: 2017-07-18 01:01:08
import sys
sys.path.append("../easyspider/utils")
sys.path.append("../easyspider")

from dbConn_for_etl import MongoConnect, BaseRedis
import argparse
import settings
from tools import get_time
from apscheduler.schedulers.blocking import BlockingScheduler
"""

1. 先取出现在的mongo结果
2. 从redis或者其他存储中取出历史的结果
3. 比较两个结果，新就更新
4. 把比较的结果存入存储中

历史结果存入mysql 待定
"""

class result_monitor_base(object):

    # 解析命令行参数，数据库连接
    def __init__(self):
        self.args = self.parse_args()
        # 连接mongo
        self.mongo_server = self.get_mongo_connect(self.args.mongo_url, self.args.mongo_db_name)
        # 连接redis
        self.redis_server = BaseRedis(self.args.redis_url)
        # 需要关注的collections 集合
        # 操他妈的...集合是会变动的怎么能写死！！弄得还以为是pymongo有缓存了呢
        # self.mongo_collections = self.get_mongo_collections()

    def parse_args(self):
        parser = argparse.ArgumentParser(description="结果监控服务")
        parser.add_argument("-r", "--redis-url", help="redis连接地址，默认从settings文件中读取")
        parser.add_argument("-m", "--mongo-url", help="mongodb连接地址，默认从settings文件中读取")
        parser.add_argument("-d", "--mongo-db-name", help="mongodb的数据库，默认从settings文件中读取")
        parser.add_argument("-c", "--mongo-collection", help="mongodb的集合名，默认为该数据库下的全部监控")
        parser.add_argument("-k", "--redis-key", help="存储历史mongo结果的redis key，默认从settings文件中读取")
        args = parser.parse_args()

        if not args.redis_url:
            args.redis_url = settings.REDIS_URL if hasattr(settings, "REDIS_URL") else "redis://127.0.0.1:6379"

        if not args.mongo_url:
            args.mongo_url = settings.MONGO_URL if hasattr(settings, "MONGO_URL") else "mongodb://127.0.0.1:27017/"

        if not args.mongo_db_name:
            args.mongo_db_name = settings.MONGO_DB_NAME if hasattr(settings, "MONGO_DB_NAME") else "easyspider"

        if not args.redis_key:
            args.redis_key = "easyspider:mongo_result_state"

        return args

    def get_mongo_connect(self, mongo_url, mongo_db_name):
        server = MongoConnect(self.args.mongo_url)
        server.select_db(self.args.mongo_db_name)
        return server

    def get_mongo_collections(self):
        if self.args.mongo_collection:
            return [self.args.mongo_collection]
        return self.mongo_server.list_all_collections()

    def run(self):
        # 集合会变动，每次都要重新查询有多少个集合
        mongo_collections = self.get_mongo_collections()
        # 查询出当前的mongo 结果记录
        current_mongo_result_state = self.get_current_mongo_result_state(mongo_collections)
        # 查询出上一次结果记录(注意如果没有记录上一次变更时间数据的话，那么就以当前的为准)
        last_mongo_result_state = self.get_last_mongo_result_state()
        # 解析当前的mongo进度
        mongo_result_rate = self.parse_mongo_result_rate(current_mongo_result_state, last_mongo_result_state)
        # 将进度存入
        self.dumps_current_mongo_reulst_state(mongo_result_rate)

    def get_current_mongo_result_state(self, mongo_collections):
        info = {}
        for c in mongo_collections:
            current_mongo_result_count = self.mongo_server.collection_count(c)
            info[c] = {
                "result_count": current_mongo_result_count,
                "check_time": get_time()
            }
        return info

    def get_last_mongo_result_state(self):
        return self.redis_server.hgetall(self.args.redis_key)[1]

    def parse_mongo_result_rate(self, current_mongo_result_state, last_mongo_result_state):
        # 不能用老记录去更新。因为在最开始，老记录是没有的
        # 但是使用新记录去更新，又会存在，如果新记录少了删除了，老记录不能被发现的问题
        # 那么就预先检查一次，新纪录没有了，老记录中有的，就置0

        # 老记录检查是否有删除的项目
        for k in last_mongo_result_state.keys():
            if not current_mongo_result_state.get(k):
                last_mongo_result_state[k] = None

        for k, v in current_mongo_result_state.items():
            # 历史记录，因为写入的时候是按照逗号分隔的
            # 第一列代表当前的值，第二列代表当前更新时间，第三列代表上次更新值，第四列代表浮动，第五列代表变更时间
            # 上次计数
            last_count =  last_mongo_result_state.get(k, "0,0,0,0,0").split(",")[0]
            # 上次检查时间
            last_check_time = last_mongo_result_state.get(k, "0,0,0,0,0").split(",")[1]
            # 上次变更时间
            last_modify_time = last_mongo_result_state.get(k, "0,0,0,0,0").split(",")[4]
            # 当前计数
            current_count = v.get("result_count")
            current_check_time = v.get("check_time")
            # 和历史记录比较的浮动 当前数目 - 上次存储的当前数目
            increase_count = int(current_count) - int(last_count)
            # 如果为0, 说明上次的记录没有变化，变更时间是上次的，不然的话，变更时间就是现在，当前变更
            modify_time = last_modify_time if increase_count == 0 else current_check_time

            current_result_state = "%s,%s,%s,%s,%s" % (current_count, current_check_time, last_count, increase_count, modify_time)
            last_mongo_result_state[k] = current_result_state
        return last_mongo_result_state


    def dumps_current_mongo_reulst_state(self, mongo_result_rate):
        for collection, values in mongo_result_rate.items():
            # 为空说明这里的集合已经在mongo中被删除
            if not values:
                # print "del %s" % collection
                self.redis_server.hdel(self.args.redis_key, collection)
            else:
                # print "update %s" % collection
                self.redis_server.hset(self.args.redis_key, collection, values)


if __name__ == '__main__':
    server = result_monitor_base()
    # server.run()
    scheduler = BlockingScheduler(daemonic=True)
    scheduler.add_job(server.run, 'interval', seconds=20)
    scheduler.start()
    # import time
    # while True:
    #     server.run()
    #     time.sleep(10)
    #     print "-------"

