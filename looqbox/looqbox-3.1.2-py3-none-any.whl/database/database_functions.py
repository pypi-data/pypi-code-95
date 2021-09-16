from looqbox.global_calling import GlobalCalling
from looqbox.objects.looq_table import ObjTable
from looqbox.utils.utils import base64_decode
import pandas as pd
import jaydebeapi
import datetime
import json
import os
import re

__all__ = ["sql_in", "sql_close", "connect", "sql_execute", "sql_between"]


def connect(connection_name, parameter_as_json=False):
    """
    Execute a connection in a database.

    :param connection_name: String or list of database names
    :param parameter_as_json: Set if the parameters will be in JSON format or not
    :return: A Connection object
    """

    if isinstance(connection_name, str):
        connection_list = [connection_name]
    else:
        connection_list = connection_name

    driver_path = list()
    for conn_name in connection_list:
        try:
            if isinstance(GlobalCalling.looq.connection_config, dict):
                file_connections = GlobalCalling.looq.connection_config
            else:
                file_connections = open(GlobalCalling.looq.connection_config)
                file_connections = json.load(file_connections)
        except FileNotFoundError:
            raise Exception("File connections.json not found")

        try:
            if not parameter_as_json:
                conn_par = GlobalCalling.looq.connection_config[conn_name]
            else:
                conn_par = file_connections[conn_name]
        except KeyError:
            raise Exception("Connection " + conn_name + " not found in the file " + GlobalCalling.looq.connection_file)

        conn_file_name, conn_file_extension = os.path.splitext(conn_par['driverFile'])

        old_driver_file_path = os.path.join(GlobalCalling.looq.jdbc_path + '/' + conn_file_name + conn_file_extension)
        new_driver_file_path = os.path.join(GlobalCalling.looq.jdbc_path + '/' + conn_file_name)

        if new_driver_file_path:

            for file in os.listdir(new_driver_file_path):
                if not file.startswith('.') and '.jar' in file:
                    driver_path.append(new_driver_file_path + '/' + file)
        elif old_driver_file_path:
            driver_path = old_driver_file_path

    conn = jaydebeapi.connect(
        conn_par['driver'],
        conn_par['connString'],
        {
            'user': conn_par['user'],
            'password': base64_decode(conn_par['pass'])
        },
        driver_path
    )

    return conn


def sql_execute(connection, query, replace_parameters=None, close_connection=True, show_query=False, null_as=None):
    """
    Function to execute a query inside the connection informed. The result of the query will be
    transformed into a ObjTable to be used inside the response.


    :param connection: Connection name or class
    :param query: Query to get the table
    :param replace_parameters: List of parameters to be used in the query. These parameters will replace the numbers
    wit h `` in the query.
        Example:
            replace_parameters = [par1, par2, par3, par4]
            query = "select * from bd where par1=`1` and par2=`2` and par3=`3` and par4=`4`

            In this case the values of `1`, `2`, `3`, `4` will be replaced by par1, par2, par3, par4 respectively (using
            the order of the list in replace_parameters).

    :param close_connection: Define if automatically closes the connection
    :param show_query: Print the query in the console
    :param null_as: Default null value of the table
    :return: A TableObject with the data retrieved from the query
    """

    if replace_parameters is not None:
        query = _sql_replace_parameters(query, replace_parameters)

    test_mode = GlobalCalling.looq.test_mode

    if show_query and test_mode:
        print(query)

    start_time = datetime.datetime.now()

    query_dataframe = ObjTable(null_as=null_as)
    query_dataframe.data, query_dataframe.metadata = GlobalCalling.log_query(connection, query, _get_query_result,
                                                                             [connection, query, close_connection])
    df_cols_and_rows = query_dataframe.data.shape
    query_dataframe.rows = df_cols_and_rows[0]
    query_dataframe.cols = df_cols_and_rows[1]

    if test_mode:
        total_sql_time = datetime.datetime.now() - start_time
        print("SQL fetch in...", total_sql_time.total_seconds(), "secs")

    if close_connection and not isinstance(connection, str):
        connection.close()

    return query_dataframe


