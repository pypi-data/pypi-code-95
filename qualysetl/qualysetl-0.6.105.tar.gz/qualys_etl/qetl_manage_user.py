#!/usr/bin/env python3
# Manage qetl users.
import argparse
import os
import sys
import re
import logging
import time
import getpass
from pathlib import Path
import qualys_etl.etld_lib.etld_lib_functions as etld_lib_functions
import qualys_etl.etld_lib.etld_lib_config as etld_lib_config
import qualys_etl.etld_lib.etld_lib_credentials as etld_lib_credentials
import qualys_etl.etld_lib.etld_lib_datetime as api_datetime

global qetl_user_home
global found_api_credentials
global command_line_arguments


def validate_username(username):
    username_match = re.fullmatch(r"[-_A-Za-z0-9]+", username)
    if username_match is None:
        return False
    else:
        return True


def validate_api_fqdn_server(api_fqdn_server):
    api_fqdn_server_match = re.fullmatch(r"^.*qualysapi\..*$", api_fqdn_server)  # Matches qualysapi.
    if api_fqdn_server_match is None:
        return False
    else:
        return True


def validate_gateway_fqdn_server(gateway_fqdn_server):
    gateway_fqdn_server_match = re.fullmatch(r"^.*gateway\..*$", gateway_fqdn_server)  # Matches gateway
    if gateway_fqdn_server_match is None:
        return False
    else:
        return True


def validate_password(password):
    password_match = re.fullmatch(r"[ ]+", password)
    if password_match is None:
        return True  # found no spaces in password, accept it for now.
    else:
        return False  # found spaces in password


def update_api_fqdn_server(cred):
    print(f"Current api_fqdn_server: {cred.get('api_fqdn_server')}")
    response = input(f"Update api_fqdn_server? ( yes or no ): ")
    if response in 'yes':
        while True:
            new_api_fqdn_server = input(f"Enter new api_fqdn_server: ")
            new_api_fqdn_server = re.sub("https://", '', new_api_fqdn_server)
            new_api_fqdn_server = re.sub("http://", '', new_api_fqdn_server)
            new_api_fqdn_server = re.sub("/", '', new_api_fqdn_server)
            if validate_api_fqdn_server(new_api_fqdn_server):
                break
            else:
                print(f"Not valid qualysapi FQDN, retry.")
        cred['api_fqdn_server'] = new_api_fqdn_server
    pass


def update_gateway_fqdn_server(cred):
    if cred.get('api_fqdn_server') in etld_lib_credentials.platform_url.keys():
        cred['gateway_fqdn_server'] = etld_lib_credentials.platform_url.get(cred.get('api_fqdn_server'))

    print(f"Current gateway_fqdn_server: {cred.get('gateway_fqdn_server')}")
    response = input(f"Update gateway_fqdn_server? ( yes or no ): ")
    if response in 'yes':
        while True:
            new_gateway_fqdn_server = input(f"Enter new gateway_fqdn_server: ")
            new_gateway_fqdn_server = re.sub("https://", '', new_gateway_fqdn_server)
            new_gateway_fqdn_server = re.sub("http://", '', new_gateway_fqdn_server)
            new_gateway_fqdn_server = re.sub("/", '', new_gateway_fqdn_server)
            if validate_gateway_fqdn_server(new_gateway_fqdn_server):
                break
            else:
                print(f"Not valid gateway FQDN, retry.")
        cred['gateway_fqdn_server'] = new_gateway_fqdn_server
    pass


def update_username(cred):
    time.sleep(1)
    print(f"\n\nCurrent username: {cred.get('username')} in config: {etld_lib_credentials.cred_file}")
    response = input(f"Update Qualys username? ( yes or no ): ")
    if response in 'yes':
        while True:
            new_username = input(f"Enter new Qualys username: ")
            if validate_username(new_username):
                break
            else:
                print(f"Found invalid characters.  Try again.  Use only AlphaNumeric or underscore in username.")
        cred['username'] = new_username
    pass


def update_password(cred):
    print(f"Update password for username: {cred.get('username')}")
    response = input(f"Update password? ( yes or no ): ")
    if response in 'yes':
        while True:
            new_password = getpass.getpass(f"Enter your Qualys password: ")
            if validate_password(new_password):
                break
            else:
                print(f"Found spaces in password, try again.")
        cred['password'] = new_password
    pass


