#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""An information packet passed between Bricks"""

import functools
import time
from dataclasses import dataclass, field

from ujotypes import UjoBase
from ujotypes.variants.none import UJO_VARIANT_NONE

from titanfe.apps.brick_runner.connection import Buffer
from titanfe.messages import PacketMessage
from titanfe.utils import create_uid, ns_to_ms, time_delta_in_ms, DictConvertable


@dataclass(repr=False)
class Packet(DictConvertable):
    """Represents an information packet (IP) passing through a flow"""

    uid: str = field(default_factory=functools.partial(create_uid, "P-"))
    started: float = field(default_factory=time.time_ns)
    port: str = ""
    payload: UjoBase = UJO_VARIANT_NONE
    buffer: Buffer = field(default_factory=Buffer)

    # ancestors: list = field(default_factory=list)
    input_entry: float = 0.0
    input_exit: float = 0.0
    output_entry: float = 0.0
    output_exit: float = 0.0

    def __repr__(self):
        return f"Packet(uid={self.uid}, payload={self.payload})"

    @property
    def traveling_time(self) -> float:
        return time_delta_in_ms(self.started)

    @property
    def queue_times(self):
        return {
            "time_in_input": ns_to_ms(self.input_exit - self.input_entry),
            "time_in_output": ns_to_ms(self.output_exit - self.output_entry),
            "time_on_wire": ns_to_ms(self.input_entry - self.output_exit),
        }

    def update_input_entry(self):
        self.input_entry = time.time_ns()

    def update_input_exit(self):
        self.input_exit = time.time_ns()

    def update_output_entry(self):
        self.output_entry = time.time_ns()

    def update_output_exit(self):
        self.output_exit = time.time_ns()

    def as_message(self):
        return PacketMessage(self.to_dict())
