# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Setups an abstraction layer such that
different types of device interfaces can be used
"""

from threading import Thread
from ..core.i2controller import MmsI2cController
from ..core.i2controller import MmsSpiController
from ..core.toolbox import scan_i2c
from ..core.toolbox import scan_spi


class ThreadWithReturnValue(Thread):
    """
    Heper class for device threading
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        """
        Setup threading model
        See threading.Thread: https://docs.python.org/3/library/threading.html
        """
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def setup(device, **kwargs):
    """
    Assign device model
    Initialize interface

    """
    if isinstance(device, MmsI2cController):
        device = [device]
    if isinstance(device, MmsSpiController):
        device = [device]
    elif not isinstance(device, list):
        raise TypeError(
            f"Incorrect type {type(device)} for \
                device [only list/I2Ccontroller/SPIcontroller]"
        )

    # Check initializations status
    for dev in device:
        if not dev.init:
            # If a single device is not initialized
            # something must have changed hardwarewise
            # and everything is re-initialized
            if isinstance(dev, MmsI2cController):
                dev = scan_i2c(dev, **kwargs)
            elif isinstance(dev, MmsSpiController):
                dev = scan_spi(dev, **kwargs)
            else:
                raise TypeError(
                    f"Incorrect type {type(dev)} during \
                        scan [only list/I2Ccontroller/SPIcontroller]"
                )

    return device
