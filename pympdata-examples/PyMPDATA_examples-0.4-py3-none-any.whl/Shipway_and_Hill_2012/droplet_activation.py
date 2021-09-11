import numba
from functools import lru_cache
from PyMPDATA.arakawa_c.enumerations import SIGN_RIGHT, INVALID_HALO_VALUE, ARG_DATA, OUTER, ARG_FOCUS
import numpy as np


@lru_cache()
def _make_scalar(value, at, halo, dr, dz):

    @numba.njit()
    def fill_halos(psi, n, sign):
        if sign == SIGN_RIGHT:
            return 0
        z = psi[ARG_FOCUS][OUTER]
        activated = np.sum(psi[ARG_DATA][z:z+1, halo:-halo])
        # assert activated < value
        result = max(0, value - activated)
        return result

    return fill_halos

    @lru_cache()
    def _make_vector(at):
        @numba.njit()
        def fill_halos(psi, n, sign):
            return 0
        return fill_halos

class DropletActivation:
    def __init__(self, value, dr, dz):
        self._value = value / dz / dr
        self.dz = dz
        self.dr = dr

    def make_scalar(self, _at, _halo):
        return _make_scalar(self._value, _at, _halo, self.dr, self.dz)

    def make_vector(self, at):
        return DropletActivation(self._value, self.dr, self.dz).make_vector(at)
