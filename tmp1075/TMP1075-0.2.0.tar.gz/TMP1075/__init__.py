import busio
import board
from adafruit_bus_device.i2c_device import I2CDevice


class TMP1075:
    """
    Driver for the TI TMP1075 temperature sensor.
    See datasheet: http://www.ti.com/lit/ds/symlink/tmp1075.pdf

    """

    def __init__(self, address: int=0x4f):
        # Could check that addr is one of the valid values...
        comm_port = busio.I2C(board.SCL, board.SDA)
        self.i2c = I2CDevice(comm_port, address)

    def get_temperature(self) -> float:
        b = bytearray(2)
        self.i2c.readinto(b)
        return ((b[0] << 4) + (b[1] >> 4)) * 0.0625