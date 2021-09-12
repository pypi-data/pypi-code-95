from .base import SwitchableDevice


class LED(SwitchableDevice):
    """ LED control

    -:param pin: The pin for control the LED
    """
    def __init__(self, pin, **kwargs):
        super().__init__(power=pin, **kwargs)
