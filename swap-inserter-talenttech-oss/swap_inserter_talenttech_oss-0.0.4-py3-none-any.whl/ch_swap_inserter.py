from abc import ABC
from clickhouse_balanced import Client

from inserter.swap_inserter import SwapInserter


class CHSwapInserter(SwapInserter, ABC):
    def __init__(
        self, script, sql_credentials, insert_table=None, add_args=None
    ):
        SwapInserter.__init__(
            self,
            script=script,
            sql_credentials=sql_credentials,
            insert_table=insert_table,
            add_args=add_args,
        )
        self.ch_client = Client(**self.sql_credentials)
        self.database = self.sql_credentials["database"]
        self.temp_table = f"{self.database}._temp_{self.insert_table}"

    def __get_table_engine(self, database, table):
        get_engine_stat = """SELECT engine, partition_key, sorting_key
                 from system.tables
                 where name = '{name}'
                       and database = '{database}'""".format(
            name=table, database=database
        )
        try:
            res = self.ch_client.execute(get_engine_stat)[0]
        except IndexError:
            raise ModuleNotFoundError(f"Error. Table {database}.{table} doesnt't exist")
        self.logger.info(get_engine_stat)
        return res[0].replace("Replicated", ""), res[1], res[2]

    def create_temporary_table(self):
        engine, partition_key, sorting_key = self.__get_table_engine(
            self.database, self.insert_table
        )
        drop_stat = f"DROP TABLE IF EXISTS {self.temp_table}"
        create_stat = f"CREATE TABLE {self.temp_table} ENGINE = {engine}() PARTITION BY  {partition_key} ORDER BY ({sorting_key}) AS {self.database}.{self.insert_table}"
        self.logger.info(drop_stat)
        self.ch_client.execute(drop_stat)
        self.logger.info(create_stat)
        self.ch_client.execute(create_stat)

    def insert_into_temporary_table(self):
        insert_stat = self._insert_stat()
        self.logger.info(insert_stat)
        self.ch_client.execute(insert_stat)

    def truncate_main_table(self):
        truncate_stat = self._truncate_stat()
        self.logger.info(truncate_stat)
        self.ch_client.execute(truncate_stat)

    def swap_temporary_to_main(self):
        swap_stat = f"INSERT INTO {self.database}.{self.insert_table} SELECT * FROM {self.temp_table}"
        self.logger.info(swap_stat)
        self.ch_client.execute(swap_stat)

    def drop_temporary_table(self):
        drop_temp_stat = f"DROP TABLE {self.temp_table}"
        self.logger.info(drop_temp_stat)
        self.ch_client.execute(drop_temp_stat)
