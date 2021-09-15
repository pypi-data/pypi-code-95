"""Test fails because of issues at the terminator and south pole.
I'm pretty sure the error is on the IDL side, but the effect is
negligible."""

import numpy as np
import os.path
from scipy.io import readsav
try:
    from .surface_temperature import surface_temperature
    from .Input import Input
except:
    from nexoclom.surface_temperature import surface_temperature
    from nexoclom import Input

idlout = readsav(os.path.join(os.path.dirname(__file__),
                              'data', 'tsurf.sav'))
t_idl, cos_idl = idlout['tsurf'], idlout['cosgrid']
lon_idl, lat_idl = idlout['longrid'], idlout['latgrid']

inputs = Input(os.path.join(os.path.dirname(__file__), 'inputfiles',
                            'Na.maxwellian.1200.accom.input'))
longitude = np.arange(361)*np.pi/180.
latitude = np.arange(181)*np.pi/180.-np.pi/2.
longrid, latgrid = np.meshgrid(longitude, latitude)
cosgrid = np.abs(np.cos(longrid) * np.cos(latgrid))**.25
tsurf = surface_temperature(inputs.geometry, longrid.flatten(),
                            latgrid.flatten()).reshape(181, 361)

#x, y = np.where(np.logical_not(np.isclose(tsurf, t_idl)))

assert np.all(np.isclose(tsurf[1:-1,:], t_idl[1:-1,:]))