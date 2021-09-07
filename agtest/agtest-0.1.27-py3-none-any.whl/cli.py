"""Console script for testtool."""
import site
import sys
import json
from collections import defaultdict, OrderedDict
import os
import re
import time
import base64
import hmac
import hashlib
import random
import shutil
import subprocess
import logging
import pathlib
import zipfile
import fileinput
import csv
import glob
import platform
import comtypes.client
from hashlib import sha256
from itertools import islice

import requests
import arrow
import regobj
import parse
import pandas as pd
import click
import psutil
import tqdm
from lxml import etree
from pdf2image import convert_from_path
from requests.auth import AuthBase
from agtest import errors_enum
from agtest import ftcompare

save_path = os.path.expanduser('~\\Desktop\\agtest.log')
logging.basicConfig(filename=save_path, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


class Clumper:
    def __init__(self, blob):
        self.blob = blob

    def keep(self, *funcs):
        data = self.blob
        for func in funcs:
            data = [d for d in data if func(d)]
        return Clumper(data)

    def head(self, n):
        return Clumper([self.blob[i] for i in range(n)])

    def tail(self, n):
        return Clumper([self.blob[-i] for i in range(1, n + 1)])

    def select(self, *keys):
        return Clumper([{k: d[k] for k in keys} for d in self.blob])

    def mutate(self, **kwargs):
        data = self.blob
        for key, func in kwargs.items():
            for i in range(len(data)):
                data[i][key] = func(data[i])
        return Clumper(data)

    def sort(self, key, reverse=False):
        return Clumper(sorted(self.blob, key=key, reverse=reverse))


def rec_dd():
    return defaultdict(rec_dd)


def take(n, iterable):
    """Return first n items of the iterable as a list"""
    return list(islice(iterable, n))


def is_os_64bit():
    return platform.machine().endswith('64')

def get_installed_plugins(plugin_dir=r'C:\ProgramData\AGCO Corporation\EDT\Plug-Ins'):
    installed_plugins = defaultdict(list)
    for dir_name, sub_dir_list, file_list in os.walk(plugin_dir):
        if 'plugin.xml' in file_list:
            dir_split = dir_name.split('\\')
            plugin = dir_split[-2].upper()
            version = dir_split[-1]
            installed_plugins[plugin].append(version)
    return dict(installed_plugins)


def get_required_plugins(models_dir):
    required_plugins = rec_dd()
    version_pattern = r"[0-9]{3}\.[0-9]{3}_[0-9]{4}\.[0-9]{2}\.[0-9]{2}_[0-9]{6}\.xml"

    for dir_name, sub_dir_list, file_list in os.walk(models_dir):
        for f in file_list:
            if re.match(version_pattern, f):
                dir_split = dir_name.split('\\')
                basename = f.replace('.xml', '')
                plugin = dir_split[-1]
                master = dir_split[-3]
                required_plugins[master].update({plugin.upper(): basename})
    return dict(required_plugins)


def compare_plugins(installed_plug, required_plug):
    found_plugins = rec_dd()
    missing_plugins = rec_dd()
    with open('plugin_results.txt', mode='wt') as f:
        for master, plugins in required_plug.items():
            f.write('Master: {}\n'.format(master))
            for plugin, version in plugins.items():
                if version in installed_plug[plugin]:
                    f.write('\t {0:<25} {1:<35} installed\n'.format(plugin, version))
                    found_plugins[master].update({plugin: version})
                else:
                    f.write('\t {0:<25} {1:<35} Not Found!!!!\n'.format(plugin, version))
                    missing_plugins[master].update({plugin: version})
    return missing_plugins, found_plugins


def compare_directories(dir_a, dir_b):
    if os.path.isdir(dir_a) and os.path.isdir(dir_b):
        changed_files = defaultdict(dict)
        added_files = defaultdict(dict)
        deleted_files = defaultdict(list)
        ft_diff_def = {'deleted_files': deleted_files, 'added_files': added_files, 'changed_files': changed_files}
        ft_compare = ftcompare.dircmp(dir_a, dir_b, ft_diff_def, ignore=None, hide=None)
        ft_compare.report_full_closure()
        returned_diff_def = ft_compare.ft_diff_def
        return returned_diff_def
    else:
        print("Please check the path to the directories. At least one parameter provided "
              "is not recognized as a directory.")


def files_in_dir(directory):
    try:
        file_set = set([f for f in os.listdir(directory)])
    except (FileNotFoundError):
        file_set = set()
    return file_set


def files_not_deleted(set_from_def, set_from_install):
    overlap = set_from_def.intersection(set_from_install)
    return overlap


def compare_hashes(location, hash):
    if get_hash(location) == hash:
        return True
    else:
        return False


def import_def(ft_diff_def):
    with open(ft_diff_def) as data_file:
        loaded_def = json.load(data_file)
        return loaded_def


def get_hash(fname):
    hash = sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


def create_report(file_name='FT_validation_report.txt'):
    report = os.path.expanduser(f'~\\Desktop\\{file_name}')
    r = open(report, mode='wt')
    return r


def get_date_x_weeks_from_now(number_of_weeks=4):
    utc = arrow.utcnow()
    x_weeks_from_now = utc.shift(weeks=+number_of_weeks)
    return x_weeks_from_now.isoformat()


def get_registry_client_id():
    try:
        client_id = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').get_subkey(r'AGCO Update')[
            'ClientID'].data
        return client_id
    except AttributeError as e:
        click.secho(
            f'Client ID was not present in registry. Please confirm that you have AGCO update client installed. {e}',
            fg='red')


def check_logs_for_errors(folder, results=None):
    if results is None:
        results = []
    results += [each for each in os.listdir(folder) if "errors" in each.lower()]
    return results


def get_registry_voucher():
    """
    gets and return the voucher in the registry
    @return: voucher code as text
    """
    try:
        voucher_id = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT['Voucher'].data
    except AttributeError as e:
        try:
            voucher_id = regobj.HKLM.SOFTWARE.Wow6432Node.get_subkey(r'AGCO Corporation').EDT['Voucher'].data  # this
            # accounts for the name difference in windows7
        except AttributeError as e:
            click.secho(f'Voucher ID was not present in registry. Please confirm that EDT has been vouchered {e}',
                        fg='red')
            logging.error(f'Voucher ID was not present in registry. Please confirm that EDT has been vouchered {e}')
            voucher_id = ''
    except KeyError:
        voucher_id = ''
    return voucher_id


def get_reg_release_name():
    try:
        release_name = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT['Release_Name'].data
        return release_name
    except AttributeError as e:
        click.secho(f'Release_Name was not present in registry. Please confirm that EDT content is attached to a '
                    f'release {e}', fg='red')


