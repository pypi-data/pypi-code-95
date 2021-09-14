# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import sys
import glob
import serial
import logging


def search_comports():
    """Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    _logger = logging.getLogger("search_comports")

    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    n_ports = len(ports)
    if n_ports == 1:
        _logger.debug("Found %d accessible port.", n_ports)
    else:
        _logger.debug("Found %d accessible ports.", n_ports)

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException) as e:
            if "Permission" in str(e):
                _logger.info("No permission to read %s", port)
            pass
    n_detected_devices = len(result)
    if n_detected_devices == 1:
        _logger.debug("%d accessible uart device.", n_detected_devices)
    else:
        _logger.debug("%d accessible uart devices.", n_detected_devices)

    return result
