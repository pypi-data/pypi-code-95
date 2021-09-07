# 1.0187707208460053e+00 3.2168693465909212e-02 4.0978586064750729e+01 4.1001997452143407e+01 9.3827000000000005e-01
# 1.0254104367327128e+00 -2.1977682486632854e-02 4.0980287617715881e+01 4.1003856811352591e+01 9.3827000000000005e-01
# 1.0290925649513989e+00 -1.0264105661284585e-03 4.0977975826623556e+01 4.1001632723600189e+01 9.3827000000000005e-01

import os
import unittest
from mcconv import detect_mc_type, apply_crossing_angle
from pyHepMC3 import HepMC3 as hm


class TestCrossingAngle(unittest.TestCase):

    def setUp(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(dir_path, 'data')

    def _get_file_path(self, path):
        """Gets data file path"""
        return os.path.join(self.data_path, path)


    def test_crossing_angle(self):
        """Test detecting BeaGLE file type"""

        evt = hm.GenEvent(hm.Units.GEV, hm.Units.MM)
        v1 = hm.GenVertex(hm.FourVector(1, 2, 3, 4))
        evt.add_vertex(v1)
        p1 = hm.GenParticle(hm.FourVector(0, 0, 40, 40), 2212, 1)
        evt.add_particle(p1)
        p2 = hm.GenParticle(hm.FourVector(0, 0, 5, 5), 11, 1)
        evt.add_particle(p2)
        v1.add_particle_in(p1)
        v1.add_particle_out(p2)

        apply_crossing_angle(0, evt, {"cross_angle": -25/1000.0})
        self.assertAlmostEqual(1, evt.particles()[0].momentum().x(), 3)
