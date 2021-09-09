import datetime
import fcntl
import chardet
import inspect
import logging
import sys
import time
import getpass
import dbm
import re
from pathlib import Path
from importlib import util as importlib_util

global logger
global logging_is_on_flag
global logger_to_file
global logging_level
global qetl_code_dir        # Parent of qualys_etl directory
global qetl_code_dir_child  # qualys_etl directory
global qetl_pip_installed_version  # qetl installed through pip
import qualys_etl

logging_is_on_flag = False


def get_dbm_type(file_name):
    dbm_type = dbm.whichdb(file_name)
    if dbm_type == '':
        dbm_type = 'unknown'

    return dbm_type


def flatten_nest(nested_data):  # Flatten nested dictionary into string
    def nested_items():
        if isinstance(nested_data, list):
            for key, value in enumerate(nested_data):
                if isinstance(value, dict) or isinstance(value, list):
                    for nested_key, nested_value in flatten_nest(value).items():
                        yield str(key) + "." + nested_key, nested_value
                else:
                    yield str(key), value
        else:
            for key, value in nested_data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    for nested_key, nested_value in flatten_nest(value).items():
                        yield key + "." + nested_key, nested_value
                else:
                    yield key, value
    return dict(nested_items())


def remove_low_high_values(chunk):  # Remove utf-8 values other than utf-8 decimal 10, 32-126
    encoding = chardet.detect(chunk)['encoding']
    chunk = chunk.decode(encoding, 'replace')
    new_chunk = ''
    for index in range(0, len(chunk)):
        try:
            size = ord(chunk[index])
            if (size == 10) or (size == 9) or (127 > size > 31):
                new_chunk = new_chunk + chunk[index]
            else:
                new_chunk = new_chunk + ""
        except Exception as e:
            new_chunk = new_chunk + ""
    chunk = new_chunk.encode('utf-8')
    return chunk


def flatten_dictionary(data):
    def data_items():
        if isinstance(data, list):
            for key, value in enumerate(data):
                if isinstance(value, dict) or isinstance(value, list):
                    for subkey, subvalue in flatten_dictionary(value).items():
                        yield str(key) + "." + subkey, subvalue
                else:
                    yield str(key), value
        else:
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    for subkey, subvalue in flatten_dictionary(value).items():
                        yield key + "." + subkey, subvalue
                else:
                    yield key, value
#
    return dict(data_items())


def truncate_csv_cell(max_length=32700, csv_cell="", truncated_field_list="", csv_column=""):
    if len(csv_cell) > max_length:
        truncated_field_list = f"{truncated_field_list}{len(csv_cell):09d}: is Length of {csv_column}, truncated at: {max_length:,}\n"
        csv_cell = csv_cell[:max_length]

    return csv_cell, truncated_field_list


def kb_csv_columns():
    csv_columns = ['QID', 'TITLE', 'VULN_TYPE', 'SEVERITY_LEVEL', 'CATEGORY', 'LAST_SERVICE_MODIFICATION_DATETIME',
                   'PUBLISHED_DATETIME', 'PATCHABLE', 'DIAGNOSIS', 'CONSEQUENCE', 'SOLUTION', 'PCI_FLAG',
                   'SUPPORTED_MODULES', 'IS_DISABLED',
                   'CVE_LIST', 'THREAT_INTELLIGENCE', 'CORRELATION', 'BUGTRAQ_LIST', 'SOFTWARE_LIST',
                   'VENDOR_REFERENCE_LIST', 'CVSS', 'CVSS_V3', 'CHANGE_LOG_LIST', 'DISCOVERY', 'PCI_REASONS',
                   'TRUNCATED_FIELD_LIST'
                   ]

    return csv_columns


def host_list_csv_columns():  # Return list of csv columns
    csv_columns = ['ID', 'ASSET_ID', 'IP', 'IPV6', 'TRACKING_METHOD', 'NETWORK_ID', 'DNS', 'DNS_DATA', 'CLOUD_PROVIDER',
                   'CLOUD_SERVICE', 'CLOUD_RESOURCE_ID', 'EC2_INSTANCE_ID', 'NETBIOS', 'OS', 'QG_HOSTID', 'TAGS',
                   'METADATA', 'CLOUD_PROVIDER_TAGS', 'LAST_VULN_SCAN_DATETIME', 'LAST_VM_SCANNED_DATE',
                   'LAST_VM_SCANNED_DURATION', 'LAST_VM_AUTH_SCANNED_DATE', 'LAST_VM_AUTH_SCANNED_DURATION',
                   'LAST_COMPLIANCE_SCAN_DATETIME', 'OWNER', 'COMMENTS', 'USER_DEF', 'ASSET_GROUP_IDS'
                   ]
    return csv_columns


