from abc import ABC
from inserter.swap_inserter import SwapInserter

from vconnector.vertica_connector import VerticaConnector


class VerticaSwapInserter(SwapInserter, ABC):
    def __init__(
            self,
            script,
            sql_credentials,
            insert_table=None,
            add_args=None
    ):
        SwapInserter.__init__(
            self,
            script=script,
            sql_credentials=sql_credentials,
            insert_table=insert_table,
            add_args=add_args,
        )
        self.database = self.sql_credentials["schema"]
        self.staging_schema = self.sql_credentials["staging_schema"]
        self.temp_table = f"{self.staging_schema}.{self.insert_table}"

    def __exec_sql(self, statement):
        with VerticaConnector(
                user=self.sql_credentials["user"],
                password=self.sql_credentials["password"],
                database=self.sql_credentials["database"],
                vertica_configs=self.sql_credentials["vertica_configs"],
                sec_to_recconect=2,
                count_retries=1,
        ) as v_connector:
            v_connector.exec_multiple_sql([statement])

    def create_temporary_table(self):
        drop_stat = f"DROP TABLE IF EXISTS {self.temp_table}"
        create_stat = f"CREATE TABLE {self.temp_table} LIKE {self.database}.{self.insert_table}"
        self.logger.info(drop_stat)
        self.__exec_sql(drop_stat)
        self.logger.info(create_stat)
        self.__exec_sql(create_stat)

    def insert_into_temporary_table(self):
        insert_stat = self._insert_stat()
        self.logger.info(insert_stat)
        self.__exec_sql(insert_stat)

    def truncate_main_table(self):
        truncate_stat = self._truncate_stat()
        self.logger.info(truncate_stat)
        self.__exec_sql(truncate_stat)

    def swap_temporary_to_main(self):
        swap_stat = f"INSERT INTO {self.database}.{self.insert_table} SELECT * FROM {self.temp_table}"
        self.logger.info(swap_stat)
        self.__exec_sql(swap_stat)

    def drop_temporary_table(self):
        drop_temp_stat = f"DROP TABLE {self.temp_table}"
        self.logger.info(drop_temp_stat)
        self.__exec_sql(drop_temp_stat)