def kill_process_by_name(process_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        current_proc_name = proc.info['name']
        if process_name in current_proc_name:
            logging.info(f'Killing process: {current_proc_name}')
            try:
                proc.kill()
                logging.debug(f'Killed process: {current_proc_name}')
            except Exception as e:
                logging.debug(f'Unable to kill process: {current_proc_name}\n{e}')


def parse_csv(filename=r".\test.csv"):
    masters_to_models = rec_dd()
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            temp = {row['CustomOptions']: row['URI']}
            masters_to_models[(row['Master'].upper())][row['Region']][row['Brand']][row['Category']][row['Model Year']][
                row['Model']].update(temp)
    return OrderedDict(masters_to_models)


def create_model_report(obj, report=r'model_lookup.json', report_save_path=os.path.expanduser('~\\Desktop\\')):
    with open(f'{report_save_path}{report}', mode='wt') as f:
        f.write(json.dumps(obj, sort_keys=True, indent=4))


def print_masters(master_to_models):
    print('List of all Masters: \n')
    for master in sorted(master_to_models.keys()):
        print(master)


def get_latest_csv():
    if os.path.isdir(r'\\aghessfs01p\EDT\BuildDrop\Model Maps Package\Model Map Reports'):
        list_of_files = glob.glob(r'\\aghessfs01p\EDT\BuildDrop\Model Maps Package\Model Map Reports\*')
        latest_file = max(list_of_files, key=os.path.getctime)
    else:
        for loc in site.getsitepackages():
            if "site-packages" in loc:
                latest_file = fr"{loc}\agtest\data\latest_mm.csv"
    return latest_file


def start_auc():
    logging.debug('Attempting to start AUC')
    if is_os_64bit():
        loc = r'C:\Program Files (x86)\AGCO Corporation\AGCO Update Client\AGCOUpdateService.exe'
    else:
        loc = r'C:\Program Files\AGCO Corporation\AGCO Update Client\AGCOUpdateService.exe'
    try:
        os.startfile(loc)
    except Exception as e:
        logging.error(f'Unable to start AGCOUpdateService.exe\n{e}')


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


def set_auc_environment(host):
    # other_urls = set(remaining_urls.values())
    logging.info(f'Attempting to set the env url of https://{host}/api/v2 in the config.ini file')
    kill_process_by_name('AGCOUpdateService')
    with fileinput.FileInput(r'C:\ProgramData\AGCO Corporation\AGCO Update\config.ini', inplace=True,
                             backup='.bak') as file:
        for line in file:
            if "UpdateHost2" in line:
                line = f'UpdateHost2=https://{host}/api/v2\n'
            elif "UpdateHost" in line:
                line = f'UpdateHost=https://{host}/api/v2\n'
            print(line, end='')
    set_service_running('AGCO Update')
    start_auc()
    time.sleep(10)


def set_edt_environment(host):
    if is_os_64bit():
        files = [r'C:\Program Files (x86)\AGCO Corporation\EDT\EDTUpdateService.exe.config',
                 r'C:\Program Files (x86)\AGCO Corporation\EDT\AgcoGT.exe.config']
    else:
        files = [r'C:\Program Files\AGCO Corporation\EDT\EDTUpdateService.exe.config',
                 r'C:\Program Files\AGCO Corporation\EDT\AgcoGT.exe.config']

    for file in files:
        logging.info(f'Attempting to set the env url to {host} in the {file}')
        root = etree.parse(file)
        for event, element in etree.iterwalk(root):
            if element.text and 'https' in element.text:
                logging.info(f'Changing url from {element.text} to https://{host}/api/v2')
                element.text = f'https://{host}/api/v2'
        with open(file, 'wb') as f:
            f.write(etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=True))
    if not os.path.isfile(r"C:\ProgramData\AGCO Corporation\EDT\Translations\Translations-test.sdf") and os.path.isfile(
            r"C:\ProgramData\AGCO Corporation\EDT\Translations\Translations.sdf"):
        shutil.copy(r"C:\ProgramData\AGCO Corporation\EDT\Translations\Translations.sdf",
                    r"C:\ProgramData\AGCO Corporation\EDT\Translations\Translations-test.sdf")


def get_license_id(base_url, mac_id, mac_token, host):
    voucher = get_registry_voucher()
    logging.info(f'Attempting to get license id using the voucher code')
    uri = f'{base_url}/api/v2/Licenses'
    payload = {
        "VoucherCode": voucher,
        "Status": "Active",
    }
    r = requests.get(uri, auth=MACAuth(mac_id, mac_token, host), params=payload)
    license_dict = json.loads(r.text)
    return license_dict['Entities'][0]['LicenseID']


def get_registry_master_versions():
    masters_versions = dict()
    try:
        edt_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT.values()
        for i in edt_values:
            if "_Version" in i.name and 'UPDATE_' in i.name and 'ContentIndex' not in i.name:
                p = parse.parse("Update_{}_Version", i.name)
                master = p[0]
                masters_versions.update({master: i.data})
    except AttributeError as e:
        click.secho('EDT does not appear to be installed. Please confirm that EDT is installed', fg='red')
    return masters_versions


def get_registry_ft_versions():
    ft_versions = dict()
    try:
        edt_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT.values()
        for i in edt_values:
            if "_Version" in i.name and 'FT_' in i.name:
                p = parse.parse("FT_{}_Version", i.name)
                master_ft_vers = p[0]
                ft_versions.update({f'{master_ft_vers}_FaultTrees': i.data})
            if "FaultTreeVersion" in i.name:
                ft_versions.update({'FaultTrees_Core': i.data})
    except AttributeError as e:
        click.secho(f'EDT does not appear to be installed. Please confirm that EDT is installed {e}', fg='red')
    return ft_versions


def get_registry_framework_versions():
    framework_versions = dict()
    framework_components = {'DataCollection_MDTVersion',
                            'Globals_Version',
                            'MTAPISync_Version',
                            'Plug-Ins_Version',
                            'Update_MF_Activity_Version',
                            'Version',
                            'X1000Components_Version',
                            'EDT.SontheimComponents_Version',
                            'VDWPlug-Ins_Version',
                            'UpdateNumber',
                            'VDW_Version',
                            'ErrorCode',
                            'SIE44J32Patch_Version',
                            }
    try:
        edt_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT.values()
        sontheim_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').get_subkey(
            r'Sontheim Components').values()
        for i in edt_values:
            if i.name in framework_components:
                framework_versions.update({i.name: i.data})
        for i in sontheim_values:
            if i.name in framework_components:
                framework_versions.update({i.name: i.data})
    except AttributeError as e:
        click.secho(f'EDT does not appear to be installed. Please confirm that EDT is installed.  {e}', fg='red')
    return framework_versions


def apply_voucher(voucher_id):
    if is_os_64bit():
        loc = "Program Files (x86)"
    else:
        loc = "Program Files"
    logging.info(f'Applying voucher via command line \"AgcoGT.exe APPLYVoucher {voucher_id} NA0001 30096\"')
    execute_command(rf'"C:\{loc}\AGCO Corporation\EDT\AgcoGT.exe" APPLYVoucher {voucher_id} NA0001 30096')


