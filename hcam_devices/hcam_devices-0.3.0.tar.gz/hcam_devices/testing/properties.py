import time


class SimulatedDeviceProperty(object):
    """
    A descriptor for access to a simulated property of a Device

    For example, one might wish to get or set the acceleration of a motor
    stage. There is a fair amount of boiler-plate code involved in getting
    or setting this property, but all that differs between them is the command
    code used and the units of the property.

    This is a perfect use of a Python descriptor
    """
    def __init__(self, name, initial, response_speed):
        """
        Parameters
        ----------
        initial : float
            initial value for property
        response_speed : float
            the rate at which property changes per second
        """
        self.name = name
        self._current_value = initial
        self._target_value = initial
        self._time_check = time.time()
        self._response_speed = response_speed

    def __get__(self, instance, cls):
        """
        In getter, we check when we last updated value and
        return the new value based on that
        """
        if instance is None:
            # called from class itself
            return self
        else:
            # called from class instance
            deltaT = time.time() - self._time_check
            value = deltaT * self._response_speed
            value = min(value, abs(self._target_value - self._current_value))
            if self._current_value - self._target_value > 0:
                value *= -1
            self._current_value += value
            self._time_check = time.time()
            return self._current_value

    def __set__(self, instance, value):
        # set value
        self._target_value = value
        # store the instance value
        instance.__dict__[self.name + '_target'] = value
        self._time_check = time.time()


class SimulatedIntegerDeviceProperty(SimulatedDeviceProperty):
    """
    An Device property that must be integer.
    """
    def __get__(self, instance, cls):
        value = super(SimulatedIntegerDeviceProperty, self).__get__(instance, cls)
        return int(value)

    def __set__(self, instance, value):
        super(SimulatedIntegerDeviceProperty, self).__set__(instance, int(value))


class SimulatedBooleanDeviceProperty(SimulatedDeviceProperty):
    """
    An Device property that must be integer.
    """
    def __get__(self, instance, cls):
        value = super(SimulatedBooleanDeviceProperty, self).__get__(instance, cls)
        return int(value)

    def __set__(self, instance, value):
        super(SimulatedBooleanDeviceProperty, self).__set__(instance, int(value))
