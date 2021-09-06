import ssl
import os
from pymongo import MongoClient
from loguru import logger
import upswingutil as ul

__PII_FIELDS__ = ['guestGiven', 'guestSurname', 'mobile', 'passportId', 'email', 'email2']


class Mongodb:
    RESOURCE_COLLECTION = 'resource'
    AREAS_COLLECTION = "areas"
    GUEST_COLLECTION = "guests"
    PROPERTY_COLLECTION = "properties"
    RESERVATION_COLLECTION = "reservations"
    TRANSACTION_COLLECTION = "transactions"
    AREA_REPORTS_BY_DAY_COLLECTION = "area_report_by_day"
    COUNTRIES_COLLECTION = 'countries'
    ORG_CONFIG_COLLECTION = 'org_config'
    COUNTERS_COLLECTION = 'counters'
    EVENTS_COLLECTION = 'events'
    DAILY_REPORTS_COLLECTION = 'daily_reports'

    def __init__(self, db_name):
        try:
            self.db_name = str(db_name)
            self.client = MongoClient(
                os.getenv('MONGO_URI', ul.MONGO_URI),
                ssl_cert_reqs=ssl.CERT_NONE
            )
            self.db = self.client[str(db_name)]
        except Exception as e:
            logger.error('Error while connecting to db')
            logger.error(e)

    def get_collection(self, name):
        try:
            return self.db[name]
        except Exception as e:
            logger.error('Error while connecting to db')
            logger.error(e)

    def execute_pipeline(self, name: str, pipeline: list):
        try:
            return list(self.db.get_collection(name).aggregate(pipeline))
        except Exception as e:
            logger.error('Error while executing pipeline')
            logger.error(e)

    def close_connection(self):
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            logger.error('Error while closing connection to db')
            logger.error(e)


if __name__ == '__main__':
    mongo = Mongodb('11249')
    val = mongo.get_collection(mongo.GUEST_COLLECTION).count()
    print(val)
    mongo.close_connection()