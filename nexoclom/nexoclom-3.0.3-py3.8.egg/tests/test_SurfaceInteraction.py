import numpy as np
import os.path
from scipy.io import readsav
try:
    from .SurfaceInteraction import SurfaceInteraction
    from .Input import Input
except:
    from nexoclom.SurfaceInteraction import SurfaceInteraction
    from nexoclom import Input

def test_SurfaceInteraction():
    idlout = readsav(os.path.join(os.path.dirname(__file__),
                                  'data', 'emit.sav'))
    emit_idl = idlout['emit']
    vgrid_idl = emit_idl['vgrid'][0].transpose()
    prob_idl = emit_idl['probability'][0]
    temp_idl = emit_idl['temperature'][0]


    inputs = Input('inputfiles/Na.maxwellian.1200.accom.input')
    emit_py = SurfaceInteraction(inputs, nt=21, nv=101, nprob=101)

    assert np.all(np.isclose(emit_py.temperature.value, temp_idl))
    assert np.all(np.isclose(emit_py.probability, prob_idl))
    assert np.all(np.isclose(emit_py.probgrid, vgrid_idl))

    # import matplotlib.pyplot as plt
    # plt.plot(emit_py.probability, emit_py.probgrid[0,:])
    # plt.plot(prob_idl, vgrid_idl[0,:])
    # plt.show()