def if_update_credentials(first_time=False):
    if command_line_arguments.credentials is not None or first_time is not False:
        etld_lib_config.main()
        etld_lib_credentials.main()
        credentials = etld_lib_credentials.get_cred()
        update_username(credentials)
        update_api_fqdn_server(credentials)
        update_gateway_fqdn_server(credentials)
        update_password(credentials)
        old_cred = etld_lib_credentials.get_cred()
        if old_cred == credentials:
            print(f"No changes to qualys username, password, api_fqdn_server or gateway_fqdn_server.")
        else:
            etld_lib_credentials.update_cred(credentials)
            new_credentials = etld_lib_credentials.get_cred()
            etld_lib_functions.logger.info(f"credentials updated.  username: {new_credentials.get('username')} "
                                           f"api_fqdn_server: {new_credentials.get('api_fqdn_server')} "
                                           f"gateway_fqdn_server: {new_credentials.get('gateway_fqdn_server')} "
                                           f"")
            print(f"You have updated your credentials.")
            print(f"  Qualys Username: {new_credentials.get('username')}")
            print(f"  Qualys api_fqdn_server: {new_credentials.get('api_fqdn_server')}\n")


def start_etl_knowledgebase():
    import qualys_etl.etld_knowledgebase.etld_00_spawn_workflow_manager_knowledgebase as etl_kb_spawn_from_qetl_manage_user
    print(f"Starting etl_knowledgebase.  For progress see your {etld_lib_config.kb_log_file}")
    etl_kb_spawn_from_qetl_manage_user.main()
    print(f"End      etl_knowledgebase.  For progress see your {etld_lib_config.kb_log_file}")


def start_etl_host_list():
    import qualys_etl.etld_host_list.etld_00_spawn_workflow_manager_host_list \
        as etl_host_list_spawn_from_qetl_manage_user
    print(f"Starting etl_host_list.  For progress see: {etld_lib_config.host_list_log_file}")
    etl_host_list_spawn_from_qetl_manage_user.main()
    print(f"End      etl_host_list.  For results see:  {etld_lib_config.host_list_log_file}")


def start_etl_asset_inventory():
    import qualys_etl.etld_asset_inventory.etld_00_spawn_workflow_manager_asset_inventory \
        as etl_asset_inventory_spawn_from_qetl_manage_user
    print(f"Starting etl_asset_inventory.  For progress see: {etld_lib_config.asset_inventory_log_file}")
    etl_asset_inventory_spawn_from_qetl_manage_user.main()
    print(f"End      etl_asset_inventory.  For progress see: {etld_lib_config.asset_inventory_log_file}")


def start_etl_host_list_detection():
    import qualys_etl.etld_host_list_detection.etld_00_spawn_workflow_manager_host_list_detection \
       as etl_host_list_detection_spawn_from_qetl_manage_user
    print(f"Starting etl_host_list_detection.  For progress see: {etld_lib_config.host_list_detection_log_file}")
    etl_host_list_detection_spawn_from_qetl_manage_user.main()
    print(f"End      etl_host_list_detection.  For results see:  {etld_lib_config.host_list_detection_log_file}")


def command_line_arguments_datetime():
    if command_line_arguments.datetime is None:
        pass
    else:
        if api_datetime.is_valid_qualys_datetime_format(command_line_arguments.datetime):
            etld_lib_config.qetl_manage_user_selected_datetime = command_line_arguments.datetime
        else:
            print(f"\nInvalid datetime: {str(command_line_arguments.datetime)}, "
                  f"please review format and retry when ready")
            print(f"Option: -d 'YYYY-MM-DDThh:mm:ssZ'")
            exit(1)


def if_execute_etl_module():
    command_line_arguments_datetime()
    if command_line_arguments.execute_etl_module == 'etl_knowledgebase':
        start_etl_knowledgebase()
    elif command_line_arguments.execute_etl_module == 'etl_host_list':
        start_etl_host_list()
    elif command_line_arguments.execute_etl_module == 'etl_host_list_detection':
        ## TODO add fcntl lock on etl_knowledgebase and etl_host_list so they are not run concurrently with etl_host_list_detection.
        ## TODO add fcntl lock check logic to stop running if host list or knowledgebase are already executing.
        start_etl_host_list_detection()
    elif command_line_arguments.execute_etl_module == 'etl_asset_inventory':
        start_etl_asset_inventory()
    elif command_line_arguments.execute_etl_module is None:
        pass
    else:
        etld_lib_functions.logger.info(f"Invalid Option: {str(command_line_arguments.execute_etl_module)}, "
                                       f"retry when ready.")
        print(f"\nInvalid Option: {str(command_line_arguments.execute_etl_module)}, retry when ready")
        print(f"Options are: -e etl_knowledgebase or -e etl_host_list or -e etl_host_list_detection")
        exit(1)