def add_services_to_license(base_url, mac_id, mac_token, host):
    license = get_license_id(base_url, mac_id, mac_token, host)
    logging.info(f'Attempting to add AuthCode to License for Dev environment')
    uri = f'{base_url}/api/v2/AuthorizationCodes'
    payload = {'DefinitionID': ' ',
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


def copy2clip(txt):
    cmd = f'echo {txt.strip()}|clip'
    return subprocess.check_call(cmd, shell=True)


def get_auth(username, password, base_url):
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


def save_to_desktop(url, filename):
    save_path = os.path.expanduser(f'~\\Desktop\\{filename}')
    try:
        r = requests.get(url, allow_redirects=True)
        try:
            open(save_path, 'wb').write(r.content)
        except:
            print(f'Unable to download the {filename}')
    except:
        print(f'The link to download the {filename} is down')


def save_auc_client():
    url = 'https://dl.agco-ats.com/AUC_EDT.exe'
    save_path = os.path.expanduser('~\\Desktop\\AUC_DL.exe')
    try:
        r = requests.get(url, allow_redirects=True)
        try:
            open(save_path, 'wb').write(r.content)
        except:
            print('Unable to download the AUC client')
    except:
        print('The link to download the latest AUC is down')


def download_auc_client_clean():
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


def execute_command(path_and_command):
    """
    Runs an inputted command. If the command returns a non-zero return code it will fail. This method is not for
    capturing the output
    """
    logging.debug(f'Attempting to execute: {path_and_command}')
    p1 = subprocess.run(path_and_command,
                        shell=True,
                        # check=True,
                        capture_output=True,
                        text=True,
                        )
    standard_out = p1.stdout
    standard_error = p1.stderr
    return_code = str(p1.returncode)
    logging.debug(f'Command: {path_and_command}')
    logging.debug(f'Standard Out: {standard_out}')
    logging.debug(f'Returncode: {return_code}')
    logging.debug(f'Standard Error: {standard_error}')
    if return_code != '0':
        print(f'Command: {path_and_command}')
        print(f'Standard Out: {standard_out}')
        print(f'Returncode: {return_code}')


def run_auc_client():
    execute_command(os.path.expanduser('~\\Desktop\\AUC_DL.exe /S'))


def print_object(obj):
    click.echo_via_pager(json.dumps(obj, sort_keys=True, indent=4))


def print_object_no_paging(obj):
    click.echo(json.dumps(obj, sort_keys=True, indent=4))


def get_voucher_type(base_url, mac_id, mac_token, host, voucher):
    pass


# def get_api_plugins(base_url, mac_id, mac_token, host, release_id):

def get_users_dict(base_url, mac_id, mac_token, host):
    """
    /GET /api/v2/Users
    :return: python dict of Users with Name and Email data for each
    """
    uri = f'{base_url}/api/v2/Users'
    payload = {
        "limit": 1000,
    }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    return_dict = json.loads(r.text)
    user_dict = defaultdict(dict)
    for item in return_dict['Entities']:
        user_id = item['UserID']
        name = item['Name']
        username = item['Username']
        email = item['Email']
        user_dict[user_id].update({'name': name, 'username': username, 'email': email})
    user_dict[0].update({'name': 'None', 'username': 'None', 'email': 'None'})
    return user_dict


def get_content_definitions(base_url, mac_id, mac_token, host, key='content_def'):
    """
    /GET /api/v2/ContentDefinitions/{contentDefinitionID}
    :return: content definitions which contains the master name and Description
    """
    uri = f'{base_url}/api/v2/ContentDefinitions'
    if key == "name":
        payload = {
            "limit": 1000,
            "includeAttributes": '*'
        }
    else:
        payload = {"limit": 1000}
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    returned_definitions = json.loads(r.text)
    content_dict = defaultdict(dict)
    for item in returned_definitions['Entities']:
        content_definition_id = item['ContentDefinitionID']
        name = item['Name']
        typeid = item['TypeID']
        description = item['Description']
        if key == 'name':
            attributes = item['Attributes']
            package_type_id = item['PackageTypeID']
        if key == 'content_def':
            content_dict[content_definition_id].update({'name': name, 'typeid': typeid, 'description': description})
        if key == 'name':
            lower_name = name.lower()
            content_dict[lower_name].update({'content_definition_id': content_definition_id, 'typeid': typeid,
                                             'description': description, 'package_type_id': package_type_id,
                                             'attributes': attributes})
    return content_dict


def get_release_content(base_url, mac_id, mac_token, host, release_id):
    """
    /GET /api/v2/ContentReleases
    :return: text of all masters in a given release
    """
    uri = f'{base_url}/api/v2/ContentReleases'
    payload = {
        "limit": 1000,
        "releaseID": release_id,
    }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    returned_content = json.loads(r.text)
    released_content_dict = defaultdict(dict)
    user_dict = get_users_dict(base_url, mac_id, mac_token, host)
    content_dict = get_content_definitions(base_url, mac_id, mac_token, host)
    for item in returned_content['Entities']:
        content_def_id = item["ContentDefinitionID"]
        version = item["Version"]
        # release_id = item["ReleaseID"]
        publisher_id = item["PublisherUserID"]
        updated_date = item["UpdatedDate"]
        # deleted = item["Deleted"]
        test_report_url = item["TestReportUrl"]
        released_content_dict[content_dict[content_def_id]['name']].update({'version': version,
                                                                            'type': content_dict[content_def_id][
                                                                                'typeid'],
                                                                            'publisher_id': publisher_id,
                                                                            'submitter_name': user_dict[publisher_id][
                                                                                'name'],
                                                                            'submitter_email': user_dict[publisher_id][
                                                                                'email'],
                                                                            'updated_date': updated_date,
                                                                            'test_report_url': test_report_url,
                                                                            })
    return released_content_dict


def get_package_id(base_url, mac_id, mac_token, host, releaseid, content_definition_id):
    """
    /GET /api/v2/ContentSubmissions
    :return: list of pacakageIDs that need downloaded
    """
    uri = f'{base_url}/api/v2/ContentSubmissions'
    payload = {"contentDefinitionID": content_definition_id,
               "releaseID": releaseid,
               }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    returned_submissions = json.loads(r.text)
    for item in returned_submissions['Entities']:
        package_id = item["PackageID"]
        return package_id


def package_download_link(base_url, mac_id, mac_token, host, package_id):
    if package_id:
        uri = f'{base_url}/api/v2/Packages/{package_id}'
        r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host))
        returned_submissions = json.loads(r.text)
        return returned_submissions['Url']


def get_all_packages(base_url, mac_id, mac_token, host):
    uri = f'{base_url}/api/v2/Packages/'
    payload = {
        "limit": 10000,
    }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    packages = json.loads(r.text)
    packages_dict = packages["Entities"]
    return packages_dict


def get_package_version(base_url, mac_id, mac_token, host, bundle_id, package_type_id):
    uri = f'{base_url}/api/v2/PackageTypetoBundles/'
    payload = {"limit": 10000,
               "BundleID": bundle_id
               }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    items = json.loads(r.text)
    for item in items["Entities"]:
        if item['PackageTypeID'] == package_type_id:
            return item['PackageVersion']


def get_package_types(base_url, mac_id, mac_token, host, package):
    uri = f'{base_url}/api/v2/PackageTypes'
    payload = {"limit": 10000}
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    items = json.loads(r.text)
    package_type_clumper = Clumper(items['Entities']).keep(lambda d: package in d['Description']).blob
    return package_type_clumper


def get_bundles_in_ug(base_url, mac_id, mac_token, host, ugid):
    """Retrieves all the bundles in a update group"""
    uri = f'{base_url}/api/v2/Bundles'
    payload = {"UpdateGroupID": ugid,
               "limit": 1000,
               }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    bundles = json.loads(r.text)
    bundles_dict = dict()
    for item in bundles['Entities']:
        bundle_id = item["BundleID"]
        description = item["Description"].replace(" ", "_")
        update_group_id = item['UpdateGroupID']
        bundle_number = item["BundleNumber"]
        active = item["Active"]
        bundles_dict.update({description: {'bundle_id': bundle_id,
                                           'bundle_number': bundle_number,
                                           'update_group_id': update_group_id,
                                           'active': active,
                                           }})
    return bundles_dict


