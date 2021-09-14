"""
Runner for the frame_detector flowgraph
This file runs the overall frame_detector flowgraph with all changing values
"""
import logging

from . import run_flowgraph
from . import file_writer
from . import get_config
from . import file_saver
from . import get_cpu_load
from . import time_estimater

_logger = logging.getLogger(__name__)

# pylint: disable=R0914,R1702,R0912,R0801,W0632


def main(args: str) -> None:
    """
    Main function where all the computations happen
    Args:
        args: sys arguments

    Returns: none

    """
    _logger.debug("Running frame detector runner")
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
    ) = get_config.parse_config_data(args.config[0], "frame_detector")
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
        save = file_saver.FileSaver(args, "frame_detector", sequential_spreading_factor=False)

    for spreading_factor in sf_list:
        # if sequential spreading factor is used make a new data frame for each spreading factor.
        if sequential_spreading_factor:
            save = file_saver.FileSaver(
                args,
                "frame_detector",
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
                                                _logger.critical("Writing frame_detector error")
                                            # run the flowgraph
                                            try:
                                                (
                                                    num_right,
                                                    num_dec,
                                                    time,
                                                ) = run_flowgraph.profile_flowgraph(
                                                    input_data,
                                                    timeout,
                                                    "frame_detector_timeout",
                                                    remove_temp_files,
                                                )

                                            except (RuntimeError, TypeError, NameError):
                                                _logger.critical(
                                                    "Error executing flowgraph of " "frame_detector"
                                                )
                                            # get the average load
                                            try:
                                                (
                                                    load_1min,
                                                    load_5min,
                                                    load_15min,
                                                ) = get_cpu_load.load_all()
                                                # calculate the derived values
                                                decoded_success_per = num_right / frames * 100
                                                decoded_error_rate = 1 - (num_right / frames)
                                                packet_detection_rate = 1 - (num_dec / frames)
                                                num_decoded_error = frames - num_dec
                                                paylen = len(input_data)
                                                data_rate = (paylen * frames) / time
                                            except (RuntimeError, TypeError, NameError):
                                                _logger.warning(
                                                    "Error in getting the cpu load values "
                                                    "of the system"
                                                )
                                            # setup data frame to hold all data
                                            data = {
                                                "template": "frame_detector",
                                                "time_wait": time_wait,
                                                "input_data": input_data,
                                                "spreading_factor": spreading_factor,
                                                "paylen": paylen,
                                                "impl_head": impl_head,
                                                "has_crc": has_crc,
                                                "coding_rate": coding_rate,
                                                "frames": frames,
                                                "num_right": num_right,
                                                "num_dec": num_dec,
                                                "time": time,
                                                "load_1min": load_1min,
                                                "load_5min": load_5min,
                                                "load_15min": load_15min,
                                                "decoded_success_per": decoded_success_per,
                                                "decoded_error_rate": decoded_error_rate,
                                                "packet_detection_err_rate": packet_detection_rate,
                                                "num_decoded_succes": num_right,
                                                "num_decoded_error": num_decoded_error,
                                                "data_rate": data_rate,
                                                "threshold": threshold,
                                                "snr": snr,
                                                "cfo": cfo,
                                                "sto": sto,
                                            }
                                            __counter = __counter + 1
                                            # save data to pandas or wandb
                                            save.saver(data)

                                            save.finish()
