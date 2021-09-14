import re
from typing import Dict, List, Optional
from solitude import hookimpl


CSUBMIT_REGEX = (
    r"c-submit\s+(?:(?:--\S+(?:\s*[=\s]\s*\S+)?\s+)*)?(?P<user>\S+)"
    r"\s+(?P<ticket>\S+)\s+(?P<duration>\d+)\s+(?P<image>\D\S+)\s*(?P<args>.*)"
)


def match_csubmit_command_str(cmd: str) -> Optional[re.Match]:
    return re.search(CSUBMIT_REGEX, cmd.strip())


def extract_dir_from_cmd(cmd: str, dir_type: str = "input") -> str:
    """
    Extracts a directory from a command (i.e.: --input-dir --output-dir)

    If a match is found then it returns the dir_type + the directory
    The dir_type is prepended to differentiate input from output dirs
    If no match is found the empty string is returned.
    This means that it is not set, so it's not the same as the current dir.
    """
    dir_match = re.search(
        f"--{dir_type}-dir" + r"[= ]\s*([\w/\\]+|\"(?!\").*\")\s+", cmd
    )
    return (
        f" {dir_type[0]}:" + dir_match.groups()[0].replace('"', "")
        if dir_match
        else ""
    )


def filter_csubmit_command_str(cmd: str) -> str:
    result = match_csubmit_command_str(cmd=cmd)
    assert result is not None
    out_dir = extract_dir_from_cmd(cmd=cmd, dir_type="output")
    in_dir = extract_dir_from_cmd(cmd=cmd, dir_type="input")
    group_dict = result.groupdict()
    return (
        f"{group_dict['image']} {group_dict['args']}{in_dir}{out_dir}"
    ).strip()


@hookimpl
def matches_command(cmd: str) -> bool:
    return match_csubmit_command_str(cmd=cmd) is not None


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
    errors = []
    if log.find("Killed") != -1:
        errors.append("NoResource")
    if log.find("CUDA_ERROR") != -1:
        errors.append("CUDA")
    errors = errors + [e[1:-1] for e in re.findall(r"\s.*Error:", log)]
    return errors
