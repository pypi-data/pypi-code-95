"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import sys
import os
import logging
import json
import shlex
from datetime import datetime
from blackduck_c_cpp.util import util
from blackduck_c_cpp.util.c_arg_parser import C_Parser
from blackduck_c_cpp.pkg_manager.pkg_manager_detector import PkgDetector
from blackduck_c_cpp.pkg_manager.pkg_manager_bom import PkgManagerBom
from blackduck_c_cpp.bdba.upload_bdba import BDBAApi
from blackduck_c_cpp.sig_scanner.emit_wrapper import EmitWrapper
from blackduck_c_cpp.bdio.bdio2_python_transformer import BDIO2Transformer
from blackduck_c_cpp.sig_scanner.run_sig_scanner import SigScanner
from blackduck_c_cpp.util.hub_api import HubAPI
from blackduck_c_cpp.coverity_json.cov_json_parse import CovJsonParser
import glob
import platform
from os.path import expanduser

"""
This class will run coverity build capture for the supplied build command.
It assumes that any setup and configuration for the build has already taken place 
prior to calling this code.
"""


def run():
    start_time = datetime.now()
    my_args = C_Parser()

    bld_dir = my_args.args.build_dir
    bld_cmd = my_args.args.build_cmd
    cov_dir = my_args.args.cov_output_dir
    blackduck_output_dir = my_args.args.output_dir
    cov_home = my_args.args.coverity_root
    bd_url = shlex.quote(my_args.args.bd_url.strip('/'))
    hub_project_name = shlex.quote(my_args.args.project_name)
    hub_project_vers = shlex.quote(my_args.args.project_version)
    codelocation_name = shlex.quote(
        my_args.args.codelocation_name) if my_args.args.codelocation_name else "{}/{}".format(
        hub_project_name, hub_project_vers)
    additional_sig_scan_args = shlex.quote(my_args.args.additional_sig_scan_args) if my_args.args.additional_sig_scan_args else None
    api_token = shlex.quote(my_args.args.api_token)
    insecure = True if my_args.args.insecure else False
    skip_transitives = my_args.args.skip_transitives
    skip_includes = my_args.args.skip_includes
    skip_dynamic = my_args.args.skip_dynamic
    use_offline_files = my_args.args.use_offline_files
    offline_mode = my_args.args.offline
    scan_cli_dir = my_args.args.scan_cli_dir if my_args.args.scan_cli_dir is not None else blackduck_output_dir
    run_modes = list(map(lambda mode: mode.lower(), map(str.strip, my_args.args.modes.split(","))))
    PKG_MGR_MODE = 'pkg_mgr'
    SIG_MODE = 'sig'
    BDBA_MODE = 'bdba'
    ALL_MODE = 'all'
    hub_api = HubAPI(bd_url, api_token, insecure)
    home = expanduser("~")

    if not cov_dir:
        cov_dir = os.path.join(home, ".synopsys", "blackduck-c-cpp", "output", hub_project_name)
    cov_output = cov_dir
    if not os.path.exists(cov_output):
        os.makedirs(cov_output)

    if not blackduck_output_dir:
        blackduck_output_dir = os.path.join(home, ".synopsys", "blackduck-c-cpp", "output", hub_project_name)
    if not os.path.exists(blackduck_output_dir):
        os.makedirs(blackduck_output_dir)

    LOG_FILENAME = 'blackduck_c_cpp.log'
    logging.basicConfig(format="%(filename)s:%(funcName)s:%(lineno)d:%(asctime)s:%(levelname)s: %(message)s",
                        level=logging.DEBUG, filename=os.path.join(blackduck_output_dir, LOG_FILENAME), filemode='w')

    def handle_uncaught_exp(type, value, traceback):
        logging.error("Logging an uncaught exception",
                      exc_info=(type, value, traceback))

    sys.excepthook = handle_uncaught_exp
    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG if my_args.args.verbose else logging.INFO)
    formatter = logging.Formatter("%(filename)s:%(funcName)s:%(lineno)d:%(asctime)s:%(levelname)s: %(message)s")
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info("coverity output files will be in {}".format(cov_output))
    logging.info("output log is written to file {}".format(os.path.join(blackduck_output_dir, LOG_FILENAME)))

    if offline_mode:
        logging.debug(
            "Storing config file to location : {}".format(os.path.join(blackduck_output_dir, "offline_config.yaml")))
        with open(os.path.join(blackduck_output_dir, "offline_config.yaml"), 'w') as f:
            json.dump(my_args.args.__dict__, f, indent=2)
    if use_offline_files:
        logging.warning(
            "Please make sure skip_* parameters are kept exactly same as in offline mode from offline configuration file {}".format(
                os.path.join(blackduck_output_dir, "offline_config.yaml")))

    cov_bin = os.path.join(cov_home, "bin")
    sig_scanner_path = blackduck_output_dir
    build_log = os.path.join(cov_output, "build-log.txt")
    binary_files_list = os.path.join(blackduck_output_dir, "all_binary_paths.txt")
    json_grep_files_list = os.path.join(blackduck_output_dir, "json_grep_files_diff.txt")
    unresolved_files_list = os.path.join(blackduck_output_dir, "unresolved_file_paths.txt")
    resolved_files_list = os.path.join(blackduck_output_dir, "resolved_file_paths.txt")
    resolved_cov_files_list = os.path.join(blackduck_output_dir, "resolved_cov_file_paths.txt")
    unresolved_cov_files_list = os.path.join(blackduck_output_dir, "unresolved_cov_file_paths.txt")
    cov_json_file_path = os.path.join(blackduck_output_dir, "cov_emit_links.json")

    if my_args.args.use_offline_files and (my_args.args.offline or not my_args.args.skip_build):
        logging.error("Cannot set use_offline_files=True and offline=True/skip_build=False")
        sys.exit(1)
    platform_name = platform.system().lower()
    cov_emit_link_path = ""

    try:
        cov_build_path = glob.glob(os.path.join(cov_bin, 'cov-build*'))[0]
        cov_manage_emit_path = glob.glob(os.path.join(cov_bin, 'cov-manage-emit*'))[0]
    except IndexError:
        logging.error("cov-build or cov-manage-emit not found in bin directory at location: {}".format(cov_bin))
        sys.exit(1)

    try:
        cov_emit_link_path = glob.glob(os.path.join(cov_bin, 'cov-emit-link*'))[0]
    except IndexError:
        pass

    if not my_args.args.skip_build:
        logging.info("******************************   Phase: Starting Build ***********************************")
        cov_conf = os.path.join(blackduck_output_dir, "conf")
        if not os.path.exists(cov_conf):
            os.makedirs(cov_conf)

        logging.debug("PLATFORM NAME IS {}".format(platform_name))
        if 'windows' in platform_name:
            conf_key = " & "
        else:
            conf_key = " \n "

        conf_cmd = util.conf_cmd("--clang", cov_bin, cov_conf)
        conf_cmd += conf_key + util.conf_cmd("--gcc", cov_bin, cov_conf)
        conf_cmd += conf_key + util.conf_cmd("--msvc", cov_bin, cov_conf)
        conf_cmd += conf_key + util.conf_cmd("--template --compiler cc --comptype gcc", cov_bin, cov_conf)
        conf_cmd += conf_key + util.conf_cmd("--template --compiler c++ --comptype g++", cov_bin, cov_conf)
        conf_cmd += conf_key + util.conf_cmd("--template --compiler ccache --comptype prefix", cov_bin, cov_conf)

        if os.path.exists(cov_emit_link_path):
            bld_cmd = "{} --emit-link-units -c {} --dir {} {}".format(cov_build_path,
                                                                      os.path.join(cov_conf, "bld.xml"),
                                                                      cov_output, bld_cmd)
        else:
            bld_cmd = "{} -c {} --dir {} {}".format(cov_build_path, os.path.join(cov_conf, "bld.xml"),
                                                    cov_output, bld_cmd)
        full_cmd = conf_cmd + conf_key + bld_cmd
        logging.info("Build Command: {}".format(bld_cmd))
        ret_code = util.run_cmd(full_cmd, bld_dir)
        if ret_code != 0:
            logging.error(
                "Build not successful, please make sure to do successful build - return code {}".format(ret_code))
            sys.exit(1)
    logging.info(
        "******************************* Phase: Running Cov Manage Emit **********************************")
    if not use_offline_files:
        blackduck_emit_wrapper = EmitWrapper(cov_home, cov_output, blackduck_output_dir, platform_name,
                                             skip_build=my_args.args.skip_build,
                                             build_log=build_log)
        emit_wrapper_output_sig = blackduck_emit_wrapper.cov_emit_output_sig
        emit_cov_header_files = blackduck_emit_wrapper.cov_header_files
    else:
        emit_wrapper_output_sig = None
        if os.path.exists(os.path.join(blackduck_output_dir, 'cov_emit_output_files')):
            logging.info("Attempting to use offline files for cov-manage-emit at location: {}".format(
                os.path.join(blackduck_output_dir, 'cov_emit_output_files')))
        else:
            logging.error(
                "Unable to find previously generated offline files for cov-manage-emit, set use_offline_files to false to generate new ones.")

    header_files_set = set()
    linker_files_set = set()
    executable_files_set = set()
    if os.path.exists(cov_emit_link_path):
        logging.info(
            "******************************* Phase: Generating Cov-emit-link json **********************************")
        if not use_offline_files:
            full_cmd = "{} --dir {} list-capture-invocations > {}".format(cov_manage_emit_path,
                                                                          cov_output, os.path.join(blackduck_output_dir,
                                                                                                   "cov_emit_links.json"))
            ret_code = util.run_cmd(full_cmd, cov_output)
            if ret_code == 0:
                cov_parser = CovJsonParser(cov_json_file_path)
                header_files_set, linker_files_set, executable_files_set = cov_parser.run()
            else:
                logging.error("coverity json not created successfully- return code {}".format(ret_code))
        else:
            if os.path.exists(os.path.join(blackduck_output_dir, 'cov_emit_links.json')):
                logging.info("Attempting to use offline files for cov-emit-link at location: {}".format(
                    os.path.join(blackduck_output_dir, 'cov_emit_links.json')))
            else:
                logging.error(
                    "Unable to find previously generated offline files for cov-emit-link, set use_offline_files to false to generate new ones.")
    else:
        logging.info("Not performing coverity json parsing due to absence of cov-emit-link in bin directory")

    logging.info(
        "******************************* Phase: Getting package manager BOM **********************************")
    # if not use_offline_files:
    pkg_manager, os_dist = PkgDetector().get_platform()
    # skips all header files from package manager and bdba matching if skip_includes is True
    if skip_includes:
        emit_cov_header_files = []
        header_files_set = []
    if use_offline_files:
        emit_cov_header_files = []
        header_files_set = []
    if pkg_manager and os_dist:
        pkg_mgr_bom = PkgManagerBom(pkg_manager,
                                    build_log,
                                    cov_home,
                                    blackduck_output_dir,
                                    os_dist,
                                    bld_dir,
                                    unresolved_files_list,
                                    resolved_files_list,
                                    binary_files_list,
                                    json_grep_files_list,
                                    my_args.args.skip_build,
                                    skip_transitives,
                                    skip_dynamic,
                                    run_modes,
                                    emit_cov_header_files, my_args.args.debug, header_files_set,
                                    linker_files_set, executable_files_set, resolved_cov_files_list,
                                    unresolved_cov_files_list, hub_api,
                                    my_args.args.offline, my_args.args.use_offline_files)
        pkg_mgr_bom.run()
    else:
        pkg_mgr_bom = None
    logging.info("***************************** Phase: BDBA ************************************")
    if (BDBA_MODE in run_modes or ALL_MODE in run_modes):
        if not use_offline_files:
            logging.info(
                "The bdba tar file to scan will be written to {}".format(
                    os.path.join(blackduck_output_dir, "bdba_ready.tar")))
        else:
            if os.path.exists(os.path.join(blackduck_output_dir, "bdba_ready.tar")):
                logging.info("Attempting to use offline files for BDBA at location: {}".format(
                    os.path.join(blackduck_output_dir, 'bdba_ready.tar')))
            else:
                logging.error(
                    "Unable to find previously generated offline files for BDBA..set use_offline_files to false to generate new ones.")
        if not offline_mode:
            BDBAApi(hub_api).upload_binary(hub_project_name,
                                           hub_project_vers,
                                           codelocation_name,
                                           os.path.join(blackduck_output_dir, "bdba_ready.tar"))

    logging.info("****************************** Phase: BDS Signature Scan ***********************************")
    if SIG_MODE in run_modes or ALL_MODE in run_modes:
        if pkg_mgr_bom:
            sig_scanner = SigScanner(cov_home,
                                     hub_api,
                                     pkg_mgr_bom.bdba_data,
                                     hub_project_name,
                                     hub_project_vers,
                                     codelocation_name,
                                     emit_wrapper_output_sig,
                                     blackduck_output_dir,
                                     sig_scanner_path,
                                     offline_mode,
                                     scan_cli_dir,
                                     use_offline_files,
                                     os_dist,
                                     insecure,
                                     additional_sig_scan_args,
                                     api_token,
                                     my_args.args.scan_interval,
                                     my_args.args.json_splitter_limit,
                                     my_args.args.disable_json_splitter,
                                     my_args.args.skip_includes)
        else:
            sig_scanner = SigScanner(cov_home,
                                     hub_api,
                                     None,
                                     hub_project_name,
                                     hub_project_vers,
                                     codelocation_name,
                                     emit_wrapper_output_sig,
                                     blackduck_output_dir,
                                     sig_scanner_path,
                                     offline_mode,
                                     scan_cli_dir,
                                     use_offline_files,
                                     os_dist,
                                     insecure,
                                     additional_sig_scan_args,
                                     api_token,
                                     my_args.args.scan_interval,
                                     my_args.args.json_splitter_limit,
                                     my_args.args.disable_json_splitter,
                                     my_args.args.skip_includes)
        sig_scanner.run()

    logging.info(
        "*****************************  Phase: BDIO from our Package Manager ************************************")
    if not offline_mode and (PKG_MGR_MODE in run_modes or ALL_MODE in run_modes):
        bdio2_python_wrapper = BDIO2Transformer(blackduck_output_dir, hub_api)
        json_file_path = os.path.join(blackduck_output_dir, "raw_bdio.json")
        if not os.path.exists(json_file_path):
            logging.warning("The raw BDIO file was not generated. There will not be BDIO results.")
            return
        with open(json_file_path, 'r') as f:
            raw_bdio_json = json.load(f)
        cov_results = [raw_bdio_json]  # Load results from input raw_bdio json
        scan_size = os.stat(json_file_path).st_size  # size of jsonld bdio2 file
        skip_bdio2 = False
        try:
            scanned_path = cov_results[0]['extended-objects'][0]['fullpath'][0]
            if not scanned_path:  # get the scanned path
                scanned_path = "/"
        except IndexError:
            logging.debug(
                "no components present in json {}".format(os.path.join(blackduck_output_dir, "raw_bdio.json")))
            skip_bdio2 = True
        if not skip_bdio2:
            result_bdio2_str, code_loc_name = bdio2_python_wrapper.generate_bdio2(codelocation_name, hub_project_name,
                                                                                  hub_project_vers,
                                                                                  cov_results, scanned_path, scan_size)
            # Rest Remains same above code then code be swapped out once bogdan release his library changes
            bdio2_output_filename = bdio2_python_wrapper.write_bdio2_document(result_bdio2_str)
            logging.info("Created bdio2 file : %s", bdio2_output_filename)
            logging.info("Uploading bdio2 to Black Duck: %s", bdio2_output_filename)
            response = hub_api.hub.upload_scan(bdio2_output_filename)
            if response.ok:
                print(bdio2_output_filename, "uploaded successfully !!")
            else:
                logging.error("Error uploading  %s bdio2 file", bdio2_output_filename)
    logging.info("Finished ..")
    end_time = datetime.now()
    logging.info('Time taken to run: {}'.format(end_time - start_time))


if __name__ == '__main__':
    run()