def get_release_list(base_url, mac_id, mac_token, host, offset=50):
    """Retrieves release ids identified by release name"""

    uri = f'{base_url}/api/v2/Releases'
    payload = {
        "limit": 1000,
        "offset": offset,
    }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    releases = json.loads(r.text)
    release_dict = defaultdict(dict)
    for item in releases['Entities']:
        release_id = item["ReleaseID"]
        release_number = item["ReleaseNumber"]
        build_date = item['BuildDate']
        release_date = item["ReleaseDate"]
        visible = item["Visible"]
        release_dict[release_id].update({'release_name': release_number,
                                         'build_date': build_date,
                                         'release_date': release_date,
                                         'visible': visible,
                                         })
    release_id_to_name = defaultdict()
    for key, value in release_dict.items():
        rel_name = value['release_name']
        release_id_to_name[key] = rel_name
    release_name_to_release_number_dict = {value: key for key, value in release_id_to_name.items()}
    return release_id_to_name, release_name_to_release_number_dict


def delete_file(file_name):
    try:
        os.remove(file_name)
    except OSError:
        print(f'Unable to delete {file_name}')


def download_master_reports(updated_content_dict, save_path=os.path.expanduser('~\\Documents\\Reports')):
    for key, value in updated_content_dict.items():
        if value['type'] == 1:
            if value['test_report_url']:
                master = key
                if not os.path.isdir(f'{save_path}\\{master}'):
                    pathlib.Path(f'{save_path}\\{master}').mkdir(parents=True, exist_ok=True)
                saved_folder_path = f"{save_path}\\{master}"
                url = value['test_report_url']
                file_name = (url.split('/'))[-1]
                full_file_path = f'{save_path}\\{master}\\{file_name}'
                try:
                    r = requests.get(url, allow_redirects=True)
                    try:
                        open(full_file_path, 'wb').write(r.content)
                        value.update(
                            {'test_report_url': f'=HYPERLINK(\"{saved_folder_path}\" , \"{saved_folder_path}\")'})
                    except:
                        print(f'Unable to save downloaded file to: {full_file_path}')

                except:
                    print(f'Unable to download file: {url}')

            else:
                print(f'There was no test report attached to the {key} master submission')


def unzip_reports(file_path):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.zip':
                try:
                    with zipfile.ZipFile(f'{root}\\{file}', 'r') as zip_ref:
                        zip_ref.extractall(root)
                        delete_file(f'{root}\\{file}')
                except:
                    print(f'Unable to extract the contents of {root}\\{file}')


def convert_downloaded_file(downloaded_reports_path):
    for root, dirs, files in os.walk(downloaded_reports_path):
        for file in files:
            extension = os.path.splitext(file)[-1]
            if extension == '.pdf':
                convert_pdf_to_img(f'{root}//{file}', root.split('\\')[-1])
            elif extension == '.docx' or extension == '.doc':
                convert_word_to_pdf(f'{root}//{file}', root.split('\\')[-1])
            else:
                pass


def convert_word_to_pdf(file_path, master_key):
    wdFormatPDF = 17
    base_file_name, extension = os.path.splitext(file_path)
    if extension == '.docx':
        renamed_path = file_path.replace('docx', 'pdf')
    if extension == '.doc':
        renamed_path = file_path.replace('doc', 'pdf')
    word = comtypes.client.CreateObject('Word.Application')
    word.Visable = True
    time.sleep(3)
    doc = word.Documents.Open(file_path)
    try:
        doc.SaveAs(renamed_path, FileFormat=wdFormatPDF)
        # updated_content_dict[master_key].update({'test_report_url': renamed_path})
    except:
        print(f'Unable to save Word document {os.path.basename(file_path)} as pdf')
    finally:
        doc.Close()
        word.Quit()
    convert_pdf_to_img(renamed_path, master_key)
    delete_file(file_path)


def convert_pdf_to_img(file_path, master_key):
    base_name, file_ext = os.path.splitext(file_path)
    split_base_name = base_name.split('\\')
    file_name = split_base_name[-1]
    path_name = ('\\').join(split_base_name[0:-1])
    try:
        convert_from_path(file_path, output_file=file_name, output_folder=path_name, fmt='jpeg')
        # updated_content_dict[master_key].update({'test_report_url': path_name})
        delete_file(file_path)
    except:
        print(f'Unable to save pdf document {os.path.basename(file_path)} as jpeg')


def create_content_table(path, name, content_dict, masters_only):
    """
    Creates a table of content submission
    :return:
    """
    path = f'{path}\\'
    my_df = pd.DataFrame.from_dict(content_dict, orient='index')
    my_df.drop(['publisher_id', ], axis=1, inplace=True)
    updated_df = my_df.rename(columns={'submitter_name': 'Submitter',
                                       'submitter_email': 'Email',
                                       'test_report_url': 'Report_Download',
                                       'updated_date': 'Submitted_Date',
                                       'type': 'Submission_Type',
                                       'version': 'Version',
                                       })
    updated_df.index.name = 'Submission'
    sorted_df = updated_df.sort_values(by='Submitter')
    if masters_only:
        sorted_df = sorted_df.loc[sorted_df['Submission_Type'] == 1]
    try:
        sorted_df.to_excel(f'{path}{name}.xlsx', header=True)
    except PermissionError:
        print('Unable to create an excel file with that name. It is possible that you have another spread sheet'
              ' open with that same name')


@click.group()
def main(args=None):
    """Command-line tool for common testing tasks"""


@main.command()
@click.option('--location', '-l', default='prod', type=click.Choice(["my_docs", 'prod', 'test']), help="Choose where it"
                                                                                                       " looks for "
                                                                                                       "masters")
@click.option('--report', '-r', required=True, type=click.Choice(['installed', 'required', 'missing', 'full']))
def plugins(location, report):
    """Console script for plugins."""
    if location == 'my_docs':
        directory = os.path.expanduser(r'~\Documents\AGCO Corporation\EDT\Models')
    elif location == 'prod' or location != 'test':
        directory = r'C:\ProgramData\AGCO Corporation\EDT\Models'
    else:
        directory = r'C:\ProgramData\AGCO Corporation\EDT Test\Models'
    installed_plugins = get_installed_plugins()
    required_plugins = get_required_plugins(directory)
    missing_plugins, found_plugins = compare_plugins(installed_plugins, required_plugins)
    if report in ['installed', 'full']:
        click.secho("Installed Plugins:\n", bold=True)
        print_object(installed_plugins)
    if report in ['required', 'full']:
        click.secho("Required Plugins:\n", bold=True)
        print_object(required_plugins)
    if report in ['missing', 'full']:
        click.secho("Missing Plugins:\n", bold=True, fg='red')
        print_object(missing_plugins)
    if report == 'full':
        click.secho("Found Plugins:\n", bold=True)
        print_object(found_plugins)
    if missing_plugins:
        return -1
    else:
        return 0


@main.group()
def faulttree():
    """Commands to create and validate FT definition files"""
    pass


@faulttree.command()
@click.argument('previous_folder', type=click.Path(exists=True))
@click.argument('updated_folder', type=click.Path(exists=True))
@click.option('--path', '-p', default=os.path.expanduser('~\\Desktop\\'), help='Allows user to save specify the folder '
                                                                               'A FT definition file will be saved to. '
                                                                               'The default location is on the Desktop')
# @click.option('--rename', '-r', default='FT_Definition.json', help='Allows user to rename the file. Default is '
#                                                                    'FT_Definition.json')
def create(previous_folder, updated_folder, path):
    """Compares two FT folders the previous FT folder and the updated FT folder (they are positional).
    The output is a file FT_Definition.json that can be used with the validate command"""
    diff_result = compare_directories(previous_folder, updated_folder)
    with open(f'{path}\\FT_Definition.json', 'w') as f:
        json.dump(diff_result, f, sort_keys=True, indent=4)


