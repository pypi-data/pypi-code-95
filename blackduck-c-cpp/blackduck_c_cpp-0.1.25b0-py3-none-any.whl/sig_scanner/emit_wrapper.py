"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.

Run coverity/bin/cov-manage-emit and capture output
"""

import logging
import os
import re
import shutil
from shutil import copy
from blackduck_c_cpp.util import util
import sys
from blackduck_c_cpp.util import global_settings
import glob


class EmitWrapper:

    def __init__(self, cov_base_path, cov_output_path, blackduck_output_dir, platform_name, skip_build=False,
                 build_log=None):

        self.cov_base_path = cov_base_path
        self.cov_output_path = cov_output_path
        self.blackduck_output_dir = blackduck_output_dir
        self.platform_name = platform_name
        self.cov_emit_output_files_path = os.path.join(self.blackduck_output_dir, 'cov_emit_output_files')
        self.cov_header_files = {}
        self.cov_emit_output_sig = {}

        logging.info("Files output by cov-emit will be copied to {}".format(self.cov_emit_output_files_path))
        # latest_emit_dir = self.get_latest_emit_dir()
        # if latest_emit_dir is not None:
        #     if skip_build:
        #         cov_host = os.path.basename(os.path.normpath(latest_emit_dir))
        #         os.environ['COV_HOST'] = cov_host
        #         logging.info("COV_HOST set to {}".format(cov_host))
        #     if not skip_build:
        #         copy(build_log, latest_emit_dir)
        # else:
        #     logging.error("emit directory is empty - please make sure cov-build and cov-emit ran successfully ")

        try:
            self.run_cov_emit()
        except Exception as e:
            logging.error("Exception occurred: {}".format(e))
            logging.error("emit directory is empty - please make sure cov-build and cov-emit ran successfully ")

    def get_latest_emit_dir(self):
        """
        get the most recently modified directory in the emit directory in the cov output directory
        """
        try:
            search_dir = os.path.join(self.cov_output_path, 'emit')
            directories = [os.path.join(search_dir, x) for x in os.listdir(search_dir) if
                           os.path.isdir(os.path.join(search_dir, x))]
            directories.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            if directories:
                return directories[0]
        except FileNotFoundError:
            logging.error(
                "emit directory not present - please verify if coverity build is successful and cov-build files are present in {}".format(
                    self.cov_output_path))
            sys.exit(1)
        return None

    def run_cov_emit(self):
        """
        run cov-manage-emit
        """
        logging.info("Running cov-emit...")
        try:
            cov_emit_path = glob.glob(os.path.join(self.cov_base_path, 'bin', 'cov-manage-emit*'))[0]
        except IndexError:
            logging.error("cov-manage-emit not present in location: {}".format(os.path.join(self.cov_base_path, 'bin')))
            sys.exit(1)
        if 'windows' in self.platform_name:
            str_cmd = 'findstr /v /c:"Translation unit:"'
        else:
            str_cmd = 'grep -v "Translation unit:"'

        tu_pattern_command = '{} --dir {} --tu-pattern \"all()\" print-source-files | {} | awk {{\'print $3\'}}'.format(
            cov_emit_path, self.cov_output_path, str_cmd)

        list_command = '{} --dir {} list | {} | awk {{\"print $3\"}}'.format(
            cov_emit_path, self.cov_output_path, str_cmd)
        logging.debug("tu_pattern command is {}".format(tu_pattern_command))
        logging.debug("list_command is {}".format(list_command))
        cov_emit_result = util.run_cmd_emit(tu_pattern_command) + util.run_cmd_emit(list_command)

        self.cov_emit_output_sig = {x for x in cov_emit_result if x != ':' and os.path.exists(x)}
        self.cov_header_files = {x for x in cov_emit_result if x != ':' and (
                re.match(global_settings.hpp_pattern, x.strip()) or re.match(global_settings.h_pattern,
                                                                             x.strip())) and os.path.exists(x)}

        logging.info("Total cov emit output files: {}".format(len(self.cov_emit_output_sig)))
        logging.info("Total header files: {}".format(len(self.cov_header_files)))

        if os.path.exists(self.cov_emit_output_files_path):
            shutil.rmtree(self.cov_emit_output_files_path)
        os.makedirs(self.cov_emit_output_files_path)

        for f in self.cov_emit_output_sig:
            try:
                copy(f, self.cov_emit_output_files_path)
            except PermissionError:
                pass
            except IsADirectoryError:
                pass
                # logging.debug("File copy failed because file already exists in target directory {}".format(f))
