import sqlite3
import re
import csv
import sys
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
global count_rows_added_to_table


def create_table_statement(primary_key, table_name, csv_columns):
    table_statement = f"CREATE TABLE {table_name} (\n"
    table_statement = f"{table_statement}{primary_key} CHAR PRIMARY KEY NOT NULL,\n"
    for column in csv_columns:
        if primary_key != column:
            table_statement = f"{table_statement}{column} CHAR,\n"
    table_statement = re.sub(",\n$", "", table_statement)
    table_statement = table_statement + ");"
    return table_statement


def create_table(table_name, csv_columns, sqlite_file, key):
    try:
        conn = sqlite3.connect(sqlite_file)
        conn.execute(f"DROP TABLE IF EXISTS {table_name};")
        table_statement = create_table_statement(key, table_name, csv_columns)
        conn.execute(table_statement)
        conn.commit()
        conn.close()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
        etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def bulk_insert_csv_file(table_name, csv_file_name, csv_columns, sqlite_file):
    global count_rows_added_to_table
    csv.field_size_limit(sys.maxsize)
    # etld_lib_functions.logger.info(f"csv.field_size_limit(sys.maxsize): {str(sys.maxsize)}")
    try:
        values_var = ""
        for column in csv_columns:
            values_var = f"{values_var}?, "
        values_var = re.sub("\?, $", "?", values_var)
        csv_headers = ""
        csv_row_list = []
        bulk_insert_count = 100
        conn = sqlite3.connect(sqlite_file)
        cursor_obj = conn.cursor()
        with open(csv_file_name, "r", encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            count_rows_added_to_table = 0
            csv_headers = next(csv_reader)  # Skip Header
            insert_command = f"INSERT INTO {table_name} VALUES({values_var})"
            for row in csv_reader:
                csv_row_list.append(row)
                if len(csv_row_list) > bulk_insert_count:
                    cursor_obj.executemany(f"INSERT INTO {table_name} VALUES({values_var})", csv_row_list)
                    conn.commit()
                    csv_row_list = []
                count_rows_added_to_table = count_rows_added_to_table + 1
            if len(csv_row_list) > 0:
                cursor_obj.executemany(f"INSERT INTO {table_name} VALUES({values_var})", csv_row_list)
                conn.commit()
                csv_row_list = []
    except Exception as e:
        etld_lib_functions.logger.error(f"Error creating table from: {csv_file_name}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Row Number: {count_rows_added_to_table}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def create_table_statement_no_primary_key(table_name, csv_columns):
    table_statement = f"CREATE TABLE {table_name} (\n"
    table_statement = f"{table_statement}\n"
    for column in csv_columns:
        table_statement = f"{table_statement}{column} CHAR,\n"
    table_statement = re.sub(",\n$", "", table_statement)
    table_statement = table_statement + ");"
    return table_statement


def create_table_no_primary_key(table_name, csv_columns, sqlite_file):
    try:
        conn = sqlite3.connect(sqlite_file)
        conn.execute(f"DROP TABLE IF EXISTS {table_name};")
        table_statement = create_table_statement_no_primary_key(table_name, csv_columns)
        conn.execute(table_statement)
        conn.commit()
        conn.close()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def get_q_knowledgebase_min_max_dates(sqlite_file):
    min_date = None
    max_date = None
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        select_statement = 'select min(LAST_SERVICE_MODIFICATION_DATETIME) MIN_DATE, ' \
                           'max(LAST_SERVICE_MODIFICATION_DATETIME) MAX_DATE ' \
                           'from Q_KnowledgeBase;'
        cursor.execute(select_statement)
        records = cursor.fetchall()
        for row in records:
            min_date = row[0]
            max_date = row[1]
        conn.close()
    except Exception as e:
        min_date = 'Not Found'
        max_date = 'Not Found'

    return min_date, max_date


def get_q_table_min_max_dates(sqlite_file, datetime_field_name, table_name):
    min_date = None
    max_date = None
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        select_statement = f'select min({datetime_field_name}) MIN_DATE, ' \
                           f'max({datetime_field_name}) MAX_DATE ' \
                           f'from {table_name};'
        cursor.execute(select_statement)
        records = cursor.fetchall()
        for row in records:
            min_date = row[0]
            max_date = row[1]
        conn.close()
    except Exception as e:
        min_date = 'Not Found'
        max_date = 'Not Found'

    return min_date, max_date


def create_table_q_knowledgebase_in_host_list_detection(sqlite_file):
    table_name = 'Q_KnowledgeBase_In_Host_List_Detection'
    kb_table_name = 'Q_KnowledgeBase'
    table_statement = f'CREATE TABLE {table_name} as ' \
                      f'select * from {kb_table_name} ' \
                      f'where QID in (select distinct(QID) from Q_Host_List_Detection);'
    try:
        conn = sqlite3.connect(sqlite_file)
        conn.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.execute(table_statement)
        conn.execute(f"DROP TABLE IF EXISTS {kb_table_name};")
        conn.commit()
        conn.close()
        conn = sqlite3.connect(sqlite_file)
        conn.isolation_level = None
        conn.execute("VACUUM")
        conn.close()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