@faulttree.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--rename', '-r', default='FT_validation_report.txt',
              help="Allows the user to rename the output report")  # TODO check the reuse of location variable
def validate(file, rename):
    """Validates the FT_Definition.json against the installed FTs"""
    # not_deleted = list()
    added_matching_files = list()
    added_non_matching_file = list()
    changed_matching_files = list()
    changed_non_matching_file = list()
    index_pattern = r'\d{4}.*?index.*?htm'
    lang_deleted = list()
    lang_added = list()
    diff_def = import_def(file)
    report = create_report(rename)
    if diff_def["deleted_files"]:
        report.write('-------\n')
        report.write('DELETED:\n')
        report.write('-------\n')
        for location, file_set in diff_def[
            'deleted_files'].items():  # Todo if a folder is deleted or is from the previous FT to the latest then 664 need an if statement to see if it is still there
            report.write(f'Files Deleted from {location}:\n')
            # if os.path.isdir(location):
            set_from_install = files_in_dir(location)
            set_from_def = set(file_set)
            files_deleted = sorted(list(set_from_def.difference(set_from_install)))
            not_deleted = sorted(list(files_not_deleted(set_from_def, set_from_install)))
            for file in files_deleted:
                report.write(f'\t{location}\\{file}\n')
                if re.match(index_pattern, file):
                    lang_deleted.append(file)
            if not_deleted:
                report.write(
                    '\tThe following files were deleted in the definition but were still present after the install:\n')
                for file in not_deleted:
                    report.write(f'\t{location}\\{file}\n')

    if diff_def["added_files"]:
        report.write('\n\n\n\n------\n')
        report.write('ADDED:\n')
        report.write('------\n')
        for location, file_hash in tqdm.tqdm(diff_def['added_files'].items(), desc=' Added Files'):
            if os.path.isfile(location):
                matches_definition = compare_hashes(location, file_hash)
                if matches_definition:
                    added_matching_files.append(location)
                else:
                    added_non_matching_file.append(location)
            else:
                print(f"\t{location}, an added file in the definition is missing from this host")
                report.write(f"\t{location}, an added file in the definition is missing from this host\n")
        # if args.verbose:
        if added_matching_files:
            print('\tThe following files matches the Added definition:\n')
            report.write('\tThe following files match the \"Added\" definition:\n\n')
            for f in sorted(added_matching_files):
                report.write(f'\t{f}\n')
                if re.match(index_pattern, f):
                    lang_added.append(f)
        # print_object(added_matching_files)
        print()

        if added_non_matching_file:
            print('\tThe following files DID NOT MATCH the Added definition:\n')
            report.write('\tThe following files match the \"Added\" definition:')
            for f in sorted(added_non_matching_file):
                report.write('\t{}'.format(f))
            # print_object(added_non_matching_file)
            print()

    if diff_def['changed_files']:
        report.write('\n\n\n\n--------\n')
        report.write('CHANGED:\n')
        report.write('--------\n')
        for location, file_hash in tqdm.tqdm(diff_def['changed_files'].items(), desc=" Changed Files"):
            if os.path.isfile(location):
                matches_definition = compare_hashes(location, file_hash)
                if matches_definition:
                    changed_matching_files.append(location)
                else:
                    changed_non_matching_file.append(location)
            else:
                print(f"\t{location}, a changed file in the definition is missing from this host")
                report.write(f"\t{location}, a changed file in the definition is missing from this host\n")
        # if args.verbose:
        if changed_matching_files:
            changed_matching_files = sorted(changed_matching_files)
            # print('\tThe following files matches the Changed definition:\n')
            report.write('\tThe following files matches the Changed definition:\n')
            for f in changed_matching_files:
                report.write(f'\t{f}\n')
            # print_object(sorted(changed_matching_files))
            print()

        if changed_non_matching_file:
            print('The following files DID NOT MATCH the Changed definition:\n')
            report.write('The following files DID NOT MATCH the Changed definition:\n')
            changed_non_matching_file = sorted(changed_non_matching_file)
            for f in changed_non_matching_file:
                report.write(f'\t{f}\n')
            print_object(changed_non_matching_file)
            print()

    if lang_deleted:
        report.write('\n\nThe following languages were removed:\n')
        for i in lang_deleted:
            report.write(f'\t{i}\n')

    if lang_added:
        report.write('\n\nThe following languages were added:\n')
        for i in lang_added:
            report.write(f'\t{i}\n')


@main.command()
@click.option('--item', '-i', default='client', type=click.Choice(['client', 'voucher', 'masters', 'errors',
                                                                   'faulttrees', 'framework', 'all']))
def registry(item):
    """Returns the following reg values: AUC client, EDT voucher, installed masters, Errors, and all EDT values"""
    if item == 'client':
        return_value = get_registry_client_id()
        copy2clip(return_value)
        click.secho(f'Client_id {return_value} was copied to the clipboard', fg="green")

    if item == 'voucher':
        return_value = get_registry_voucher()
        copy2clip(return_value)
        click.secho(f'Voucher {return_value} was copied to the clipboard', fg="green")

    if item == 'masters':
        masters_versions = get_registry_master_versions()
        print_object(masters_versions)

    if item == 'errors':
        edt_errors = {}
        edt_reg_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT.values()
        for i in edt_reg_values:
            entry = i.name
            data = i.data
            if ('_err' in entry.lower()) or ('Error' in entry):
                edt_errors.update({i.name: i.data})
        for key, value in edt_errors.items():
            num_val = int(value)
            if num_val:
                try:
                    click.secho(f'{key:.<40}{value:<15}{errors_enum.ErrorCode(num_val).name}', fg='red')
                except ValueError:
                    click.secho(f'{key:.<40}{value:<15}{num_val} not defined', fg='red')
            else:
                click.secho(f'{key:.<40}{value:<15}', fg='green')
        return edt_errors

    if item == 'faulttrees':
        faulttree_values = get_registry_ft_versions()
        print_object(faulttree_values)

    if item == 'framework':
        framework_values = get_registry_framework_versions()
        print_object(framework_values)

    if item == 'all':
        edt_values = {}
        agco_update = {}
        try:
            edt_reg_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').EDT.values()
            for i in edt_reg_values:
                edt_values.update({i.name: i.data})
            for key, value in edt_values.items():
                if ('_err' in key.lower()) or ('Error' in key):
                    if int(value):
                        click.secho(f'{key:.<40}{value:<15}', fg='red', bg='black')
                    else:
                        click.secho(f'{key:.<40}{value:<15}', fg='green', bg='black')
                else:
                    click.secho(f'{key:.<40}{value:<15}', fg='blue', bg='black')
        except AttributeError as e:
            click.secho('EDT does not appear to be installed. Please confirm that EDT is installed', fg='red')
        try:
            update_reg_values = regobj.HKLM.SOFTWARE.WOW6432Node.get_subkey(r'AGCO Corporation').get_subkey(
                r'AGCO Update').values()
            for i in update_reg_values:
                agco_update.update({i.name: i.data})
            for key, value in agco_update.items():
                click.secho(f'{key:.<40}{value:<15}', fg='yellow', bg='black')
        except AttributeError as e:
            click.secho('AGCO update client does not appear to be installed. Please install AUC.', fg='red')
        return edt_values


