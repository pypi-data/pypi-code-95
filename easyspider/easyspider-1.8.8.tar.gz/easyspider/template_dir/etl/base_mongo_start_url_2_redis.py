# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-18 17:23:00
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-07-18 18:12:07

from base_etl import base_etl
from dbConn_for_etl import BaseRedis
import logging
logger = logging.getLogger(__name__)

"""
python base_mongo_result_2_mysql.py -mongo-collection medicine_all
"""
class base_mongo_start_url_2_redis(base_etl):

    def run(self):
        args = self.parse_cmd()
        
        logger.info("start connect mongo & get result")
        mongo_result = self.get_mongo_all_result(args.mongo_url, args.mongo_db_name, args.mongo_collection)

        # 一般来说拿出来mongo里面的内容要个性化解析之后，才能存到redis里面作为起始链接
        logger.info("get mongo data successed, get %d mongo result, now start clean mongo result" % len(mongo_result))
        clean_result = self.parse_mongo_result(mongo_result)
        
        logger.info("clean mongo result successed, now mongo result count is %d, now start load clean result to redis" % len(clean_result))
        # 如果没有给定redis的名
        if not args.redis_key:
        	args.redis_key = "next_%s:start_urls" % args.mongo_collection
        self.load_clean_result_2_redis(args.redis_url, args.redis_key, clean_result)

        logger.info("all successed !")

    # 这个函数子类可以覆盖，来达到个性化解析mongodb内容的效果
    # 默认情况是，是只提取mongo里面的url字段，并且不做处理直接插入
    # 一种虽然只需要url字段但是需要处理的情况是：url某个字段错了，需要批量替换
    def parse_mongo_result(self, mongo_result):
        clean_result = [{"url": line.get("url")} for line in mongo_result]
        return clean_result

    def load_clean_result_2_redis(self, redis_url, redis_key, clean_result):
        server = BaseRedis(redis_url)
        server.rpush(redis_key, clean_result)



if __name__ == '__main__':
    base_mongo_start_url_2_redis().run()
