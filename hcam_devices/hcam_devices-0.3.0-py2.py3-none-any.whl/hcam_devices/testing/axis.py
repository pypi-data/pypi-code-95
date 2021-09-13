import time


class AxisEmulator(object):
    """
    Simple class to emulate a moving stage
    """
    def __init__(self, speed):
        # units of microsteps
        self.home_position = 0
        self._current_position = 0
        self._target_position = 0
        self.moving = False
        self.speed = speed

    @property
    def current_position(self):
        if not self.moving:
            return self._current_position

        deltaT = time.time() - self._time_check
        value = abs(int(deltaT * self.speed))

        if value > abs(self._target_position - self._current_position):
            value = abs(self._target_position - self._current_position)
            self.moving = False

        if self._current_position > self._target_position:
            value *= -1

        self._current_position += value
        self._time_check = time.time()
        return int(self._current_position)

    @property
    def target_position(self):
        return self._target_position

    @target_position.setter
    def target_position(self, value):
        if value != self.current_position:
            self._target_position = int(value)
            self._time_check = time.time()
            self.moving = True
