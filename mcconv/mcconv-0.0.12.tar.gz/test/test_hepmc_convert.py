from mcconv import GenericTextReader, UnparsedTextEvent, hepmc_convert

import os
import unittest
from mcconv import detect_mc_type, McFileTypes
from pyHepMC3 import HepMC3 as hm


class TestGenericTextReader(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def _data_path(self, file_name):
        """Gets data file path"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, 'data', file_name)

    def _tmp_path(self, file_name):
        """Gets output temporary file path"""

        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp', file_name)

    def test_convert_lund_gemc(self):
        """Test detecting BeaGLE file type"""

        # Beam particles in px, py, pz, e, pid
        beams = [
            (0, 0, -5., 5., 11),
            (0, 0, 110., 110., 2212),
        ]

        hepmc_convert(self._data_path('gemc-lund.3evt.txt'),
                      self._tmp_path('lund-convert.hepmc'),
                      McFileTypes.LUND_GEMC,
                      beam_particles=beams)

        inputA = hm.ReaderAscii(self._tmp_path('lund-convert.hepmc'))
        if inputA.failed():
            raise "inputA.failed()"

        evt = hm.GenEvent()
        inputA.read_event(evt)
        vtx: hm.GenVertex = evt.vertices()[0]
        particle: hm.GenParticle = vtx.particles_out()[0]
        self.assertAlmostEqual(-4.457052e+00, particle.momentum().px())
        self.assertAlmostEqual(-3.140872e+00, particle.momentum().py())
        self.assertAlmostEqual(-9.044077e+00, particle.momentum().pz())
        self.assertEqual(11, particle.pid())

        # check 1st beam particle
        beam_particle_one: hm.GenParticle = vtx.particles_in()[0]
        self.assertAlmostEqual(0, beam_particle_one.momentum().px())
        self.assertAlmostEqual(0, beam_particle_one.momentum().py())
        self.assertAlmostEqual(-5, beam_particle_one.momentum().pz())
        self.assertEqual(11, beam_particle_one.pid())

        beam_particle_two: hm.GenParticle = vtx.particles_in()[1]
        self.assertAlmostEqual(0, beam_particle_two.momentum().px())
        self.assertAlmostEqual(0, beam_particle_two.momentum().py())
        self.assertAlmostEqual(110, beam_particle_two.momentum().pz())
        self.assertEqual(2212, beam_particle_two.pid())

        # Read the 2nd event
        evt.clear()
        inputA.read_event(evt)
        # gemc lund doesn't provide event number, so it should be io event number (io event)
        self.assertEqual(evt.event_number(), 1, "event number should be 1 as it is second event in file")

        evt.clear()
        inputA.close()


    def test_convert_py6_eic(self):
        """Test detecting BeaGLE file type"""
        hepmc_convert(self._data_path('pythia6-radcor-10evt.txt'),
                      self._tmp_path('pythia6-radcor-10evt.hepmc'),
                      McFileTypes.UNKNOWN, "hepmc2")

        inputA = hm.ReaderAsciiHepMC2(self._tmp_path('pythia6-radcor-10evt.hepmc'))
        if inputA.failed():
            raise "inputA.failed()"

        evt = hm.GenEvent()
        inputA.read_event(evt)
        vtx: hm.GenVertex = evt.vertices()[0]
        particle: hm.GenParticle = vtx.particles_out()[0]

        self.assertAlmostEqual(-0.000341, particle.momentum().px())
        self.assertAlmostEqual(0.000687, particle.momentum().py())
        self.assertAlmostEqual(-9.711257, particle.momentum().pz())
        self.assertEqual(11, particle.pid())

        # check 1st beam particle
        beam_particle_one: hm.GenParticle = vtx.particles_in()[0]
        self.assertAlmostEqual(0, beam_particle_one.momentum().px())
        self.assertAlmostEqual(0, beam_particle_one.momentum().py())
        self.assertAlmostEqual(-10, beam_particle_one.momentum().pz())
        self.assertEqual(11, beam_particle_one.pid())

        beam_particle_two: hm.GenParticle = vtx.particles_in()[1]
        self.assertAlmostEqual(0, beam_particle_two.momentum().px())
        self.assertAlmostEqual(0, beam_particle_two.momentum().py())
        self.assertAlmostEqual(100, beam_particle_two.momentum().pz())
        self.assertEqual(2212, beam_particle_two.pid())

        # Test event number
        # io number of event is 0, but pythia6 event number of this event is 1 (2-nd column of ev. record)
        self.assertEqual(evt.event_number(), 1)

        evt.clear()
        inputA.close()

    def test_transform_func(self):

        def transform_func(index, event, params):
            self.assertEqual(index, 0)
            self.assertEqual(len(event.particles()), 13, "Event particles: 2 beam particles and 11 outgoing particles")
            self.assertEqual(25, params["angle"])

        hepmc_convert(self._data_path('pythia6-radcor-10evt.txt'),
                      self._tmp_path('pythia6-radcor-10evt.hepmc'),
                      McFileTypes.UNKNOWN,
                      transform_func=transform_func,
                      transform_args={"angle": 25},
                      nprocess=1)

    def test_hepmc2_convert(self):
        hepmc_convert(self._data_path('hepmc2.hepmc'),
                      self._tmp_path('hepmc3_from_hepmc2.hepmc'),
                      McFileTypes.UNKNOWN,
                      nprocess=10)

        hepmc_convert(self._data_path('hepmc2.hepmc'),
                      self._tmp_path('hepmc2_from_hepmc2.hepmc'),
                      McFileTypes.UNKNOWN,
                      hepmc_vers=2,
                      nprocess=1)

    def test_hepmc3_convert(self):
        hepmc_convert(self._data_path('hepmc3.hepmc'),
                      self._tmp_path('hepmc3_from_hepmc3.hepmc'),
                      McFileTypes.UNKNOWN,
                      nprocess=1)
