#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The output with it's server and ports"""

import asyncio
from functools import partial
from itertools import chain

from .port import Port
from ..metrics import QueueWithMetrics


class Output:
    """The output side of a brick runner creates a Server.
       It will then send packets as requested by the following inputs.

    Arguments:
        runner (BrickRunner): instance of a parent brick runner
        name (str): a name for the output destination
        address (NetworkAddress): the network address of the output server
    """

    def __init__(self, logger, create_output_queue):
        self.log = logger.getChild("Output")
        self.create_queue = create_output_queue

        self.ports = {}

    def __iter__(self):
        return iter(self.ports.values())

    def __getitem__(self, port_name):
        try:
            port = self.ports[port_name]
        except KeyError:
            port = self.ports[port_name] = Port(port_name)

        return port

    def __repr__(self):
        return f"Output(ports={repr(self.ports)})"

    @classmethod
    async def create(cls, logger, metric_emitter):
        """Creates a new instance"""
        output = cls(logger, create_output_queue=partial(QueueWithMetrics, metric_emitter))
        return output

    def make_ports_and_groups(self, consumers_by_port):
        for port_name, consumers in consumers_by_port.items():
            for consumer in consumers:
                self.log.debug("add consumer group: %r on %r", consumer, port_name)
                self.add_consumer_group(port_name, consumer)

    def add_consumer_group(self, port_name, consumer):
        """add a configured output target"""
        target_instance_id = consumer["InstanceID"]
        self[port_name].add_consumer_group(
            target_instance_id, self.create_queue(target_instance_id), consumer, self.log
        )

    async def close(self):
        """close all connections and the server itself"""
        if self.ports:
            await asyncio.wait({port.close() for port in self})

    @property
    def consumer_groups(self):
        return chain.from_iterable(self)

    @property
    def is_empty(self):
        """True, if no packets are waiting to be outputted"""
        return not any(group.has_unfinished_business for group in self.consumer_groups)
