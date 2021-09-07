from mcconv import GenericTextReader, UnparsedTextEvent, hepmc_convert

import os
import unittest
from mcconv import detect_mc_type, McFileTypes
from pyHepMC3 import HepMC3 as hm

class TestGenericTextReader(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def _tmp_path(self, file_name):
        """Gets output temporary file path"""
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp', file_name)

    def test_create_save_load(self):
        hepmc2_out = hm.WriterAsciiHepMC2(self._tmp_path("test_create_save_load.hepmc2"))
        hepmc3_out = hm.WriterAscii(self._tmp_path("test_create_save_load.hepmc3"))
        evt = hm.GenEvent(hm.Units.GEV, hm.Units.MM)
        evt.set_event_number(1)
        evt.add_attribute("signal_process_id", hm.IntAttribute(20))

        v1 = hm.GenVertex()
        evt.add_vertex(v1)

        p1 = hm.GenParticle(hm.FourVector(0, 0, 100, 100), 2212, 1)
        evt.add_particle(p1)
        p1.add_attribute("theta", hm.DoubleAttribute(1.1))
        p1.add_attribute("phi", hm.DoubleAttribute(2.2))

        p2 = hm.GenParticle(hm.FourVector(0, 0, -7, 7), 11, 1)
        evt.add_particle(p2)
        p2.add_attribute("theta", hm.DoubleAttribute(1.1))
        p2.add_attribute("phi", hm.DoubleAttribute(2.2))

        p3 = hm.GenParticle(hm.FourVector(.750, -1.569, 32.191, 32.238), 1, 1)
        evt.add_particle(p3)
        p3.add_attribute("theta", hm.DoubleAttribute(3.3))
        p3.add_attribute("phi", hm.DoubleAttribute(4.4))

        v1.add_particle_in(p1)
        v1.add_particle_in(p2)
        v1.add_particle_out(p3)

        hepmc2_out.write_event(evt)
        hepmc3_out.write_event(evt)

        hepmc2_out.close()
        hepmc3_out.close()

        hepmc2_in = hm.ReaderAsciiHepMC2(self._tmp_path('test_create_save_load.hepmc2'))
        hepmc3_in = hm.ReaderAscii(self._tmp_path('test_create_save_load.hepmc3'))

        def read_hepmc_file(input_file):
            if input_file.failed():
                raise "test_create_save_load.failed()"

            while True:
                evt = hm.GenEvent()
                input_file.read_event(evt)
                if input_file.failed():
                    break
                print(f"  evt numbr: {evt.event_number()}")
                print(f"    prt count: {len(evt.particles())}")
                print(f"    vtx count: {len(evt.vertices())}")
                evt.clear()

            input_file.close()

        print("Load hepmc2 file")
        read_hepmc_file(hepmc2_in)

        print("Load hepmc3 file")
        read_hepmc_file(hepmc3_in)