@main.command()
@click.option('--installer', '-i', type=click.Choice(['auc', 'aucclean', 'choco']))
def install(installer):
    """Allows for install of common testing tools"""
    if installer == 'auc':
        save_to_desktop('https://dl.agco-ats.com/AUC_EDT.exe', 'AUC_DL.exe')
        # run_auc_client()
    if installer == 'aucclean':
        save_to_desktop('https://agcoedtdyn.azurewebsites.net/AGCOUpdateClient', 'AGCOUpdateClient.exe')
        # download_auc_client_clean()

    if installer == 'choco':  # TODO Not working correctly
        subprocess.call(r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe Set-ExecutionPolicy Bypass -Scope '
                        r'Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = '
                        r'[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iwr '
                        r'https://chocolatey.org/install.ps1 -UseBasicParsing | iex', shell=True)


@main.command()
@click.option('--env', '-e', required=True, type=click.Choice(['prod', 'test', 'dev']), help='Choose between '
                                                                                             'environments')
@click.option('--tool', '-t', default='both', type=click.Choice(['auc', 'edt', 'both']), help="Select the tool you will"
                                                                                              " change the environment "
                                                                                              "for")
def change(env, tool):
    """Allows user to change environments for edt, auc or both """
    env_dict = {'dev': 'edtsystems-webtest-dev.azurewebsites.net',
                'prod': 'secure.agco-ats.com',
                'test': 'edtsystems-webtest.azurewebsites.net',
                }
    environment = env_dict[env]
    if tool in {'auc', 'both'}:
        set_auc_environment(environment)
    if tool in {'edt', 'both'}:
        set_edt_environment(environment)


@main.command()
@click.option("--file", "-f", help=r"The input for this is the output of of the EDT Admins tool Model Mapping Export")
@click.option("--report", "-r", is_flag=True, help="Creates a report of in a .json file")
@click.option("--list_masters", "-lm", is_flag=True, help="Prints a list of masters in the file")
@click.option("--master", "-m", help='Returns all content under a given master')
@click.option("--model", "-md", help='Returns all content that matches a given model')
@click.option("--locale", "-l", help='Returns all content with a given locale')
@click.option("--brand", "-b", help='Returns all content within a given brand')
@click.option("--author", "-a", help='Returns all content developed by a given author')
def lookup(file, report, list_masters, master, model, locale, brand, author):
    """Tool to look up the Masters in a given model maps it uses the output of of the EDT Admins tool Model
    Mapping Export """
    if not file:
        file = get_latest_csv()
    data = pd.read_csv(file)
    values = {'Model Year': 'No year provided', 'CustomOptions': 'No custom options provided',
              'Category': 'No category provided'}
    data.fillna(value=values, inplace=True)

    if master:
        data = data.loc[data.Master.str.contains(master, case=False, regex=True), :]
    if locale:
        data = data.loc[data.Region.str.contains(locale, case=False, regex=True), :]
    if brand:
        data = data.loc[data.Brand.str.contains(brand, case=False, regex=True), :]
    if model:
        data = data.loc[data.CustomOptions.str.contains(model, case=False, regex=True), :]
    if author:
        data = data.loc[data.Author.str.contains(author, case=False, regex=True), :]
    data.to_csv('test.csv', index=False)
    master_to_models = parse_csv()
    if list_masters:
        print_masters(master_to_models)
    if report:
        create_model_report(master_to_models)
        # print_object(master_to_models)
    else:
        print_object_no_paging(master_to_models)


@main.group()
@click.option('--env', '-e', default='prod', type=click.Choice(['prod', 'test', 'dev']), help='Choose the environment '
                                                                                              'that the API calls will'
                                                                                              ' be directed')
@click.option('--username', '-u', prompt=True, default=lambda: os.environ.get('AGTEST_USER', ''), help='Enter username')
@click.option('--password', '-p', prompt=True, hide_input=True, default=lambda: os.environ.get('AGTEST_PW', ''),
              help='Enter password')
@click.pass_context
def api(ctx, env, username, password):
    """API commands to assist with testing"""
    if not os.environ.get('AGTEST_USER'):
        os.system(f'SETX AGTEST_USER {username} /M')
    if not os.environ.get('AGTEST_PW'):
        os.system(f'SETX AGTEST_PW {password} /M')
    if env == 'dev':
        HOST = 'edtsystems-webtest-dev.azurewebsites.net'
    elif env == 'test':
        HOST = 'edtsystems-webtest.azurewebsites.net'
    else:
        HOST = "secure.agco-ats.com"
    BASE_URL = f'https://{HOST}'
    ctx.ensure_object(dict)
    ctx.obj['HOST'] = HOST
    ctx.obj['BASE_URL'] = BASE_URL
    m_id, m_token = get_auth(username, password, BASE_URL)
    ctx.obj['MAC_ID'] = m_id
    ctx.obj['MAC_TOKEN'] = m_token


@api.group()
@click.pass_context
def download(ctx):
    """
    Allows for package download via Release, Bundle, or Version
    """
    pass


