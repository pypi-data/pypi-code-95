from ...Internal import Instrument
from time import sleep
from ...enums import MovementDirection


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Azimuth:
    """Methods for the Azimuth axis control"""

    def __init__(self, io: Instrument):
        self._io = io

    @property
    def step_movement(self):
        """Commands for azimuth step movement"""
        if not hasattr(self, '_stepMovement'):
            from .StepMovement import StepMovement
            self._stepMovement = StepMovement(self._io)
        return self._stepMovement

    @property
    def trigger_output(self):
        """Commands for azimuth trigger output control"""
        if not hasattr(self, '_triggerOutput'):
            from .TriggerOutput import TriggerOutput
            self._triggerOutput = TriggerOutput(self._io)
        return self._triggerOutput

    def set_target_value(self, target: float) -> None:
        """CONT:AZIM:POS:TARG \n
        Sets the target position in degrees for the next movement of the azimuth axis (turntable).
        Range: -181 to 181"""
        self._io.write_int('CONT:AZIM:POS:TARG', target)

    def set_speed(self, speed: int) -> None:
        """CONT:AZIM:SPE \n
        Sets the speed in degrees per second (°/s).
        Values below 0 or above the maximum limit are merged automatically to the minimum or maximum limit, respectively.
        We recommend a maximum azimuth speed of 70°/s for stepped measurement and 50°/s for hardware triggered measurement, or lower speeds for heavy DUTs.
        Range: 1 to 150"""
        self._io.write_int('CONT:AZIM:SPE', speed)

    def set_acceleration(self, acc: int) -> None:
        """CONT:AZIM:ACC \n
        Sets the acceleration in degrees per second squared (°/s2).
        Values below 0 or above the maximum limit are merged automatically to the minimum or maximum limit, respectively. We recommend a maximum azimuth acceleration of 2000°/s2.
        Range: 1 to 15000"""
        self._io.write_int('CONT:AZIM:ACC', acc)

    def set_offset(self, offset: float) -> None:
        """CONT:AZIM:OFFS \n
        Configures the offset for the Azimuth axis.
        Range: -180 to 180"""
        self._io.write_float('CONT:AZIM:OFFS', offset)

    def get_current_position(self) -> float:
        """SENS:AZIM:POS? \n
        Queries the current Azimuth position."""
        return self._io.query_float('SENS:AZIM:POS?')

    def get_current_activity(self) -> bool:
        """SENS:AZIM:BUSY? \n
        Queries the current Azimuth activity and returns True, if the axis is moving."""
        return self._io.query_bool('SENS:AZIM:BUSY?')

    def start_movement(self) -> None:
        """CONT:AZIM:STAR \n
        Starts the Azimuth movement and stops when it reaches the desired position.
        The method does not wait for the azimuth to reach the desired position. For that purpose, you can use the method start_and_wait()"""
        self._io.write('CONT:AZIM:STAR')

    def stop_movement(self) -> None:
        """CONT:AZIM:STOP \n
        Stops the Azimuth movement."""
        self._io.write('CONT:AZIM:STOP')

    def wait_for_movement_finish(self) -> None:
        """SENS:AZIM:BUSY? \n
        Waits until the Azimuth movement activity stops."""
        while self.get_current_activity():
            sleep(0.010)

    def start_cont_movement(self, direction: MovementDirection) -> None:
        """CONT:AZIM:VELO:STAR POS|NEG \n
        Starts the movement of the Azimuth in the desired direction and stop on the limit."""
        assert isinstance(direction, MovementDirection), f'input variable "direction", value {direction} is not of enums.MovementDirection type'
        cmd = 'CONT:AZIM:VELO:STAR '
        if direction == MovementDirection.POSitive:
            cmd += 'POS'
        elif direction == MovementDirection.NEGative:
            cmd += 'NEG'
        self._io.write(cmd)
