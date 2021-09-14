# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Example script for running a measurement using i2c senors only.
"""

from ..devices.FTDI import init_all
from ..tools.bulk import setup, ThreadWithReturnValue
from ..core.i2controller import MmsI2cController
from ..core.i2controller import MmsSpiController

import logging

logging.basicConfig(level=logging.DEBUG)


def reinitialize(dev):
    for m in dev.mux:
        for s in m.sensors:
            if s["obj"] is not None:
                s["obj"].prepare_measurement()


def runMeasurement(setup, log):
    for dev in setup:
        if isinstance(dev, MmsI2cController):
            for mux in dev.mux:
                for sensor in mux.sensors:
                    if sensor["obj"] is not None:
                        val = sensor["obj"].prepare_measurement()
        elif isinstance(dev, MmsSpiController):
            for sensor in dev.sensors:
                val = sensor["obj"].prepare_measurement()

    for i in range(3000):
        for dev in setup:
            if isinstance(dev, MmsI2cController):
                for mux in dev.mux:
                    for sensor in mux.sensors:
                        sensor = sensor["obj"]
                        val = sensor.get_data()
                        if sensor.disconnected_ftdi:
                            # if a ftdi disconnected all
                            # sensors have to be reinitialized
                            for m in dev.mux:
                                for s in mux.sensors:
                                    if s["obj"] is not None:
                                        s["obj"].prepare_measurement()
                            sensor.disconnected_ftdi = False
                        sn = sensor.serial_number

                        out = f"{val['sensor_type']: >10}"
                        if val["SENSORserial"] is None:
                            out += f"{'': >20}"
                        else:
                            out += f"{val['SENSORserial']: >20}"
                        if "values" in val:
                            for value in val["values"]:
                                v = val["values"][value]["value"]
                                u = val["values"][value]["unit"]
                                res = f"{v: 0.2f} {u}"
                                out += f"{res: >20}"
                        else:
                            out += "Reading error"
                        log.info(out)

            elif isinstance(dev, MmsSpiController):
                for sensor in dev.sensors:
                    val = sensor["obj"].get_data()
                    out = f"{val['sensor_type']: >10}"

                    if val["SENSORserial"] is None:
                        out += f"{'': >20}"
                    else:
                        out += f"{val['SENSORserial']: >20}"
                    if "values" in val:
                        for qty in val["values"]:
                            if val["values"][qty]["value"] is not None:
                                v = val["values"][qty]["value"]
                                u = val["values"][qty]["unit"]
                                res = f"{v: 0.2f} {u}"
                                out += f"{res: >20}"
                            else:
                                out += "\t Reading error"
                        log.info(out)


if __name__ == "__main__":
    fmt = "%(asctime)s | %(levelname)s | %(message)s"
    loglvl = logging.INFO
    logging.basicConfig(format=fmt, level=loglvl)
    log = logging.getLogger()
    hdl = log.handlers[0].setFormatter(logging.Formatter(fmt))
    Bus = []
    setups = []
    CS_MUX = False

    # Check how many serial converters are connected
    supported_converters = [(0x0403, 0x6014)]
    dev = init_all(supported_converters, CS_MUX=CS_MUX)

    log.info("Found %s FTDI", len(dev))
    for d in dev:
        Bus.append(d)

    threads = []
    for bus in Bus:
        j = ThreadWithReturnValue(target=setup, args=(bus,), kwargs={"loglvl": loglvl})
        j.start()
        threads.append(j)

    for t in threads:
        setups.append(t.join())
    threads = []
    if len(setups) > 0:
        for s in setups:
            if s is not None:
                j = ThreadWithReturnValue(target=runMeasurement, args=(s, log))
                j.start()
                threads.append(j)
    else:
        raise SystemError("No FTDI found.")

    for t in threads:
        setups.append(t.join())