def _get_query_result(connection, query, close_connection):
    """
    Function to get the table resulting from the query

    :param connection: Connection name or class
    :param query: Query to get the table
    :param close_connection: Define if automatically closes the connection
    :return: Return the data frame resulting from the query.
    """

    try:
        if isinstance(connection, str):
            connection = connect(connection)

        conn_curs = connection.cursor()

    except:
        if close_connection and not isinstance(connection, str):
            conn_curs.close()
            sql_close(conn_curs)

        raise Exception("Error to connect in database.")

    try:
        conn_curs.execute(query)
        col_names = [i[0] for i in conn_curs.description]
        fetch_tuple = conn_curs.fetchall()

        metadata = get_column_types(conn_curs)

        # Fix error when fetch brings one None row
        query_df = pd.DataFrame()
        if fetch_tuple or len(fetch_tuple) > 0:
            if len(fetch_tuple[0]) == 1:
                if fetch_tuple[0][0] is not None:
                    query_df = pd.DataFrame(fetch_tuple, columns=col_names)
            else:
                query_df = pd.DataFrame(fetch_tuple, columns=col_names)

        sql_close(conn_curs)

        return query_df, metadata
    except:
        if close_connection and not isinstance(connection, str):
            conn_curs.close()
            sql_close(conn_curs)

        raise Exception("Error to execute query.")


def get_column_types(cursor):
    metadata = dict()
    for column in cursor.description:
        column_name = column[0]
        column_type = filter_types(column[1].values)
        metadata[column_name] = {
            "type": column_type
        }
    return metadata


def filter_types(type_list):
    type_dict = {
        'CHAR': ('CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR', 'OTHER'),
        'LONGVARCHAR': ('CLOB', 'LONGVARCHAR', 'LONGNVARCHAR', 'NCLOB', 'SQLXML'),
        'BINARY': ('BINARY', 'BLOB', 'LONGVARBINARY', 'VARBINARY'),
        'INTEGER': ('BOOLEAN', 'BIGINT', 'BIT', 'INTEGER', 'SMALLINT', 'TINYINT'),
        'FLOAT': ('FLOAT', 'REAL', 'DOUBLE'),
        'NUMERIC': ('DECIMAL', 'NUMERIC'),
        'DATE': ('DATE'),
        'TIME': ('TIME'),
        'TIMESTAMP': ('TIMESTAMP'),
        'ROWID': ('ROWID')
    }
    column_type = None
    for db_type, aliases in type_dict.items():
        if type_list == aliases:
            column_type = db_type
    return column_type


def _sql_replace_parameters(query, replace_parameters):
    """
    This function get the query and replace all the values between backticks to the values in the replace_parameters
    list, the values are substituted using the order in replace parameters, for example, the `1` in the query will be
    substituted by the value replace_parameters[0] and so goes on.
    Example:
        query = "select * from database where x = `1` and z = `3` and y = `2`"
        replace_parameters = [30, 50, 60}

        returns = "select * from database where x = 30 and z = 60 and y = 50"

    :param query: Query to be changed
    :param replace_parameters: List that contains the values to be substitute
    :return: Query with the values changed
    """
    for replace in range(len(replace_parameters)):
        query = query.replace('`' + str((replace + 1)) + '`', '"' + str(replace_parameters[replace]) + '"')

    return query


def sql_in(query=None, values_list=None):
    """
    Transform the list in values_list to be used inside a IN statement of the SQL.
    Example:
        values_list = [1,2,3,4,5]
        query = 'select * from database where' + sql_in(" col in", values_list)

        "select * from database where col in (1, 2, 3, 4, 5)"


    :param query: Query header with the first part of the query
    :param values_list: list to be transformed as a IN format
    :return: query concatenated with values_list as a IN format
    """
    if values_list is None:
        return ""

    if not isinstance(values_list, list):
        values_list = [values_list]

    separated_list = str(values_list).replace('[', '(').replace(']', ')')

    if query is None:
        return separated_list
    else:
        return query + " " + separated_list


def sql_between(query=None, values_list=None):
    """
    Transform the list in values_list to be used as a between statement of the SQL.
    Example:
        values_list = ['2018-01-01', '2018-02-02']
        query = 'select * from database where sql_between(' date', date_int)'

        "select * from database where date between '2018-01-01' and '2018-02-02')"


    :param query: Query header with the first part of the query
    :param values_list: list to be used in a between statement
    :return: query concatenated with values_list as a between statement
    """
    if values_list is None:
        return ""

    if len(values_list) != 2:
        raise Exception("To use sql_between values_list must be of two positions")

    if not isinstance(values_list, list):
        values_list = [values_list]

    if isinstance(values_list[0], int) or isinstance(values_list[1], int):
        between_query = query + " between " + str(values_list[0]) + " and " + str(values_list[1])
    else:
        between_query = query + " between '" + values_list[0] + "' and '" + values_list[1] + "'"

    return between_query


def sql_close(conn):
    """
    Close a connection
    :param conn: Connection of the type JayBeDeApi
    """
    conn.close()


def reload_database_connection(conn_file_path=GlobalCalling.looq.connection_file):
    if os.path.isfile(conn_file_path):
        GlobalCalling.looq.connection_config = json.loads(conn_file_path)
    else:
        print("Missing connection file: " + GlobalCalling.looq.connection_file)
        GlobalCalling.looq.connection_config = None
