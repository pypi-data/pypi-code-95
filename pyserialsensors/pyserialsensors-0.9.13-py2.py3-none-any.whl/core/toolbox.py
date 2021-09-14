# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

# ######################################################################################################################
# Class : ToolBox
#
# Description : ToolBox for the configuration of Sensirion sensors
# ######################################################################################################################

import os
import logging

from ..devices.shtxx import SHT85
from ..devices.sfm3xxx import SFM3XXX
from ..devices.bme280 import BME280
from ..devices.scd30 import SCD30
from ..devices.sdp.sdp8xx import SDP8XX
from ..devices.max31865 import MAX31865
from ..devices.nau7802.nau7802 import NAU7802
from ..devices.ads1015 import ADS1015
from ..devices.qwiicrelay import QwiicQuadRelay
from ..devices.sps30 import SPS30
from ..devices.smgair2 import SMGair2
from ..devices.s8000 import S8000

# For type checking
from ..core.i2controller import MmsI2cController as I2cController
from ..core.i2controller import MmsSpiController as SpiController
from ..core.i2controller import MUX

FTDI_SENSOR_CLASSES = [
    SHT85,
    SFM3XXX,
    BME280,
    ADS1015,
    NAU7802,
    SCD30,
    SDP8XX,
    QwiicQuadRelay,
]

UART_SENSOR_CLASSES = [SPS30, SMGair2, S8000]


def scan_spi(spibus, loglvl: int = logging.ERROR, **kwargs):
    if type(spibus) is SpiController:
        spibus = [spibus]
    elif type(spibus) is not list:
        raise TypeError(
            f"spibus in scan_spi is of type {type(spibus)} but only list \
                  and pyftdi.spi.SpiController are supported"
        )

    log_id = f"SPIscan[{spibus[0].ftdi._usb_dev.serial_number}"
    if len(spibus) > 1:
        for bus in spibus[1:]:
            log_id += f",{bus.ftdi._usb_dev.serial_number}"
    log_id += "]"

    _logger = logging.getLogger(log_id)
    _logger.setLevel(loglvl)
    _logger.info("Started SPI scanning")

    for bus in spibus:
        if bus.CS_MUX:
            n_ports = 16
        else:
            n_ports = 5

        for cs in range(n_ports):
            max31865 = prove_max31865(bus, cs)
            if max31865:
                sensor = {"port": cs, "class": MAX31865, "check": True, "obj": max31865}
                bus.sensors.append(sensor)

    _logger.info("Sensors: %s", bus.sensors)
    return spibus


def get_min_frequency(sensor_classes):
    """
    Get minimum supported frequency from a list of sensor classes
    :param sensor_classes: list of sensor classes
    :returns: frequency that works for all sensors combined
    :rtype: float
    """
    freq = 3e6
    for sensor in sensor_classes:
        if sensor._i2c_freq < freq:
            freq = sensor._i2c_freq
    return freq


def scan_uart(port: str, measurement_obj=None, **kwargs):
    """"""

    if type(port) is not str:
        raise TypeError(
            "Uart in scan_uart is of type {type(uart)} but only str is supported"
        )

    # Setup Log
    if isinstance(port, list):
        log_id = f"Uart [{port}"
        for bus in port[1:]:
            log_id += f",{port}"
    else:
        log_id = f"Uart{port}"

    log_id += "]"

    _logger = logging.getLogger(log_id)

    if "loglvl" in kwargs:
        _logger.setLevel(kwargs["loglvl"])

    _logger.info("Started scanning")

    for uart_sensor in UART_SENSOR_CLASSES:
        # check if the sensor is connected
        if not os.path.exists(port):
            return None
        if uart_sensor(port, scan=True).sensor_exists():
            _logger.info(f"Found {uart_sensor.__name__}")
            # Progress update
            if measurement_obj is not None:
                measurement_obj.detected_sensors += 1
                measurement_obj.sensors_initialized += 1
                measurement_obj.save()
            else:
                _logger.debug("No update on a measurement object.")
            return uart_sensor(port)
        else:
            _logger.debug(f"No known {uart_sensor.__name__} @ {port}")

    _logger.info(f"No known device @ {port}")
    return None


