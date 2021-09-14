"""Run flowgraph module, runs the temporary flowgraph located in temp/flowgraph.py

    Returns:
        time: time needed for flowgraph execution
        num_right: number of rightfully decoded messages
        num_dec: number of decoded messages
    """

import subprocess
import re
import time as td
import random
import os
import string
import logging

_logger = logging.getLogger(__name__)
# pylint: disable=R0914,R1705


def profile_flowgraph(string_input: str, timeout: int, template: str, remove_temp_files: bool):
    """
    Runs the actual flowgraph
    Args:
        template: template to use
        string_input: string input to verify against
        timeout : maximum number of seconds to let the flowgraph run
        remove_temp_files: boolean value to remove temp files or not

    Returns: the number of decoded messages

    """
    _logger.debug("Starting new flowgraph run")
    # generate random string to hold the temporary output
    ran = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    results_file = str(ran)
    results_converted = "temp/" + results_file + "-converted.txt"
    results_file = "temp/" + results_file + ".txt"
    _logger.debug("Random output file : %s", results_file)
    # set start time
    start_time = td.time()
    # call bash script to execute flowgraph
    subprocess.call(
        "gr_lora_sdr_profiler/bash_scripts/run.sh {0} {1}".format(timeout, results_file), shell=True
    )
    time = td.time() - start_time
    if template == "cran":
        return time
    else:
        subprocess.call(
            "gr_lora_sdr_profiler/bash_scripts/convert.sh {} {}".format(
                results_file, results_converted
            ),
            shell=True,
        )
        # open output for parsing processing
        with open(results_converted, "r") as file1:
            try:
                stdout = file1.readlines()
            except (RuntimeError, TypeError, NameError):
                _logger.error("Error reading the output of the run")
                stdout = "nothing"

        if remove_temp_files:
            # delete temporary file
            os.remove(results_file)
            os.remove(results_converted)

        return parse_stdout(stdout, string_input, time, template)


def parse_stdout(stdout, string_input, time, template):
    """
    Parses the stdout file of the flowgraph runner to find the number
    of decoded and rightfully decoded messages

    Args:
        stdout ([lines]): output of stdout
        string_input ([string]): string to match against
        time (int): execution time
        template (string) : template file to use

    Returns:
        [int]: number of rightfully decoded messages
    """
    # Number of rightlyfully decoded messages
    num_right = 0
    # Number of decoded messages
    num_dec = 0
    # for each line in stdout find the number of rightfull and decoded messages
    if template == "frame_detector":
        num_dec_err = 0
        num_dec_suc = 0
        for out in stdout:
            try:
                line = str(out)
                # look for decoded pakcets
                re_text_right = "msg:" + str(string_input)
                out_right = re.search(re_text_right, line)
                re_text_dec = "msg:"
                out_dec = re.search(re_text_dec, line)
                # look for detected packets of the frame detector
                re_text_packet_dec_err = "Packet Detection Error"
                out_dec_packet_err = re.search(re_text_packet_dec_err, line)
                re_text_packet_dec_suc = "Good Packet Detected"
                out_dec_packet_suc = re.search(re_text_packet_dec_suc, line)

                # check if the search found match objects
                if out_right is not None:
                    num_right = num_right + 1
                if out_dec is not None:
                    num_dec = num_dec + 1
                if out_dec_packet_err is not None:
                    num_dec_err = num_dec_err + 1
                if out_dec_packet_suc is not None:
                    num_dec_suc = num_dec_suc + 1

            except (RuntimeError, TypeError, NameError):
                _logger.error("Error in parsing from line %s of template %s", line, template)

        # return all  parsed values
        return num_right, num_dec, num_dec_suc, num_dec_err, time
    # use standard approach
    else:
        for out in stdout:
            try:
                line = str(out)
                re_text_right = "msg:" + str(string_input)
                out_right = re.search(re_text_right, line)
                re_text_dec = "msg:"
                out_dec = re.search(re_text_dec, line)
                # check if the search found match objects
                if out_right is not None:
                    num_right = num_right + 1
                if out_dec is not None:
                    num_dec = num_dec + 1
            except (RuntimeError, TypeError, NameError):
                _logger.error("Error in parsing from line %s of template %s", line, template)
        # return all  parsed values
        return num_right, num_dec, time
