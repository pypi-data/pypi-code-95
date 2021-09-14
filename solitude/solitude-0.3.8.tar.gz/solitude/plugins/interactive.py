from typing import Dict, List
from solitude import hookimpl
from solitude.plugins.csubmit import (
    get_errors_from_log as _get_errors_from_log,
)
from solitude.plugins.csubmit import (
    filter_csubmit_command_str,
    match_csubmit_command_str,
)


@hookimpl
def matches_command(cmd: str) -> bool:
    return (" --interactive " in cmd) and (
        match_csubmit_command_str(cmd=cmd) is not None
    )


@hookimpl
def get_command_hash(cmd: str) -> str:
    return filter_csubmit_command_str(cmd=cmd)


@hookimpl
def retrieve_state(cmd: str) -> Dict:
    return {}


@hookimpl
def is_command_job_done(cmd: str, state: Dict) -> bool:
    return False


@hookimpl
def get_command_status_str(cmd: str, state: Dict) -> str:
    return filter_csubmit_command_str(cmd=cmd)


@hookimpl
def get_errors_from_log(log: str) -> List[str]:
    return _get_errors_from_log(log=log)
