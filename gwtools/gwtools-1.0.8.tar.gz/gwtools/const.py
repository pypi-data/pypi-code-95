'''This file defines constants used by romgw, gwsurrogate and gwtools.

Many of the older values of these constants are commented out in case 
previous tests/analysis needs to be repeated.'''

## Constants obtained from LAL version 6.18.0.1 (CODATA 2010)
c = 2.99792458e+08                      # Speed of light (m/s)
#G = 6.67384e-11                         # Gravitation constant (m^3/kg/s^2)
#Msun = 1.9885469549614615e+30           # Solar mass (kg)
Msuninsec = 4.925491025543576e-06       # Solar mass (seconds) = lal.MSUN_SI * lal.G_SI / (lal.C_SI**3.0)
PCinm = 3.085677581491367e+16           # Parsec (meters)
gamma_E = 0.5772156649015329            # Euler-Mascheroni constant

## Constants obtained from LAL version 6.21.0.1 (CODATA 2018)
G = 6.6743e-11                                   # Gravitation constant (m^3/kg/s^2)
Msun = 1.988409902147041637325262574352366540e30 # Solar mass (kg)


# Derived constants
Mpcinm = PCinm * 1e6                    # Megaparsec (meters)
Mpcinkm   = Mpcinm/1000.0               # Megaparsec (km)
Msuninkg  = Msun                        # for romgw


# override some of the above values, if necessary
"""
# romgw constants, and older gwsurroate constants # 
# Older version of code used these values
G         = 6.67428e-11      # Gravitation constant (MKS)
Msun      = 1.98892e30       # Solar mass (kg)
Msuninsec = Msun * G / c**3  # Solar mass (secs)
Mpcinm    = 3.08568025e22    # Megaparsecs (m)
Mpcinkm   = Mpcinm/1000.0    # Megaparsecs (km)
Msuninkg  = Msun             # for romgw 

# Jonathan's constants
#Msun = 1.9891e30
#Mpcinm = 3.08567758e22
#SPEED_OF_LIGHT_C = 299792458
#GRAVITATIONAL_CONSTANT_G = 6.67384e-11
#G = 6.67384e-11
#Msuninsec = Msun * G / c**3
#Mpcinkm   = Mpcinm/1000.0    # Megaparsecs (km)
"""


# rename some variables for convenience
PC_SI = PCinm

# check if our constants differ from current lal
try:
  import lal
  if lal.PC_SI != PC_SI:
    print("lal.PC_SI != PC_SI")
  if lal.C_SI != c:
    print("lal.C_SI != c")
  if lal.G_SI != G:
    print("lal.G_SI != G")
  if lal.MSUN_SI != Msun:
    print("lal.MSUN_SI != Msun")
except:
  print("cannot import LAL")
