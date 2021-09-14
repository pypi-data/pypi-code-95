"""Gets Linux cpu load

    Returns:
        load_1min: 1 minute avg load
        load_5_min: 5 minute avg load
        load_15_min: 15 minute avg load
    """
import subprocess
import logging

_logger = logging.getLogger(__name__)


def load_avg_1min() -> float:
    """
    Query's the Linux system with the average 1 min Linux load
    Returns: average 1 min Linux load

    """
    with subprocess.Popen(
        "cat /proc/loadavg | awk '{ print $1; }'", shell=True, stdout=subprocess.PIPE
    ) as process:
        out, err = process.communicate()
        load = float(out.decode("utf-8")[:-1])
        if err is not None:
            _logger.warning("Bash error in 1 min load avg")
        return load


def load_avg_5min() -> float:
    """
    Query's the Linux system with the average 5 min Linux load
    Returns: average 5 min Linux load

    """
    with subprocess.Popen(
        "cat /proc/loadavg | awk '{ print $2; }'", shell=True, stdout=subprocess.PIPE
    ) as process:
        out, err = process.communicate()
        load = float(out.decode("utf-8")[:-1])
        if err is not None:
            _logger.warning("Bash error in 5 min load avg")
        return load


def load_avg_15min() -> float:
    """
    Query's the Linux system with the average 15 min Linux load
    Returns: average 15 min Linux load

    """
    with subprocess.Popen(
        "cat /proc/loadavg | awk '{ print $3; }'", shell=True, stdout=subprocess.PIPE
    ) as process:
        out, err = process.communicate()
        load = float(out.decode("utf-8")[:-1])
        if err is not None:
            _logger.warning("Bash error in 15 min load avg")
        return load


def load_all() -> list:
    """
    Runs the above functions to get all the loads (1, 5 and 15 minutes)
    Returns: [list] with load figures

    """
    load_1min = load_avg_1min()
    load_5min = load_avg_5min()
    load_15min = load_avg_15min()

    return load_1min, load_5min, load_15min
