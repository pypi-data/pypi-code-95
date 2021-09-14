from typing import Dict, List

import pluggy

from solitude import TOOL_NAME

hookspec = pluggy.HookspecMarker(TOOL_NAME.lower())


@hookspec
def matches_command(cmd: str) -> bool:
    """Should this command be processed by this plugin?

    :param cmd: the command to test
    :return: True if command matches False otherwise
    """


@hookspec
def get_command_hash(cmd: str) -> str:
    """Computes the hash for the command
    This is used to uniquely link job status to commands.
    So if the exact same command is found they both link to the same job.
    Therefore it is recommended to remove parts from cmd that do not change
    the final results for the job.
    If you are uncertain what to do just return `cmd` as hash

    :param cmd: the command to compute the hash for
    :return: the command hash
    """


@hookspec
def retrieve_state(cmd: str) -> Dict:
    """Retrieve state for the job which can be set in a dictionary

    :param cmd: the command to test
    :return: a dictionary with the retrieved state (used in other calls)
    """


@hookspec
def is_command_job_done(cmd: str, state: Dict) -> bool:
    """Checks if the command has finished

    :param cmd: the command to test
    :param state: the retrieved state dictionary for this job
    :return: True if job is done False otherwise
    """


@hookspec
def get_command_status_str(cmd: str, state: Dict) -> str:
    """Retrieve state for the job which can be set in a dictionary

    :param cmd: the command to test
    :param state: the retrieved state dictionary for this job
    :return: a string containing job information and progress status
    """


@hookspec
def get_errors_from_log(log: str) -> List[str]:
    """Checks the log for errors

    :param log: the log string to parse
    :return: A list of error messages, empty list if no errors were found
    """
