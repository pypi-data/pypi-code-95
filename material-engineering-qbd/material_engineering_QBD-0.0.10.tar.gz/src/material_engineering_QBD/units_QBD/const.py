"""
Module contain constant phrases.
"""

#### SI UNITS PREFIXES
PREFIXES = {}
PREFIXES['y']   = '1E-24'
PREFIXES['z']   = '1E-21'
PREFIXES['a']   = '1E-18'
PREFIXES['f']   = '1E-15'
PREFIXES['p']   = '1E-12'
PREFIXES['n']   = '1E-09'
PREFIXES['u']   = '1E-06'
PREFIXES['m']   = '1E-03'
PREFIXES['c']   = '1E-02'
PREFIXES['d']   = '1E-01'
PREFIXES['da']  = '1E+01'
PREFIXES['h']   = '1E+02'
PREFIXES['k']   = '1E+03'
PREFIXES['M']   = '1E+06'
PREFIXES['G']   = '1E+09'
PREFIXES['T']   = '1E+12'
PREFIXES['P']   = '1E+15'
PREFIXES['E']   = '1E+18'
PREFIXES['Z']   = '1E+21'
PREFIXES['Y']   = '1E+24'

#### BASIC SI UNITS
SI          = {}
SI['m']     = (1., 'm')
SI['kg']    = (1., 'kg')
SI['s']     = (1., 's')
SI['A']     = (1., 'A')
SI['K']     = (1., 'K')
SI['mol']   = (1., 'mol')
SI['cd']    = (1., 'cd')

#### DERIVED SI UNITS    
SI_                 = {}
SI_['Ang']          = (1.0E-10,         'm')
SI_['Angs']         = (1.0E-10,         'm')
SI_['Angstorm']     = (1.0E-10,         'm')
SI_['Angstorms']    = (1.0E-10,         'm')
SI_['rad']          = (1.,              'm*m**-1')
SI_['sr']           = (1.,              'm**2*m**-2')
SI_['Hz']           = (1.,              's**-1')
SI_['N']            = (1.,              'kg*m*s**-2')
SI_['Pa']           = (1.,              'kg*m**-1*s**-2')
SI_['J']            = (1.,              'kg*m**2*s**-2')
SI_['eV']           = (1.602176634E-19, 'kg*m**2*s**-2')
SI_['W']            = (1.,              'kg*m**2*s**-3')
SI_['C']            = (1.,              'A*s')
SI_['V']            = (1.,              'kg*m**2*s**-3*A**-1')
SI_['F']            = (1.,              'kg**-1m**-2*s**4*A**2')
SI_['Ohm']          = (1.,              'kg*m**2*s**-3*A**-2')
SI_['S']            = (1.,              'kg**-1m**-2*s**3*A**2')
SI_['Wb']           = (1.,              'kg*m**2*s**-2*A**-1')
SI_['T']            = (1.,              'kg*s**-2*A**-1')
SI_['H']            = (1.,              'kg*m**2*s**-2*A**-2')

#### QUANTITIES
E = 1.602176634e-19                     # (C)   elementary charge               https://en.wikipedia.org/wiki/Elementary_charge
K_B = 1.380649e-23                      # (J/K) Boltzman constant               https://en.wikipedia.org/wiki/Boltzmann_constant

#### OPERATORS
OPERATORS = ('*', '/', '**', '^')

