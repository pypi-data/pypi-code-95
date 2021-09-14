"""
==================
Physical utilities
==================

These physical tools are helpers around CFD-related problems.

- **solid_material** is a class to store solid properties for CHT problems.
- **thermodyn_properties** is a set of tools for propertiesand correlations used in CHT problems
- **wall_thermal_equilibrium** compute the thermal equilibrium for a 2-layer wall (Metal/ceramic)
- **yk_from_phi** compute the mass fraction set according to equivalence ratio.

"""


from .solid_material import *
from .thermodyn_properties import *
from .wall_thermal_equilibrium import *
from .yk_from_phi import *