def host_list_detection_csv_columns():  # Return list of csv columns
   # < !ELEMENT
   # HOST_LIST(HOST +) > <!ELEMENT
   # HOST(
   # ID, ASSET_ID?, IP?, IPV6?, TRACKING_METHOD?, NETWORK_ID?, OS?, OS_CPE?, DNS?, DNS_DATA?, CLOUD_PROVIDER?,
   # CLOUD_SERVICE?, CLOUD_RESOURCE_ID?, EC2_INSTANCE_ID?, NETBIOS?, QG_HOSTID?,
   # LAST_SCAN_DATETIME?, LAST_VM_SCANNED_DATE?, LAST_VM_SCANNED_DURATION?, LAST_VM_AUTH_SCANNED_DATE?,
   # LAST_VM_AUTH_SCANNED_DURATION?, LAST_PC_SCANNED_DATE?,
   # TAGS?, METADATA?, CLOUD_PROVIDER_TAGS?, DETECTION_LIST) >

    csv_columns = [
                   'ID', 'ASSET_ID', 'IP', 'IPV6', 'TRACKING_METHOD', 'NETWORK_ID', 'OS', 'OS_CPE', 'DNS', 'DNS_DATA',
                   'CLOUD_PROVIDER', 'CLOUD_SERVICE', 'CLOUD_RESOURCE_ID', 'EC2_INSTANCE_ID', 'NETBIOS', 'QG_HOSTID',
                   'LAST_SCAN_DATETIME', 'LAST_VM_SCANNED_DATE', 'LAST_VM_SCANNED_DURATION',
                   'LAST_VM_AUTH_SCANNED_DATE', 'LAST_VM_AUTH_SCANNED_DURATION', 'LAST_PC_SCANNED_DATE',
                   'TAGS', 'METADATA', 'CLOUD_PROVIDER_TAGS', 'DETECTION_LIST'
                   ]
    return csv_columns


def host_list_detection_qid_csv_columns():  # Return list of csv columns
    # < !ELEMENT
    # DETECTION_LIST(DETECTION +) > <!ELEMENT
    # DETECTION(
    # QID, TYPE, SEVERITY?, PORT?, PROTOCOL?, FQDN?, SSL?, INSTANCE?, RESULTS?, STATUS?,
    # FIRST_FOUND_DATETIME?, LAST_FOUND_DATETIME?, TIMES_FOUND?, LAST_TEST_DATETIME?, LAST_UPDATE_DATETIME?,
    # LAST_FIXED_DATETIME?, FIRST_REOPENED_DATETIME?, LAST_REOPENED_DATETIME?, TIMES_REOPENED?, SERVICE?,
    # IS_IGNORED?, IS_DISABLED?, AFFECT_RUNNING_KERNEL?, AFFECT_RUNNING_SERVICE?, AFFECT_EXPLOITABLE_CONFIG?,
    # LAST_PROCESSED_DATETIME?
    csv_columns = [
                   'QID', 'TYPE', 'STATUS', 'PORT', 'PROTOCOL', 'SEVERITY', 'FQDN', 'SSL', 'INSTANCE',
                   'LAST_PROCESSED_DATETIME', 'FIRST_FOUND_DATETIME', 'LAST_FOUND_DATETIME', 'TIMES_FOUND',
                   'LAST_TEST_DATETIME', 'LAST_UPDATE_DATETIME', 'LAST_FIXED_DATETIME', 'FIRST_REOPENED_DATETIME',
                   'LAST_REOPENED_DATETIME', 'TIMES_REOPENED', 'SERVICE', 'IS_IGNORED', 'IS_DISABLED',
                   'AFFECT_RUNNING_KERNEL', 'AFFECT_RUNNING_SERVICE', 'AFFECT_EXPLOITABLE_CONFIG',
                   'RESULTS'
                  ]
    return csv_columns


def asset_inventory_csv_columns():  # Return list of csv columns

    csv_columns = [
        'assetId', 'assetUUID', 'hostId', 'lastModifiedDate', 'agentId', 'createdDate', 'sensorLastUpdatedDate',
        'sensor_lastVMScanDate', 'sensor_lastComplianceScanDate', 'sensor_lastFullScanDate', 'inventory_createdDate',
        'inventory_lastUpdatedDate', 'agent_lastActivityDate', 'agent_lastCheckedInDate', 'agent_lastInventoryDate',
        'assetType', 'address', 'dnsName', 'assetName', 'netbiosName', 'timeZone', 'biosDescription', 'lastBoot',
        'totalMemory', 'cpuCount', 'lastLoggedOnUser', 'hwUUID', 'biosSerialNumber', 'biosAssetTag', 'isContainerHost',
        'operatingSystem', 'hardware', 'userAccountListData', 'openPortListData', 'volumeListData',
        'networkInterfaceListData', 'softwareListData', 'provider', 'cloudProvider', 'agent', 'sensor', 'container',
        'inventory', 'activity', 'tagList', 'serviceList', 'lastLocation', 'processor', 'TRUNCATED_FIELD_LIST'
                   ]
    return csv_columns


