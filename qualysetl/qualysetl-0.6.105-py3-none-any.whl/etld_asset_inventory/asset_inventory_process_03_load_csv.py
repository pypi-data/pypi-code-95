import csv
import shelve
import re
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
global count_host_ids_written
global count_host_qids_written
global asset_inventory_item
global asset_inventory_csv_truncate_cell_limit
global asset_inventory_csv_file


def prepare_csv_cell(csv_cell, csv_column):
    if csv_cell is None:
        csv_cell = ""
    elif 'Date' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
        csv_cell = re.sub("\..*$", "", csv_cell)
    elif 'lastBoot' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
        csv_cell = re.sub("\..*$", "", csv_cell)
    elif isinstance(csv_cell, int):
        csv_cell = str(csv_cell)
    elif not isinstance(csv_cell, str):  # Flatten Nested XML into String
        flatten = etld_lib_functions.flatten_nest(csv_cell)
        csv_cell = ""
        for key in flatten.keys():
            csv_cell = f"{csv_cell}{key}:{flatten[key]}\n"

    return csv_cell


def asset_inventory_to_csv():  # Create CSV File from Shelve Database
    global count_host_ids_written
    global asset_inventory_csv_file
    global asset_inventory_item

    asset_inventory_csv_file = etld_lib_config.asset_inventory_csv_file     # Output CSV File
    csv_columns = etld_lib_functions.asset_inventory_csv_columns()         # Host List Columns
    count_host_ids_written = 0
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(asset_inventory_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_row = csv_headers.copy()
            # Iterate through Shelve Database
            with shelve.open(str(etld_lib_config.asset_inventory_shelve_file), flag='r') as shelve_database:  # Open Host List Shelve DB
                for shelve_database_item in shelve_database:
                    asset_inventory_item = shelve_database[shelve_database_item]
                    truncated_field_list = ""
                    for csv_column in csv_columns:  # Iterate through expected columns (contract)
                        if csv_column in asset_inventory_item.keys():  # Iterate through columns found in Shelve
                            asset_inventory_item[csv_column] = prepare_csv_cell(asset_inventory_item[csv_column],
                                                                                csv_column)
                            csv_row[csv_column], truncated_field_list = \
                                etld_lib_functions.truncate_csv_cell(
                                                  max_length=etld_lib_config.asset_inventory_csv_truncate_cell_limit,
                                                  csv_cell=asset_inventory_item[csv_column],
                                                  truncated_field_list=truncated_field_list,
                                                  csv_column=csv_column)
                        else:
                            csv_row[csv_column] = ""  # Ensure blank is added to each required empty field
                            if csv_column == 'TRUNCATED_FIELD_LIST':
                                asset_inventory_item[csv_column] = truncated_field_list
                                csv_row[csv_column] = asset_inventory_item[csv_column]
                    # Write CSV row, Prepare for next row.
                    writer.writerow(csv_row)
                    count_host_ids_written = count_host_ids_written + 1
                    csv_row = csv_headers.copy()

    except Exception as e:
        etld_lib_functions.logger.error(f"Error writing to file: {str(asset_inventory_csv_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def start_msg_asset_inventory_csv():
    etld_lib_functions.logger.info(f"start")


def end_msg_asset_inventory_csv():
    global count_host_ids_written
    global count_host_qids_written
    etld_lib_functions.logger.info(f"count host ids written (hosts) written to csv: {count_host_ids_written:,}")
    etld_lib_functions.log_file_info(etld_lib_config.asset_inventory_shelve_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.asset_inventory_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.asset_inventory_csv_file)
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_asset_inventory_csv()
    asset_inventory_to_csv()
    end_msg_asset_inventory_csv()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_csv')
    etld_lib_config.main()
    main()
