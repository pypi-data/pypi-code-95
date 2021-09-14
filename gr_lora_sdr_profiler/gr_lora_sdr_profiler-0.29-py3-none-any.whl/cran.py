"""
Runner for the cran flowgraph
This file runs the overall cran_send flowgraph with all changing values
"""
import logging
import glob,os 
import pandas as pd
from . import run_flowgraph
from . import file_writer
from . import get_config
from . import file_saver
from . import get_cpu_load
from . import time_estimater

_logger = logging.getLogger(__name__)

# pylint: disable=R0914,R1702,R0912,R0801


def main(args: str) -> None:
    """
    Main function where all the computations happen
    Args:
        args: sys arguments

    Returns: none

    """
    _logger.debug("Running cran_send runner")
    filename = args.filename
    timeout = args.timeout
    remove_temp_files = not args.no_remove_temp
    sequential_spreading_factor = args.sequential_spreading_factor
    __counter = 0

    # parse the config for the values to use
    (
        input_data,
        sf_list,
        frames_list,
        impl_head_list,
        has_crc_list,
        cr_list,
        time_wait_list,
        threshold_list,
        snr_list,
        sto_list,
        cfo_list,
    ) = get_config.parse_config_data(args.config[0], "cran")
    # initilize a saver object

    n_times = (
        len(cfo_list)
        * len(sto_list)
        * len(snr_list)
        * len(threshold_list)
        * len(cr_list)
        * len(has_crc_list)
        * len(impl_head_list)
        * len(frames_list)
        * len(sf_list)
    )
    _logger.info("Flowgraph needs to run %s times", n_times)
    # if no sequential spreading factor put everything into one large fram
    if not sequential_spreading_factor:
        save = file_saver.FileSaver(args, "cran", sequential_spreading_factor=False)

    for spreading_factor in sf_list:
        # if sequential spreading factor is used make a new data frame for each spreading factor.
        if sequential_spreading_factor:
            save = file_saver.FileSaver(
                args,
                "cran",
                sequential_spreading_factor=True,
                spreading_factor=spreading_factor,
            )
        # loop over all values that needs to be runned
        for cfo in cfo_list:
            for sto in sto_list:
                for snr in snr_list:
                    for threshold in threshold_list:
                        for time_wait in time_wait_list:
                            for coding_rate in cr_list:
                                for has_crc in has_crc_list:
                                    for impl_head in impl_head_list:
                                        for frames in frames_list:
                                            est_time = time_estimater.get_time_estimate(
                                                spreading_factor, n_times, __counter, frames
                                            )
                                            _logger.debug(
                                                "Starting new run, estimated time to "
                                                "completion %s",
                                                est_time,
                                            )
                                            # write template file
                                            try:
                                                file_writer.write_template_frame_detector(
                                                    filename,
                                                    input_data,
                                                    spreading_factor,
                                                    impl_head,
                                                    has_crc,
                                                    coding_rate,
                                                    frames,
                                                    time_wait,
                                                    threshold,
                                                    snr,
                                                    sto,
                                                    cfo,
                                                )
                                            except (RuntimeError, TypeError, NameError):
                                                _logger.critical("Writing cran error")
                                            # run the flowgraph
                                            try:
                                                (
                                                    time,
                                                ) = run_flowgraph.profile_flowgraph(
                                                    input_data,
                                                    timeout,
                                                    "cran",
                                                    remove_temp_files,
                                                )

                                            except (RuntimeError, TypeError, NameError):
                                                _logger.critical(
                                                    "Error executing flowgraph of cran"
                                                )
                                            # get the average load
                                            try:
                                                (
                                                    load_1min,
                                                    load_5min,
                                                    load_15min,
                                                ) = get_cpu_load.load_all()
                                                # calculate the derived values
                                                paylen = len(input_data)
                                                data_rate = (paylen * frames) / time
                                            except (RuntimeError, TypeError, NameError):
                                                _logger.warning(
                                                    "Error in getting the cpu load values "
                                                    "of the system"
                                                )
                                            #load the data from the csv object
                                            try:
                                                files = glob.glob("*.csv")
                                                files.sort(key=os.path.getmtime)
                                                last_file = files[-1].split("_")[0]
                                                latency = last_file+"_latency.csv"
                                                packets = last_file+"_packets.csv"
                                                #TODO figure out how to do this ?
                                                pd_packets = pd.read_csv(packets)
                                                num_dec = pd_packets['packets_decoded'].iloc[-1]
                                                num_recv = pd_packets['packets_recieved'].iloc[-1]
                                                num_send = pd_packets['packets_send'].iloc[-1]
                                            except:
                                                _logger.warning("Error in loading the data")

                                            # setup data frame to hold all data
                                            data = {
                                                "template": "cran",
                                                "time_wait": time_wait,
                                                "input_data": input_data,
                                                "spreading_factor": spreading_factor,
                                                "paylen": paylen,
                                                "impl_head": impl_head,
                                                "has_crc": has_crc,
                                                "coding_rate": coding_rate,
                                                "frames": frames,
                                                "time": time,
                                                "load_1min": load_1min,
                                                "load_5min": load_5min,
                                                "load_15min": load_15min,
                                                "data_rate": data_rate,
                                                "threshold": threshold,
                                                "snr": snr,
                                                "cfo": cfo,
                                                "sto": sto,
                                                "num_dec" : num_dec,
                                                "num_recv" : num_recv,
                                                "num_send" : num_send,
                                            }
                                            __counter = __counter + 1
                                            # save data to pandas or wandb
                                            save.saver(data)

                                            save.finish()