@download.command()
@click.argument('package', required=True)
@click.pass_context
def release(ctx, package):
    """Takes package name and will prompt for release, then it downloads any package that matches name within release"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    updated_content_dict = rec_dd()
    get_release_list(base_url, mac_id, mac_token, host)  # prints list of release and their corresponding ids
    release_id_no = int(input('Please input the Release number that corresponds with your desired release: '))
    content_def_dict = get_content_definitions(base_url, mac_id, mac_token, host, 'name')
    for key, value in content_def_dict.items():
        if package.lower() in key:
            updated_content_dict[key].update(value)
    print_object(updated_content_dict)
    packages = []
    for key, value in updated_content_dict.items():
        content_def_id = value["content_definition_id"]
        package = get_package_id(base_url, mac_id, mac_token, host, release_id_no, content_def_id)
        packages.append(package)
    for packageid in packages:
        if packageid:
            download_url = package_download_link(base_url, mac_id, mac_token, host, packageid)
            packagename = download_url.split('/')[-1]
            save_to_desktop(download_url, packagename)


@download.command()
@click.pass_context
def bundle(ctx):
    """Takes package name and will prompt for UG/Bundle, then it downloads any package that matches within the bundle"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    updated_content_dict = rec_dd()
    package_type_dict = {"globals": "e0049dcb-5988-470c-bea1-df061db77bd9",
                         "model_maps": "da50e47a-5812-4d29-a452-86e90a1bca6f",
                         "plugins": "b033a8f0-da1c-4f9d-8cc3-8da3dd517b14",
                         "fault_trees": "054e707e-de16-46bb-8f66-35e48e2f9058",
                         "framework": "882150c6-d7bc-4769-8694-308d71068371",
                         "vdw": "51d05953-13e6-4689-a7ed-6cde3b33b2ef",
                         "vdw_plugins": "42ca87cb-61c2-43bd-bd08-07248f73479d"
                         }

    id_to_update_group = {"eb91c5e8-ffb1-4060-8b97-cb53dcd4858d": "EDTUpdates",
                          "d76d7786-1771-4d3b-89b1-c938061da4ca": "EDTUpdates_INTERNAL_TestPush",
                          "42dd2226-cdaa-46b4-8e23-aa98ec790139": "EDTUpdates_TestPush",
                          "30ae5793-67a2-4111-a94a-876a274c3814": "EDTUpdates_ReleaseCandidate",
                          "75a00edd-417b-459f-80d9-789f0c341131": "EDTUpdates_INTERNAL_ReleaseCandidate",
                          "6ed348f3-8e77-4051-a570-4d2a6d86995d": "EDT Development INTERNAL",
                          "29527dd4-3828-40f1-91b4-dfa83774e0c5": "EDT_Development",
                          }

    update_group_to_id = {value: key for key, value in id_to_update_group.items()}
    print()
    [print(x) for x in update_group_to_id.keys()]
    print()
    ug = click.prompt("Please enter the update group you want to list the bundles for, from the list above: ",
                      type=click.Choice(update_group_to_id.keys()))
    ugid = update_group_to_id[ug]
    bundles = get_bundles_in_ug(base_url, mac_id, mac_token, host, ugid)
    bundles_filtered = dict()
    for key, value in bundles.items():
        if value['bundle_number'] < 700:
            bundles_filtered.update({key: value})

    # bundles_clump = (Clumper(bundles).keep(lambda d: d['bundle_number'] < 900).blob)
    first_five_bundles = take(5, bundles_filtered.items())
    list_top_five_bundles = list()
    # sorted_bundles_by_bundle_number = {k: v for k, v in (bundles.items())}
    for bundle_description, bundle_dict in first_five_bundles:
        list_top_five_bundles.append(bundle_description)
        print(bundle_description)
    print()
    bundle_to_query = click.prompt("Please enter the Bundle you want to query to get your package: ",
                                   type=click.Choice(list_top_five_bundles))
    print()
    bundle_id = bundles[bundle_to_query]['bundle_id']
    [print(x) for x in list(package_type_dict.keys())]
    print()
    package = click.prompt("Please enter the type of package you are looking for from the following list: ",
                           type=click.Choice(package_type_dict.keys()))
    package_type = package_type_dict[package]
    package_version = get_package_version(base_url, mac_id, mac_token, host, bundle_id, package_type)
    packages_dict = get_all_packages(base_url, mac_id, mac_token, host)
    print()
    packages_clump = Clumper(packages_dict).keep(lambda d: package_type in d['PackageTypeID']) \
        .keep(lambda d: package_version == d['Version']).blob
    if len(packages_clump) > 1:
        full_or_delta = click.prompt("Do you want the full or delta installer?: ",
                                     type=click.Choice(['Full', 'Delta']))
        for item in packages_clump:
            download_url = item['Url']
            if full_or_delta in item['Notes']:
                packagename = download_url.split('/')[-1]
                packagename = packagename.split('.')[0]
                save_to_desktop(download_url, f'{packagename}_{package_version}_{full_or_delta}.exe')
                if full_or_delta == 'Delta':
                    if click.confirm("Do you want to download previous versions full installer?", abort=True):
                        delta_cmp = Clumper(packages_dict).keep(lambda d: d["Version"] == item["PreviousVersion"]) \
                            .keep(lambda d: d["PreviousVersion"] == 0) \
                            .keep(lambda d: package.lower() in d["Url"].lower()).blob
                        if delta_cmp[0]["Url"]:
                            delta_download_url = delta_cmp[0]["Url"]
                            delta_version = delta_cmp[0]["Version"]
                            delta_package_name = download_url.split('/')[-1]
                            delta_package_name = packagename.split('.')[0]
                            save_to_desktop(delta_download_url, f'{delta_package_name}_{delta_version}_full.exe')
    else:
        if len(packages_clump) == 0:
            print(f'The {package} was not found in provided Bundle!')
        for item in packages_clump:
            if item['Url']:
                download_url = item['Url']
                packagename = download_url.split('/')[-1]
                packagename = packagename.split('.')[0]
                save_to_desktop(download_url, f'{packagename}_{item["Version"]}.exe')


@download.command(name='version')
@click.argument('package', required=True)
@click.option('--version', '-v', type=click.INT, help="If you want to specify the version number to download, otherwise"
                                                      "if left out it will grab the highest version number available")
@click.pass_context
def by_version(ctx, package, version):
    """Finds packages from the API that match the version and package name in the url of the download """
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    # package_type_dict = get_package_types(base_url, mac_id, mac_token, host, package)
    packages_dict = get_all_packages(base_url, mac_id, mac_token, host)
    # for item in package_type_dict:
    #     package_type = item["PackageTypeID"]
    if not version:
        temp_clump = Clumper(packages_dict).keep(lambda d: package.lower() in d["Url"].lower()) \
            .sort(lambda d: d['Version'], reverse=True).blob
        highest_version = temp_clump[0]['Version']
        package_clump = Clumper(temp_clump).keep(lambda d: package.lower() in d["Url"].lower()) \
            .keep(lambda d: d['Version'] == highest_version).blob
    else:
        package_clump = Clumper(packages_dict).keep(lambda d: package.lower() in d["Url"].lower()) \
            .keep(lambda d: version == d['Version']).blob
    if len(package_clump) > 1:
        if package_clump[0]['PackageTypeID'] == package_clump[1]['PackageTypeID']:
            full_or_delta = click.prompt("Do you want the full or delta installer?: ",
                                         type=click.Choice(['Full', 'Delta']))
            for item in package_clump:
                if item['Url']:
                    download_url = item['Url']
                    if full_or_delta in item['Notes']:

                        packagename = download_url.split('/')[-1]
                        packagename = packagename.split('.')[0]
                        save_to_desktop(download_url, f'{packagename}_{item["Version"]}_{full_or_delta}.exe')
                        if full_or_delta == 'Delta':
                            if click.confirm("Do you want to download previous versions full installer?", abort=True):
                                delta_cmp = Clumper(packages_dict).keep(
                                    lambda d: d["Version"] == item["PreviousVersion"]) \
                                    .keep(lambda d: d["PreviousVersion"] == 0) \
                                    .keep(lambda d: package.lower() in d["Url"].lower()).blob
                                if delta_cmp[0]["Url"]:
                                    delta_download_url = delta_cmp[0]["Url"]
                                    delta_version = delta_cmp[0]["Version"]
                                    delta_package_name = download_url.split('/')[-1]
                                    delta_package_name = packagename.split('.')[0]
                                    save_to_desktop(delta_download_url,
                                                    f'{delta_package_name}_{delta_version}_full.exe')
        else:
            print(f'The search for {package} returned too many results please use the below data to refine your search')
            print_object(package_clump)
    else:
        if len(package_clump) == 0:
            print(f'The {package} with {version} was not found!')
        for item in package_clump:
            if item['Url']:
                download_url = item['Url']
                packagename = download_url.split('/')[-1]
                packagename = packagename.split('.')[0]
                save_to_desktop(download_url, f'{packagename}_{item["Version"]}.exe')


@api.group()
@click.pass_context
def voucher(ctx):
    """
    Performs api calls for common voucher actions such as extend and create
    """
    pass


@voucher.command()
@click.option('--duration', '-d', default=8, help='Allows the user to extend a Temporary or RightToRepair voucher a'
                                                  ' specified number of weeks. If not specified it will default to 8'
                                                  ' weeks from the current date')
