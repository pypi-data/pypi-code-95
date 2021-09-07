"""
Description of EVM script with structure.
"""
import json

from typing import List
from dataclasses import dataclass, field, asdict

from ..exceptions import (
    ParseMismatchLength
)

from ..script_specification import (
    LENGTH_SPEC_ID, LENGTH_ADDRESS, LENGTH_METHOD_ID,
    add_hex_prefix, DEFAULT_SPEC_ID
)


@dataclass
class SingleCall:
    """
    Contains fields of the single call from script body.
    """

    # 20 bytes
    address: str
    # 4 bytes
    call_data_length: int
    # 4 bytes
    method_id: str
    # (call_data_length - 4) bytes
    encoded_call_data: str

    def __post_init__(self):
        """Check length constraints and perform normalized to hex."""
        if len(self.address) != LENGTH_ADDRESS:
            raise ParseMismatchLength(
                'address', len(self.address), LENGTH_ADDRESS
            )

        if len(self.method_id) != LENGTH_METHOD_ID:
            raise ParseMismatchLength(
                'method id', len(self.method_id), LENGTH_METHOD_ID
            )

        call_data_length_without_method_id = (
                self.call_data_length * 2 - len(self.method_id)  # noqa
        )
        if len(self.encoded_call_data) != call_data_length_without_method_id:
            raise ParseMismatchLength(
                'encoded call data',
                len(self.encoded_call_data),
                call_data_length_without_method_id
            )

        self.address = add_hex_prefix(self.address)
        self.method_id = add_hex_prefix(self.method_id)
        self.encoded_call_data = add_hex_prefix(self.encoded_call_data)


@dataclass
class EVMScript:
    """
    Contains data of the whole EVM script.
    """

    # Script executor id
    spec_id: str = field(default=DEFAULT_SPEC_ID)
    # Calls data
    calls: List[SingleCall] = field(default_factory=list)

    def __post_init__(self):
        """Check length constraints and perform normalized to hex."""
        if len(self.spec_id) != LENGTH_SPEC_ID:
            raise ParseMismatchLength(
                'spec id', len(self.spec_id), LENGTH_SPEC_ID
            )

        self.spec_id = add_hex_prefix(self.spec_id)

    def to_json(self) -> str:
        """Encode structure into json format."""
        return json.dumps(asdict(self))
