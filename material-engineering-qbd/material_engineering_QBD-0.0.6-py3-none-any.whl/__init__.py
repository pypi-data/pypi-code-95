"""
x, y = material_engineering_QBD.read_sheet("
AlGaAs 2A
AsSb 4 nm
GaInAs 8um
Al 2
GaAs 7nm

C 10
", 'nm')
print(x, y)

"""

from . tools import *
from . numeric import *