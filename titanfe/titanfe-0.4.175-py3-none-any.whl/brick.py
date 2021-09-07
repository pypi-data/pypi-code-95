#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Abstract base classes for building Bricks"""

from abc import ABCMeta, abstractmethod
from typing import Type, Optional, Dict

from ujotypes import UjoBase

from titanfe.apps.brick_runner.adapter import BrickAdapter


class ConfigurationError(Exception):
    pass


class BrickBase(metaclass=ABCMeta):
    """An abstract base class for building Bricks"""

    def __init__(self, adapter: BrickAdapter, parameters: Optional[Dict] = None):
        """ Initialize the Brick

        Arguments:
            adapter (BrickAdapter):
                the BrickAdapter provides an interface between the BrickRunner and the Brick

            parameters (Optional[Dict]):
                if any parameters are required, the module should be accompanied with a `config.yml`
                this will be the base for parameters and their default values
                which are then updated with values from the current flow configuration
        """
        self.adapter = adapter
        self.parameters = parameters

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def setup(self):
        """ Upon loading the Brick in the BrickRunner the setup-method is run once
        and can be used to e.g. open connections that will be held persistent.
        """

    def teardown(self):
        """ When unloading the Brick from the BrickRunner the teardown-method is run once,
        implement it to e.g. close connections opened during `setup`"""

    @abstractmethod
    def process(self, input: Type[UjoBase], port: str):  # pylint: disable=redefined-builtin
        """ Do the input processing.

        To modify the payload of the current packet simply return a new value.
        Use the adapter's `emit_new_packet` to create a data packet and insert it into the flow.

        Arguments:
            input (Type[UjoBase]): the input data to be processed

        Returns:
             Optional[UjoBase]:
                the new payload for current data packet traveling in the flow.
                When returning `None` the current packet get's dropped.
        """


class InletBrickBase(BrickBase, metaclass=ABCMeta):
    """An abstract base class for building bricks that will run a continous `process`"""

    @abstractmethod
    def stop_processing(self):
        """ The BrickRunner needs a way to properly end continuously running bricks.
        It will call this method upon receiving a termination request
        and expect the processing to be aborted/terminated.
        """
