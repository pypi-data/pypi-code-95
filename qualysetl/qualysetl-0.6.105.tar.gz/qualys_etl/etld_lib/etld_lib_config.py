from pathlib import Path
import os
import oschmod
import re
import yaml
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime as api_date
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables

global setup_completed_flag           # Set to true when completed
# APPLICATION
global qetl_code_dir                  # Parent Directory of qualys_etl
global qetl_code_dir_child            # qualys_etl directory
global qetl_user_root_dir             # opt/qetl/users/{$USER NAME}
global qetl_all_users_dir             # opt/qetl/users
# USER INIT
global qetl_create_user_dirs_ok_flag  # False.  Set to true by qetl_manage_user
global qualys_etl_user_home_env_var
global qetl_user_home_dir
global qetl_user_data_dir
global qetl_user_log_dir
global qetl_user_config_dir
global qetl_user_cred_dir
global qetl_user_bin_dir
global qetl_user_default_config
global qetl_user_config_settings_yaml_file
global qetl_user_config_settings_yaml
global etld_lib_config_settings_yaml_dict
global qetl_manage_user_selected_datetime
# USER KNOWLEDGEBASE
global kb_data_dir
global kb_bin_dir
global kb_export_dir
global kb_last_modified_after
global kb_xml_file
global kb_shelve_file
global kb_sqlite_file
global kb_cve_qid_file
global kb_cve_qid_map_shelve
global kb_csv_file
global kb_json_file
global kb_log_file
global kb_lock_file
global kb_log_rotate_file
global kb_table_name
global kb_csv_truncate_cell_limit
global kb_data_files
# USER HOST LIST
global host_list_data_dir
global host_list_export_dir
global host_list_vm_processed_after
global host_list_payload_option
global host_list_xml_file_list
global host_list_other_xml_file
global host_list_ec2_xml_file
global host_list_gcp_xml_file
global host_list_azure_xml_file
global host_list_shelve_file
global host_list_sqlite_file
global host_list_csv_file
global host_list_json_file
global host_list_log_file
global host_list_lock_file
global host_list_log_rotate_file
global host_list_table_name
global host_list_csv_truncate_cell_limit
global host_list_data_files
# USER HOST LIST DETECTION
global host_list_detection_data_dir
global host_list_detection_export_dir
global host_list_detection_vm_processed_after
global host_list_detection_payload_option
global host_list_detection_xml_file
global host_list_detection_xml_dir
global host_list_detection_shelve_file
global host_list_detection_sqlite_file
global host_list_detection_csv_truncate_cell_limit
global host_list_detection_csv_file
global host_list_detection_json_file
global host_list_detection_log_file
global host_list_detection_lock_file
global host_list_detection_log_rotate_file
global host_list_detection_concurrency_limit
global host_list_detection_multi_proc_batch_size
global host_list_detection_limit_hosts
global host_list_detection_table_name
global host_list_detection_data_files

# USER ASSET INVENTORY
global asset_inventory_data_dir
global asset_inventory_export_dir
global asset_inventory_asset_last_updated
global asset_inventory_payload_option
global asset_inventory_json_batch_file
global asset_inventory_json_dir
global asset_inventory_shelve_file
global asset_inventory_sqlite_file
global asset_inventory_csv_truncate_cell_limit
global asset_inventory_csv_file
global asset_inventory_json_file
global asset_inventory_log_file
global asset_inventory_lock_file
global asset_inventory_log_rotate_file
global asset_inventory_concurrency_limit
global asset_inventory_multi_proc_batch_size
global asset_inventory_limit_hosts
global asset_inventory_table_name
global asset_inventory_data_files
global asset_inventory_temp_shelve_file

# Initialize Some Globals

qetl_create_user_dirs_ok_flag = False      # Automatically create unknown user directories default - False
qetl_manage_user_selected_datetime = None  # Initialize qetl_manage_user datetime to None


