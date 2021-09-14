# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Example script for running a measurement using i2c senors only.
"""

import argparse
import time
import logging
from pySerialMeasurement.devices.FTDI import init_all_i2c, UM232H
from pySerialMeasurement.tools.bulk import setup, ThreadWithReturnValue

# logging.basicConfig(level=logging.DEBUG)


def runMeasurement(setup, n):
    for dev in setup:
        for mux in dev.mux:
            for sensor in mux.sensors:
                val = sensor["obj"].prepare_measurement()

    for dev in setup:
        for mux in dev.mux:
            for sensor in mux.sensors:
                val = sensor["obj"].get_data()
                out = f"{val['sensor_type']: >10}"
                if val["serialno"] is None:
                    out += f"{'': >20}"
                else:
                    out += f"{val['serialno']: >20}"
                results = [0] * len(val["values"])
                units = []
                for i in range(n):
                    val = sensor["obj"].get_data()
                    if "values" in val:
                        for i, value in enumerate(val["values"]):
                            res = val["values"][value]["value"]
                            results[i] += res / float(n)
                            if len(units) != len(val["values"][value]["unit"]):
                                units.append(val["values"][value]["unit"])
                    else:
                        out += "Reding error"
                for i, res in enumerate(results):
                    res_str = f"{res:0.4g} {units[i]}"

                print(f"{out} {res_str: >20}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculates mean value of all connected sensors."
    )
    parser.add_argument(
        "samples", metavar="n", type=int, help="Number of samples for mean calculation."
    )
    args = parser.parse_args()
    n = args.samples

    log = logging.getLogger("exampleThreading")
    Bus = []
    setups = []

    # Check how many serial converters are connected
    supported_converters = [(0x0403, 0x6014)]
    dev = init_all_i2c(supported_converters)

    t0_threaded = time.time()
    log.info("Found %s FTDI", len(dev))
    for d in dev:
        bus = UM232H(serial=d).i2c()[d]
        Bus.append(bus)

    threads = []
    for bus in Bus:
        j = ThreadWithReturnValue(target=setup, args=(bus,))
        j.start()
        threads.append(j)
    for t in threads:
        setups.append(t.join())

    threads = []
    if len(setups) > 0:
        for s in setups:
            j = ThreadWithReturnValue(target=runMeasurement, args=(s, n))
            j.start()
            threads.append(j)

    for t in threads:
        j.join()
    t1_threaded = time.time()
