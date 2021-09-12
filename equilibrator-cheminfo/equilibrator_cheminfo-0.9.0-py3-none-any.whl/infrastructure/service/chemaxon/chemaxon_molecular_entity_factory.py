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


"""Provide a ChemAxon-based factory for molecular entities."""
from typing import List, Optional

from equilibrator_cheminfo.domain.model import (
    AbstractMolecularEntityFactory,
    ErrorMessage,
    ManualStructureExceptionSpecification,
    Microspecies,
    MolecularEntity,
    Structure,
)

from .chemaxon_error import ChemAxonError
from .chemaxon_major_microspecies_service import ChemAxonMajorMicrospeciesService
from .chemaxon_molecule import ChemAxonMolecule
from .chemaxon_proton_dissociation_constants_service import (
    ChemAxonProtonDissociationConstantsService,
)


class ChemAxonMolecularEntityFactory(AbstractMolecularEntityFactory):
    """Define a factory for molecular entities that uses ChemAxon services."""

    @classmethod
    def make(
        cls,
        structure: Structure,
        majorms_service: ChemAxonMajorMicrospeciesService,
        pka_service: ChemAxonProtonDissociationConstantsService,
    ) -> Optional[MolecularEntity]:
        """Return a molecular entity created from ChemAxon services."""
        if ManualStructureExceptionSpecification.is_satisfied_by(structure):
            return
        try:
            # Create a molecule, preferably from a SMILES rather than an InChI.
            if structure.smiles is not None:
                molecule = ChemAxonMolecule.from_smiles(structure.smiles)
            else:
                molecule = ChemAxonMolecule.from_inchi(structure.identifier.inchi)
        except ChemAxonError as exc:
            # Without a valid molecule, we cannot run ChemAxon predictions and must
            # return early. Since creating a molecule failed, we expect no microspecies.
            return MolecularEntity(
                identifier=structure.identifier,
                errors=cls._create_error_messages(exc),
            )
        result = MolecularEntity(identifier=structure.identifier)
        errors = []
        cls._add_pka_values(result, molecule, errors, pka_service)
        cls._add_microspecies(result, molecule, errors, majorms_service)
        cls._recover_microspecies(result, structure, molecule)
        result.errors = errors
        return result

    @classmethod
    def _add_microspecies(
        cls,
        entity: MolecularEntity,
        molecule: ChemAxonMolecule,
        errors: List[ErrorMessage],
        majorms_service: ChemAxonMajorMicrospeciesService,
    ) -> None:
        """Add a major microspecies to the molecular entity in a failsafe way."""
        try:
            result = majorms_service.estimate_major_microspecies(molecule)
            entity.microspecies = [
                Microspecies(
                    is_major=True,
                    smiles=result.smiles,
                    atom_bag=result.atom_bag,
                    charge=result.charge,
                )
            ]
        except ChemAxonError as exc:
            errors.extend(cls._create_error_messages(exc))

    @classmethod
    def _add_pka_values(
        cls,
        entity: MolecularEntity,
        molecule: ChemAxonMolecule,
        errors: List[ErrorMessage],
        pka_service: ChemAxonProtonDissociationConstantsService,
    ) -> None:
        """Add a pKa values to the molecular entity in a failsafe way."""
        try:
            entity.pka_values = pka_service.estimate_pka_values(molecule)
        except ChemAxonError as exc:
            errors.extend(cls._create_error_messages(exc))

    @classmethod
    def _recover_microspecies(
        cls,
        entity: MolecularEntity,
        structure: Structure,
        molecule: ChemAxonMolecule,
    ) -> None:
        """
        Recover a microspecies in the case that the prediction by ChemAxon failed.

        If the original structure had a SMILES description, we simply assume that to be
        the major microspecies.
        """
        if structure.smiles is not None and not entity.microspecies:
            entity.microspecies = [
                Microspecies(
                    is_major=True,
                    smiles=structure.smiles,
                    atom_bag=molecule.atom_bag,
                    charge=molecule.charge,
                )
            ]