def if_qualys_test_login(first_time=False):
    if command_line_arguments.test is not None or first_time is not False:
        etld_lib_functions.main(log_level=logging.INFO, my_logger_prog_name='qetl_manage_user')
        etld_lib_config.main()
        etld_lib_credentials.main()
        credentials = etld_lib_credentials.get_cred()
        print(f"Qualys Login Test for {credentials.get('username')} "
              f"at api_fqdn_server: {credentials.get('api_fqdn_server')}\n")
        etld_lib_credentials.test_basic_auth()
        if etld_lib_credentials.login_failed is not True:
            print(f"Testing Qualys Login for {credentials.get('username')} "
                  f"Succeeded at {credentials.get('api_fqdn_server')}\n"
                  f"    with HTTPS Return Code: {etld_lib_credentials.http_return_code}.")
        etld_lib_functions.main(log_level=logging.WARN, my_logger_prog_name='qetl_manage_user')


def if_qualys_test_gateway_login(first_time=False):
    if command_line_arguments.test is not None or first_time is not False:
        etld_lib_functions.main(log_level=logging.INFO, my_logger_prog_name='qetl_manage_user')
        etld_lib_config.main()
        etld_lib_credentials.main()
        credentials = etld_lib_credentials.get_cred()
        print(f"Qualys Login Test for {credentials.get('username')} "
              f"at gateway_fqdn_server: {credentials.get('gateway_fqdn_server')}\n")
        etld_lib_credentials.test_gateway_auth()
        if etld_lib_credentials.login_failed is not True:
            print(f"Testing Qualys Login for {credentials.get('username')} "
                  f"Succeeded at {credentials.get('api_fqdn_server')}\n"
                  f"    with HTTPS Return Code: {etld_lib_credentials.http_return_code}.")
        etld_lib_functions.main(log_level=logging.WARN, my_logger_prog_name='qetl_manage_user')


def if_print_report():
    if command_line_arguments.report is not None:
        print(f"Report on user: {etld_lib_config.qetl_user_home_dir}")
        for path in sorted(etld_lib_config.qetl_user_home_dir.rglob('*')):
            depth = len(path.relative_to(etld_lib_config.qetl_user_home_dir).parts)
            spacer = '    ' * depth
            print(f'{spacer}+ {path.name}')
        print("\n")


def help_message(notes):
    help_mess = f'''
        
    {notes}
        
    usage: qetl_manage_user [-h] -u qetl_USER_HOME_DIR [-e execute etl module] [-c] [-t] [-d] [-r] [-l]
    
    Setup and execute etl module for your qualys qetl users.  
    
    optional arguments:
      -h, --help                show this help message and exit
      -u Home Directory Path, --qetl_user_home_dir Home directory Path
                                   Include prefix opt/qetl/users/[user dir] 
                                   Examples:
                                   1) /home/dgregory/opt/qetl/users/q_username 
                                   2) /opt/qetl/users/q_username
      -e etl module name,     --execute_etl_module module name
                                  Ex.  -e etl_knowledgebase or -e etl_host_list or -e etl_host_list_detection
      -d YYMMDDThh:mm:ssZ,    --datetime        YYYY-MM-DDThh:mm:ssZ UTC. Get All Data On or After Date. 
                                                Ex. 1970-01-01T00:00:00Z acts as flag to obtain all data.
      -c, --credentials       update qualys api user credentials: qualys username, password or api_fqdn_server
      -t, --test              test qualys credentials
      -l, --logs              detailed logs sent to stdout
      -r, --report            brief report of the users directory structure.
     
    '''
    print(f"{help_mess}")


def test_command_line_arguments():
    results = command_line_arguments
    # If no options check for -u.  If -u exists, help_message.  If -u does not exist, continue to new user prompts.
    # If -u is not set, help_message
    if results.qetl_user_home_dir is None:
        help_message(f"Please enter -u [ your /opt/qetl/users/ user home directory path ]\n\n"
                     f"    Note: /opt/qetl/users/newuser is the root directory for your qetl userhome directory,\n" 
                     f"           enter a new path including the opt/qetl/users/newuser \n"
                     f"           in the path you have authorization to write to.\n"
                     f"           the prefix to your user directory opt/qetl/users is required.\n"
                     f"    Example:\n"
                     f"             qetl_manage_user -u /opt/qetl/users/[your_user_name]\n"
                     f" ")
        exit(6)  # 6 is for testing the command works. Ex. qetl_manage_user; if [[ "$?" == "6"]]; then : ...

    test_qetl_user_home_dir = Path(results.qetl_user_home_dir).absolute()
    if test_qetl_user_home_dir.parent.parent.is_dir() and \
            os.access(str(test_qetl_user_home_dir.parent.parent), os.W_OK) and \
            test_qetl_user_home_dir.parent.name == 'users' and \
            test_qetl_user_home_dir.parent.parent.name == 'qetl' and \
            test_qetl_user_home_dir.parent.parent.parent.name == 'opt':
        pass
    else:
        help_message(f"Please check permissions on {test_qetl_user_home_dir.parent.parent},\n "
                     f"   You don't appear to have authorization to write to that directory.\n")
        exit(1)

    ##TODO Add datetime methods to test date entered.

    if test_qetl_user_home_dir.is_dir():
        if results.execute_etl_module is None and \
                results.credentials is None and \
                results.test is None and \
                results.logs is None and \
                results.report is None:
            help_message(f"Please select an option for qetl_user: {results.qetl_user_home_dir}")
            exit(1)
    else:
        pass


