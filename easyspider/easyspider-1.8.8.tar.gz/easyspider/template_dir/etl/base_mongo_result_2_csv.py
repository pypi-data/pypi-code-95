# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-19 09:08:33
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-07-27 15:46:56
from base_etl import base_etl
from dbConn_for_etl import join_insert_sql_for_print
import logging
logger = logging.getLogger(__name__)

"""
python base_mongo_result_2_csv.py -mongo-collection noaaCrawler
"""
class base_mongo_result_2_csv(base_etl):

    def run(self):
        args = self.parse_cmd()

        logger.info("start connect mongo & get result")
        mongo_result = self.get_mongo_all_result(
            args.mongo_url, args.mongo_db_name, args.mongo_collection)

        # 一般来说拿出来mongo里面的内容要个性化解析之后，才能存到redis里面作为起始链接
        logger.info(
            "get mongo data successed, get %d mongo result, now start clean mongo result" % len(mongo_result))
        clean_result = self.parse_mongo_result(mongo_result)

        logger.info(
            "clean mongo result successed, now mongo result count is %d, now start convert mongo result -> sheet" % len(clean_result))
        sheet_result = [self._convert_mongo_2_sheet(result, args.interval, filter_callback=self.filter_sheet).copy() for result in clean_result]

        if not args.csv_file:
        	args.csv_file = "result_csv_%s.csv" % args.mongo_collection
        self.write_2_csv_file(sheet_result, args.csv_file, args.csv_split_symbol)

        logger.info("all successed !")

    # 这个函数子类可以覆盖，来达到个性化解析mongodb内容的效果
    # 默认情况是，是只提取mongo里面的url字段，并且不做处理直接插入
    # 一种虽然只需要url字段但是需要处理的情况是：url某个字段错了，需要批量替换
    def parse_mongo_result(self, mongo_result):
        # 都需要去除_id字段
        map(lambda result: result.pop("_id"), mongo_result)
        return mongo_result

    def write_2_csv_file(self, result_sheets, csv_file, csv_split_symbol):
        fields = set()
        for result in result_sheets:
            for k in result.keys():
                fields.add(k)
        fields = list(fields)
        with open(csv_file, "w") as f:
        	f.write("%s\n" % csv_split_symbol.join(fields))
        	# f.write("%s\n" % csv_split_symbol.join([ result.get(key,"None")  for key in fields  for result in result_sheets]))
        	for result in result_sheets:
        		f.write("%s\n" % csv_split_symbol.join([result.get(key, "None").replace("\n", "") for key in fields]))

    def filter_sheet(self, key_name):
    	# if key_name in ("detail", "bottom_table"):
    	# 	return False
    	return True
if __name__ == '__main__':
    base_mongo_result_2_csv().run()
