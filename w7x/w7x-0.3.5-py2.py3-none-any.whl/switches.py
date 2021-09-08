"""
Global switches
"""
from rna.pattern.switch import Switch
from rna.pattern.link import exposed  # noqa:F401


# pylint:disable=invalid-name
class distribute(Switch):
    """
    Global switch for the use of distributed computing
    """

    ENABLED = False


# pylint:disable=invalid-name
class stateful(Switch):
    """
    Global switch for the use of graph wrappers
    """
