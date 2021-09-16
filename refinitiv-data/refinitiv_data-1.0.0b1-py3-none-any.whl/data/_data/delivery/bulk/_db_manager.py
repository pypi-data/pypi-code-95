import sqlite3
from logging import Logger
from string import Template
from typing import Optional, Iterable

import mysql.connector
import pandas as pd
import os
from urllib.parse import urlparse

from ._actions import Actions
from ._errors import (
    KeyNotFoundException,
    TableNotFoundException,
    UpdateDBException,
    DBModuleNotFoundException,
)
from ...content._content_provider import Data
from ...core.log_reporter import _LogReporter
from ...tools._common import get_from_path, urljoin


def has_table(table_name, names):
    return table_name in names or table_name.lower() in names


def uri_to_path(value):
    if isinstance(value, str):
        p = urlparse(value)
    else:
        p = value
    path = p.path
    path = urljoin(p.netloc, path)
    return os.path.normpath(path)


def get_query(value):
    p = urlparse(value)
    if p.scheme == "file":
        path = uri_to_path(p)
        with open(path, "r") as f:
            result = f.read()
    else:
        result = value
    return result


value_name_tmpl = Template("#$name#")
str_tmpl = Template("'$s'")


def prepare_insert_query(query: str, data: dict, file_attrs: dict = None) -> str:
    """
    Parameters
    ----------
    query: str
        query is like
        "INSERT (INSERT_DATE, INSTRUMENT) VALUES (#File.DateTime#, #Fields.Instrument#)"
    data: dict
    file_attrs: dict, optional

    Returns
    -------
    str
    """
    # varnames is list like: ["File.DateTime", "Fields.Instrument"]
    values_names = query.split("#")[1::2]
    for value_name in values_names:
        value = get_value_from_data(value_name, data, file_attrs)
        pat = value_name_tmpl.substitute(name=value_name)
        query = query.replace(pat, value)
    return query


def prepare_search_query(
    query: str, universe: Iterable[str], columns: Iterable[str] = None
) -> str:
    """
    Parameters
    ----------
    query: str
        query is like:
         "SELECT * FROM TABLE WHERE INSTRUMENT IN #universe#"
         "SELECT COLUMN1, COLUMN2 FROM TABLE WHERE INSTRUMENT IN #universe#"
    universe: list of str
        universe is like ['4295865175', '4295906529']
    columns: list of str, optional
        columns is like ['COLUMN1', 'COLUMN2']

    Returns
    -------
    str
        Returns query is like
        "SELECT COLUMN1, COLUMN2
         FROM TABLE WHERE INSTRUMENT IN ('4295865175', '4295906529')"
    """
    if columns and "*" in query:
        query = query.replace("*", ", ".join(columns))

    pat = "#universe#"
    # repl is '4295865175','4295906529'
    repl = ",".join(str_tmpl.substitute(s=s) for s in universe)
    # repl is ('4295865175','4295906529')
    repl = f"({repl})"
    return query.replace(pat, repl)


def get_value_from_data(value_name, data, file_data=None):
    first, *path = value_name.split(".")

    if first == "Fields":
        value = data

    elif first == "File":
        value = file_data

    else:
        raise KeyNotFoundException(f"wrong name '{first}'")

    value = get_from_path(value, path)

    # if value is str like "Cabela's LLC"
    # then it will insert in query like:
    #   "INSERT (organization, score) VALUES ('Cabela's LLC', '0.123')"
    # and will get error while db.exec(query)
    # This 'if' statement is fixing the situation above
    if value and "Name" in value_name and "'" in value:
        # value is 'Cabela\'\'s LLC'
        value = value.replace("'", r"''")

    return value if value is not None else "null"


