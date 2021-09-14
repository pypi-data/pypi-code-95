# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Example script for running a measurement using uart devices only.
"""

from pyserialsensors.core.toolbox import scan_uart
from pyserialsensors.core.comPortController import search_comports

if __name__ == "__main__":
    ports = search_comports()
    devices = []
    for port in ports:
        device = scan_uart(port)
        if device is not None:
            devices.append(device)

    for device in devices:
        # setup devices
        device.start()

    # start measurement
    for device in devices:
        values = device.get_data()
        print(values)
