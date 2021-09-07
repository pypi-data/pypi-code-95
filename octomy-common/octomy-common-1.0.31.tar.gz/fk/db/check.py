import psycopg2
import logging

from .DatabaseConnection import DatabaseConnection

logger = logging.getLogger(__name__)


class DatabaseCheck:
    def __init__(self, config):
        self.config = config
        self.dbc = DatabaseConnection.get_connection(self.config)
        assert self.dbc.is_ok()
        self.create_tables()

    def create_tables(self):
        # Create a table to keep track of test items
        self.dbc.query_none(
            """
            create table if not exists "test_access" (
                id serial primary key,
                created_at timestamptz not null default now(),
                updated_at timestamptz not null default now()
            );
            comment on column test_access.id is 'Unique internal id for this item';
            comment on column test_access.created_at is 'When the item was first created';
            comment on column test_access.updated_at is 'When the item was last updated';
            """
        )

    # Insert a new test acceess item into db
    def insert_item(self):
        return self.dbc.query_one(
            """
                insert into test_access default values
                returning id
                ;
                """
        )

    # Get counts of test acceess
    def get_counts(self):
        return self.dbc.query_one(
            """
                select count(*) as count
                from test_access
                ;
                """
        )

    # Get current time from db
    def get_now(self):
        return self.dbc.query_one(
            """
                select now() as now;
                """
        )

    def verify_old(self):
        try:
            count1 = self.get_counts()
            if count1 is None:
                logger.warning("Could not get first count")
                return False
            self.insert_item()
            count2 = self.get_counts()
            if count2 is None:
                logger.warning("Could not get second count")
                return False
            # logger.info(f"count1: {count1}, count2: {count2}")
            return count2.get("count", 0) > count1.get("count", 0)
        except Exception as e:
            logger.warning(f"Unknown error '{e}':", exc_info=True)
            return False

    def verify(self):
        try:
            now = self.get_now()
            return True
        except Exception as e:
            logger.warning(f"Unknown error '{e}':", exc_info=True)
            return False
