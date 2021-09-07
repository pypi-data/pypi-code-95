from influxdb import InfluxDBClient
from pprint import pformat
import traceback
import logging

logger = logging.getLogger(__name__)


# Helper class to manage influxdb
class Influx:
    def __init__(self, credentials):
        logger = setup_logging(self.__class__.__name__)
        self.credentials = credentials
        self.client = InfluxDBClient(self.credentials["influx-hostname"], self.credentials["influx-port"], self.credentials["influx-username"], self.credentials["influx-password"], self.credentials["influx-dbname"])
        self.client.create_database(self.credentials["influx-dbname"])
        self.transaction_points = None
        self.transaction_tags = {}
        self.transaction_time_precision = "ms"

    # Begin super basic transaction
    def begin_transaction(self, time_precision="ms"):
        if None is not self.transaction_points:
            logger.error("Another transaction is in progress, aborting")
            return False
        self.transaction_points = []
        self.transaction_tags = {}
        self.transaction_time_precision = time_precision
        return True

    # Add point to super basic transaction
    def add_point_transaction(self, measurement, time, tags={}, fields={}):
        if None is self.transaction_points:
            logger.error("Transaction not started, aborting")
            return False
        # Keep tags in set
        for key, val in tags.items():
            self.transaction_tags[key] = val
        # Keep point
        point_body = {"measurement": measurement, "tags": tags, "time": time, "fields": fields}
        self.transaction_points.append(point_body)
        return True

    # Commit super basic transaction
    def commit_transaction(self):
        ret = False
        if self.transaction_points is not None:
            try:
                ret = self.client.write_points(points=self.transaction_points, time_precision=self.transaction_time_precision, tags=self.transaction_tags)
            except Exception as e:
                logger.error(f" ")
                logger.error(f"#########################################################")
                logger.error(f"## ERROR: Could not commit influx transaction")
                logger.error(f"## Transaction details':")
                logger.error(f"##")
                logger.error(f"## time_precision={self.transaction_time_precision}")
                logger.error(f"## points=")
                logger.error(pformat(self.transaction_points))
                logger.error(f"## tags=")
                logger.error(pformat(self.transaction_tags))
                logger.error(f"##")
                logger.error(f"## {e}:")
                logger.error(f"##")
                traceback.print_exc()
                logger.error(f"##")
                logger.error(f"#########################################################")
                logger.error(f" ")
            self.transaction_points = None
            self.transaction_tags = {}
        return ret

    # Simple single point insertion
    def put_point(self, measurement, time, tags={}, fields={}):
        body = [{"measurement": measurement, "tags": tags, "time": time, "fields": fields}]
        return self.client.write_points(body)

    # Perform query
    def query(self, q):
        return self.client.query(q)