def set_path_qetl_user_home_dir():
    global qualys_etl_user_home_env_var
    global qetl_user_home_dir
    global qetl_user_root_dir
    global qetl_all_users_dir
    global qetl_user_data_dir
    global qetl_user_log_dir
    global qetl_user_config_dir
    global qetl_user_cred_dir
    global qetl_user_bin_dir

    if os.environ.keys().__contains__("qualys_etl_user_home") is not True:
        # qetl_all_users_dir = Path(Path.home(), 'opt', 'qetl', 'users')
        # qetl_user_root_dir = Path(Path.home(), 'opt', 'qetl', 'users', 'default_user')
        # qetl_user_home_dir = Path(qetl_user_root_dir, 'qetl_home')
        # Entry is now qetl_manage_user.  If qualys_etl_user_home env is not set, then abort.
        try:
            etld_lib_functions.logger.error(f"Error, no qualys_etl_user_home.")
            etld_lib_functions.logger.error(f"Ensure you are running qetl_manage_user to run your job")
            etld_lib_functions.logger.error(f"see qetl_manage_user -h for options.")
            exit(1)
        except AttributeError as e:
            print(f"Error, no qualys_etl_user_home.")
            print(f"Ensure you are using opt/qetl/users as part of your path")
            print(f"see qetl_manage_user -h for options.")
            exit(1)
    else:
        qualys_etl_user_home_env_var = Path(os.environ.get("qualys_etl_user_home"))
        # Strip qetl_home if the user accidentally added it.
        qualys_etl_user_home_env_var = Path(re.sub("/qetl_home.*$","", str(qualys_etl_user_home_env_var)))
        # Ensure prefix is opt/qetl/users
        if qualys_etl_user_home_env_var.parent.name == 'users' and \
            qualys_etl_user_home_env_var.parent.parent.name == 'qetl' and \
                qualys_etl_user_home_env_var.parent.parent.parent.name == 'opt':
            # Valid directory ${USER DIR}/opt/qetl/users/{QualysUser}/qetl_home
            qetl_all_users_dir = qualys_etl_user_home_env_var.parent
            qetl_user_root_dir = qualys_etl_user_home_env_var
            qetl_user_home_dir = Path(qualys_etl_user_home_env_var, 'qetl_home')
        else:
            # User directory not set correctly to include opt/qetl/users, abort
            try:
                etld_lib_functions.logger.error(f"error setting user home directory: {qualys_etl_user_home_env_var}")
                etld_lib_functions.logger.error(f"Ensure you are using opt/qetl/users as part of your path")
                etld_lib_functions.logger.error(f"see qetl_manage_user -h for options.")
                exit(1)
            except AttributeError as e:
                print(f"error setting user home directory: {qualys_etl_user_home_env_var}")
                print(f"Ensure you are using opt/qetl/users as part of your path")
                print(f"see qetl_manage_user -h for options.")
                exit(1)

    qetl_user_data_dir = Path(qetl_user_home_dir, "data")       # Data downloaded from API
    qetl_user_log_dir = Path(qetl_user_home_dir, "log")         # Optional Logs
    qetl_user_config_dir = Path(qetl_user_home_dir, "config")   # YAML FORMAT CONFIG
    qetl_user_cred_dir = Path(qetl_user_home_dir, "cred")       # YAML FORMAT CONFIG
    qetl_user_bin_dir = Path(qetl_user_home_dir, "bin")         # YAML FORMAT CONFIG
    validate_char_qetl_user_home_dir(qetl_user_home_dir)        # FINAL VALIDATION OF PATH
    setup_kb_vars()
    setup_host_list_vars()
    setup_host_list_detection_vars()
    setup_asset_inventory_vars()


def create_user_data_dirs():
    global qetl_user_data_dir
    global qetl_user_log_dir
    global qetl_user_config_dir
    global qetl_user_cred_dir
    global qetl_user_bin_dir
    global qetl_create_user_dirs_ok_flag  # False.  Set to true by qetl_manage_user
    if qetl_create_user_dirs_ok_flag is True:
        try:
            os.makedirs(qetl_user_home_dir, exist_ok=True)
            oschmod.set_mode(qetl_user_home_dir, "a+rwx,g-rwx,o-rwx")
            os.makedirs(qetl_user_data_dir, exist_ok=True)
            oschmod.set_mode(qetl_user_data_dir, "a+rwx,g-rwx,o-rwx")
            os.makedirs(qetl_user_log_dir, exist_ok=True)
            oschmod.set_mode(qetl_user_log_dir, "a+rwx,g-rwx,o-rwx")
            os.makedirs(qetl_user_config_dir, exist_ok=True)
            oschmod.set_mode(qetl_user_config_dir, "a+rwx,g-rwx,o-rwx")
            os.makedirs(qetl_user_cred_dir, exist_ok=True)
            oschmod.set_mode(qetl_user_cred_dir, "a+rwx,g-rwx,o-rwx")
            os.makedirs(qetl_user_bin_dir, exist_ok=True)
            oschmod.set_mode(qetl_user_bin_dir, "a+rwx,g-rwx,o-rwx")
        except Exception as e:
            etld_lib_functions.logger.error(f"error creating qetl home directories.  check permissions on "
                                  f"{str(qetl_user_home_dir.parent.parent)}")
            etld_lib_functions.logger.error(f"determine if permissions on file allow creating directories "
                                  f"{str(qetl_user_home_dir.parent.parent)}")
            etld_lib_functions.logger.error(f"Exception: {e}")
    elif Path(qetl_user_home_dir).is_dir() and \
        Path(qetl_user_log_dir).is_dir() and \
            Path(qetl_user_config_dir).is_dir() and \
            Path(qetl_user_cred_dir).is_dir() and \
            Path(qetl_user_bin_dir).is_dir() and \
            Path(qetl_user_data_dir).is_dir():
        pass
    else:
        try:
            etld_lib_functions.logger.error(f"error with qetl home directories. "
                                  f" Check {str(qetl_user_home_dir)} for data,config,log,bin,cred directories exist.")
            etld_lib_functions.logger.error(f"Use qetl_manage_user -h to create your qetl "
                                  f"user home directories if they don't exists.")
            exit(1)
        except AttributeError as ae:
            print(f"error with qetl home directories. "
                                  f" Check {str(qetl_user_home_dir)} for data,config,log,bin,cred directories exist.")
            print(f"Use qetl_manage_user -h to create your qetl user home directories if they don't exists.")
            exit(1)


