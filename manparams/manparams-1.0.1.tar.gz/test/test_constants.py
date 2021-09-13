from dataclasses import dataclass

from manparams.constants import unset


@dataclass
class Params:
    """Simulation params"""

    attr_none: int = None
    attr_set: int = 1
    attr_unset: int = unset


def test_unset_is_valid_type():
    params = Params()

    assert params.attr_unset is unset


def test_unset_can_be_replaced():
    params = Params(attr_unset=1)

    assert params.attr_unset is not unset
