from ...Internal import Instrument
from time import sleep


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FeedSwitcher:
    """Methods for the FeedSwitcher motor's control"""

    def __init__(self, io: Instrument):
        self._io = io

    def set_power(self, state: bool) -> None:
        """CONT:FESW:APOW \n
        Sets the power of the feed switcher's motor module."""
        self._io.write_bool_as_int('CONT:FESW:APOW', state)

    def get_power(self) -> bool:
        """CONT:FESW:APOW? \n
        Queries the power of the feed switcher's motor module."""
        return self._io.query_bool('CONT:FESW:APOW?')

    def get_current_position(self) -> int:
        """SENS:FESW:POS? \n
        Queries the number of the feed antenna that is located in the center position of the feed switcher and ready to measure."""
        return self._io.query_int('SENS:FESW:POS?')

    def set_target_position(self, feed_antenna: int) -> None:
        """CONT:FESW:POS:TARG \n
        Selects the feed antenna to be moved to the center position by the feed switcher. Start the antenna movers by the method start_movement.
        The movement stops automatically, when the selected feed antenna has reached its target position in the center of the feed switcher,
        or you can stop the movement with the method stop_movement()."""
        self._io.write_int('CONT:FESW:POS:TARG', feed_antenna)

    def get_current_activity(self) -> bool:
        """SENS:FESW:BUSY? \n
        Queries the current activity state of the feed switcher. Only start a measurement when the feed switcher is not busy anymore."""
        return self._io.query_bool('SENS:FESW:BUSY?')

    def start_movement(self) -> None:
        """CONT:FESW:STAR \n
        Starts the movement of the feed switcher's antenna movers to enable the selected feed antenna; see set_target_position()."""
        self._io.write('CONT:FESW:STAR')

    def stop_movement(self) -> None:
        """CONT:FESW:STOP \n
        Stops the movement of the feed switcher."""
        self._io.write('CONT:FESW:STOP')

    def wait_for_movement_finish(self) -> None:
        """SENS:FESW:BUSY? \n
        Waits until the Feed Switcher movement activity stops."""
        while self.get_current_activity():
            sleep(0.010)
