import time
import sys
import logging
import vertica_python

from vconnector.vertica_insert import insert as vertica_insert
from vconnector.vertica_merge import merge as vertica_merge

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.captureWarnings(True)


def read_commands_from_file(path):
    f = open(path, "r")
    ddl_txt = f.read()
    commands = [x + ";" for x in ddl_txt.replace("\n", "").split(";") if x != ""]
    return commands


class VerticaConnector:
    def __init__(
            self,
            user,
            password,
            database,
            vertica_configs,
            debug=True,
            sec_to_recconect=5,
            count_retries=1
    ):

        """pass params to connector
        :param user user in connection info
        :type  str
        :param password password in connection info
        :type  str
        :param database
        :type str
        :param vertica_configs - other  required params including host, port, connection_load_balance, backup_server_node
        :param sec_to_recconect: seconds to reconnect
        :param count_retries
        """

        self.sec_to_recconect = sec_to_recconect or 5
        self.count_retries = count_retries
        self.connection_info = vertica_configs
        self.connection_info["user"] = user
        self.connection_info["connection_load_balance"] = True
        self.connection_info["password"] = password
        self.connection_info["database"] = database
        self.debug = debug
        self.cnx = None
        if "backup_server_node" not in self.connection_info:
            raise BaseException(
                "Error. You should specify backup_server_node list in connection_info"
            )
        if len(self.connection_info["backup_server_node"]) == 0:
            raise BaseException(
                "Error. backup_server_node list has to contain at least one backup node"
            )
        if (
                "connection_load_balance" not in self.connection_info
                or not self.connection_info["connection_load_balance"]
        ):
            raise BaseException(
                "Error. You have to specify connection_load_balance=True param"
            )
        for param in ["host", "port", "user", "password", "database"]:
            if param not in self.connection_info:
                raise BaseException("Error. You have to specify {} param".format(param))
        self.foreign_keys_ddl = []

    def __str__(self):
        return "VerticaConnector to {}".format(self.connection_info["database"])

    def __check_connectivity(self):
        if self.cnx is None:
            raise Exception("Execution should be in  with method")

    def exec_commands_from_file(self, path):
        self.exec_multiple_sql(read_commands_from_file(path))

    def exec_multiple_sql(self, sqls):
        """
        EXEC list of sql queries
        :param sqls: list of sql queries
        :return: nothing
        """
        self.__check_connectivity()
        cur = self.cnx.cursor()
        cur.execute("START TRANSACTION;")
        for sql in sqls:
            if self.debug:
                logging.info(sql)
            cur.execute(sql)
        cur.execute("COMMIT;")

    def reload_main_table(self, table_name, schema, staging_schema, table_suffix=None):
        """
        Replace non empty temporary table with main table
        :param table_name:
        :param schema:
        :param staging_schema:
        :param table_suffix: table_suffix specified for temporary table
        :return: Nothing
        """
        staging_table_name = table_name + (table_suffix or "")
        sqls = [
            "drop table if exists {schema}.{table_name} cascade;"
        ]
        if staging_schema != schema:
            sqls += [
                "alter table {staging_schema}.{staging_table_name} set schema {schema};"
            ]

        if table_suffix:
            sqls += [
                "alter table {schema}.{staging_table_name} rename to {table_name};"
            ]

        sqls += ["drop table if exists {staging_schema}.{staging_table_name} cascade;"]

        sqls = [
                   sql.format(
                       schema=schema,
                       table_name=table_name,
                       staging_schema=staging_schema,
                       staging_table_name=staging_table_name,
                   )
                   for sql in sqls
               ] + self.foreign_keys_ddl
        self.exec_multiple_sql(sqls)

    def create_staging_table(
            self, table_name, schema, staging_schema, ddl_path=None, table_suffix=None
    ):
        """
        Create temporary table in staging schema
        :param table_suffix: table_suffix specified for temporary table
        :param table_name:
        :param schema:
        :param staging_schema:
        :param ddl_path: path to ddl for read, None if
        :return:
        """
        staging_table_name = table_name + (table_suffix or "")
        drop_statement = (
            "drop table if exists {staging_schema}.{table_name} cascade;".format(
                staging_schema=staging_schema, table_name=staging_table_name
            )
        )

        if ddl_path:
            staging_table_name = table_name + (table_suffix or "")
            commands = read_commands_from_file(ddl_path + "/" + table_name + ".sql")
            commands[0] = commands[0].replace(
                schema + "." + table_name, staging_schema + "." + staging_table_name
            )
            self.foreign_keys_ddl = commands[1:]
            sqls = [drop_statement] + commands[0:1]
        else:
            create_statement = "create table {staging_schema}.{staging_table_name} like  {schema}.{table_name} INCLUDING PROJECTIONS".format(
                schema=schema,
                staging_schema=staging_schema,
                table_name=table_name,
                staging_table_name=staging_table_name,
            )
            sqls = [drop_statement] + [create_statement]

        self.exec_multiple_sql(sqls)

    def insert(
        self,
        table_name,
        data,
        schema=None,
        table_suffix=None,
        enforcelength="ABORT ON ERROR",
    ):
        """
        custom insert for vertica using json
        :param enforcelength: Determines whether COPY truncates or rejects data rows of type char, varchar, binary, and varbinary if they do not fit the target table. Specifying the optional ENFORCELENGTH parameter rejects rows.
        :param table_name:
        :param data:
        :param schema:
        :param table_suffix: change table to insert
        :return: nothing
        """
        self.__check_connectivity()
        keys_data = list(data[0].keys())
        columns = self.get_columns(
            table_name=table_name + (table_suffix or ""), schema=schema
        )
        keys_to_remove = list(set(keys_data) - set(columns))
        keys_data = [key for key in keys_data if key in columns]
        for item in data:
            for key in keys_to_remove:
                if key in item:
                    del item[key]
        fields_json = [
            key
            for key in keys_data
            if key in columns and columns[key].find("long varbinary") > -1
        ]
        vertica_insert(
            vertica_cnx=self.cnx,
            target=schema + "." + table_name + (table_suffix or ""),
            fields_json=fields_json,
            fields=keys_data,
            data=data,
            enforcelength=enforcelength
        )

    def insert_merge_vertica(
        self,
        table_name,
        data,
        staging_schema,
        schema=None,
        staging_table_suffix=None,
        key_fields=["id"],
        filter_merge_fields=None,
        enforcelength="ABORT ON ERROR",
        working_fields=None
    ):
        """
        Insert and update data in target table using temporary staging table, only for vertica
        :param working_fields: list of fields to working with in merge, type list
        :param enforcelength:
        :param filter_merge_fields:
        :param key_fields:
        :param table_name:
        :param data:
        :param staging_schema:
        :param schema:
        :param staging_table_suffix:
        :return: Nothing
        """

        staging_table_name = (
            "{staging_schema}.{table_name}{staging_table_suffix}".format(
                staging_schema=staging_schema,
                table_name=table_name,
                staging_table_suffix=staging_table_suffix or "",
            )
        )
        sql_create_staging = (
            "create table {staging_table_name} like {schema}.{table_name}".format(
                staging_table_name=staging_table_name,
                table_name=table_name,
                schema=schema,
            )
        )
        sql_drop_staging = "drop table if exists {staging_table_name} cascade".format(
            staging_table_name=staging_table_name
        )
        self.__check_connectivity()
        cursor = self.cnx.cursor("dict")
        try:
            if self.debug:
                logging.info(sql_drop_staging)
            cursor.execute(sql_drop_staging)
            if self.debug:
                logging.info(sql_create_staging)
            cursor.execute(sql_create_staging)
            self.insert(
                table_name=table_name,
                data=data,
                schema=staging_schema,
                table_suffix=staging_table_suffix,
                enforcelength=enforcelength
            )
            vertica_merge(
                vertica_cnx=self.cnx,
                table_name=schema + "." + table_name,
                staging_table_name=staging_table_name,
                fields=self.get_columns(table_name=table_name, schema=schema) if not working_fields else working_fields,
                key_fields=key_fields,
                filter_merge_fields=filter_merge_fields,
                debug=self.debug,
            )
        finally:
            if self.debug:
                logging.info(sql_drop_staging)
            cursor.execute(sql_drop_staging)

    def get_columns(self, table_name, schema):
        """
        :param table_name:
        :param schema:
        :return: list of column name
        """
        self.__check_connectivity()
        cur = self.cnx.cursor()
        sql = """SELECT column_name,  data_type
                 FROM   v_catalog.columns
                 WHERE  table_schema='{schema}'
                        AND table_name='{table_name}'
                 ORDER  BY ordinal_position;
             """.format(
            schema=schema, table_name=table_name
        )
        res = cur.execute(sql)
        rows = res.fetchall()
        res = dict(zip([row[0] for row in rows], [row[1] for row in rows]))
        if len(res) == 0:
            raise ModuleNotFoundError("Table {} not found".format(table_name))
        return res

    def __enter__(self):
        """ start point to connect """
        if self.debug:
            logging.info("Connecting to Vertica...")
        for i in range(self.count_retries + 1):
            try:
                self.cnx = vertica_python.connect(**self.connection_info)
                break
            except vertica_python.errors.ConnectionError as exc:
                logging.info(
                    "{}, waiting {} sec to reconnect".format(
                        str(exc), self.sec_to_recconect
                    )
                )
                time.sleep(self.sec_to_recconect)

        if self.debug:
            cur = self.cnx.cursor("dict")
            sql_sessions = """SELECT node_name, client_hostname, session_id, login_timestamp, transaction_id, client_version FROM CURRENT_SESSION"""
            cur.execute(sql_sessions)
            row = cur.fetchone()
            params = []
            for key, value in row.items():
                params.append(str(key) + ": " + str(value))

            logging.info(
                "Connected to Vertica: {current_session_info}".format(
                    current_session_info=", ".join(params)
                )
            )
        return self

    def __exit__(self, type, value, traceback):
        self.cnx.close()
        if self.debug:
            logging.info("Vertica connection closed")
