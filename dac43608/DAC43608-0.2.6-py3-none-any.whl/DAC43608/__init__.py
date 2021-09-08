# -*- coding: utf-8 -*-
from typing import NewType, Tuple, TypeVar
import busio
import board
from adafruit_bus_device.i2c_device import I2CDevice

Register = NewType("Register", int)
Channel = NewType("Channel", Register)
Bytes2_or_Tuple2 = TypeVar("Bytes2_or_Tuple2", Tuple[int, int], bytes)
Float_0_to_1 = TypeVar("Float_0_to_1", bound=float)


class DAC43608:

    # DAC43608 Command Byte
    # Controls which command is executed and which is being accessed.
    _DEVICE_CONFIG = Register(1)
    _STATUS = Register(2)
    _BRDCAST = Register(3)
    A = Channel(Register(8))
    B = Channel(Register(9))
    C = Channel(Register(10))
    D = Channel(Register(11))
    E = Channel(Register(12))
    F = Channel(Register(13))
    G = Channel(Register(14))
    H = Channel(Register(15))

    def __init__(self, address: int = 0x49):
        comm_port = busio.I2C(board.SCL, board.SDA)
        self.i2c = I2CDevice(comm_port, address)

    def power_up_all(self):
        # sets all channels to their registered value (default is 1 if nothing is in the register, i.e. maximum)
        self.write_config((0x00, 0x00))

    def power_up(self, channel: Channel):
        """
        Turn on the output to its register value

        Parameters
        -----------

        channel: int
           an int between 8 to 15, aka, a `DAC43608.X` value


        Notes
        --------
        The on-off state is represented by 8 bits in the config, 1 being off, 0 being on.
        We bit-flip the channel we want, so if the config is

        11111110

        ie channel A is on, but we want to also turn channel C on, so our desired state is

        11111010

        """

        # this needs to first read the current state of the config, and then make the modification
        current_config = self.read_config()[1]

        new_config = ~((~current_config) | 1 << (channel - 8))

        self.write_config([0x00, new_config])

    def power_down_all(self):
        """
        power down all outputs by setting the PDN-All config input to 1
        """
        self.write_config([0x01, 0xFF])

    def power_down(self, channel: Channel):
        """
        Turn off the output

        Parameters
        -----------

        channel: int
           an int between 8 to 15, aka, a `DAC43608.X` value


        Notes
        --------
        The on-off state is represented by 8 bits in the config, 1 being off, 0 being on.
        We bit-flip the channel we want to turn off, so if the config is

        11111110

        ie channel A is on, but we want to turn it off:

        11111111

        """

        current_config = self.read_config()[1]

        new_config = current_config | (1 << (channel - 8))
        self.write_config([0x00, new_config])

    def set_intensity_to(self, channel: Channel, fraction: Float_0_to_1):
        """
        Set the output to a fraction of the maximum output. This only set it's in the register, you
        still need to power up the channel using `power_up`. This can happen before or after the register is
        populated.

        Parameters
        -----------

        channel: int
           an int between 8 to 11, aka, a `DAC43608.X` value
        fraction: float
           a float between 0 to 1, representing how much of the total maximum current
           to release.
        """

        assert 0 <= fraction <= 1, "must be between 0 and 1 inclusive."

        # really, the only difference between DAC43608 and DAC53608 is that
        # SHIFT = 2 and SPAN = 1023
        SPAN = 255
        SHIFT = 4
        target = round(SPAN * fraction)
        self.write_dac(
            channel, (target << SHIFT).to_bytes(2, "big")
        )  # this is a length 2 bytes, which can be *'ed
        return

    ### low level API

    def read_config(self) -> bytearray:
        write_buffer = bytearray([self._DEVICE_CONFIG])
        read_buffer = bytearray(2)
        self.i2c.write_then_readinto(write_buffer, read_buffer)
        return read_buffer

    def write_dac(self, command: Register, data: Bytes2_or_Tuple2):
        buffer_ = bytearray([command, *data])
        self.i2c.write(buffer_)
        return

    def write_config(self, config_bytes):
        self.write_dac(self._DEVICE_CONFIG, config_bytes)
        return

    def write_dac_A(self, DACn_DATA: Bytes2_or_Tuple2):
        """
        DACn_DATA is an iterable of two bytes/integers, ex: [0x08, 0x04] or [15, 20]
        """
        self.write_dac(self.A, DACn_DATA)
        return

    def write_dac_B(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.B, DACn_DATA)
        return

    def write_dac_C(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.C, DACn_DATA)
        return

    def write_dac_D(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.D, DACn_DATA)
        return

    def write_dac_E(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.E, DACn_DATA)
        return

    def write_dac_F(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.F, DACn_DATA)
        return

    def write_dac_G(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.G, DACn_DATA)
        return

    def write_dac_H(self, DACn_DATA: Bytes2_or_Tuple2):
        self.write_dac(self.H, DACn_DATA)
        return