def validate_char_qetl_user_home_dir(p: Path):
    p_match = re.fullmatch(r"[_A-Za-z0-9/]+", str(p))
    if etld_lib_functions.logging_is_on_flag is False:
        logging_method = print
    else:
        logging_method = etld_lib_functions.logger.error

    if p_match is None:
        logging_method(f"see qetl_manage_user -h, malformed parent directory: {p}")
        logging_method(f" Characters other than [_A-Za-z0-9/]+ found: {str(p)}")
        exit(1)
    if p.name != 'qetl_home':
        logging_method(f"see qetl_manage_user -h, malformed parent directory: {p}")
        logging_method(f" qetl_home not found: {str(p)}")
        exit(1)
    if p.parent.parent.name != 'users':
        logging_method(f"see qetl_manage_user -h, malformed parent directory: {p}")
        logging_method(f" users not found in parent: {str(p)}")
        exit(1)
    if p.parent.parent.parent.name != 'qetl':
        logging_method(f"see qetl_manage_user -h, malformed parent directory: {p}")
        logging_method(f" qetl not found in parent: {str(p)}")
        exit(1)
    if p.parent.parent.parent.parent.name != 'opt':
        logging_method(f"see qetl_manage_user -h, malformed parent directory: {p}")
        logging_method(f" opt not found in parent: {str(p)}")
        exit(1)

# DATA ENVIRONMENT AND DIRECTORIES
#
# Data Directory Structures and contents are:
#  - qetl_user_home_dir
#  - qetl_user_home_dir/qetl_home/data - All XML, JSON, CSV, SQLITE Data
#  - qetl_user_home_dir/qetl_home/log  - Optional Logs Location
#  - qetl_user_home_dir/qetl_home/config - date configurations for knowledgebase, host list and host list detection
#  - qetl_user_home_dir/qetl_home/cred   - Qualys Credentials Directory, ensure this is secure.
#  - qetl_user_home_dir/qetl_home/bin    - Initial Canned Scripts for Qualys API User


