"""
Package contain functions which are useful for operations at International System of Units SI units.

e.g.
print(units.compare__units('1/m', 'm**-1', 'm^-2*m', values=True))

e.g.
out = units_QBD.standardise('Angs')
x = out.value
y = out.expression 
print(x, y)

e.g.
x, y = units_QBD.standardise__statement('12 Angs/K')
print(x, y)
"""

from .standardise_ import *
from .const import *
from .tools import *

