#!/usr/bin/env python
# pylint: disable=C0326,W1202,C0111
"""
Pymodbus Synchronous Server Example
--------------------------------------------------------------------------

The synchronous server is implemented in pure python without any third
party libraries (unless you need to use the serial protocols which require
pyserial). This is helpful in constrained or old environments where using
twisted just is not feasable. What follows is an examle of its use:
"""
# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
import threading
import logging
from pymodbus.server.sync import StartTcpServer, ModbusTcpServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

NUMBER_OF_REGS_AND_COILS = 100


class ModbusTCPServer(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.setDaemon(True)
        self.server = None

    def run(self):

        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0, 0, 1, 1, 0, 0, 1, 1],),
            co=ModbusSequentialDataBlock(0, [0, 0, 1, 1, 0, 0, 1, 1]),
            hr=ModbusSequentialDataBlock(0, [i for i in range(100)]),
            ir=ModbusSequentialDataBlock(0, [i for i in range(100)]),
            zero_mode=True
            )

        for key, value in store.store.items():
            log.debug('number of coils/registers in {}: {}'.format(key, len(value.values)))

        context = ModbusServerContext(slaves=store, single=True)

        identity = ModbusDeviceIdentification()
        identity.VendorName = 'Pymodbus'
        identity.ProductCode = 'PM'
        identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
        identity.ProductName = 'Pymodbus Server'
        identity.ModelName = 'Pymodbus Server'
        identity.MajorMinorRevision = '1.5'

        self.server = ModbusTcpServer(context, identity=identity, address=("localhost", 5020))
        log.info("starting modbus tcp server [localhost:5020]: {}".format(self.server))
        self.server.serve_forever()



if __name__ == "__main__":
    server = ModbusTCPServer()
    server.start()
    server.join()

