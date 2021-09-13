
import os
import sys

sys.path.append(os.getcwd())

from openspace.math.measurements import Angle, Distance
from openspace.math.linear_algebra import Vector
from openspace.math.constants import ZERO
from openspace.math.coordinates import (
    spherical_to_cartesian, 
    cartesian_to_spherical,
    coes_to_vector
)

def test_spherical_to_cartesian():
    r = 3643
    lat = Angle(28, "degrees").to_unit("radians")
    long = Angle(50, "degrees").to_unit("radians")
    test_input = Vector([r, lat, long])
    expected_output = Vector([2067.576, 2464.042, 1710.285])
    angle = expected_output.angle(spherical_to_cartesian(test_input))
    assert angle <= ZERO

def test_cartesian_to_spherical():
    test_input = Vector([2067.576, 2464.042, 1710.285])
    output = cartesian_to_spherical(test_input)
    r = 3643
    lat = Angle(28, "degrees").to_unit("radians")
    long = Angle(50, "degrees").to_unit("radians")

    assert abs(output.get_element(0) - r) <= 1e-3
    assert abs(output.get_element(1) - lat) <= ZERO
    assert abs(output.get_element(2) - long) <= ZERO

def test_coes_to_vector():
    conversion_factor = Distance(1, "nautical miles").to_unit("meters")
    a = 4193.935*conversion_factor
    e = 5.96096410e-2
    i = Angle(30, "degrees").to_unit("radians")
    ta = Angle(23.55315, "degrees").to_unit("radians")
    aop = Angle(50, "degrees").to_unit("radians")
    raan = Angle(40, "degrees").to_unit("radians")

    p, v = coes_to_vector(a, e, i, ta, aop, raan)

    
    expected_p = Vector([-1256.137, 3242.352, 1900.184]).scale(conversion_factor)
    expected_v = Vector([-3.675879, -1.676277, 0.6227918]).scale(conversion_factor)

    print(p)
    print(v)
    assert p.angle(expected_p) < ZERO
    assert v.angle(expected_v) < ZERO
