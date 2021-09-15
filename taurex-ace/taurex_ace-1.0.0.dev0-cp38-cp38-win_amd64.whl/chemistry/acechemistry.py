from taurex.chemistry import AutoChemistry
from taurex_ace.external.ace import md_ace
from taurex.data.fittable import fitparam
import numpy as np
import math
from taurex.cache import OpacityCache
import pkg_resources
from taurex.exceptions import InvalidModelException
from taurex.constants import AMU

class ACEChemistry(AutoChemistry):
    """
    Equilibrium chemistry
    Computes chemical profile using the Aerotherm Chemical Equilibrium (ACE)
    Fortran code by
    Agúndez, M., Venot, O., Iro, N., et al. 2012, AandA, 548,A73

    Parameters
    ----------
    metallicity : float
        Stellar metallicity in solar units

    co_ratio : float
        C/O ratio

    therm_file : str , optional
        Location of NASA.therm file. If not set will use file included
        in library

    spec_file : str , optional
        Location of composes.dat.  If not set will use file included in library


    """

    ace_H_solar = 12.0
    """H solar abundance"""
    ace_He_solar = 10.93
    """He solar abundance"""
    ace_C_solar = 8.43
    """C solar abundance"""
    ace_O_solar = 8.69
    """O solar abundance"""
    ace_N_solar = 7.83
    """N solar abundance"""

    def __init__(self, ace_metallicity=1.0,
                 ace_co_ratio=0.54951,
                 metallicity = None,
                 co_ratio = None,
                 therm_file=None,
                 spec_file=None):

        super().__init__('ACE')
        self.ace_metallicity = metallicity or ace_metallicity
        self.ace_co = co_ratio or ace_co_ratio
        self._get_files(therm_file, spec_file)
        self._mix_profile = None

        self.load_species()
        self.determine_active_inactive()

    @property
    def gases(self):
        return self._species

    @property
    def mixProfile(self):
        return self._mix_profile


    def _get_files(self, therm_file, spec_file):
        import os
        import taurex_ace.external

        self._specfile = spec_file
        self._thermfile = therm_file
        if self._specfile is None:
            self._specfile = pkg_resources.resource_filename('taurex_ace','external/Data/composes.dat')
        if self._thermfile is None:
            self._thermfile = pkg_resources.resource_filename('taurex_ace','external/Data/NASA.therm')

    def load_species(self):
        with open(self._specfile,'r') as f:
            self._species = [l.split()[1].strip() for l in f if not l.split()[1].strip().endswith('c')]
        with open(self._specfile,'r') as f:
            self._molar_masses = np.array([float(l.split()[2].strip()) for l in f])

        self._species_map = {a: idx for idx,a in enumerate(self._species)}

        self._masses = self._molar_masses*AMU


    def get_molecular_mass(self, molecule):
        idx = self._species_map[molecule]
        return self._masses[idx]



    def set_ace_params(self):

        # set O, C and N abundances given metallicity (in solar units) and CO
        self.O_abund_dex = math.log10(self.ace_metallicity *
                                      (10**(self.ace_O_solar-12.)))+12.
        self.N_abund_dex = math.log10(self.ace_metallicity *
                                      (10**(self.ace_N_solar-12.)))+12.

        self.C_abund_dex = self.O_abund_dex + math.log10(self.ace_co)

        # H and He don't change
        self.H_abund_dex = self.ace_H_solar
        self.He_abund_dex = self.ace_He_solar

    def compute_active_gas_profile(self, nlayers, altitude_profile,
                                   pressure_profile,
                                   temperature_profile):
        """Computes gas profiles of both active and inactive molecules for each layer

        Parameters
        ----------

        altitude_profile : array_like
            Altitude profile of atmosphere (usually computed in model)

        pressure_profile : array_like
            Pressure profile of atmosphere

        temperature_profile : array_like
            Temperature profile of atmosphere

        """

        self.set_ace_params()

        # Call FORTRAN ACE function
        self._mix_profile = md_ace(len(self.gases),self._specfile,
                                   self._thermfile,
                                   altitude_profile/1000.0,
                                   pressure_profile/1.e5,
                                   temperature_profile,
                                   self.He_abund_dex,
                                   self.C_abund_dex,
                                   self.O_abund_dex,
                                   self.N_abund_dex)

        if np.any(np.isnan(self._mix_profile)):
            raise InvalidModelException(f'Nans produced using parameters Z: {self.ace_metallicity} CO: {self.ace_co}')



    def initialize_chemistry(self, nlayers=100, temperature_profile=None,
                             pressure_profile=None, altitude_profile=None):
        """
        Sets up and and constructs chemical profiles. Called by forward
        model before path calculation

        Parameters
        ----------

        nlayers : int
            Number of layers in atmosphere

        altitude_profile : array_like
            Altitude profile of atmosphere (usually computed in model)

        pressure_profile : array_like
            Pressure profile of atmosphere

        temperature_profile : array_like
            Temperature profile of atmosphere

        """

        self.info('Initializing chemistry model')
        z = np.zeros_like(pressure_profile)
        self.compute_active_gas_profile(nlayers,z,
                                        pressure_profile, temperature_profile)

        self.compute_mu_profile(nlayers)

    @fitparam(param_name='ace_metallicity',
              param_latex='Metallicity',
              default_mode='log',
              default_fit=False,
              default_bounds=[-1, 4])
    def aceMetallicity(self):
        """
        Metallicity of star in solar units
        """
        return self.ace_metallicity

    @aceMetallicity.setter
    def aceMetallicity(self, value):
        self.ace_metallicity = value


    @fitparam(param_name='metallicity',
              param_latex='Z',
              default_mode='log',
              default_fit=False,
              default_bounds=[-1, 4])
    def aceMetallicityAlt(self):
        """
        Metallicity of star in solar units
        """
        return self.ace_metallicity

    @aceMetallicityAlt.setter
    def aceMetallicityAlt(self, value):
        self.ace_metallicity = value

    @fitparam(param_name='ace_co',
              param_latex='C/O',
              default_fit=False,
              default_bounds=[0, 2])
    def aceCORatio(self):
        """
        CO ratio of star
        """
        return self.ace_co

    @aceCORatio.setter
    def aceCORatio(self, value):
        self.ace_co = value


    @fitparam(param_name='C_O_ratio',
              param_latex='C/O',
              default_fit=False,
              default_bounds=[0, 2])
    def aceCORatioAlt(self):
        """
        CO ratio of star
        """
        return self.ace_co

    @aceCORatioAlt.setter
    def aceCORatioAlt(self, value):
        self.ace_co = value

    def write(self, output):

        gas_entry = super().write(output)
        gas_entry.write_scalar('ace_metallicity', self.ace_metallicity)
        gas_entry.write_scalar('ace_co_ratio', self.ace_co)
        if self._thermfile is not None:
            gas_entry.write_string('therm_file', self._thermfile)
        if self._specfile is not None:
            gas_entry.write_string('spec_file', self._specfile)

        return gas_entry

    @classmethod
    def input_keywords(self):
        return ['ace', 'equilibrium', ]
    
    BIBTEX_ENTRIES = [
        """
        @ARTICLE{Agundez2012,
            author = {{Ag{\'u}ndez}, M. and {Venot}, O. and {Iro}, N. and {Selsis}, F. and
                {Hersant}, F. and {H{\'e}brard}, E. and {Dobrijevic}, M.},
                title = "{The impact of atmospheric circulation on the chemistry of the hot Jupiter HD 209458b}",
            journal = {A\&A},
            keywords = {astrochemistry, planets and satellites: atmospheres, planets and satellites: individual: HD 209458b, Astrophysics - Earth and Planetary Astrophysics},
                year = "2012",
                month = "Dec",
            volume = {548},
                eid = {A73},
                pages = {A73},
                doi = {10.1051/0004-6361/201220365},
        archivePrefix = {arXiv},
            eprint = {1210.6627},
        primaryClass = {astro-ph.EP},
            adsurl = {https://ui.adsabs.harvard.edu/abs/2012A&A...548A..73A},
            adsnote = {Provided by the SAO/NASA Astrophysics Data System}
        }
        """,
    ]