from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables

global host_list_sqlite_file


def host_list_sqlite():
    global host_list_sqlite_file

    etld_lib_sqlite_tables.create_table(etld_lib_config.host_list_table_name,
                                        etld_lib_functions.host_list_csv_columns(),
                                        host_list_sqlite_file,
                                        key='ID')
    etld_lib_sqlite_tables.bulk_insert_csv_file(etld_lib_config.host_list_table_name,
                                                etld_lib_config.host_list_csv_file,
                                                etld_lib_functions.host_list_csv_columns(),
                                                host_list_sqlite_file)


def start_msg_host_list_sqlite():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_sqlite():
    etld_lib_functions.logger.info(f"count host rows added to table: {etld_lib_sqlite_tables.count_rows_added_to_table:,}")
    etld_lib_functions.log_file_info(etld_lib_config.host_list_csv_file, 'in')
    etld_lib_functions.log_file_info(host_list_sqlite_file)
    etld_lib_functions.logger.info(f"end")


def setup_vars():
    global host_list_sqlite_file
    try:
        host_list_sqlite_file
    except:
        host_list_sqlite_file = etld_lib_config.host_list_sqlite_file


def main():
    start_msg_host_list_sqlite()
    setup_vars()
    host_list_sqlite()
    end_msg_host_list_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_sqlite')
    etld_lib_config.main()
    main()

