import sys
import logging


class SwapInserter:
    def __init__(self, script, sql_credentials, insert_table=None, add_args=None):
        """

        :param script:   script for inserting
        :param sql_credentials:
        :param insert_table:
        :param add_args: additional arguments for replacing in code
        """
        log_format = "%(asctime)-15s %(name)s:%(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
        logging.basicConfig(format=log_format, stream=sys.stderr, level=logging.ERROR)
        logging.captureWarnings(True)
        self.logger = logging.getLogger(__class__.__name__)

        self.insert_table = insert_table
        self.sql_credentials = sql_credentials
        self.script = script
        self.add_args = add_args or {}

    def run(self):
        self.create_temporary_table()
        self.insert_into_temporary_table()
        self.truncate_main_table()
        self.swap_temporary_to_main()
        self.drop_temporary_table()

    def _truncate_stat(self):
        truncate_stat = "TRUNCATE TABLE {database}.{table}".format(
            database=self.database, table=self.insert_table
        )
        return truncate_stat

    def _insert_stat(self):
        insert_statement = f"INSERT INTO  {self.temp_table}"
        script = self.script.format(**self.add_args)
        script = insert_statement + " " + script
        return script

    def create_temporary_table(self):
        pass

    def insert_into_temporary_table(self):
        pass

    def truncate_main_table(self):
        pass

    def swap_temporary_to_main(self):
        pass

    def drop_temporary_table(self):
        pass
