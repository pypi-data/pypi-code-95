# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Device Class for Qwiic Relay
This is library is for the SparkFun Qwiic Quad Relay.
"""
__copyright__ = "German Aerospace Center"
__author__ = ["Konstantin Niehaus"]
__credits__ = ["Gaston Williams"]
__license__ = "MIT"
__version__ = "0.1.0"
__email__ = "konstantin.niehaus [at] dlr.de"

# imports
import time
from ..core.error import Error
from ..core.sensor import I2CSensor

# private constants
# class
class QwiicQuadRelay(I2CSensor):
    """Class for the Sparkfun QwiicRelay"""

    __name__ = "QwiicQuadRelay"

    # default I2C Address
    _SENSOR_ADDRESS = 0x6D
    description = "4 channel i2c relay card"

    # Registers
    _RELAY_ALL_OFF = 0xA
    _RELAY_ALL_ON = 0xB
    _RELAY_OFF = 0x00
    _RELAY_ON = 0xF
    _RELAY_CHANGE_ADDRESS = 0x03
    _RELAY_NOTHING_NEW = 0x99
    _i2c_freq = 1e4
    _state = [0] * 4
    _units = {"relay": "-"}

    def __init__(self, *args, **kwargs):
        """Initialize Qwiic Relay for i2c communication."""
        super().__init__(*args, **kwargs)
        self.exists = self.sensor_exists()
        self.input_channels = {
            "ch01": self.single_channel,
            "ch02": self.single_channel,
            "ch03": self.single_channel,
            "ch04": self.single_channel,
            "all_on": self.all_on,
            "all_off": self.all_off,
        }

    def register(self):
        info = super().register()
        for ch in self.input_channels:
            if "ch" in ch:
                i = int(ch[2:]) - 1
                entry = {
                    "current": self._state[i],
                    "setpoint": self._state[i],
                    "channel_number": i,
                    "unit": "-",
                    "application": ch,
                    "channel_function": ch,
                }
                info["channel"].append(entry)

        entry = {
            "current": 0,
            "setpoint": 0,
            "channel_number": 4,
            "unit": "-",
            "application": "all",
            "channel_function": "all_on",
        }
        info["channel"].append(entry)
        entry = {
            "current": 0,
            "setpoint": 0,
            "channel_number": 5,
            "unit": "-",
            "application": "all",
            "channel_function": "all_off",
        }
        info["channel"].append(entry)
        print(info)

        return info

    def sensor_exists(self):
        """Check to see of the relay is available.  Returns True if successful."""
        d = self.txrx(self._RELAY_ALL_OFF)
        self._state = [0] * 4
        self.serial_number = f"{self.ftdi_serial}@{self.mux.address}/{self.mux_port}/{self._SENSOR_ADDRESS}"
        return True

    def all_on(self, ch, data):
        if data == 1:
            return self.all_channels("", 1)

    def all_off(self, ch, data):
        if data == 1:
            return self.all_channels("", 0)

    def all_channels(self, ch, data):
        if data == 1:
            for i in self._state:
                if i != 1:
                    self.txrx(self._RELAY_ALL_ON)
                    self._state = [1] * 4
                    break
        else:
            self.txrx(self._RELAY_ALL_OFF)
            self._state = [0] * 4

    def single_channel(self, ch, data):
        """Setting the status 1 turns relay on, 0 turns relay off."""
        # Get state index from key
        idx = int(ch[-1]) - 1
        # Check if state change is needed
        if self._state[idx] != data:
            self.txrx(idx + 1, readlen=0)
            self._state[idx] = data

    def update(self, entry):
        """
        Compatibility function
        """
        channels = entry.channel_set.all()
        all_off = channels.get(channel_function="all_off")
        all_on = channels.get(channel_function="all_on")
        # First check if all off is triggered
        print(int(all_on.setpoint) == 1)
        if int(all_off.setpoint) == 1:
            ch = all_off
            self.input_channels[ch.channel_function](ch.channel_function, ch.setpoint)
        # Second check if all on is triggered
        elif int(all_on.setpoint) == 1:
            ch = all_on
            self.input_channels[ch.channel_function](ch.channel_function, ch.setpoint)
        # Else control single channels
        else:
            for ch in channels.filter(channel_function__startswith="ch"):
                self.input_channels[ch.channel_function](
                    ch.channel_function, ch.setpoint
                )

    def set_data(self, data):
        for d in data:
            if d in self.input_channels:
                self.input_channels[d](d, data[d])
            else:
                self._logger.warning("Unknown command %s", d)

    def get_data(self):
        self.data = self.default_data()
        if self.error is not None:
            try:
                self.sensor_exists()
                self.error = None
            # TODO: Error type is just a place holder until it is known
            # what kinds of error to expect
            except TypeError:
                self.error = Error().read(self)
                self.data["object"] = "ERROR"
                return self.data

        for i, state in enumerate(self._state):
            self.data["values"][f"ch{i+1:02d}"] = {
                "value": state,
                "unit": self._units["relay"],
            }
        return self.data

    def set_i2c_address(self, new_address):
        """Change the i2c address of Relay snd return True if successful."""

        # check range of new address
        if new_address < 8 or new_address > 119:
            self._logger.error("ERROR: Address outside 8-119 range")
            return False

        # write new address
        self.txrx([self._RELAY_CHANGE_ADDRESS, new_address], readlen=0)

        # wait a second for relay to settle after change
        time.sleep(1)
        # try to re-create new i2c device at new address
        if not self.mux.poll(new_address):
            self._logger.error("Address Change Failure")
            return False

        # if we made it here, everything went fine
        return True
