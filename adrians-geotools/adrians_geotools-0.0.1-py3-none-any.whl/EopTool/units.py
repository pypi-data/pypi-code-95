""" Units

This module contains a number of named tuples used for standard unit convertions.
"""

from collections import namedtuple

Unit = namedtuple("Unit", ["symbol", "convertion_factor"])

#Unitless
one = Unit("", 1)
micro = Unit("e-6", 10**6)

#micro
#Angles
milli_arcsecond = Unit("mas",  10**3)
micro_arcsecond = Unit("uas",  10**6)

#Seconds
second = Unit("s", 1)
micro_second = Unit("us", 10**6)