def setup_user_home_directories():
    # TODO setup home directories before logging so
    # TODO we can reference paths in qetl_manage_user before logging is turned on.
    # Directory Structure
    #  ${ANYDIR}/opt/qetl/users/${NAME OF USER}/qetl_home
    #
    #  qetl_user_root_dir = ${ANYDIR}/opt/qetl/users/{$NAME OF USER} = directory of a qetl user.
    #                       Ex. /home/dgregory/opt/qetl/users/{$NAME OF USER}
    #                       Ex. /opt/qetl/users/{$NAME OF USER}
    #  qetl_user_home_dir = ${ANYDIR}/opt/qetl/users/{$NAME OF USER}/qetl_home
    #                       Ex. /home/dgregory/opt/qetl/users/quays01/qetl_home
    #
    # Top level directories
    global qetl_all_users_dir            # opt/qetl/users
    global qetl_user_root_dir            # Parent directory for qetl_user_home_dir
    global qualys_etl_user_home_env_var  # Environment variable set to qualys_etl_user_home
    global qetl_user_home_dir            # Home directory for api data, config, credentials, logs.
    # Directories holding a users data
    global qetl_user_data_dir            # xml,json,csv,sqlite,shelve data
    global qetl_user_log_dir             # logs
    global qetl_user_config_dir          # configuration
    global qetl_user_cred_dir            # credentials
    global qetl_user_bin_dir             # TODO determine what to do with qetl_user_bin_dir

    global qetl_user_config_settings_yaml_file
    global qetl_user_config_settings_yaml

    global qetl_code_dir                 # Parent Directory of qualys_etl code dir.
    global qetl_user_default_config      # Initial configuration populated into qetl_user_config_dir

    set_path_qetl_user_home_dir()
    # TODO is it best to create directories if qetl_manage_user sets a flag? Yes.
    # TODO if flag unset, then prompt user or direct to qetl_manage_user?  Yes.
    create_user_data_dirs()

    etld_lib_functions.logger.info(f"parent user app dir  - {str(qetl_user_root_dir)}")
    etld_lib_functions.logger.info(f"user home directory  - {str(qetl_user_home_dir)}")
    etld_lib_functions.logger.info(f"qetl_all_users_dir   - All users dir       - {qetl_all_users_dir}")
    etld_lib_functions.logger.info(f"qetl_user_root_dir   - User root dir       - {qetl_user_root_dir}")
    etld_lib_functions.logger.info(f"qetl_user_home_dir   - qualys user         - {qetl_user_home_dir}")
    etld_lib_functions.logger.info(f"qetl_user_data_dir   - xml,json,csv,sqlite - {qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"qetl_user_log_dir    - log files           - {qetl_user_log_dir}")
    etld_lib_functions.logger.info(f"qetl_user_config_dir - yaml configuration  - {qetl_user_config_dir}")
    etld_lib_functions.logger.info(f"qetl_user_cred_dir   - yaml credentials    - {qetl_user_cred_dir}")
    etld_lib_functions.logger.info(f"qetl_user_bin_dir    - etl scripts         - {qetl_user_bin_dir}")


def load_etld_lib_config_settings_yaml():
    #
    # sets global etld_lib_config_settings_yaml_dict for reuse
    #
    global qetl_user_home_dir
    global qetl_user_data_dir
    global qetl_user_log_dir
    global qetl_user_config_dir
    global qetl_user_cred_dir
    global qetl_user_bin_dir
    global qetl_user_default_config
    global etld_lib_config_settings_yaml_dict
    global qetl_user_config_settings_yaml_file

# Create Default YAML if it doesn't exist.
    qetl_user_config_settings_yaml_file = Path(qetl_user_config_dir, "etld_config_settings.yaml")
    if not Path.is_file(qetl_user_config_settings_yaml_file):  # api_home/cred/etld_config_settings.yaml
        etld_lib_config_template = Path(qetl_code_dir, "qualys_etl",
                                             "etld_templates", "etld_config_settings.yaml")
        # Get Template
        with open(str(etld_lib_config_template), "r", encoding='utf-8') as etld_lib_config_template_f:
            etld_lib_config_template_string = etld_lib_config_template_f.read()

        # Write etld_lib_config_template_string to users directory.
        with open(qetl_user_config_settings_yaml_file, 'w', encoding='utf-8') as acf:
            local_date = api_date.get_local_date()  # Add date updated to file
            etld_lib_config_template_string = re.sub('\$DATE', local_date, etld_lib_config_template_string)
            acf.write(etld_lib_config_template_string)

    oschmod.set_mode(str(qetl_user_config_settings_yaml_file), "u+rw,u-x,go-rwx")

# Read YAML into global etld_lib_config_settings_yaml_dict

    try:
        with open(qetl_user_config_settings_yaml_file, 'r', encoding='utf-8') as etld_lib_config_yaml_file:
            etld_lib_config_settings_yaml_dict = yaml.safe_load(etld_lib_config_yaml_file)
            for key in etld_lib_config_settings_yaml_dict.keys():
                etld_lib_functions.logger.info(f"etld_config_settings.yaml - {key}: {etld_lib_config_settings_yaml_dict.get(key)} ")
    except Exception as e:
        etld_lib_functions.logger.error(f"etld_config_settings.yaml Exception: {e}")
        exit(1)


def get_kb_user_config():
    global kb_export_dir
    global kb_last_modified_after
    global qetl_user_config_settings_yaml_file
    global kb_csv_truncate_cell_limit

    kb_export_dir = etld_lib_config_settings_yaml_dict.get('kb_export_dir')
    kb_last_modified_after = etld_lib_config_settings_yaml_dict.get('kb_last_modified_after')

    etld_lib_functions.logger.info(f"knowledgeBase config - {qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"kb_export_dir yaml   - {kb_export_dir}")
    kb_csv_truncate_cell_limit = etld_lib_config_settings_yaml_dict.get('kb_csv_truncate_cell_limit')
    if isinstance(kb_csv_truncate_cell_limit, int):
        pass
    else:
        etld_lib_functions.logger.error(f"kb_csv_truncate_cell_limit is not an integer, please reconfigure.")
        etld_lib_functions.logger.error(f"kb_csv_truncate_cell_limit file: {qetl_user_config_settings_yaml_file}")
        exit(1)

    if qetl_manage_user_selected_datetime is not None:
        kb_last_modified_after = qetl_manage_user_selected_datetime
        etld_lib_functions.logger.info(f"kb_last_modified_after set by qetl_manage_user -d option - {kb_last_modified_after}")
    elif kb_last_modified_after == 'default':
        kb_last_modified_after = api_date.get_utc_date_minus_days(7)
        # TODO kb_last_modified_after is reset in knowledgebase_process_00_extract via function
        # TODO setup_vars_required_for_direct_execution_of_main.  Move function here for consistency.
        #etld_lib_functions.logger.info(f"kb_last_modified_after utc.now minus 7 days - {kb_last_modified_after}")
    else:
        etld_lib_functions.logger.info(f"kb_last_modified_after yaml - {kb_last_modified_after}")


def setup_kb_vars():
    global qetl_user_data_dir
    global kb_data_dir
    global kb_bin_dir
    global kb_xml_file
    global kb_shelve_file
    global kb_sqlite_file
    global kb_cve_qid_file
    global kb_cve_qid_map_shelve
    global kb_csv_file
    global kb_json_file
    global kb_log_file
    global kb_lock_file
    global kb_log_rotate_file
    global kb_table_name
    global kb_data_files

    kb_data_dir = qetl_user_data_dir
    kb_bin_dir = qetl_user_bin_dir
    kb_xml_file = Path(kb_data_dir, "kb.xml")
    kb_shelve_file = Path(kb_data_dir, "kb_shelve")
    kb_sqlite_file = Path(kb_data_dir, "kb_load_sqlite.db")
    kb_cve_qid_file = Path(kb_data_dir, "kb_cve_qid_map.csv")
    kb_cve_qid_map_shelve = Path(kb_data_dir, "kb_cve_qid_map_shelve")
    kb_csv_file = Path(kb_data_dir, "kb.csv")
    kb_json_file = Path(kb_data_dir, "kb.json")
    kb_log_file = Path(qetl_user_log_dir, "kb.log")
    kb_lock_file = Path(qetl_user_log_dir, ".kb.lock")
    kb_log_rotate_file = Path(qetl_user_log_dir, "kb.1.log")
    kb_table_name = 'Q_KnowledgeBase'
    kb_data_files = [kb_xml_file, kb_shelve_file, kb_sqlite_file, kb_cve_qid_file, kb_cve_qid_map_shelve, kb_csv_file,
                     kb_json_file]


def get_host_list_user_config():
    global host_list_data_dir
    global host_list_export_dir
    global qetl_user_config_settings_yaml_file
    global host_list_vm_processed_after
    global host_list_payload_option
    global qetl_manage_user_selected_datetime
    global host_list_csv_truncate_cell_limit
    global host_list_sqlite_file

    host_list_export_dir = etld_lib_config_settings_yaml_dict.get('host_list_export_dir')
    host_list_data_dir = qetl_user_data_dir
    host_list_vm_processed_after = etld_lib_config_settings_yaml_dict.get('host_list_vm_processed_after')
    host_list_payload_option = etld_lib_config_settings_yaml_dict.get('host_list_payload_option')

    etld_lib_functions.logger.info(f"host list config - {qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"host_list_export_dir yaml - {host_list_export_dir}")

    host_list_csv_truncate_cell_limit = etld_lib_config_settings_yaml_dict.get('host_list_csv_truncate_cell_limit')
    if isinstance(host_list_csv_truncate_cell_limit, int):
        pass
    else:
        etld_lib_functions.logger.error(f"host_list_csv_truncate_cell_limit is not an integer, please reconfigure.")
        etld_lib_functions.logger.error(f"host_list_csv_truncate_cell_limit file: {qetl_user_config_settings_yaml_file}")
        exit(1)

    if qetl_manage_user_selected_datetime is not None:
        host_list_vm_processed_after = qetl_manage_user_selected_datetime
        etld_lib_functions.logger.info(f"host_list_vm_processed_after set by qetl_manage_user -d option - "
                             f"{host_list_vm_processed_after}")
    elif host_list_vm_processed_after == 'default':
        #  By default get last 1 days of changes or if host_list_sqlite.db file exists
        #  use max_date to execute from that date.
        (min_date, max_date) = etld_lib_sqlite_tables.get_q_table_min_max_dates(
            host_list_sqlite_file, "LAST_VULN_SCAN_DATETIME", "Q_Host_List")
        if max_date.startswith("20"):
            etld_lib_functions.logger.info(f"Found Q_Host_List Min Date: {min_date} Max Date: {max_date}")
            max_date = re.sub(":..$", ":00", max_date)
            max_date = re.sub(" ", "T",max_date)
            max_date = re.sub("$", "Z", max_date)
            host_list_vm_processed_after = max_date
            etld_lib_functions.logger.info(f"host_list_vm_processed_after using max_date from database - {host_list_vm_processed_after}")
        else:
            host_list_vm_processed_after = api_date.get_utc_date_minus_days(1)
            etld_lib_functions.logger.info(f"host_list_vm_processed_after using utc.now minus 1 days - {host_list_vm_processed_after}")
    else:
        etld_lib_functions.logger.info(f"host_list_vm_processed_after yaml - {host_list_vm_processed_after}")

    if host_list_payload_option == 'notags':
        etld_lib_functions.logger.info(f"host_list_payload_option yaml - {host_list_payload_option}")
    else:
        host_list_payload_option = 'tags'
        etld_lib_functions.logger.info(f"host_list_payload_option yaml - {host_list_payload_option}")


def setup_host_list_vars():
    global qetl_user_data_dir
    global host_list_data_dir
    global host_list_xml_file_list
    global host_list_other_xml_file
    global host_list_ec2_xml_file
    global host_list_gcp_xml_file
    global host_list_azure_xml_file
    global host_list_shelve_file
    global host_list_sqlite_file
    global host_list_csv_file
    global host_list_json_file
    global host_list_log_file
    global host_list_lock_file
    global host_list_log_rotate_file
    global host_list_table_name
    global host_list_data_files

    host_list_data_dir = qetl_user_data_dir
    host_list_other_xml_file = Path(host_list_data_dir, "host_list_other_file.xml")
    host_list_ec2_xml_file = Path(host_list_data_dir, "host_list_ec2_file.xml")
    host_list_gcp_xml_file = Path(host_list_data_dir, "host_list_gcp_file.xml")
    host_list_azure_xml_file = Path(host_list_data_dir, "host_list_azure_file.xml")
    host_list_xml_file_list = [host_list_other_xml_file, host_list_ec2_xml_file,
                               host_list_gcp_xml_file, host_list_azure_xml_file]
    host_list_shelve_file = Path(host_list_data_dir, "host_list_shelve")
    host_list_sqlite_file = Path(host_list_data_dir, "host_list_sqlite.db")
    host_list_csv_file = Path(host_list_data_dir, "host_list.csv")
    host_list_json_file = Path(host_list_data_dir, "host_list.json")
    host_list_log_file = Path(qetl_user_log_dir, "host_list.log")
    host_list_lock_file = Path(qetl_user_log_dir, ".host_list.lock")
    host_list_log_rotate_file = Path(qetl_user_log_dir, "host_list.1.log")
    host_list_table_name = 'Q_Host_List'
    host_list_data_files = [host_list_other_xml_file, host_list_ec2_xml_file, host_list_gcp_xml_file,
                            host_list_azure_xml_file, host_list_shelve_file, host_list_sqlite_file,
                            host_list_csv_file, host_list_json_file]


def get_host_list_detection_user_config():
    global host_list_detection_data_dir
    global host_list_detection_export_dir
    global host_list_detection_vm_processed_after
    global host_list_detection_payload_option
    global host_list_detection_concurrency_limit
    global host_list_detection_multi_proc_batch_size
    global host_list_detection_limit_hosts
    global host_list_detection_csv_truncate_cell_limit
    global qetl_user_config_settings_yaml_file
    global qetl_manage_user_selected_datetime
    global host_list_vm_processed_after

    host_list_detection_export_dir = etld_lib_config_settings_yaml_dict.get('host_list_detection_export_dir')
    host_list_detection_csv_truncate_cell_limit = \
        etld_lib_config_settings_yaml_dict.get('host_list_detection_csv_truncate_cell_limit')
    host_list_detection_data_dir = qetl_user_data_dir
    host_list_detection_vm_processed_after = etld_lib_config_settings_yaml_dict.get('host_list_detection_vm_processed_after')
    host_list_detection_payload_option = etld_lib_config_settings_yaml_dict.get('host_list_detection_payload_option')
    host_list_detection_csv_truncate_cell_limit = etld_lib_config_settings_yaml_dict.get('host_list_detection_csv_truncate_cell_limit')
    if isinstance(host_list_detection_csv_truncate_cell_limit, int):
        pass
    else:
        etld_lib_functions.logger.error(f"host_list_detection_csv_truncate_cell_limit is not an integer, please reconfigure.")
        etld_lib_functions.logger.error(f"host_list_detection_csv_truncate_cell_limit file: {qetl_user_config_settings_yaml_file}")
        exit(1)

    host_list_detection_concurrency_limit = etld_lib_config_settings_yaml_dict.get('host_list_detection_concurrency_limit')
    host_list_detection_multi_proc_batch_size = \
        etld_lib_config_settings_yaml_dict.get('host_list_detection_multi_proc_batch_size')
    host_list_detection_limit_hosts = \
        etld_lib_config_settings_yaml_dict.get('host_list_detection_limit_hosts')

    etld_lib_functions.logger.info(f"host list detection config - {qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"host_list_detection_export_dir yaml - {host_list_detection_export_dir}")
    etld_lib_functions.logger.info(f"host_list_detection_concurrency_limit yaml - {host_list_detection_concurrency_limit}")
    etld_lib_functions.logger.info(f"host_list_detection_multi_proc_batch_size yaml - {host_list_detection_multi_proc_batch_size}")

    if qetl_manage_user_selected_datetime is not None:
        host_list_detection_vm_processed_after = qetl_manage_user_selected_datetime
        host_list_vm_processed_after = qetl_manage_user_selected_datetime
        etld_lib_functions.logger.info(f"host_list_detection_vm_processed_after and host_list_vm_processed_after "
                                       f"set by qetl_manage_user -d option - "
                                       f"{host_list_detection_vm_processed_after}")
    elif host_list_detection_vm_processed_after == 'default':
        (min_date, max_date) = etld_lib_sqlite_tables.get_q_table_min_max_dates(
            host_list_sqlite_file, "LAST_VULN_SCAN_DATETIME", "Q_Host_List")
        if max_date.startswith("20"):
            max_date = re.sub(":..$", ":00", max_date)
            max_date = re.sub(" ", "T", max_date)
            max_date = re.sub("$", "Z", max_date)
            host_list_detection_vm_processed_after = max_date
            host_list_vm_processed_after = max_date
            etld_lib_functions.logger.info(f"Found Q_Host_List Min Date: {min_date} Max Date: {max_date}")
            etld_lib_functions.logger.info(f"host_list_detection_vm_processed_after and host_list_vm_processed_after using "
                                           f"max_date from Q_Host_List database - "
                                           f"{host_list_detection_vm_processed_after}")
        else:
            host_list_detection_vm_processed_after = api_date.get_utc_date_minus_days(1)
            host_list_vm_processed_after = host_list_detection_vm_processed_after
            etld_lib_functions.logger.info(f"host_list_detection_vm_processed_after and host_list_vm_processed_after "
                                           f" using utc.now minus 1 days - {host_list_detection_vm_processed_after}")
    else:
        etld_lib_functions.logger.info(f"host_list_detection_vm_processed_after yaml - "
                                       f"{host_list_detection_vm_processed_after}")

    if host_list_detection_payload_option == 'notags':
        etld_lib_functions.logger.info(f"host_list_detection_payload_option yaml - {host_list_detection_payload_option}")
    else:
        host_list_detection_payload_option = 'tags'
        etld_lib_functions.logger.info(f"host_list_detection_payload_option yaml - {host_list_detection_payload_option}")


def setup_host_list_detection_vars():
    global qetl_user_data_dir
    global host_list_detection_data_dir
    global host_list_detection_xml_file
    global host_list_detection_xml_dir
    global host_list_detection_shelve_file
    global host_list_detection_sqlite_file
    global host_list_detection_csv_file
    global host_list_detection_csv_truncate_cell_limit
    global host_list_detection_json_file
    global host_list_detection_log_file
    global host_list_detection_lock_file
    global host_list_detection_log_rotate_file
    global host_list_detection_table_name
    global host_list_detection_data_files

    host_list_detection_data_dir = Path(qetl_user_data_dir)
    host_list_detection_xml_dir = Path(host_list_detection_data_dir, "host_list_detection_xml_dir")
    host_list_detection_xml_file = Path(host_list_detection_xml_dir, "host_list_detection_rename_me_to_batch.xml")
    host_list_detection_shelve_file = Path(host_list_detection_data_dir, "host_list_detection_shelve")
    host_list_detection_sqlite_file = Path(host_list_detection_data_dir, "host_list_detection_sqlite.db")
    host_list_detection_csv_file = Path(host_list_detection_data_dir, "host_list_detection.csv")
    host_list_detection_json_file = Path(host_list_detection_data_dir, "host_list_detection.json")
    host_list_detection_log_file = Path(qetl_user_log_dir, "host_list_detection.log")
    host_list_detection_lock_file = Path(qetl_user_log_dir, ".host_list_detection.lock")
    host_list_detection_log_rotate_file = Path(qetl_user_log_dir, "host_list_detection.1.log")
    host_list_detection_table_name = 'Q_Host_List_Detection'
    host_list_detection_data_files = [host_list_detection_shelve_file, host_list_detection_sqlite_file,
                                      host_list_detection_csv_file, host_list_detection_json_file]


def get_asset_inventory_user_config():
    global asset_inventory_data_dir
    global asset_inventory_export_dir
    global asset_inventory_asset_last_updated
    global asset_inventory_payload_option
    global asset_inventory_concurrency_limit
    global asset_inventory_multi_proc_batch_size
    global asset_inventory_limit_hosts
    global asset_inventory_csv_truncate_cell_limit
    global qetl_user_config_settings_yaml_file
    global qetl_manage_user_selected_datetime

    asset_inventory_export_dir = etld_lib_config_settings_yaml_dict.get('asset_inventory_export_dir')
    asset_inventory_csv_truncate_cell_limit = \
        etld_lib_config_settings_yaml_dict.get('asset_inventory_csv_truncate_cell_limit')
    asset_inventory_data_dir = qetl_user_data_dir
    asset_inventory_asset_last_updated = etld_lib_config_settings_yaml_dict.get('asset_inventory_asset_last_updated')
    asset_inventory_payload_option = etld_lib_config_settings_yaml_dict.get('asset_inventory_payload_option')
    asset_inventory_csv_truncate_cell_limit = etld_lib_config_settings_yaml_dict.get('asset_inventory_csv_truncate_cell_limit')
    if isinstance(asset_inventory_csv_truncate_cell_limit, int):
        pass
    else:
        etld_lib_functions.logger.error(f"asset_inventory_csv_truncate_cell_limit is not an integer, please reconfigure.")
        etld_lib_functions.logger.error(f"asset_inventory_csv_truncate_cell_limit file: {qetl_user_config_settings_yaml_file}")
        exit(1)

    asset_inventory_concurrency_limit = etld_lib_config_settings_yaml_dict.get('asset_inventory_concurrency_limit')
    asset_inventory_multi_proc_batch_size = \
        etld_lib_config_settings_yaml_dict.get('asset_inventory_multi_proc_batch_size')
    asset_inventory_limit_hosts = \
        etld_lib_config_settings_yaml_dict.get('asset_inventory_limit_hosts')

    etld_lib_functions.logger.info(f"asset inventory config - {qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"asset_inventory_export_dir yaml - {asset_inventory_export_dir}")
    etld_lib_functions.logger.info(f"asset_inventory_json_dir yaml - {asset_inventory_json_dir}")
    etld_lib_functions.logger.info(f"asset_inventory_concurrency_limit yaml - {asset_inventory_concurrency_limit}")
    etld_lib_functions.logger.info(f"asset_inventory_multi_proc_batch_size yaml - {asset_inventory_multi_proc_batch_size}")
    etld_lib_functions.logger.info(f"asset_inventory_csv_truncate_cell_limit yaml - {asset_inventory_csv_truncate_cell_limit}")

    if qetl_manage_user_selected_datetime is not None:
        asset_inventory_asset_last_updated = qetl_manage_user_selected_datetime
        etld_lib_functions.logger.info(f"asset_inventory_asset_last_updated "
                                       f"set by qetl_manage_user -d option - "
                                       f"{asset_inventory_asset_last_updated}")
    elif asset_inventory_asset_last_updated == 'default':
        asset_inventory_asset_last_updated = api_date.get_utc_date_minus_days(1)
        etld_lib_functions.logger.info(f"asset_inventory_asset_last_updated default set to  "
                                       f"utc.now minus 1 days - {asset_inventory_asset_last_updated}")
    else:
        etld_lib_functions.logger.info(f"asset_inventory_asset_last_updated yaml - "
                                       f"{asset_inventory_asset_last_updated}")


def setup_asset_inventory_vars():
    global qetl_user_data_dir
    global asset_inventory_data_dir
    global asset_inventory_json_batch_file
    global asset_inventory_json_dir
    global asset_inventory_shelve_file
    global asset_inventory_sqlite_file
    global asset_inventory_csv_file
    global asset_inventory_csv_truncate_cell_limit
    global asset_inventory_json_file
    global asset_inventory_log_file
    global asset_inventory_lock_file
    global asset_inventory_log_rotate_file
    global asset_inventory_table_name
    global asset_inventory_data_files
    global asset_inventory_temp_shelve_file

    asset_inventory_data_dir = Path(qetl_user_data_dir)
    asset_inventory_json_dir = Path(asset_inventory_data_dir, "asset_inventory_json_dir")
    asset_inventory_json_batch_file = Path(asset_inventory_json_dir, "asset_inventory_rename_me_to_batch.xml")
    asset_inventory_temp_shelve_file = Path(asset_inventory_json_dir, "asset_inventory_temp_shelve.db")
    asset_inventory_shelve_file = Path(asset_inventory_data_dir, "asset_inventory_shelve")
    asset_inventory_sqlite_file = Path(asset_inventory_data_dir, "asset_inventory_sqlite.db")
    asset_inventory_csv_file = Path(asset_inventory_data_dir, "asset_inventory.csv")
    asset_inventory_json_file = Path(asset_inventory_data_dir, "asset_inventory.json")
    asset_inventory_log_file = Path(qetl_user_log_dir, "asset_inventory.log")
    asset_inventory_lock_file = Path(qetl_user_log_dir, ".asset_inventory.lock")
    asset_inventory_log_rotate_file = Path(qetl_user_log_dir, "asset_inventory.1.log")
    asset_inventory_table_name = 'Q_Asset_Inventory'
    asset_inventory_data_files = [asset_inventory_shelve_file, asset_inventory_sqlite_file,
                                  asset_inventory_csv_file, asset_inventory_json_file]


def setup_completed():
    global setup_completed_flag
    setup_completed_flag = True


def get_qetl_code_dir():
    global qetl_code_dir         # Parent of qualys_etl directory
    global qetl_code_dir_child   # qualys_etl directory
    qetl_code_dir = etld_lib_functions.qetl_code_dir
    qetl_code_dir_child = etld_lib_functions.qetl_code_dir_child


def main():
    get_qetl_code_dir()
    setup_user_home_directories()

    load_etld_lib_config_settings_yaml()

    setup_kb_vars()
    get_kb_user_config()

    setup_host_list_vars()
    get_host_list_user_config()

    setup_host_list_detection_vars()
    get_host_list_detection_user_config()

    setup_asset_inventory_vars()
    get_asset_inventory_user_config()

    setup_completed()


if __name__ == '__main__':
    etld_lib_functions.main()
    main()
