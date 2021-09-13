import time
import numpy as np


class SensorEmulator(object):
    """
    Simple class to emulate a device sensor

    Noise is added as a Gaussian Random Walk
    """
    def __init__(self, initial_value, response_speed, noise):
        self._current = initial_value
        self._target = initial_value
        self.speed = response_speed
        self.noise = noise
        self._time_check = time.time()

    @property
    def current_value(self):
        deltaT = time.time() - self._time_check
        value = abs((deltaT * self.speed))
        if value > abs(self._target - self._current):
            value = abs(self._target - self._current)

        if self._current > self._target:
            value *= -1

        self._current += value + np.random.normal(0, self.noise)
        self._time_check = time.time()
        return self._current

    @property
    def target_value(self):
        return self._target

    @target_value.setter
    def target_value(self, value):
        self._time_check = time.time()
        self._target = value