def scan_i2c(
    i2cbus, measurement_obj=None, mux_address_list=None, loglvl: int = logging.ERROR
):
    """
    Searches a given i2cbus for supported sensors.
    :param i2cbus: [LIST] List of initialized I2C controllers
    :param i2cbus: [pyftdi.i2c.I2cController] initialized I2C controller
    :return: [LIST] a list of sensor [DICT] which have been found
    """

    # If i2cbus is not a list
    if type(i2cbus) is I2cController:
        i2cbus = [i2cbus]
    elif type(i2cbus) is not list:
        raise TypeError(
            f"i2cbus in scan_i2c is of type {type(i2cbus)} but only list \
                  and pyftdi.i2c.I2cController are supported"
        )

    log_id = f"I2Cscan[{i2cbus[0].ftdi._usb_dev.serial_number}"
    if len(i2cbus) > 1:
        for bus in i2cbus[1:]:
            log_id += f",{bus.ftdi._usb_dev.serial_number}"
    log_id += "]"

    _logger = logging.getLogger(log_id)
    _logger.setLevel(loglvl)

    _logger.info("Started scanning")

    min_supported_sensor_frequency = get_min_frequency(FTDI_SENSOR_CLASSES)
    _logger.info("Setting min. common frequency: %s", min_supported_sensor_frequency)

    for bus in i2cbus:
        bus.ftdi.set_frequency(min_supported_sensor_frequency)

    # Get MUX information for scan status reports

    # Get number of ports available in each multiplexer
    ports_per_mux = len(MUX.MUX_PORT_LIST)

    # Calculate number of ports needed to be scanned
    if mux_address_list is not None:
        number_of_ports_to_scan = len(mux_address_list) * ports_per_mux
    else:
        number_of_ports_to_scan = len(MUX.MUX_ADDRESS_LIST) * ports_per_mux

    # Report number of ports needed to be scanned to external
    if measurement_obj is not None:
        measurement_obj.total_ports += number_of_ports_to_scan
        measurement_obj.save()

    _logger.info("Starting MUX detection...")

    # Use poll to find all connected mux
    for bus in i2cbus:
        for mux_addr in MUX.MUX_ADDRESS_LIST:
            mux = MUX(bus, mux_addr, loglvl=loglvl)
            if mux.connected():
                # assign mux to the i2c bus
                bus.mux.append(mux)
    _logger.info("Finished MUX detection")

    _logger.info("Starting sensor polling...")
    # Use poll on all mux assigned to bus
    # to check, if a sensor is present

    # For all available busses
    min_detected_sensor_frequency = 3e6
    for bus in i2cbus:
        # For all multiplexers connected to a bus
        for mux in bus.mux:
            # for all ports available on a multiplexer
            for mux_port in mux.MUX_PORT_LIST:
                # open the multiplexer port
                mux.open_single_port(mux_port)
                # for all supported sensors

                # Progress update
                if measurement_obj:
                    measurement_obj.scanned_ports += 1
                    measurement_obj.save()

                for sensor in FTDI_SENSOR_CLASSES:
                    # check if the sensor is connected
                    if mux.poll(sensor._SENSOR_ADDRESS):
                        _logger.info(f"Found {sensor.__name__}")
                        s = sensor
                        if sensor._i2c_freq < min_detected_sensor_frequency:
                            min_detected_sensor_frequency = sensor._i2c_freq
                        mux.sensors.append(
                            {"port": mux_port, "class": s, "check": False, "obj": None}
                        )

                        # Progress update
                        if measurement_obj:
                            measurement_obj.detected_sensors += 1
                            measurement_obj.save()

    _logger.info("Finished sensor polling.")

    # Eventually speed up by setting FTDI
    # frequency to the maximum frequency supported by
    # the detected sensors
    _logger.info("Revisit clock frequency.")
    if min_detected_sensor_frequency != min_supported_sensor_frequency:
        _logger.info("Adjusting common frequency: %s", min_detected_sensor_frequency)
        for bus in i2cbus:
            bus.ftdi.set_frequency(min_detected_sensor_frequency)

    # Check if detected sensors are working
    # by retrieving (pseudo)-serial numbers
    _logger.info("Sensor validation")
    for bus in i2cbus:
        for mux in bus.mux:
            for sensor in mux.sensors:
                p = sensor["port"]
                s = sensor["class"](bus, mux, p, loglvl=loglvl)
                _logger.info(f"Checking {s}...")
                sensor["check"] = s.exists
                if sensor["check"]:
                    _logger.info(f"{s} initialized successfully.")
                    sensor["obj"] = s

                    # Progress update
                    if measurement_obj:
                        measurement_obj.sensors_initialized += 1
                        measurement_obj.save()
                else:
                    _logger.error(f"Failed to initialize {s}.")
        bus.init = True

    _logger.info("Finished sensor evaluation.")
    return i2cbus


def prove_max31865(spibus, cs):
    max31865_pt100 = MAX31865(spibus, cs)
    if max31865_pt100.exists():
        return max31865_pt100
    return False
