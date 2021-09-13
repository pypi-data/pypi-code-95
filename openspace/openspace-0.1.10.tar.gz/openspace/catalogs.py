from math import pi, sin
import os
from openspace.propagators import TwoBodyModel
from openspace.configs.formats import STANDARD_EPOCH_FMT
from openspace.bodies import Earth
from openspace.math.measurements import Angle, Epoch
from openspace.math.coordinates import coes_to_vector
import openspace.math.time_conversions as tc
import urllib.request
import pkg_resources

CELESTRAK_URL = "https://celestrak.com/NORAD/elements/geo.txt"
LATEST_ACTIVE_GEO_PATH = pkg_resources.resource_filename(
            __name__, 
            "resources/tles/latest_active_geo_tles.txt"
            )

class TwoLineElsets(dict):
    
    def __init__(self, fpath):

        dict.__init__(self)
        with open(fpath, "r") as f:
            lines = f.readlines()

        i = 1
        while i < len(lines):
            
            ln0 = lines[i-1]
            ln1 = lines[i]
            ln2 = lines[i+1]
            scc = ln1 [2:7]

            epoch = tc.tle_epoch_string_to_timestamp(ln1[18:31])

            mm = float(ln2[52:62])
            mm/=86400
            mm*=(2*pi)
            a = (Earth().mu/mm**2)**(1/3)
            e = float("."+ln2[26:32])
            inc = Angle(float(ln2[8:15]), "degrees").to_unit("radians")
            ma = Angle(float(ln2[43:50]), "degrees").to_unit("radians")
            aop = Angle(float(ln2[34:41]), "degrees").to_unit("radians")
            raan = Angle(float(ln2[17:24]), "degrees").to_unit("radians")

            ta = (ma + (2*e - .25*e**3)*sin(ma) + 
                1.25*e**2*sin(2*ma) + (13/12)*e**3*sin(3*ma))

            r, v = coes_to_vector(a, e, inc, ta, aop, raan)

            self[scc] = [Epoch.from_timestamp(epoch), r, v, ln0.strip()]
            i+=3

    def get_latest_celetrak_active_geo():
        url = CELESTRAK_URL
        uf = urllib.request.urlopen(url)
        in_lines = uf.readlines()

        out_lines = [ln.decode('UTF-8').strip() + "\n" for ln in in_lines]
        with open(LATEST_ACTIVE_GEO_PATH, "w") as f:
            f.writelines(out_lines)

        print(int(len(out_lines)/3), "tles saved.")

    @classmethod
    def load_from_latest_active_geos(cls):
        if not os.path.exists(LATEST_ACTIVE_GEO_PATH):
            cls.get_latest_celetrak_active_geo()

        return cls(LATEST_ACTIVE_GEO_PATH)