def get_command_line_arguments(args=None):
    global command_line_arguments
    parser = argparse.ArgumentParser(description='Setup and execute etl for your qualys qetl users.')
    parser.add_argument('-u', '--qetl_user_home_dir', default=None, help="Please enter -u option")
    parser.add_argument('-e', '--execute_etl_module', default=None, help='Execute etl_knowledgebase, etl_host_list or etl_host_list_detection')
    parser.add_argument('-d', '--datetime', default=None,
                        help='YYYY-MM-DDThh:mm:ssZ UTC. Get All Data On or After Date.  Ex. 1970-01-01T00:00:00Z acts as flag to obtain all data.')
    parser.add_argument('-c', '--credentials', default=None, action="store_true",
                        help='update qualys api user credentials: qualys uername, password or api_fqdn_server')
    parser.add_argument('-t', '--test', default=None, action="store_true", help='test qualys credentials')
    parser.add_argument('-l', '--logs', default=None, action="store_true", help='detailed logs sent to stdout')
    parser.add_argument('-r', '--report', default=None, action="store_true",
                        help='Brief report of the users directory structure.')
    command_line_arguments = parser.parse_args(args)


def setup_qetl_user_home_dir_environment():
    global qetl_user_home
    global command_line_arguments
    # Reset Logging.
    if command_line_arguments.execute_etl_module is None:
        if command_line_arguments.logs is None:
            etld_lib_functions.main(log_level=logging.WARNING, my_logger_prog_name='qetl_manage_user')
        else:
            etld_lib_functions.main(log_level=logging.INFO, my_logger_prog_name='qetl_manage_user')
    else:
        pass

    # qetl_user_home_dir
    os.environ['qualys_etl_user_home'] = command_line_arguments.qetl_user_home_dir
    etld_lib_config.set_path_qetl_user_home_dir()  # If qetl_user_home_dir is malformed, we abort here.
    if etld_lib_config.qetl_user_home_dir.is_dir():
        # Directory Exists.  Options are test, report, execute, etc...
        pass
    else:
        # Potential New User, Query for confirmation
        time.sleep(1)
        print(f"\nqetl_user_home_dir does not exist: {etld_lib_config.qetl_user_home_dir}")
        response = input(f"Create new qetl_user_home_dir? {etld_lib_config.qetl_user_home_dir} ( yes or no ): ")
        if response == 'yes':
            if command_line_arguments.execute_etl_module is not None:
                if command_line_arguments.logs is None:
                    etld_lib_functions.main(log_level=logging.WARNING, my_logger_prog_name='qetl_manage_user')
                else:
                    etld_lib_functions.main(log_level=logging.INFO, my_logger_prog_name='qetl_manage_user')
            etld_lib_config.qetl_create_user_dirs_ok_flag = True
            etld_lib_config.main()
            time.sleep(1)
            print(f"\nqetl_user_home_dir created: {etld_lib_config.qetl_user_home_dir}")
            if_update_credentials(first_time=True)
            response = input(f"\nWould you like to test login/logout of Qualys API? ( yes or no ): ")
            if response == 'yes':
                print("")
                if_qualys_test_login(first_time=True)
            # response = input(f"\nWould you like to test login/logout of Qualys Gateway? ( yes or no ): ")
            # if response == 'yes':
            #     print("")
            #     if_qualys_test_gateway_login(first_time=True)
            print(f"\nThank you, exiting.\n")
            exit(0)
        else:
            print(f"\nThank you, exiting.\n")
            exit(1)


def main():
    get_command_line_arguments(sys.argv[1:])
    test_command_line_arguments()
    setup_qetl_user_home_dir_environment()
    if_update_credentials()
    if_qualys_test_login()
    if_execute_etl_module()
    if_print_report()


if __name__ == '__main__':
    main()



