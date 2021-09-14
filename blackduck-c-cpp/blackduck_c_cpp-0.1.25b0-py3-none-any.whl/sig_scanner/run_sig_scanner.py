"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import logging
import os
import tarfile
import re
import platform
import json
import glob
import shutil
import requests
import tqdm
import time
from blackduck_c_cpp.util import util
from blackduck_c_cpp.util.zip_file import MyZipFile
from blackduck_c_cpp.util import global_settings


class SigScanner:

    def __init__(self, cov_base_path, hub_api, files_notdetect_from_pkgmgr, project_name, project_version_name,
                 code_location_name, cov_emit_output_sig, blackduck_output_dir, sig_scanner_path, offline_mode,
                 scan_cli_dir, use_offline_files, os_dist, insecure=False, additional_sig_scan_args=None, api_token=None,
                 scan_interval=60, json_splitter_limit=4750000000,
                 disable_json_splitter=False, skip_includes=False):
        self.hub_api = hub_api
        self.sleep_interval = scan_interval  # time to wait between scans
        self.project_name = project_name
        self.project_version_name = project_version_name
        self.code_location_name = code_location_name + '-sig'
        self.insecure = insecure
        self.additional_sig_scan_args = additional_sig_scan_args
        self.json_splitter_limit = json_splitter_limit
        self.disable_json_splitter = disable_json_splitter
        self.skip_includes = skip_includes
        self.cov_emit_output_sig = cov_emit_output_sig
        self.offline_mode = offline_mode
        self.use_offline_files = use_offline_files
        self.os_dist = os_dist
        self.api_token = api_token if api_token else os.environ.get('BLACKDUCK_API_TOKEN')
        self.cov_base_path = cov_base_path
        self.sig_scan_output_directory = os.path.join(blackduck_output_dir, 'sig_scan')
        self.sig_scan_tar_output_directory = os.path.join(self.sig_scan_output_directory, 'tar_file')
        self.tar_output_path = os.path.join(self.sig_scan_tar_output_directory, 'sig_scan.tar.gz')
        self.scan_cli_home = sig_scanner_path
        self.scan_cli_dir = scan_cli_dir
        self.files_notdetect_from_pkgmgr = files_notdetect_from_pkgmgr
        self.scan_cli_directory = None
        self.scan_cli_path = None
        self.cov_header_files = {}
        self.sig_scanner_found = False
        self.json_file = None

    def tar_files(self):
        """
        compress the files from run_cov_emit and from files_notdetect_from_pkgmgr into a tar archive
        os.path.exists() check done in emit_wrapper.py
        """
        logging.info("The signature tar file to scan will be written to {}".format(self.tar_output_path))
        logging.info("Tarring files returned by cov-emit...")
        if self.skip_includes:
            self.cov_emit_output_sig = [emit_file for emit_file in self.cov_emit_output_sig if not (
                    re.match(global_settings.hpp_pattern, emit_file.strip()) or re.match(global_settings.h_pattern,
                                                                                         emit_file.strip()))]

        files_to_tar = set(self.cov_emit_output_sig)

        if not os.path.exists(self.sig_scan_tar_output_directory):
            os.makedirs(self.sig_scan_tar_output_directory)

        if self.files_notdetect_from_pkgmgr:
            [[[files_to_tar.add(path) for path in paths if os.path.exists(path)] for paths in type.values()] for type in
             self.files_notdetect_from_pkgmgr.values()]

        with tarfile.open(self.tar_output_path, 'w:gz') as tar:
            for f in tqdm.tqdm(files_to_tar, total=len(files_to_tar)):
                tar.add(f)

    def download_sig_scanner(self):
        """
        download the signature scanner if necessary
        """
        logging.debug("Checking if the signature scanner exists and downloading if necessary...")
        op_sys = platform.system()
        if self.offline_mode:
            if self.scan_cli_dir is not None:
                self.scan_cli_home = os.path.dirname(self.scan_cli_dir)
                self.scan_cli_directory = os.path.basename(self.scan_cli_dir)
            else:
                try:
                    self.scan_cli_directory = os.path.basename(
                        glob.glob(os.path.join(self.scan_cli_home, 'scan.cli-*'))[0])
                except IndexError:
                    logging.error("scan cli not found at location: {}".format(self.scan_cli_home))
                    return
        else:
            sig_scanner_url = self.hub_api.hub.config['baseurl'] + '/download/scan.cli'
            self.scan_cli_directory = 'scan.cli-{}'.format(self.hub_api.hub.version_info['version'])
        logging.debug("scan cli directory is at {}".format(self.scan_cli_directory))
        logging.debug("scan cli home is at {}".format(self.scan_cli_home))
        self.scan_cli_path = os.path.join(self.scan_cli_home, self.scan_cli_directory)
        if os.path.exists(self.scan_cli_path):
            logging.info("Scan cli has been found, will not be downloaded. Location: {}".format(self.scan_cli_path))
            self.sig_scanner_found = True
        else:
            if self.offline_mode:
                logging.warning("sig_scanner not found in offline mode at location {}".format(self.scan_cli_path))
                self.sig_scanner_found = False
            else:
                if op_sys == 'Windows':
                    sig_scanner_url += '-windows'
                if op_sys == 'Darwin':
                    sig_scanner_url += '-macosx'
                sig_scanner_url += '.zip'
                logging.info("The signature scanner will be downloaded to {}".format(self.scan_cli_home))
                logging.info(
                    "Scan cli not found, downloading from {} to {}".format(sig_scanner_url, self.scan_cli_path))
                headers = self.hub_api.hub.get_headers()
                # use requests bc blackduck.execute_get() doesn't allow redirects
                response = requests.get(sig_scanner_url, allow_redirects=True, headers=headers,
                                        verify=not self.hub_api.hub.config['insecure'])

                open(os.path.join(self.scan_cli_home, 'sig-scanner.zip'), 'wb').write(response.content)
                with MyZipFile(os.path.join(self.scan_cli_home, 'sig-scanner.zip'), 'r') as zip_obj:
                    zip_obj.extractall(self.scan_cli_home)
                self.sig_scanner_found = True

    @staticmethod
    def json_splitter(scan_path, max_node_entries=200000, max_scan_size=4750000000):
        """
        Splits a json file into multiple jsons so large scans can be broken up with multi-part uploads
        Modified from source: https://github.com/blackducksoftware/json-splitter

        :param scan_path: the path to the json file to split
        :param max_node_entries: the max node entries per scan
        :param max_scan_size: the max size of any single scan in bytes
        :return: a list of the newly generated json files to upload
        """
        new_scan_files = []

        with open(scan_path, 'r') as f:
            scan_data = json.load(f)

        data_length = len(scan_data['scanNodeList'])

        scan_size = sum(node['size'] for node in scan_data['scanNodeList'] if node['uri'].startswith("file://"))

        if scan_size < max_scan_size:
            return [scan_path]

        logging.info("Source directory greater than 4.75GB. Splitting the json.")

        scan_name = scan_data['name']
        scan_node_list = scan_data.pop('scanNodeList')
        scan_data.pop('scanProblemList')
        scan_data['scanProblemList'] = []
        base = scan_node_list[0]

        # Computing split points for the file
        scan_chunk_size = 0
        scan_chunk_nodes = 0
        split_at = [0]
        for i in range(0, data_length - 1):
            if scan_chunk_size + scan_node_list[i + 1][
                'size'] > max_scan_size or scan_chunk_nodes + 1 > max_node_entries:
                scan_chunk_size = 0
                scan_chunk_nodes = 0
                split_at.append(i)
            if scan_node_list[i]['uri'].startswith('file://'):
                scan_chunk_size = scan_chunk_size + scan_node_list[i]['size']
            scan_chunk_nodes += 1

        # Create array of split points shifting by one position
        split_to = split_at[1:]
        split_to.append(data_length - 2)  # don't include the last entry because it's the one for the entire tar archive

        # Splitting and writing the chunks
        new_scan_path = scan_path.split('.json')[0]
        for i in range(len(split_at)):
            logging.debug("Processing range {}, {}".format(split_at[i], split_to[i]))
            # for i in range(0, dataLength, maxNodeEntries):
            node_data = scan_node_list[split_at[i]:split_to[i]]
            if i > 0:
                node_data.insert(0, base)
            # scanData['baseDir'] = baseDir + "-" + str(i)
            scan_data['scanNodeList'] = node_data
            scan_data['name'] = scan_name + "-" + str(split_at[i])
            filename = new_scan_path + "-" + str(split_at[i]) + '.json'
            with open(filename, 'w') as outfile:
                json.dump(scan_data, outfile)
            scan_data.pop('scanNodeList')
            new_scan_files.append(filename)

        return new_scan_files

    def run_sig_scanner(self):
        """
        scan the tar files created by tar_files()
        """

        logging.info("Running the signature scanner")

        i = ''
        if self.insecure:
            i = ' --insecure'

        if os.path.exists(os.path.join(self.sig_scan_output_directory, 'data')):
            shutil.rmtree(os.path.join(self.sig_scan_output_directory, 'data'))  # remove data directory if exists
        env = dict(os.environ)
        if self.os_dist.lower() == 'mac':
            java_path = os.path.join(self.scan_cli_path, 'jre', 'Contents', 'Home', 'bin', 'java')
        else:
            java_path = os.path.join(self.scan_cli_path, 'jre', 'bin', 'java')
        try:
            standalone_jar_path = glob.glob(os.path.join(self.scan_cli_path, 'lib', '*-standalone.jar'))[0]
            logging.debug("standalone jar path is {}".format(standalone_jar_path))
        except IndexError:
            logging.error("scan cli jar not found at location: {}".format(self.scan_cli_path))
            return
        if self.offline_mode:
            sig_scanner_command = "{} -Done-jar.silent=true -Done-jar.jar.path={} -Xmx4096m -jar {} --no-prompt {} -v --project {} --release {} --name {} --individualFileMatching=ALL --binaryAllowedList h,hpp,cpp,c {} --dryRunWriteDir {}".format(
                java_path,
                os.path.join(self.scan_cli_path, 'lib', 'cache', 'scan.cli.impl-standalone.jar'),
                standalone_jar_path,
                i, self.project_name, self.project_version_name,
                self.code_location_name,
                self.sig_scan_tar_output_directory,
                self.sig_scan_output_directory)
        else:
            sig_scanner_command = "{} -Done-jar.silent=true -Done-jar.jar.path={} -Xmx4096m -jar {} --no-prompt --scheme https --host {} --port 443 {} -v --project {} --release {} --name {} --individualFileMatching=ALL --binaryAllowedList h,hpp,cpp,c {} --dryRunWriteDir {}".format(
                java_path,
                os.path.join(self.scan_cli_path, 'lib', 'cache', 'scan.cli.impl-standalone.jar'),
                standalone_jar_path,
                re.search(r'https:\/\/(.*)', self.hub_api.hub.config['baseurl']).group(1), i, self.project_name,
                self.project_version_name,
                self.code_location_name,
                self.sig_scan_tar_output_directory,
                self.sig_scan_output_directory)
            env['BD_HUB_TOKEN'] = self.api_token
        if self.additional_sig_scan_args:
            sig_scanner_command += ' {}'.format(self.additional_sig_scan_args)

        logging.info("sig scanner command is {}".format(sig_scanner_command))
        util.run_cmd(sig_scanner_command, env=env, curdir=self.sig_scan_output_directory)
        json_files = glob.glob(os.path.join(self.sig_scan_output_directory, 'data', '*.json'))
        if len(json_files) > 0:
            self.json_file = json_files[0]
        else:
            logging.error(
                "There was an error running the signature scanner. Please check the signature scanner output.")
            return
        logging.info("Finished running the signature scanner")

    def upload_sig_results(self):
        try:
            if not self.offline_mode:
                self.hub_api.authenticate()  # prevent timeout
                if self.disable_json_splitter or (os.stat(self.tar_output_path).st_size < self.json_splitter_limit):
                    self.hub_api.hub.upload_scan(self.json_file)
                else:
                    json_lst = self.json_splitter(self.json_file, max_scan_size=self.json_splitter_limit)
                    for j in json_lst:
                        self.hub_api.hub.upload_scan(j)
                        logging.info(
                            'Uploading {} of {} json files'.format(str(json_lst.index(j) + 1), str(len(json_lst))))
                        if json_lst.index(j) < len(json_lst) - 1:
                            time.sleep(self.sleep_interval)
            else:
                logging.debug("signature scanner run in offline mode. Files are stored at Location: {}".format(
                    self.sig_scan_output_directory))
        except:
            logging.error("signature scanner file not uploaded..please verify if signature scanner ran successfully")

    def load_sig_results(self):
        try:
            logging.info("Using old signature scan from previous offline scan at location {}".format(
                self.sig_scan_output_directory))
            if not os.path.exists(os.path.join(self.sig_scan_output_directory, 'data')) and os.path.exists(
                    self.tar_output_path):
                self.run_sig_scanner()
            json_files = glob.glob(os.path.join(self.sig_scan_output_directory, 'data', '*.json'))
            if len(json_files) > 0:
                self.json_file = json_files[0]
        except:
            logging.error(
                "The signature scan json file was not generated. There will not be signature matching results.")

    def run(self):
        if not self.use_offline_files:
            self.tar_files()
        else:
            # finding if tar file is present
            logging.info("Attempting to use offline files for signature scanner tar file at location: {}".format(
                self.tar_output_path))
            if os.path.exists(self.tar_output_path):
                logging.info("Found signature scanner tar file at location: {}".format(
                    self.tar_output_path))
                # if tar file is present, see if json file is present
                if os.path.exists(os.path.join(self.sig_scan_output_directory, 'data')):
                    logging.info("Found signature scanner data file at location: {}".format(
                        os.path.join(self.sig_scan_output_directory, 'data')))
                    self.sig_scanner_found = True
                else:
                    logging.info(
                        "signature scanner json file not found at location {}. running signature scanner..".format(
                            self.sig_scan_output_directory))
            else:
                logging.error(
                    "Unable to find previously generated offline tar files for signature scanner, set use_offline_files to false to generate new ones.")
                return
        if not self.offline_mode:
            self.hub_api.authenticate()
            logging.info(
                "Will wait {} seconds between scan uploads if there are multiple scans".format(
                    str(self.sleep_interval)))
            logging.info("Results will be uploaded to {}".format(self.hub_api.hub.config['baseurl']))
            logging.info(
                "Results will be mapped to project {} version {} and code location {}".format(self.project_name,
                                                                                              self.project_version_name,
                                                                                              self.code_location_name))
            if self.insecure:
                logging.info("SSL verification has been disabled")
        if not self.sig_scanner_found:
            self.download_sig_scanner()
        if not self.use_offline_files:
            if self.scan_cli_path:
                self.run_sig_scanner()
        else:
            self.load_sig_results()
        if not self.offline_mode:
            self.upload_sig_results()