def check_python_version():
    py_version = sys.version.split('\n')
    try:
        if (sys.version_info[0] >= 3) and (sys.version_info[1] >= 8):
            logger.info(f"Python version found is: {py_version}")
        else:
            logger.info("Error: sys.version.info failed.  Please use Python version 3.8 or greater.")
            raise ValueError(f"Python version < 3.8 found: {py_version}")
    except Exception as e:
        logger.error(f"Please install a version of python that can work with this product.")
        logger.error(f"Exception: {e}")
        exit(1)


def get_file_size(path_to_file):
    if Path(path_to_file).is_file():
       return Path(path_to_file).stat().st_size


def get_file_mtime(path_to_file):
    if Path(path_to_file).is_file():
        statinfo = Path(path_to_file).stat()
        return statinfo.st_mtime


def dbm_type_message(dbm_file):
    dbm_type = get_dbm_type(str(dbm_file))
    if dbm_type == "dbm.gnu":
        message = "dbm.gnu is best performing DBM, you are good to go!"
    else:
        message = f"{dbm_type} may result in errors.  Please consider moving to dbm.gnu which is optimal."
    return message


def get_sqlite_version():
    global logger
    import sqlite3
    version_info = sqlite3.sqlite_version_info
    if (version_info[0] >= 3) and (version_info[1] >= 31):
        logger.info(f"SQLite version found is: {sqlite3.sqlite_version}.")
    else:
        logger.error(f"SQLite version {sqlite3.sqlite_version} is older than 3.31. Please upgrade sqlite.")
        exit(1)

    return sqlite3.version


def setup_logging_stdout(log_level=logging.INFO, my_logger_prog_name=None):
    global logger
    global logging_is_on_flag

    logging_is_on_flag = True
    logging.Formatter.converter = time.gmtime
    d = datetime.datetime.utcnow()
    td = f"{d.year}{d.month:02d}{d.day:02d}{d.hour:02d}{d.minute:02d}{d.second:02d}"
    username = getpass.getuser()
    prog = Path(__file__).name
    if my_logger_prog_name is not None:
        prog = my_logger_prog_name

    prog = f"{prog}: {td}"

    logging.basicConfig(format=f"%(asctime)s | %(levelname)-8s | {prog:54s} | {username:15} | %(funcName)-50s | %(message)s",
                        level=log_level,
                        )

    logger = logging.getLogger()  # Useful in qetl_manage_user when we want to set the name.
    logger.info(f"PROGRAM:     {sys.argv}")
    logger.info(f"QUALYSETL VERSION: {qualys_etl.__version__}")
    logger.info(f"LOGGING SUCCESSFULLY SETUP FOR STREAMING")


def setup_logging_to_file(logfile_path, log_level=logging.INFO):
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(format=f"%(asctime)s - %(levelname)s - %(message)s",
                        filename=logfile_path,
                        level=log_level)
    global logger
    logger = logging.getLogger(__name__)
    logger.info(f"LOGGING SUCCESSFULLY SETUP TO {str(logfile_path)}")


def lineno():
    return inspect.currentframe().f_back.f_lineno


def check_modules():
    try:
        import requests
        import oschmod
        import yaml
        import xmltodict
        import boto3
        import base64
        import shutil
        import chardet
    except ImportError as e:
        logger.error(f"Missing Required Module: {e}")
        logger.error(f"Please review installation instructions and ensure you have all required modules installed.")
        exit(1)


def set_logging_level(log_level=logging.INFO):
    global logging_level
    logging_level = log_level  # Set to logging.WARNING to only log Warnings and Errors.


