"""
Simple python file to give a time estimate on how long it takes to run the flowgraph.
"""

import logging
import datetime

_logger = logging.getLogger(__name__)


def get_time_estimate(spreading_factor: int, n_times: int, counter: int, frames: int) -> datetime:
    """
    Gets an time estimate of how long the run is going to take
    using a simple lookup table

    Args:
        spreading_factor: spreading factor that is being used
        n_times: total number of runs the script must make
        counter: current script counter
        frames : number of frames that must be send in each run

    Returns: time: current time estimate in seconds

    """
    # if no last time is given use approx times
    default_approx_times = {7: 0.3, 8: 0.35, 9: 0.4, 10: 0.4, 11: 0.5, 12: 0.5}
    time = (
        default_approx_times[spreading_factor] * n_times
        - counter * default_approx_times[spreading_factor]
    ) * frames

    return datetime.timedelta(seconds=time)
