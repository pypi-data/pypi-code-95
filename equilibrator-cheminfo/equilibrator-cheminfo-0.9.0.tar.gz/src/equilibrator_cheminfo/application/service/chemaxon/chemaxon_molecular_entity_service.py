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


"""Provide a coordinating service for creating molecular entities with ChemAxon."""


from typing import Optional

from equilibrator_cheminfo.domain.model import MolecularEntity, Structure
from equilibrator_cheminfo.infrastructure.service.chemaxon import (
    ChemAxonMajorMicrospeciesService,
    ChemAxonMolecularEntityFactory,
    ChemAxonProtonDissociationConstantsService,
)

from ..abstract_molecular_entity_service import AbstractMolecularEntityService


class ChemAxonMolecularEntityService(AbstractMolecularEntityService):
    """Define a multiprocessing-compatible molecular entity service using ChemAxon."""

    @staticmethod
    def setup(
        minimum_ph: float,
        maximum_ph: float,
        fixed_ph: float,
        use_large_model: bool,
    ) -> None:
        """Set up globally configured ChemAxon adapters."""
        global _pka
        global _majorms

        _pka = ChemAxonProtonDissociationConstantsService(
            minimum_ph=minimum_ph,
            minimum_basic_pka=minimum_ph,
            maximum_ph=maximum_ph,
            maximum_acidic_pka=maximum_ph,
            use_large_model=use_large_model,
        )
        _majorms = ChemAxonMajorMicrospeciesService(ph=fixed_ph)

    @staticmethod
    def run(structure: Structure) -> Optional[MolecularEntity]:
        """Run all ChemAxon Marvin predictions returning a molecular entity."""
        global _pka
        global _majorms

        return ChemAxonMolecularEntityFactory.make(
            structure=structure,
            majorms_service=_majorms,
            pka_service=_pka,
        )