def set_qetl_code_dir(log=True): # Module Directories
    global qetl_code_dir         # Parent of qualys_etl directory
    global qetl_code_dir_child   # qualys_etl directory

    test_exec_for_qetl_code_dir = __file__
    test_spec_for_qetl_code_dir = importlib_util.find_spec("qualys_etl")  # Installed on system

    result = ""
    if test_exec_for_qetl_code_dir.__contains__("qualys_etl"):
        result = re.sub("qualys_etl.*", '', test_exec_for_qetl_code_dir)
    elif test_spec_for_qetl_code_dir is not None:
        result = re.sub("qualys_etl.*", '', test_spec_for_qetl_code_dir.origin)
    else:
        logger.error(f"test_exec_for_qetl_code_dir - {test_exec_for_qetl_code_dir}")
        logger.error(f"test_spec_for_qetl_code_dir  - {test_spec_for_qetl_code_dir}")
        logger.error(f"Could not determine qetl code directory location.")
        logger.error(f"Please execute qetl_manage_users.py to test user")
        exit(1)

    # Module Directories
    qetl_code_dir = Path(result)
    qetl_code_dir_child = Path(qetl_code_dir, "qualys_etl")
    qetl_code_dir_child_api_host_list = Path(qetl_code_dir_child, "etld_host_list")
    qetl_code_dir_child_api_knowledgebase = Path(qetl_code_dir_child, "etld_knowledgebase")
    qetl_code_dir_child_api_lib = Path(qetl_code_dir_child, "etld_lib")
    qetl_code_dir_child_api_templates = Path(qetl_code_dir_child, "etld_templates")

    # Ensure modules are on sys.path
    modules = [qetl_code_dir_child, qetl_code_dir_child_api_lib, qetl_code_dir_child_api_templates,
               qetl_code_dir_child_api_knowledgebase, qetl_code_dir_child_api_host_list]
    for path in modules:
        if not sys.path.__contains__(str(path.absolute())):
            sys.path.insert(0, str(path))

    logger.info(f"qualysetl app dir    - {qetl_code_dir}")
    logger.info(f"qualys_etl code dir  - {qetl_code_dir_child}")
    logger.info(f"etld_lib             - {qetl_code_dir_child_api_lib}")
    logger.info(f"etld_templates       - {qetl_code_dir_child_api_templates}")
    logger.info(f"etld_knowledgebase   - {qetl_code_dir_child_api_knowledgebase}")
    logger.info(f"etld_host_list        - {qetl_code_dir_child_api_host_list}")


def log_dbm_info(file_name, msg=""):
    dbm_type = get_dbm_type(str(file_name))
    logger.info(f"{msg}dbm type - {dbm_type} - {str(file_name)}")
    if dbm_type == "dbm.gnu" or dbm_type is None:
        pass
    else:
        logger.info(f"{msg}dbm type warning - {dbm_type} may lead to inconsistent results.")
        logger.info(f"{msg}dbm type warning - {dbm_type} move to linux gnu dbm.")


def get_formatted_file_info_dict(file_name):
    file_path = Path(file_name)
    if file_path.is_file():
        file_size = human_readable_size(Path(file_name).stat().st_size)
        file_change_time = Path(file_name).stat().st_ctime
        d = datetime.datetime.fromtimestamp(file_change_time)
        td = f"{d.year}-{d.month:02d}-{d.day:02d} {d.hour:02d}:{d.minute:02d}:{d.second:02d} local timezone"
        dbm_type = get_dbm_type(str(file_name))
        return {'file_size': file_size, 'file_change_time': td, 'dbm_type': dbm_type}
    else:
        return {'file_size': '', 'file_change_time': '', 'dbm_type': ''}


def human_readable_size(size_in_bytes):
    my_bytes = float(size_in_bytes)
    kilobytes = float(1024)
    megabytes = float(kilobytes ** 2)
    gigabytes = float(kilobytes ** 3)
    terabytes = float(kilobytes ** 4)
    petabytes = float(kilobytes ** 5)

    if my_bytes < kilobytes:
        message = 'bytes' if 0 == my_bytes > 1 else 'byte'
        return f'{my_bytes} {message}'
    elif kilobytes <= my_bytes < megabytes:
        return f'{(my_bytes / kilobytes):0.2f} kilobytes'
    elif megabytes <= my_bytes < gigabytes:
        return f'{(my_bytes / megabytes):0.2f} megabytes'
    elif gigabytes <= my_bytes < terabytes:
        return f'{(my_bytes / gigabytes):0.2f} gigabytes'
    elif terabytes <= my_bytes:
        return f'{(my_bytes / terabytes):0.2f} terabytes'
    elif petabytes <= my_bytes:
        return f'{(my_bytes / petabytes):0.2f} petabytes'


def log_file_info(file_name, msg1='output file', msg2=""):
    file_info = get_formatted_file_info_dict(file_name)
    msg1 = re.sub('^in$', 'input file', msg1)
    logger.info(f"{msg2}{msg1} - {str(file_name)} size: {file_info.get('file_size')} "
                f"change time: {file_info.get('file_change_time')}")


def file_is_locked(test_lock_file=None):
    # TODO determine if checking locking in each method is needed.
    # TODO note that all actions should be run through qetl_manage_user which locks the jobstream.
    try:
        if Path(test_lock_file).is_file():
            with open(test_lock_file, 'wb+') as tlf:        # If locked, exit.
                # lock file is free
                return False
        else:
            # lock file doesn't exist
            return False
    except Exception as e:
        return True


def main(log_level=logging.INFO, my_logger_prog_name=None):
    global logging_level
    setup_logging_stdout(log_level, my_logger_prog_name)
    check_modules()
    check_python_version()
    get_sqlite_version()
    set_qetl_code_dir()


if __name__ == '__main__':
    main()
