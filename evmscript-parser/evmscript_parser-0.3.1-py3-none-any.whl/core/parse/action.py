"""
Parsing encoded EVM script.
"""
from typing import (
    Tuple
)

from ..script_specification import (
    LENGTH_SPEC_ID, LENGTH_ADDRESS,
    LENGTH_METHOD_ID, LENGTH_DATA_LEN,
    HEX_PREFIX
)

from .structure import EVMScript, SingleCall


def _parse_single_call(
        encoded_script: str, index: int
) -> Tuple[int, SingleCall]:
    """Parse one call segment and shift index."""
    address = encoded_script[index: index + LENGTH_ADDRESS]
    index += LENGTH_ADDRESS

    data_length = int(encoded_script[index:index + LENGTH_DATA_LEN], 16)
    index += LENGTH_DATA_LEN

    method_id = encoded_script[index: index + LENGTH_METHOD_ID]
    index += LENGTH_METHOD_ID

    offset = data_length * 2 - LENGTH_METHOD_ID
    call_data = encoded_script[index: index + offset]
    index += offset

    return index, SingleCall(
        address, data_length, method_id, call_data
    )


def parse_script(encoded_script: str) -> EVMScript:
    """
    Parse encoded EVM script.

    :param encoded_script: str, encoded EVM script.
    :return: parsed script as instance of EVMScript object.
    """
    if encoded_script.startswith(HEX_PREFIX):
        encoded_script = encoded_script[len(HEX_PREFIX):]
    spec_id = encoded_script[:LENGTH_SPEC_ID]

    calls_data = []
    i = LENGTH_SPEC_ID
    while i < len(encoded_script):
        i, one_call = _parse_single_call(encoded_script, i)
        calls_data.append(one_call)

    return EVMScript(
        spec_id, calls_data
    )
