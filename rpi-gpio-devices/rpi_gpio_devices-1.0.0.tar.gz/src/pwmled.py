from .base import PWMDevice


class PWMLED(PWMDevice):
    """ Control an LED with PWM signal

    -:param pin: The pin for output the PWM signal
    -:param frequency: Frequency used for the pwm signal (hz)
    """
    def __init__(self, pin, frequency=1000, **kwargs):
        super().__init__(power=False, pwm=pin, frequency=frequency, **kwargs)

    def set_brightness(self, percent):
        """ Set LED brightness

        -:param percent: Brightness between 0% and 100%
        """
        self.set_duty_cycle(percent)