class DBManager(_LogReporter):
    def __init__(self, connection, config, actions: Actions, logger) -> None:
        super().__init__(logger=logger)
        self._connection = connection
        self._cursor = self._connection.cursor()
        self._config = config
        self._actions = actions

    def exec(self, sql):
        self._cursor.execute(sql)
        result = self._cursor.fetchall()
        return result

    def commit(self):
        self._connection.commit()

    def close(self):
        self._cursor.close()
        self._connection.close()

    def has_table(self, table_name, check_if_exists_query):
        has = False
        if check_if_exists_query:
            result = self.exec(check_if_exists_query)
            has = table_name in result or table_name.lower() in result

        return has

    def create_table(self):
        self._actions.update()
        created_tables = self._actions.get_created_tables()
        items = self._config.get("create-table-queries")

        for item in items:
            table_name = item.get("table-name")

            if table_name in created_tables:
                continue

            check_if_exists_query = item.get("check-if-exists-query")
            if self.has_table(table_name, check_if_exists_query):
                continue

            create_query = get_query(item.get("create-query"))
            if not create_query:
                raise TableNotFoundException("table doesn't exists")

            self._info(f'executing the "CREATE TABLE" query, table_name={table_name} ')
            self.exec(create_query)
            self.commit()
            self._actions.table_created(**{"table-name": table_name})

    def update_db(self, filesdata_for_update: list):
        if not filesdata_for_update and not self._actions.get_downloaded():
            message = "no init file found in folder"
            self._actions.add("ERROR", message=message)
            self._error(f"error: {message}")
            raise FileNotFoundError(message)

        if not filesdata_for_update:
            self._actions.add("NO DATA TO UPDATE")
            self._info("no data to update")
            return

        self.create_table()

        insert_queries = list(map(get_query, self._config.get("insert-queries")))
        stop_on_error = self._config.get("stop-on-error")

        for filename, items, file_attrs in filesdata_for_update:
            lines = 0
            for line_n, data in enumerate(items):
                for query in insert_queries:
                    try:
                        query = prepare_insert_query(query, data, file_attrs)
                        self.exec(query)
                    except Exception as e:
                        error_details = {
                            "message": str(e),
                            "line_number": line_n,
                            "filename": filename,
                        }
                        self._actions.add("ERROR", **error_details)
                        error_details["query"] = query
                        self._info(f"error: {error_details}")

                        if stop_on_error:
                            raise UpdateDBException(str(error_details))

                        else:
                            continue

                lines += 1

            self.commit()
            self._actions.updated(filename=filename, lines=lines)

    def cleanup_db(self):
        clean_up_queries = self._config.get("clean-up-queries")
        for query in clean_up_queries:
            self.exec(query)
        self.commit()
        self._actions.cleaned_up_db()
        self._info("clean up database")

    def get_data(self, universe: Iterable[str], fields: Iterable[str] = None) -> Data:
        fields = fields or []
        query = self._config.get("search-query")

        column_by_field = self._config["output-fields-mapping"].as_dict()
        field_by_column = {v: k for k, v in column_by_field.items()}
        columns = [
            field_by_column[field] for field in fields if field in field_by_column
        ]

        try:
            query = prepare_search_query(query, universe, columns)
            raw = self.exec(query)
            error = None
        except Exception as e:
            raw = {}
            error = {
                "message": str(e),
            }
            self._actions.add("ERROR", **error)
            error["query"] = query
            self._info(f"error: {error}")

        if error:
            df = pd.DataFrame([])
            return Data(raw, df)

        columns = self._cursor.description
        fields = [
            column_by_field.get(column, column)
            for i, (column, *_) in enumerate(columns)
        ]
        df = pd.DataFrame(raw, columns=fields)
        if not df.empty:
            df = df.convert_dtypes()
        return Data(raw, df)


def create_sqlite_connector(config):
    connection = sqlite3.connect(
        database=config.get("connection.parameters.database"), uri=True
    )
    return connection


def create_mysql_connector(config):
    conn_params = config["connection"]["parameters"]
    connection = mysql.connector.connect(
        user=conn_params.get("user"),
        password=conn_params.get("password"),
        host=conn_params.get("host"),
        port=conn_params.get("port"),
        database=conn_params.get("database"),
    )
    return connection


connections_makers_by_db_modules = {
    "sqlite3": create_sqlite_connector,
    "mysql": create_mysql_connector,
}


def create_db_manager(config, actions, logger):
    db_module_name = config.get("connection.module")
    create_connection = connections_makers_by_db_modules.get(db_module_name)

    if not create_connection:
        raise DBModuleNotFoundException(f"module {db_module_name} not found")

    connection = create_connection(config)
    manager = DBManager(connection, config, actions, logger)
    return manager


def create_db_manager_by_package_name(
    package_name,
    actions: Optional[Actions] = None,
    logger: Optional[Logger] = None,
):
    from ._package_manager import create_logpath, get_console_logger
    from ... import configure

    id_ = f"{package_name}"
    config = configure.get(f"bulk.{package_name}.db")
    actions = actions or Actions(
        id_=id_,
        logpath=create_logpath(package_name),
    )
    logger = logger or get_console_logger(id_)
    manager = create_db_manager(config, actions, logger)
    return manager
