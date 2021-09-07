import json
import os
import sqlite3
import pprint
import psycopg2
import psycopg2.extras
import traceback
import sys
import logging

import pytz
from fk.utils import *
from pprint import pformat

logger = logging.getLogger(__name__)


class DatabaseConnection:

    # Global connection
    connection_instance = None

    def __init__(self, config):
        self.config = config
        self.db_hostname = self.config.get("db-hostname", None)
        self.db_port = self.config.get("db-port", None)
        self.db_username = self.config.get("db-username", None)
        self.db_password = self.config.get("db-password", None)
        self.db_database = self.config.get("db-database", None)
        self.db = None
        connstr = f"postgres://{self.db_username}:{redact(self.db_password)}@{self.db_hostname}:{self.db_port}/{self.db_database}"
        logger.info(f"DATABASE: {connstr}")
        self.connection_error = None
        self._prepare_db()

    def __del____(self):
        self._unprepare_db()

    def is_ok(self):
        return self.db_hostname and self.db_port and self.db_username and self.db_password and self.db_database

    @staticmethod
    def get_connection(config):
        if not DatabaseConnection.connection_instance:
            DatabaseConnection.connection_instance = DatabaseConnection(config)
        return DatabaseConnection.connection_instance

    def _unprepare_db(self):
        if self.db:
            try:
                # Make sure data is stored
                self.db.commit()
                self.db.close()
            except Exception as e1:
                pass
            try:
                del self.db
            except Exception as e2:
                pass
            self.db = None
            logger.info("PostgreSQL connection is closed")

    # Internal helper to connect to database
    def _prepare_db(self):
        try:
            self.db = psycopg2.connect(host=self.db_hostname, port=self.db_port, user=self.db_username, password=self.db_password, database=self.db_database)

            # Create a cursor to let us work with the database
            with self.db:
                with self.db.cursor() as c:
                    # logger.info( self.db.get_dsn_parameters(),"\n")

                    c.execute("SELECT version();")
                    record = c.fetchone()
                    logger.info(f"Connected to: {record[0]}\n")
                    return True

        except (Exception, psycopg2.Error) as error:
            logger.warning("###   ###   ###   ###   ###   ###   ###   #")
            logger.warning("##   ###   ###   ###   ###   ###   ###   ##")
            logger.warning("")
            logger.warning(f"Error while connecting to PostgreSQL {error}")
            self.connection_error = error
            self._unprepare_db()
        return False

    def _query(self, query, data={}, mode="none"):
        cursor = None
        try:
            if not self.db:
                logger.warning("###   ###   ###   ###   ###   ###   ###   #")
                logger.warning("##   ###   ###   ###   ###   ###   ###   ##")
                logger.warning("")
                logger.warning("No database while making query")
                if self.connection_error:
                    logger.warning(f"Connection error was {self.connection_error}")
                else:
                    logger.warning("No connection error was set, did we even try to connect?")
            with self.db:
                with self.db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(query, data)
                    if mode == "many":
                        res = cursor.fetchall()
                        # Convert to real dictionaries
                        if res is None:
                            return None
                        out = []
                        for row in res:
                            out.append(dict(row))
                        return out
                    elif mode == "one":
                        res = cursor.fetchone()
                        if res is None:
                            return None
                        return dict(res)
                    elif mode == "exists":
                        res = cursor.fetchone()
                        return res is not None
                    else:
                        return
        except Exception as e:
            logger.error("")
            logger.error("")
            logger.error(f"###############################################")
            logger.error(f"#    Querying: {query}")
            if cursor and cursor.query:
                logger.error(f"#    Injected: {cursor.query.decode()}")
            logger.error(f"#         For: {mode}")
            logger.error(f"# Failed with:")
            if isinstance(e, psycopg2.InterfaceError):
                logger.error(f"# + Connection error({type(e).__name__}): e={e} ")
            elif isinstance(e, psycopg2.Error):
                logger.error(f"# + e={e} ({type(e).__name__})")
                logger.error(f"# + e.pgerror:{e.pgerror}")
                logger.error(f"# + e.pgcode: {e.pgcode}")
                logger.error(f"# + e.cursor: {e.cursor}")
                if e.diag:
                    logger.error(f"# + e.diag:")
                    logger.error(f"#   + column_name:             {e.diag.column_name}")
                    logger.error(f"#   + constraint_name:         {e.diag.constraint_name}")
                    logger.error(f"#   + context:                 {e.diag.context}")
                    logger.error(f"#   + datatype_name:           {e.diag.datatype_name}")
                    logger.error(f"#   + internal_position:       {e.diag.internal_position}")
                    logger.error(f"#   + internal_query:          {e.diag.internal_query}")
                    logger.error(f"#   + message_detail:          {e.diag.message_detail}")
                    logger.error(f"#   + message_hint:            {e.diag.message_hint}")
                    logger.error(f"#   + message_primary:         {e.diag.message_primary}")
                    logger.error(f"#   + schema_name:             {e.diag.schema_name}")
                    logger.error(f"#   + severity:                {e.diag.severity}")
                    logger.error(f"#   + source_file:             {e.diag.source_file}")
                    logger.error(f"#   + source_function:         {e.diag.source_function}")
                    logger.error(f"#   + source_line:             {e.diag.source_line}")
                    logger.error(f"#   + sqlstate:                {e.diag.sqlstate}")
                    logger.error(f"#   + statement_position:      {e.diag.statement_position}")
                    logger.error(f"#   + table_name:              {e.diag.table_name}")
                    logger.error(f"#   + severity_nonlocalized:   {e.diag.severity_nonlocalized}")
            else:
                logger.error(f"# + NON DB ERROR({type(e).__name__}): e={e} ")
            logger.error(f"#          At:")
            traceback.print_exception(type(e), e, e.__traceback__)
            logger.error(f"#       Stack:")
            traceback.print_stack()
            logger.error(f"#       Using data:")
            logger.error(pprint.pformat(data))
            logger.error(f"#######################################")
            logger.error("")
            logger.error("")

    def query_many(self, query, data={}):
        return self._query(query, data, "many")

    def query_one(self, query, data={}):
        return self._query(query, data, "one")

    def query_none(self, query, data={}):
        return self._query(query, data, "none")

    def query_exists(self, query, data={}):
        return self._query(query, data, "exists")
