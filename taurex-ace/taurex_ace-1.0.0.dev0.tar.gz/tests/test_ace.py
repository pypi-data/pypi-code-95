import pytest
import numpy as np
import unittest.mock as mock

def test_ace_molecules():
    from taurex_ace import ACEChemistry
    from taurex.cache import OpacityCache
    nlayers = 10

    T = np.linspace(1000,500, nlayers)

    P = np.logspace(6,1, nlayers)
    
    molecules_active = ['H2O', 'CH4', 'CO2']

    with mock.patch.object(OpacityCache, "find_list_of_molecules") as mock_my_method:
        mock_my_method.return_value = molecules_active
        ace = ACEChemistry()

    ace.initialize_chemistry(nlayers=nlayers, temperature_profile=T, pressure_profile=P)

    gases = ace.gases

    num_gases = len(gases)
    num_active = len(molecules_active)
    num_inactive = num_gases - num_active

    mix_profile = ace.mixProfile

    for m in molecules_active:
        assert m in gases
    for m in molecules_active:
        assert m in ace.activeGases

    for m in molecules_active:
        assert m not in ace.inactiveGases  

    assert ace.mixProfile.shape == (num_gases, nlayers)
    assert ace.activeGasMixProfile.shape == (num_active, nlayers)
    assert ace.inactiveGasMixProfile.shape == (num_inactive, nlayers)

