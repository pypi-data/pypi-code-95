from pystrict import strict
from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp
from .formulae import si, Formulae, const
import numpy as np
from .arakawa_c import arakawa_c
from typing import Optional
from PyMPDATA_examples.Olesik_et_al_2020.settings import ksi_1 as default_ksi_1


@strict
class Settings:
    def __init__(self, dt: float, dz: float, w_1: float, t_max: float = 15 * si.minutes, nr: int = 1,
                 r_min: float = np.nan, r_max: float = np.nan, p0: Optional[float] = None,
                 ksi_1: float = default_ksi_1.to_base_units().magnitude,
                 z_max: float = 3000 * si.metres):
        self.dt = dt
        self.dz = dz

        self.nr = nr
        self.ksi_1 = ksi_1

        self.z_max = z_max
        self.t_max = t_max

        self.qv = interp1d((0, 740, 3260), (.015, .0138, .0024))
        self._th = interp1d((0, 740, 3260), (297.9, 297.9, 312.66))

        # note: not in the paper, https://github.com/BShipway/KiD/blob/bad81aa6efa4b7e4743b6a1867382fc74c10a884/src/physconst.f90#L43
        p0 = p0 or 1000 * si.hPa

        self.rhod0 = Formulae.rho_d(p0, self.qv(0), self._th(0))
        self.thd = lambda z: Formulae.th_dry(self._th(z), self.qv(z))

        def drhod_dz(z, rhod):
            T = Formulae.T(rhod[0], self.thd(z))
            p = Formulae.p(rhod[0], T, self.qv(z))
            return Formulae.drho_dz(const.g, p, T, self.qv(z), const.lv)

        z_points = np.arange(0, self.z_max + self.dz / 2, self.dz / 2)
        rhod_solution = solve_ivp(
            fun=drhod_dz,
            t_span=(0, self.z_max),
            y0=np.asarray((self.rhod0,)),
            t_eval=z_points
        )
        assert rhod_solution.success

        self.rhod = interp1d(z_points, rhod_solution.y[0])

        self.t_1 = 600 * si.s
        self.w = lambda t: w_1 * np.sin(np.pi * t / self.t_1) if t < self.t_1 else 0

        self.r_min = r_min
        self.r_max = r_max
        self.bin_boundaries, self.dr = np.linspace(
            self.r_min,
            self.r_max,
            self.nr + 1, retstep=True
        )

        self.dr_power = {}
        for k in (1, 2, 3, 4):
            self.dr_power[k] = self.bin_boundaries[1:] ** k - self.bin_boundaries[:-1] ** k
            self.dr_power[k] = self.dr_power[k].reshape(1, -1).T

        self.z_vec = self.dz * arakawa_c.z_vector_coord((self.nz,))

    @property
    def nz(self):
        nz = self.z_max / self.dz
        assert nz == int(nz)
        return int(nz)

    @property
    def nt(self):
        nt = self.t_max / self.dt
        assert nt == int(nt)
        return int(nt)
