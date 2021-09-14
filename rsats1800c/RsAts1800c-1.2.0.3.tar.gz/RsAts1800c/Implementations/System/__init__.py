from ...Internal import Instrument
from typing import Tuple
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class System:
    """General System methods."""

    def __init__(self, io: Instrument):
        self._io = io

    def get_current_status(self) -> Tuple:
        """SCPI command: SYST:STAT? \n
        Queries the Azimuth and Elevation positions and movement status all in one command.
        Returns Tuple of: azimuth_pos, azimuth_movement, elevation_pos, elevation_movement"""
        response = self._io.query_str('SYST:STAT?')
        data = Conversions.str_to_str_list(response)
        azim_pos = Conversions.str_to_float(data[1])
        azim_mov = Conversions.str_to_bool(data[2])
        elev_pos = Conversions.str_to_float(data[4])
        elev_mov = Conversions.str_to_bool(data[5])

        feed_sw_pos = -1
        feed_sw_mov = False
        # Check if the feed switcher is also available
        if len(data) > 6:
            feed_sw_pos = Conversions.str_to_float(data[7])
            feed_sw_mov = Conversions.str_to_bool(data[8])
        return azim_pos, azim_mov, elev_pos, elev_mov, feed_sw_pos, feed_sw_mov

    def preset(self) -> None:
        """SCPI command: SYST:PRES \n
        Presets the instrument to the default settings:
        Azimuth:
        Velocity [°/s]: 20
        Acceleration [°/s2] 2000
        Deceleration [°/s2] 2000
        Jerk [°/s3] 7000
        StepSize [°] 10
        Custom offset [°] 0

        Elevation:
        Velocity [°/s]: 10
        Acceleration [°/s2] 400
        Deceleration [°/s2] 400
        Jerk [°/s3] 1000
        StepSize [°] 10
        Custom offset [°] 0
        """
        self._io.write('SYST:PRES')

    def wait_for_movements_finish(self) -> None:
        """SYST:STAT? \n
        Waits until the Azimuth, Elevation and Feed Switcher movement activities stop."""
        moving = True
        while moving:
            status = self.get_current_status()
            moving = status[1] or status[3] or status[5]

    def set_pos_system_power(self, state: bool) -> None:
        """CONT:SYST:APOW \n
        Sets the power state of the positioning system."""
        self._io.write_bool_as_int('CONT:SYST:APOW', state)

    def get_pos_system_power(self) -> bool:
        """CONT:SYST:APOW? \n
        Gets the power state of the positioning system."""
        return self._io.query_bool('CONT:SYST:APOW?')

    def set_dut_power(self, state: bool) -> None:
        """CONT:SYST:DUT:APOW \n
        Enables or disables the AC power socket for providing power to the DUT."""
        self._io.write_bool_as_int('CONT:SYST:DUT:APOW', state)

    def get_dut_power(self) -> bool:
        """CONT:SYST:DUT:APOW? \n
        Return's the state of the AC power socket providing power to the DUT."""
        return self._io.query_bool('CONT:SYST:DUT:APOW?')

    def get_temperature(self) -> str:
        """CONT:SYST:TEMP? \n
        Queries the current temperature of the chamber."""
        return self._io.query_str('CONT:SYST:TEMP?')

    def get_door_state(self) -> bool:
        """SYST:DOOR? \n
        Queries the chamber's door status. Returns True if the door is locked."""
        return self._io.query_bool('SYST:DOOR?')

    def start_fw_update(self) -> None:
        """SYST:WEB:FWUPDATE \n
        Starts an update of the chamber's firmware. As a prerequisite, a USB flash drive with a compatible installation file must be connected
        to the USB port [A412], labeled [SW Upd], at the lower rear of the chamber."""
        self._io.write('SYST:WEB:FWUPDATE')

    def reset_connection(self) -> None:
        """SYST:WEB:RST \n
        Resets the entire TCP/IP connection, including the browser-based user interface. Use this command, if the user interface is not loading.
        The execution of reset and startup typically takes up to 3 s. You get no feedback on sending this command."""
        self._io.write('SYST:WEB:RST')
