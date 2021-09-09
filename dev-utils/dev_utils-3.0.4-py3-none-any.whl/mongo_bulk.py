from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
import time


class MongoDB:
    def __init__(self, host=None, port=None, username=None, password=None):
        if password and username:
            self._conn = MongoClient("mongodb://{}:{}@{}:{}".format(username, password, host, port))
        else:
            self._conn = MongoClient("mongodb://{}:{}".format(host, port))

    def get_col(self, class_):
        split = class_.split("_")
        if len(split) != 2:
            raise IndexError("parse_class error,need like this 'dbname_tablename', input was {}".format(class_))
        return self._conn[split[0]][split[1]]

    def bulk_upsert(self, items, class_):
        if not items:
            print("[Warning] upsert bulk items == [].")
            return
        col = self.get_col(class_)
        operations = []
        for item in items:
            op = UpdateOne(
                {
                    '_id': item['_id']
                },
                {
                    '$set': item
                },
                upsert=True
            )
            operations.append(op)
        start_time = time.time()
        try:
            ret = col.bulk_write(operations, ordered=False)
            diff_time = time.time() - start_time
            print('class {}, cost {}, inserted {}, modified {}, duplicated {}'
                  .format(class_, diff_time, ret.upserted_count, ret.modified_count, 0))
            return ret.upserted_count, ret.modified_count, 0
        except BulkWriteError as bwe:
            inserted = bwe.details['nUpserted']
            modified = bwe.details['nModified']
            duplicated = len(items) - inserted - modified
            diff_time = time.time() - start_time
            print('class {}, cost {}, inserted {}, modified {}, duplicated {}'
                  .format(class_, diff_time, inserted, modified, duplicated))
            return inserted, modified, duplicated
