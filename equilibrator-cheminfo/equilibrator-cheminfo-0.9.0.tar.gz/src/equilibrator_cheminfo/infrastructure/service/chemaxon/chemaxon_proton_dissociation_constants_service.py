# Copyright (c) 2021, Moritz E. Beber.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Provide a concrete ChemAxon-based proton dissociation constants service."""


from itertools import chain
from typing import Iterable, List, Tuple

from equilibrator_cheminfo.domain.service import (
    AbstractProtonDissociationConstantsService,
)

from .abstract_chemaxon_adapter import AbstractChemAxonAdapter
from .chemaxon_manager import ChemAxonManager
from .chemaxon_molecule import ChemAxonMolecule


class ChemAxonProtonDissociationConstantsService(
    AbstractChemAxonAdapter, AbstractProtonDissociationConstantsService
):
    """
    Define the concrete service to estimate pKa values.

    The service is designed as an adapter to the ChemAxon pKaPlugin.

    """

    _plugin_cls = ChemAxonManager.get_instance().chemaxon.marvin.calculations.pKaPlugin

    def __init__(
        self,
        *,
        minimum_ph: float = 0.0,
        maximum_ph: float = 14.0,
        ph_step: float = 0.25,
        minimum_basic_pka: float = -10.0,
        maximum_acidic_pka: float = 20.0,
        use_large_model: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the acid base chemistry parameters."""
        assert maximum_ph > minimum_ph
        assert ph_step > 0.0
        assert maximum_acidic_pka > minimum_basic_pka
        super().__init__(**kwargs)

        self._plugin.setpHLower(minimum_ph)
        self._plugin.setpHUpper(maximum_ph)
        self._plugin.setpHStep(ph_step)

        self._plugin.setBasicpKaLowerLimit(minimum_basic_pka)
        self._plugin.setAcidicpKaUpperLimit(maximum_acidic_pka)

        if use_large_model:
            self._plugin.setModel(self._plugin.MODEL_LARGE)
        else:
            self._plugin.setModel(self._plugin.MODEL_SMALL)

    def estimate_pka_values(self, molecule: ChemAxonMolecule) -> List[float]:
        """Return sorted acidic and basic proton dissociation constants (pKa values)."""
        self.molecule = molecule
        result = []
        if (basic := self._plugin.getMacropKaValues(self._plugin.BASIC)) is not None:
            result.append(memoryview(basic))
        if (acidic := self._plugin.getMacropKaValues(self._plugin.ACIDIC)) is not None:
            result.append(memoryview(acidic))
        return sorted(chain.from_iterable(result), reverse=True)

    def get_ph_values(self, molecule: ChemAxonMolecule) -> List[float]:
        """Get the full array of pH values considered."""
        self.molecule = molecule
        return list(self._plugin.getpHs())

    def estimate_microspecies_distribution(
        self, molecule: ChemAxonMolecule
    ) -> Iterable[Tuple[ChemAxonMolecule, List[float]]]:
        """Estimate all microspecies and their abundances at the defined pH values."""
        self.molecule = molecule
        return (
            (
                ChemAxonMolecule(molecule=self._plugin.getMsMolecule(i)),
                list(self._plugin.getMsDistribution(i)),
            )
            for i in range(self._plugin.getMsCount())
        )
