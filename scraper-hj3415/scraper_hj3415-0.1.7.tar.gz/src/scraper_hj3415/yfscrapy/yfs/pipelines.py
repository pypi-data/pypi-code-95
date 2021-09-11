# reference from https://livedata.tistory.com/27?category=1026425 (scrapy pipeline usage)
from . import items
from db_hj3415 import mongo, setting, sqlite


import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class MongoPipeline:
    # 몽고 데이터 베이스에 저장하는 파이프라인
    def __init__(self):
        self.mongo_addr = setting.load()['mongo']
        logger.info(f"mongodb addr : {self.mongo_addr}")

    def process_item(self, item, spider):
        if self.mongo_addr != '':
            if isinstance(item, items.C103items):
                page = ''.join(['c103', item['title']])
                print(f"\tIn the {self.__class__.__name__}...ticker : {item['ticker']} / page : {page}")
                # 코드는 6자리숫자인 문제해결
                # mongo.C103(code=item['ticker'], page=page).save(c103_list=item['df'].to_dict('records'))
            return item
        else:
            print(f"\tIn the {self.__class__.__name__}...skipping save to db ")
            return item


class SqlitePipeline:
    # Sqlite3 데이터 베이스에 저장하는 파이프라인
    def __init__(self):
        self.sqlite3_addr = setting.load()['sqlite3']
        logger.info(f"sqlite3db addr : {self.sqlite3_addr}")

    def process_item(self, item, spider):
        if self.sqlite3_addr != '':
            if isinstance(item, items.C103items):
                page = ''.join(['c103', item['title']])
                print(f"\tIn the {self.__class__.__name__}...ticker : {item['ticker']} / page : {page}")
                # 코드는 6자리숫자인 문제해결
                # sqlite.C103(code=item['ticker'], page=page).save(c103_df=item['df'])
            return item
        else:
            print(f"\tIn the {self.__class__.__name__}...skipping save to db ")
            return item