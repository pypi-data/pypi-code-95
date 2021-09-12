"""
09/21, R James, F Alder
"""

import numpy as np
import time
import os

import PyRPStream as rp
export, __all__ = rp.exporter()


@export
class BinaryDecoder:
    """
    """
    def __init__(self, name, ignore_calib=False):
        # Device name
        self.name = name
        # Calibration parameters
        if os.path.isfile(self.name + '_calib.txt') and not ignore_calib:
            file = open(self.name + '_calib.txt', 'r')
            calib_consts = file.readlines()
            self.ch1_offset = float(calib_consts[0])
            self.ch1_gain = float(calib_consts[1])
            self.ch2_offset = float(calib_consts[2])
            self.ch2_gain = float(calib_consts[3])
        else:
            self.ch1_offset = 0
            self.ch1_gain = 1
            self.ch2_offset = 0
            self.ch2_gain = 1


    def decode_file(channel, timestamp):
        """
        """
        try:
            assert(channel == 1 or 2)
        except:
            raise ValueError('Invalid channel value (must be 1 or 2)')

        try:
            assert(timestamp > 0)
        except:
            raise TypeError('Invalid timestamp value')

        if channel == 1:
            filename = 'red_pitaya_data_ch1_' + f'{timestamp}' + '.bin'
        elif channel == 2:
            filename = 'red_pitaya_data_ch2_' + f'{timestamp}' + '.bin'

        try:
            assert os.path.isfile(filename)
        except:
            raise OSError('Data at specified timestamp and channel does not exist')

        data_btyes = np.loadtxt(filename)

        data_decoded = np.frombuffer(data_bytes, dtype=np.int16)

        print(data_decoded)
        # ch1_data_calib = self.ch1_gain * (ch1_data_no_calib  * self.input_range_V / 2 ** self.input_bits + self.ch1_offset)
