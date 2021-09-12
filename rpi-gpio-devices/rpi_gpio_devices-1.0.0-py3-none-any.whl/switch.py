from .base import SwitchableDevice


class Switch(SwitchableDevice):
    """ A simple switch

    -:param pin: The pin for control the switch
    """
    def __init__(self, pin, **kwargs):
        super().__init__(power=pin, **kwargs)
