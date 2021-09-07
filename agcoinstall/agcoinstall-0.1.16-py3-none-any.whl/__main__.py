"""Command-line interface."""
import base64
import fileinput
import hashlib
import hmac
import logging
import os
import random
import site
# from win32com.client import Dispatch
import subprocess
import time
import json
import configparser
import psutil
import platform
# import xml.etree.ElementTree as ET
# from collections import defaultdict
# import enum

import arrow
import click
import regobj
import requests
import pyautogui
from lxml import etree
from requests.auth import AuthBase

host = ''
base_url = ''
mac_id = ''
mac_token = ''
state = 'InitialMonitoring'

save_path = os.path.expanduser('~\\Desktop\\agcoinstall.log')
logging.basicConfig(filename=save_path, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


class MACAuth(AuthBase):
    """
    Attaches HTTP Authentication to the given Request object, and formats the header for every API call used
    """

    def __init__(self, mac_id, mac_token, host):
        # setup any auth-related data here
        self.mac_id = mac_id
        self.mac_token = mac_token
        self.host = host

    def __call__(self, r):
        # modify and return the request
        r.headers['Authorization'] = self.generate_header(r.method, r.path_url)
        return r

    def get_hmac(self, method, uri, milliseconds, nonce):
        http_version = 'HTTP/1.1'
        # host = HOST
        request_string = f'{method} {uri} {http_version}\n{self.host}\n{milliseconds}\n{nonce}\n'
        return base64.b64encode(
            hmac.new(self.mac_token.lower().encode(), request_string.encode(), hashlib.sha256).digest()).decode()

    def generate_header(self, method, uri):
        milliseconds = str(int(time.time() * 1000))
        nonce = ''.join(str(random.randint(0, 9)) for _i in range(8))
        formatted_hmac = self.get_hmac(method, uri, milliseconds, nonce)
        return f'MAC kid={self.mac_id},ts={milliseconds},nonce={nonce},mac=\"{formatted_hmac}\"'


class RegistryValues:

    def __init__(self):
        self._voucher = ''
        self._edt_update = ''
        self._mtapi = ''

    @property
    def voucher(self):
        """
        gets and return the voucher in the registry
        @return: voucher code as text
        """
        try:
            voucher_id = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT['Voucher'].data
        except AttributeError as e:
            click.secho(f'Voucher ID was not present in registry. Please confirm that EDT has been vouchered {e}',
                        fg='red')
            logging.error(f'Voucher ID was not present in registry. Please confirm that EDT has been vouchered {e}')
            voucher_id = ''
        except KeyError:
            voucher_id = ''
        self._voucher = voucher_id
        return voucher_id

    @property
    def edt_update(self):
        """
            gets and return the edt_update in the registry
            @return: edt_update code as text
            """
        try:
            edt_update = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT['UpdateNumber'].data
        except AttributeError as e:
            click.secho(f'UpdateNumber was not present in registry. It does not appear that EDT is currently'
                        f'installed.  \n {e}', fg='red')
            edt_update = ''
        except KeyError:
            edt_update = ''
        self._edt_update = edt_update
        return edt_update

    @property
    def mtapi(self):
        """
            gets and return the mtapi in the registry
            @return: mtapi code as text
        """
        try:
            mtapi = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT['MTAPISync_Version'].data
        except AttributeError as e:
            click.secho(f'UpdateNumber was not present in registry. It does not appear that EDT is currently '
                        f'installed. \n {e}', fg='red')
            mtapi = ''
        except KeyError:
            mtapi = ''
        self._mtapi = mtapi
        return mtapi


class ConfigIni:

    def __init__(self):
        self._ready_to_install = ''
        self._active_packages = 0
        self._pause_downloads_set = False

    @property
    def ready_to_install(self):
        if os.path.isfile(r"C:\ProgramData\AGCO Corporation\AGCO Update\config.ini"):
            try:
                parser = configparser.ConfigParser()
                parser.read(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini')
                ready_to_install_value = parser.get('Status', 'ReadyToInstall')
                logging.debug(f'ReadyToInstallValue: {ready_to_install_value}')
                self._ready_to_install = ready_to_install_value
                return ready_to_install_value
            except configparser.NoSectionError as e:
                print(e)
                logging.exception(e)
                time.sleep(5)
            except AttributeError as e:
                print(e)
                logging.exception(e)
                time.sleep(5)

    @property
    def active_packages(self):
        parser = configparser.ConfigParser()
        try:
            parser.read(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini')
            active_packages_string = parser.get('Status', 'ActivePackages')
            logging.info(f'Number of active packages in AUC: {active_packages_string}')
        except:
            active_packages_string = 0
        self._active_packages = int(active_packages_string)
        return int(active_packages_string)

    @property
    def pause_downloads_set(self):
        parser = configparser.ConfigParser()
        try:
            parser.read(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini')
            download_schedule_value = parser.get('Settings', 'DownloadSchedule')
            logging.info(f'DownloadSchedule: {download_schedule_value}')
            result = 'toggle' in download_schedule_value
        except:
            click.secho('Could not read config.ini for Settings>>DownloadSchedule')
            result = False
        self._pause_downloads_set = result
        return result


class InstallState:

    def __init__(self, updategroup, config_ini, registry):
        self._updategroup = updategroup
        self._state = "InitialMonitoring"
        self._config_ini = config_ini
        self._registry = registry
        self._models_installed = False

    @property
    def voucher(self):
        return self._registry._voucher

    @property
    def edt_update(self):
        return self._registry._edt_update

    @property
    def mtapi(self):
        return self._registry._mtapi

    @property
    def ready_to_install(self):
        return self._config_ini._ready_to_install

    @property
    def active_packages(self):
        return self._config_ini._active_packages

    @property
    def pause_downloads_set(self):
        return self._config_ini._pause_downloads_set

    @property
    def models_installed(self):
        if os.path.isdir(r'C:\ProgramData\AGCO Corporation\EDT\Models'):
            models_dir = next(os.walk('C:\ProgramData\AGCO Corporation\EDT\Models'))[1]
            self._models_installed = len(models_dir)
            return len(models_dir)
        else:
            return False

    @property
    def get_state(self):
        self._config_ini.ready_to_install
        self._config_ini.pause_downloads_set
        self._config_ini.active_packages
        self._registry.edt_update
        self._registry.mtapi
        self._registry.voucher
        self.models_installed

        if self._config_ini._ready_to_install and not self._registry.edt_update:
            logging.info("Changing current_state to ReadyToInstallCorePackages")
            self._state = 'ReadyToInstallCorePackages'
            return "ReadyToInstallCorePackages"

        elif self._config_ini._ready_to_install and self._registry._voucher and self._config_ini._active_packages != 0 \
                and self._updategroup in ('EDTUpdates', 'InternalTestPush', 'TestPush'):
            logging.info("Changing current_state to ReadyToInstallAdditional")
            self._state = 'ReadyToInstallAdditional'
            return "ReadyToInstallAdditional"

        elif not self._config_ini._ready_to_install and self._registry.edt_update and \
                self._config_ini._active_packages == 0 and not self._registry._voucher:
            logging.info("Changing current_state to EDTNeedsVouchered")
            self._state = 'EDTNeedsVouchered'
            return 'EDTNeedsVouchered'

        elif self._config_ini._pause_downloads_set and self._config_ini._active_packages > 1:
            logging.info("Changing current_state to DownloadsPaused")
            self._state = 'DownloadsPaused'
            return 'DownloadsPaused'

        elif self._config_ini._active_packages == 0 and not self._config_ini._ready_to_install and \
                self._registry._mtapi and self._updategroup in ('EDTUpdates', 'InternalTestPush', 'TestPush') \
                and self._models_installed:
            logging.info("Changing current_state to AllDownloadsCompleted")
            self._state = 'AllDownloadsCompleted'
            return 'AllDownloadsCompleted'

        elif self._config_ini._active_packages == 0 and not self._config_ini._ready_to_install and \
                self._registry._mtapi and self._updategroup not in ('EDTUpdates', 'InternalTestPush', 'TestPush') \
                and not self._models_installed:
            logging.info("Changing current_state to AllDownloadsCompleted")
            self._state = 'AllDownloadsCompleted'
            return 'AllDownloadsCompleted'

        else:
            self._state = 'InitialMonitoring'
            return 'InitialMonitoring'


def is_os_64bit():
    return platform.machine().endswith('64')


def download_auc_client():
    url = 'https://agcoedtdyn.azurewebsites.net/AGCOUpdateClient'
    save_path = os.path.expanduser('~\\Desktop\\AGCOUpdateClient.exe')
    try:
        r = requests.get(url, allow_redirects=True)
        try:
            open(save_path, 'wb').write(r.content)
        except:
            logging.error('Unable to download the AUC client')
    except:
        logging.error('The link to download the latest AUC is down')


def install_auc():
    execute_command(os.path.expanduser('~\\Desktop\\AGCOUpdateClient.exe /S /V INITCLIENT 1'))


def config_ini_find_and_replace(find_text, replace_text):
    logging.info(f'Attempting to replace \"{find_text}\" with \"{replace_text}\" in the config.ini file')
    kill_process_by_name('AGCOUpdateService')
    with fileinput.FileInput(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini', inplace=True,
                             backup='.bak') as file:
        for line in file:
            print(line.replace(find_text, replace_text), end='')
    set_service_running('AGCO Update')
    start_auc()
    time.sleep(10)


def get_auth(username, password):
    auth = requests.auth.HTTPBasicAuth(username, password)
    uri = f'{base_url}/api/v2/Authentication'

    payload = {'username': username,
               'password': password
               }
    r = requests.post(uri, auth=auth, data=payload)
    user_auth = r.json()
    m_id = user_auth['MACId']
    m_token = user_auth['MACToken']
    return m_id, m_token


def set_auc_environment(env_base_url):
    # other_urls = set(remaining_urls.values())
    logging.info(f'Attempting to set the env url of {env_base_url} in the config.ini file')
    kill_process_by_name('AGCOUpdateService')
    with fileinput.FileInput(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini', inplace=True,
                             backup='.bak') as file:
        for line in file:
            if "UpdateHost2" in line:
                line = f'UpdateHost2={env_base_url}/api/v2\n'
            elif "UpdateHost" in line:
                line = f'UpdateHost={env_base_url}/api/v2\n'
        print(line, end='')
    set_service_running('AGCO Update')
    start_auc()
    time.sleep(10)


def get_license_id():
    voucher = get_voucher()
    logging.info(f'Attempting to get license id using the voucher code')
    uri = f'{base_url}/api/v2/Licenses'
    payload = {
        "VoucherCode": voucher,
        "Status": "Active",
    }
    r = requests.get(uri, auth=MACAuth(mac_id, mac_token, host), params=payload)
    license_dict = json.loads(r.text)
    return license_dict['Entities'][0]['LicenseID']


def add_services_to_license():
    license = get_license_id()
    logging.info(f'Attempting to add AuthCode to License for Dev environment')
    uri = f'{base_url}/api/v2/AuthorizationCodes'
    payload = {'DefinitionID': '7a3d3576-62c6-48bb-8456-0c27fa3e5eec',
               'ValidationParameters': [
                   {'Name': 'EDTInstanceID',
                    'Value': license}
               ],
               'DataParameters': [
                   {'Name': 'AGCODA',
                    'Value': 'True'},

                   {'Name': 'VDW',
                    'Value': 'True'},

                   {'Name': 'TestMode',
                    'Value': 'True'}
               ]
               }
    r = requests.post(uri, auth=MACAuth(mac_id, mac_token, host), json=payload)
    if not r.status_code == 200:
        click.secho(f'The attempt to authorize {license} to enable VDW, AGCODA, and TestMode was unsuccessful')


def restart_auc():
    logging.info(f'Attempting to restart AUC')
    kill_process_by_name('AGCOUpdateService')
    set_service_running('AGCO Update')
    start_auc()
    time.sleep(10)


def launch_edt():
    logging.debug('Attempting to start EDT')
    subprocess.call(r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe Start-Process '
                    r'\"C:\Progra~2\AGCO Corporation\EDT\AgcoGT.exe\" EDT', shell=True)


def set_config_ini_to_original():
    with fileinput.FileInput(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini', inplace=True,
                             backup='.bak') as file:
        for line in file:
            print(line.replace('IsExplicitInstallRunning=True', 'IsExplicitInstallRunning=False'), end='')


def execute_command(path_and_command):
    """
    Runs an inputted command. If the command returns a non-zero return code it will fail. This method is not for
    capturing the output
    """
    logging.debug(f'Attempting to execute: {path_and_command}')
    p1 = subprocess.run(path_and_command,
                        shell=True,
                        check=True,
                        capture_output=True,
                        text=True,
                        )
    logging.debug(f'Command: {path_and_command}')
    logging.debug(f'ReturnCode: {str(p1.returncode)}')


def kill_process_by_name(process_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        current_proc_name = proc.info['name']
        if process_name in current_proc_name:
            logging.info(f'Killing process: {current_proc_name}')
            try:
                proc.kill()
                logging.debug(f'Killed process: {current_proc_name}')
            except:
                logging.debug(f'Unable to kill process: {current_proc_name}')


def start_auc():
    logging.debug('Attempting to start AUC')
    if is_os_64bit():
        loc = r'C:\Program Files (x86)\AGCO Corporation\AGCO Update Client\AGCOUpdateService.exe'
    else:
        loc = r'C:\Program Files\AGCO Corporation\AGCO Update Client\AGCOUpdateService.exe'
    try:
        os.startfile(loc)
    except:
        logging.error('Unable to start AGCOUpdateService.exe')


def apply_certs():
    logging.info('Attempting to apply Trusted Publish certificates')
    for loc in site.getsitepackages():
        if "site-packages" in loc:
            subprocess.call(
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe certutil -addstore TrustedPublisher "
                fr"{loc}\agcoinstall\data\SontheimCertificate1.cer", shell=True)
            subprocess.call(
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe certutil -addstore TrustedPublisher "
                fr"{loc}\agcoinstall\data\SontheimCertificate2.cer", shell=True)


def set_service_running(service):
    """
    Sets a windows service's start-up type to running
    :param service: string name of windows service
    """
    logging.debug(f'Attempting to set the following service to running: {service}')

    p1 = subprocess.run(fr'net start "{service}"',
                        shell=True,
                        capture_output=True,
                        text=True,
                        check=True,
                        )
    save_path = os.path.expanduser('~\\Desktop\\')
    with open(fr'{save_path}temp_output.txt', 'w') as f:
        f.write(p1.stdout)
    with open(fr'{save_path}temp_output.txt', 'r') as f:
        for line in f.readlines():
            if f"The {service} service was started successfully." in line:
                logging.debug(f"{service} has started")


def set_edt_environment(env_base_url):
    if is_os_64bit():
        files = [r'C:\Program Files (x86)\AGCO Corporation\EDT\EDTUpdateService.exe.config',
                 r'C:\Program Files (x86)\AGCO Corporation\EDT\AgcoGT.exe.config']
    else:
        files = [r'C:\Program Files\AGCO Corporation\EDT\EDTUpdateService.exe.config',
                 r'C:\Program Files\AGCO Corporation\EDT\AgcoGT.exe.config']

    for file in files:
        logging.info(f'Attempting to set the env url to {env_base_url} in the {file}')
        root = etree.parse(file)
        for event, element in etree.iterwalk(root):
            if element.text and 'https' in element.text:
                logging.info(f'Changing url from {element.text} to https://{env_base_url}/api/v2')
                element.text = f'https://{env_base_url}/api/v2'
        with open(file, 'wb') as f:
            f.write(etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=True))


def apply_voucher():
    voucher = create_voucher()
    if is_os_64bit():
        loc = rf'"C:\Program Files (x86)\AGCO Corporation\EDT\AgcoGT.exe" APPLYVoucher {voucher} NA0001 30096'
    else:
        loc = rf'"C:\Program Files\AGCO Corporation\EDT\AgcoGT.exe" APPLYVoucher {voucher} NA0001 30096'

    logging.info(f'Applying voucher via command line \"AgcoGT.exe APPLYVoucher {voucher} NA0001 30096\"')
    execute_command()


def get_client_id():
    try:
        return (
            regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation')
                .get_subkey(r'AGCO Update')['ClientID']
                .data
        )
    except AttributeError as e:
        click.secho("Client Id was not present in registry. Please confirm that you have AUC installed \n{e}", fg='red')


def get_voucher():
    """
    gets and return the voucher in the registry
    @return: voucher code as text
    """
    try:
        voucher_id = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT['Voucher'].data
    except AttributeError as e:
        click.secho(f'Voucher ID was not present in registry. Please confirm that EDT has been vouchered {e}', fg='red')
        logging.error(f'Voucher ID was not present in registry. Please confirm that EDT has been vouchered {e}')
        voucher_id = ''
    except KeyError:
        voucher_id = ''
    return voucher_id


def get_reg_client_id():
    try:
        client_id = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').get_subkey(r'AGCO Update')[
            'ClientID'].data
    except AttributeError as e:
        click.secho(
            f'Client ID was not present in registry. Please confirm that you have AGCO update client installed. {e}',
            fg='red')
        client_id = ''
    return client_id


def bypass_download_scheduler():
    """Bypasses the download Scheduler by writing a line in the registry that the current AUC checks before applying
    the download scheduler"""
    current_time = arrow.utcnow().format('MM/DD/YYYY h:mm:ss A')
    try:
        regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').get_subkey(r'AGCO Update')[
            'AUCConfiguration.LastExecutedUTC'] = current_time
    except AttributeError as e:
        logging.error(
            f'AGCO Update was not found in the registry. Please confirm that you have AGCO update client '
            f'installed. {e}')
        click.secho(f'AGCO Update was not found in the registry. Please confirm that you have AGCO update client '
                    f'installed. {e}', fg='red')


def set_edt_region(region=1):
    try:
        regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT[
            'Region'] = region
    except AttributeError as e:
        logging.error(f'EDT was not found in registry. Please confirm that EDT is installed to set the region {e}')
        click.secho(f'EDT was not found in registry. Please confirm that EDT is installed to set the region {e}',
                    fg='red')


def get_date_x_weeks_from_now(number_of_weeks=8):
    utc = arrow.utcnow()
    x_weeks_from_now = utc.shift(weeks=+number_of_weeks)
    return x_weeks_from_now.isoformat()


def create_voucher(duration=8):
    """Creates temporary voucher"""
    expire_date = get_date_x_weeks_from_now(duration)
    logging.info(f'Attempting to create a voucher that expires {expire_date}')
    uri = f'{base_url}/api/v2/Vouchers'
    payload = {
        "Type": "Temporary",
        "DealerCode": "NA0001",
        "LicenseTo": "Darrin Fraser",
        "Purpose": "Testing",
        "Email": "darrin.fraser@agcocorp.com",
        "ExpirationDate": expire_date,
    }
    r = requests.post(f'{uri}', auth=MACAuth(mac_id, mac_token, host), data=payload)
    return r.text.strip('"')


def get_client_relationships(client_id):
    uri = f'{base_url}/api/v2/UpdateGroupClientRelationships'
    payload = {
        "limit": 100,
        "ClientID": client_id
    }
    r = requests.get(uri, auth=MACAuth(mac_id, mac_token, host), params=payload)
    returned_relationships = json.loads(r.text)
    return returned_relationships['Entities']


def subscribe_or_update_client_relationships(ug_to_be_assigned, ug_client_relationships, remove_ug_dict, client_id):
    ugs_to_be_removed = set(remove_ug_dict.values())
    to_be_assigned_in_relationships = False
    for relationship in ug_client_relationships:
        if ug_to_be_assigned == relationship['UpdateGroupID'] and relationship['Active'] is True:
            to_be_assigned_in_relationships = True

        if relationship['UpdateGroupID'] in ugs_to_be_removed and relationship['Active'] is True:
            relationship['Active'] = False
            relationship_id = relationship['RelationshipID']
            uri = f'{base_url}/api/v2/UpdateGroupClientRelationships/{relationship_id}'
            r = requests.put(uri, auth=MACAuth(mac_id, mac_token, host), data=relationship)

        if relationship['UpdateGroupID'] == ug_to_be_assigned and relationship['Active'] is False:
            relationship['Active'] = True
            relationship_id = relationship['RelationshipID']
            uri = f'{base_url}/api/v2/UpdateGroupClientRelationships/{relationship_id}'
            r = requests.put(uri, auth=MACAuth(mac_id, mac_token, host), data=relationship)
            to_be_assigned_in_relationships = True

    if not to_be_assigned_in_relationships:
        win_ug = 'f23c4a77-a200-4551-bf61-64aef94c185e'
        ug_plus_basic_inventory = [ug_to_be_assigned, win_ug]
        for ug in ug_plus_basic_inventory:
            try:
                uri = f'{base_url}/api/v2/UpdateGroupClientRelationships'
                relationship = {'UpdateGroupID': ug,
                                'ClientID': client_id,
                                'Active': True,
                                }
                r = requests.post(uri, auth=MACAuth(mac_id, mac_token, host), data=relationship)
            except Exception as ex:
                logging.error(f'There was an error assigning UpdateGroup: {ug}...\n{ex}')


def click_on_image(imagefile):
    logging.info(f'Attempting to click on {imagefile}')
    center = pyautogui.locateCenterOnScreen(imagefile)
    pyautogui.click(center)


def file_watcher(updategroup):
    install_state = InstallState(updategroup, ConfigIni(), RegistryValues())
    state_on_exit = "Initial"
    moddate = os.stat(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini')[8]
    logging.debug(f'Starting file_watcher module: {moddate}')
    while True:
        current_moddate = os.stat(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini')[8]
        if current_moddate == moddate:
            time.sleep(5)
        else:
            current_state = install_state.get_state
            moddate = current_moddate

            if current_state != state_on_exit:
                logging.info(f"Change detected from {state_on_exit} to {current_state}")

                if current_state == 'ReadyToInstallCorePackages':
                    config_ini_find_and_replace('IsExplicitInstallRunning=False', 'IsExplicitInstallRunning=True')
                    state_on_exit = current_state

                if current_state == 'ReadyToInstallAdditional':
                    config_ini_find_and_replace('IsExplicitInstallRunning=False', 'IsExplicitInstallRunning=True')
                    state_on_exit = current_state

                if current_state == 'EDTNeedsVouchered':
                    apply_voucher()
                    set_edt_region(1)
                    launch_edt()
                    restart_auc()
                    state_on_exit = current_state

                if current_state == 'AllDownloadsCompleted':
                    click.secho('All downloads are complete closing Watcher')
                    break

                if current_state == 'DownloadsPaused':
                    config_ini_find_and_replace('DownloadSchedule=Start: On  Toggle: 06:00, 18:00',
                                                'DownloadSchedule=Start: On')
                    state_on_exit = current_state


@click.command()
@click.version_option()
@click.option('--env', '-e', default='prod', type=click.Choice(['prod', 'test', 'dev']))
# @click.option('--auc_env_change', '-aec', is_flag=True)
@click.option('--updategroup', '-ug', default='InternalTestPush', type=click.Choice(['EDTUpdates',
                                                                                     'Dev',
                                                                                     'RC',
                                                                                     'TestPush',
                                                                                     'InternalTestPush',
                                                                                     'InternalDev',
                                                                                     'InternalRC',
                                                                                     ]))
@click.option('--username', '-u', prompt=True, help='Enter username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Enter password')
def main(env, updategroup, username, password) -> None:
    """Agcoinstall."""

    global host, base_url, mac_id, mac_token

    ug_dict = {'EDTUpdates': 'eb91c5e8-ffb1-4060-8b97-cb53dcd4858d',
               'Dev': '29527dd4-3828-40f1-91b4-dfa83774e0c5',
               'RC': '30ae5793-67a2-4111-a94a-876a274c3814',
               'InternalTestPush': 'd76d7786-1771-4d3b-89b1-c938061da4ca',
               'TestPush': '42dd2226-cdaa-46b4-8e23-aa98ec790139',
               'InternalDev': '6ed348f3-8e77-4051-a570-4d2a6d86995d',
               'InternalRC': "75a00edd-417b-459f-80d9-789f0c341131",
               }

    env_dict = {'dev': 'edtsystems-webtest-dev.azurewebsites.net',
                'prod': 'secure.agco-ats.com',
                'test': 'edtsystems-webtest.azurewebsites.net',
                }

    update_group_id = ug_dict.pop(updategroup)

    host = 'secure.agco-ats.com'
    base_url = f'https://{host}'
    m_id, m_token = get_auth(username, password)
    mac_id = m_id
    mac_token = m_token

    apply_certs()
    if not os.path.isdir(r'C:\ProgramData\AGCO Corporation\AGCO Update'):
        download_auc_client()
        install_auc()
    cid = get_client_id()
    bypass_download_scheduler()
    c_relationships = get_client_relationships(cid)
    subscribe_or_update_client_relationships(update_group_id, c_relationships, ug_dict, cid)
    # if auc_env_change:
    #   set_auc_environment(base_url)
    restart_auc()
    time.sleep(10)
    file_watcher(updategroup)
    if updategroup in {'Dev', 'InternalDev'}:
        add_services_to_license()

    if env in {'dev', 'test'}:
        host = env_dict[env]
        base_url = f'https://{host}'
        set_auc_environment(base_url)
        set_edt_environment(host)
        apply_voucher()


if __name__ == "__main__":
    main(prog_name="agcoinstall")  # pragma: no cover
