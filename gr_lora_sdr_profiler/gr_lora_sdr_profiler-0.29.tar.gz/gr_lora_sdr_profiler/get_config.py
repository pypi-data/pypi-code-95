"""
Functions to parse the yaml config file
"""
import logging
import yaml

_logger = logging.getLogger(__name__)


# pylint: disable=W1401,R0914,R0801


def increment_list(start: float, stop: float, increment: float, *skip: float) -> list:
    """
    Converts the input values from start to stop to an list
    Args:
        start: start value
        stop: stop value
        increment: increment value
        *skip : value to skip

    Returns: list of values
    """
    temp_list = []
    i = start
    while i < stop + increment:
        # round up to two decimal places
        if isinstance(i, float):
            i = round(i, 2)
        if i is not skip:
            temp_list.append(i)
        i += increment

    return temp_list


def get_label(x_colum_name: str, y_colum_name: str, *names) -> list:
    """

    Args:
        x_colum_name: x colum name to search for
        y_colum_name: y colum name to search for
        *names : more names you want to have the labels of

    Returns: list(x_label,y_label)

    """
    return_list = []
    # all labels possible
    labels = {
        "template": "string",
        "input_data": "string",
        "time_wait": "$t_{wait}$",
        "sf": "$SF$",
        "paylen": "Payload length [B]",
        "impl_head": "Impl head modus",
        "has_crc": "CRC modus",
        "cr": "Coding Rate",
        "frames": "$N_{frames}$",
        "time": "$t$",
        "data_rate": "Throughput [bytes/s]",
        "load_1_min": "1 min cpu load",
        "load_5_min": "5 min cpu load",
        "load_15_min": "15 min cpu load",
        "num_right": "Rightfully decoded messages",
        "num_dec": "Number of decoded messages",
        "decoded_success_per": "$\eta$",
        "decoded_error_rate": "PER",
        "packet_detection_err_rate": "DER",
        "num_decoded_error": "Num error detection",
        "num_decoded_succes": "Num decoded succes",
        "threshold": "$Th$",
        "snr": "$SNR (dB)$",
        "sto": "STO",
        "cfo": "CFO",
        "delay": "Delay",
    }
    return_list.append(labels[x_colum_name])
    return_list.append(labels[y_colum_name])

    # more names you want to have labels of
    for name in names:
        return_list.append(labels[name])

    return return_list


def parse_config_colums(template: str) -> list:
    """
    Returns the colums names (to be used in pandas) to use for diffrent templates
    Args:
        template: name of the template currenlty in use

    Returns:
        list of column names
    """
    # list ot hold all configs values
    colum_names = []

    colum_names.extend(
        [
            "template",
            "time_wait",
            "input_data",
            "spreading_factor",
            "paylen",
            "impl_head",
            "has_crc",
            "coding_rate",
            "frames",
        ]
    )
    # add the derived general quantities
    colum_names.extend(
        [
            "time",
            "data_rate",
            "load_1min",
            "load_5min",
            "load_15min",
            "decoded_success_per",
            "decoded_error_rate",
            "packet_detection_err_rate",
            "num_decoded_error",
            "num_decoded_succes",
            "cfo",
            "snr",
            "sto",
            "threshold",
        ]
    )
    if template == "multi_stream":
        colum_names.extend(["test"])

    return colum_names


def parse_config_data(cfg: str, template: str) -> list:
    """
    Parses the cfg file and returns all values as a list object.
    Args:
        cfg: file name of the yml config to load
        template: template to use

    Returns: list of all values described in the config file

    """

    # list ot hold all configs values
    config_list = []
    # open
    with open(r"{}".format(cfg)) as file:
        documents = yaml.full_load(file)
        config_list = documents["frame_detector"]
    input_list = config_list["input_string"]
    sf_list = increment_list(
        config_list["sf"]["start"], config_list["sf"]["end"], config_list["sf"]["increment"]
    )
    frames_list = increment_list(
        config_list["frames"]["start"],
        config_list["frames"]["end"],
        config_list["frames"]["increment"],
    )
    impl_head_list = increment_list(
        config_list["impl_head"]["start"], config_list["impl_head"]["end"], 1
    )
    has_crc_list = increment_list(config_list["has_crc"]["start"], config_list["has_crc"]["end"], 1)
    cr_list = increment_list(
        config_list["cr"]["start"], config_list["cr"]["end"], config_list["cr"]["increment"], 1
    )
    time_wait_list = increment_list(
        config_list["time_wait"]["start"],
        config_list["time_wait"]["end"],
        config_list["time_wait"]["increment"],
    )

    if template == "single":
        with open(r"{}".format(cfg)) as file:
            documents = yaml.full_load(file)

    if template == "frame_detector":
        threshold_list = increment_list(
            config_list["threshold"]["start"],
            config_list["threshold"]["end"],
            config_list["threshold"]["increment"],
        )
        snr_list = increment_list(
            config_list["snr"]["start"],
            config_list["snr"]["end"],
            config_list["snr"]["increment"],
        )
        sto_list = increment_list(
            config_list["sto"]["start"],
            config_list["sto"]["end"],
            config_list["sto"]["increment"],
        )
        cfo_list = increment_list(
            config_list["cfo"]["start"],
            config_list["cfo"]["end"],
            config_list["cfo"]["increment"],
        )

        return (
            input_list,
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
        )

    return (
        input_list,
        sf_list,
        frames_list,
        impl_head_list,
        has_crc_list,
        cr_list,
        time_wait_list,
    )