@click.pass_context
def extend(ctx, duration):
    """Extends temporary vouchers"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    voucher = get_registry_voucher()
    if voucher.startswith('A'):
        voucher_type = 'Temporary'
    elif voucher.startswith('P'):
        voucher_type = "RightToRepair"
    elif voucher.startswith('N'):
        voucher_type = "Internal"
    elif voucher.startswith('E'):
        voucher_type = "Commercial"
    else:
        voucher_type = "Invaild"

    if voucher_type in {"RightToRepair", "Temporary"}:
        expir_date = get_date_x_weeks_from_now(duration)
        uri = f'{base_url}/api/v2/Vouchers'
        payload = {'Temporary': {"VoucherCode": voucher,
                                 "Type": voucher_type,
                                 "DealerCode": "NA0001",
                                 "ExpirationDate": expir_date,
                                 },
                   "RightToRepair": {"VoucherCode": voucher,
                                     "Type": voucher_type,
                                     "DealerCode": "NA0001",
                                     "OrderNumber": "ABCTest",
                                     "ExpirationDate": expir_date,
                                     }
                   }
        r = requests.put(f'{uri}', auth=MACAuth(mac_id, mac_token, host), data=payload[voucher_type])
        return r.text
    else:
        print(f"{voucher_type} voucher type does not support an  expiration date.")


@voucher.command()
@click.pass_context
@click.option('--duration', '-d', default=8, help='Specify the number of weeks the voucher lasts. This only works with'
                                                  ' Temporary and RightToRepair vouchers')
@click.option('--apply', '-a', is_flag=True, help='This flag will attempt to apply the voucher via cli')
@click.option('--vouchertype', '-vt', default='temp', type=click.Choice(['temp', 'internal', 'commercial', 'r2r']),
              help='Choose the voucher type that you want to create')
def create(ctx, duration, apply, vouchertype):
    """Creates temporary voucher"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    expire_date = get_date_x_weeks_from_now(duration)
    uri = f'{base_url}/api/v2/Vouchers'
    payload = {'temp': {"Type": "Temporary",
                        "DealerCode": "NA0001",
                        "Email": "darrin.fraser@agcocorp.com",
                        "ExpirationDate": expire_date,
                        },
               'internal': {"Type": "Internal",
                            "DealerCode": "NA0001",
                            "Purpose": "Testing",
                            "LicenseTo": "Darrin Fraser",
                            "Email": "darrin.fraser@agcocorp.com",
                            },
               'commercial': {"Type": "Commercial",
                              "DealerCode": "NA0001",
                              "OrderNumber": "ABCTest",
                              "Email": "darrin.fraser@agcocorp.com",
                              },
               'r2r': {"Type": "RightToRepair",
                       "DealerCode": "NA0001",
                       "OrderNumber": "ABCTest",
                       "ExpirationDate": expire_date,
                       "Email": "darrin.fraser@agcocorp.com",
                       },

               }

    r = requests.post(f'{uri}', auth=MACAuth(mac_id, mac_token, host), data=payload[vouchertype])
    voucher_text = (r.text).strip('"')
    copy2clip(voucher_text)
    click.secho(f'{payload[vouchertype]["Type"]} voucher created, and copied to clipboard'
                f'\nVoucher: {voucher_text}')
    if apply:
        apply_voucher(voucher_text)
    return voucher_text


@voucher.command()
@click.pass_context
def vdw(ctx):
    """Updates .lic to allow access to VDW, Test Mode, and AGCO DA"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    add_services_to_license(base_url, mac_id, mac_token, host)


@api.group()
@click.pass_context
def release(ctx):
    """
    Performs api calls for common release actions
    """
    pass


@release.command(name='plugins')
@click.argument('release_id', type=click.INT, required=True)
@click.pass_context
def api_plugins(ctx, release_id):
    """Parses the plugins for a given release"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    api_plugins_dict = defaultdict(list)
    uri = f'{base_url}/api/v2/ContentSubmissions'
    payload = {
        "contentDefinitionID": 1234,
        "includeAttributes": 'IncludedPlugIn',
        "releaseID": release_id,
    }
    r = requests.get(f'{uri}', auth=MACAuth(mac_id, mac_token, host), params=payload)
    plugins_response = r.json()
    for item in plugins_response['Entities'][0]['Attributes']:
        unedited_item = item['Value']
        plugin, _sep, plug_value = unedited_item.partition('::')
        api_plugins_dict[plugin.upper()].append(plug_value)
    print_object(api_plugins_dict)
    return api_plugins_dict


@release.command(name='list')
@click.pass_context
def get_list(ctx):
    """Retrieves release ids identified by release name"""
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    release_id_to_name, _release_list_by_name = get_release_list(base_url, mac_id, mac_token, host)
    for key, value in release_id_to_name.items():
        click.secho(f'{key:2} : {value}')


@release.command()
@click.argument('release_id', type=click.INT, required=True)
@click.option('--create_table', '-ct', is_flag=True, help='Creates .xlsx spreadsheet of output of release info')
@click.option('--path', '-p', default=os.path.expanduser('~\\Documents\\reports\\'), help='Allows user to save to '
                                                                                          'alternate location')
@click.option('--name', '-n', default='Released_Content', help='Allows user to save file with alternate name')
@click.option('--masters_only', '-mo', is_flag=True, help='Used in conjunction with create table.')
@click.pass_context
def content(ctx, release_id, create_table, path, name, masters_only):
    """
    Text of all released content in a given release with
    """
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    released_content_dict = get_release_content(base_url, mac_id, mac_token, host, release_id)
    updated_name = f'{release_id}_{name}'
    if create_table:
        create_content_table(path, updated_name, released_content_dict, masters_only)
    else:

        print_object(released_content_dict)

    return released_content_dict


@release.command()
@click.argument('current_id', type=click.INT, required=True)
@click.argument('previous_id', type=click.INT, required=True)
@click.option('--create_table', '-ct', is_flag=True, help='Creates .xlsx spreadsheet of output of release info')
@click.option('--path', '-p', default=os.path.expanduser('~\\Documents\\reports\\'), help='Allows user to save to '
                                                                                          'alternate location')
@click.option('--name', '-n', default='Released_Content', help='Allows user to save file with alternate name')
@click.option('--masters_only', '-mo', is_flag=True, help='Used in conjunction with create table.')
@click.option('--download', '-d', is_flag=True, help='Downloads reports for all submissions that are new or changed')
@click.pass_context
def compare(ctx, current_id, previous_id, create_table, path, name, masters_only, download):
    """
    Text of added or changed items in a release. Requires the current release ID of the current as well as the previous
    release ID
    """
    host = ctx.obj.get('HOST')
    base_url = ctx.obj.get('BASE_URL')
    mac_id = ctx.obj.get('MAC_ID')
    mac_token = ctx.obj.get('MAC_TOKEN')
    updated_content_dict = defaultdict(dict)
    current_content_dict = get_release_content(base_url, mac_id, mac_token, host, current_id)
    current_name = f'{current_id}_vs_{previous_id}_{name}'
    previous_content_dict = get_release_content(base_url, mac_id, mac_token, host, previous_id)
    for key, value in current_content_dict.items():
        if key in previous_content_dict:
            if value['updated_date'] == previous_content_dict[key]['updated_date']:
                continue
            else:
                updated_content_dict[key].update(value)
        else:
            updated_content_dict[key].update(value)

    if create_table:
        create_content_table(path, current_name, updated_content_dict, masters_only)
    else:
        print_object(updated_content_dict)

    if download:
        download_master_reports(updated_content_dict, path)
        unzip_reports(path)
        convert_downloaded_file(path)

    return updated_content_dict


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
        nonce = ''.join([str(random.randint(0, 9)) for i in range(8)])
        formatted_hmac = self.get_hmac(method, uri, milliseconds, nonce)
        return f'MAC kid={self.mac_id},ts={milliseconds},nonce={nonce},mac=\"{formatted_hmac}\"'


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
