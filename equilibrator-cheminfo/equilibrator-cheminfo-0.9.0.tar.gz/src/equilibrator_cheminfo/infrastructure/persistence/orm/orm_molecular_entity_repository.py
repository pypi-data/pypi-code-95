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


"""Provide a molecular entity repository backed by an ORM."""


import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from equilibrator_cheminfo.domain.model import (
    AbstractMolecularEntityRepository,
    ErrorMessage,
    Microspecies,
    MolecularEntity,
    StructureIdentifier,
)

from .orm_base import ORMSession
from .orm_error_message import ORMErrorMessage
from .orm_microspecies import ORMMicrospecies
from .orm_molecular_entity import ORMMolecularEntity
from .orm_proton_dissociation_constant import ORMProtonDissociationConstant


logger = logging.getLogger(__name__)


class ORMMolecularEntityRepository(AbstractMolecularEntityRepository):
    """Define an ORM-based molecular entity repository."""

    def __init__(self, *, session: ORMSession, **kwargs) -> None:
        """Initialize the base."""
        super().__init__(**kwargs)
        self._session = session

    @classmethod
    def reconstruct(cls, molecular_entity: ORMMolecularEntity) -> MolecularEntity:
        """Build an ORM representation of a molecular entity."""
        return MolecularEntity(
            identifier=StructureIdentifier(
                inchikey=molecular_entity.inchikey, inchi=molecular_entity.inchi
            ),
            microspecies=[
                Microspecies(
                    is_major=ms.is_major,
                    smiles=ms.smiles,
                    atom_bag=ms.atom_bag,
                    charge=ms.charge,
                )
                for ms in molecular_entity.microspecies
            ],
            pka_values=[
                pka.value for pka in molecular_entity.proton_dissociation_constants
            ],
            errors=[
                ErrorMessage(message=error.message, level=error.level)
                for error in molecular_entity.error_messages
            ],
        )

    def find_by_inchikey(self, inchikey: str) -> MolecularEntity:
        """Find a molecular entity in the repository by its InChIKey."""
        identifier = StructureIdentifier(
            inchikey=inchikey, inchi="InChI=1"
        ).neutralize_protonation()
        try:
            entity: ORMMolecularEntity = (
                self._session.query(ORMMolecularEntity)
                .options(selectinload(ORMMolecularEntity.proton_dissociation_constants))
                .options(selectinload(ORMMolecularEntity.microspecies))
                .options(selectinload(ORMMolecularEntity.error_messages))
                .filter_by(inchikey=identifier.inchikey)
                .one()
            )
        except NoResultFound:
            raise KeyError(f"{inchikey} is not in the repository.")
        return self.reconstruct(entity)

    def add(self, molecular_entity: MolecularEntity) -> None:
        """Add a molecular entity to the repository."""
        try:
            result: ORMMolecularEntity = (
                self._session.query(ORMMolecularEntity)
                .options(selectinload(ORMMolecularEntity.proton_dissociation_constants))
                .options(selectinload(ORMMolecularEntity.microspecies))
                .options(selectinload(ORMMolecularEntity.error_messages))
                .filter_by(inchikey=molecular_entity.identifier.inchikey)
                .one()
            )
        except NoResultFound:
            result = ORMMolecularEntity(
                inchikey=molecular_entity.identifier.inchikey,
                inchi=molecular_entity.identifier.inchi,
            )
        result.microspecies = [
            ORMMicrospecies(
                is_major=ms.is_major,
                smiles=ms.smiles,
                atom_bag=ms.atom_bag,
                charge=ms.charge,
            )
            for ms in molecular_entity.microspecies
        ]
        result.proton_dissociation_constants = [
            ORMProtonDissociationConstant(value=pka)
            for pka in molecular_entity.pka_values
        ]
        result.error_messages = [
            ORMErrorMessage(message=error.message, level=error.level)
            for error in molecular_entity.errors
        ]
        self._session.add(result)
        self._session.commit()

    def remove(self, molecular_entity: MolecularEntity) -> None:
        """Remove a molecular entity from the repository."""
        try:
            result = (
                self._session.query(ORMMolecularEntity)
                .filter_by(inchikey=molecular_entity.identifier.inchikey)
                .one()
            )
        except NoResultFound:
            raise KeyError(
                f"{molecular_entity.identifier.inchikey} is not in the repository."
            )
        self._session.delete(result)
        self._session.commit()

    def log_summary(self) -> None:
        """Summarize the information on molecular entities."""
        logger.info("Molecular entity summary:")
        base_query = self._session.query(ORMMolecularEntity.id).select_from(
            ORMMolecularEntity
        )
        num_total = base_query.count()
        logger.info(f"- {num_total:n} unique InChIKeys")
        num_with_pka = base_query.join(ORMProtonDissociationConstant).distinct().count()
        logger.info(
            f"- {num_with_pka:n} ({num_with_pka / num_total:.2%}) with pKa values"
        )
        num_with_major_ms = base_query.join(ORMMicrospecies).distinct().count()
        logger.info(
            f"- {num_with_major_ms:n} ({num_with_major_ms / num_total:.2%}) with major "
            f"microspecies at pH 7"
        )
        num_with_error = base_query.join(ORMErrorMessage).distinct().count()
        logger.info(
            f"- {num_with_error:n} ({num_with_error / num_total:.2%}) with errors:"
        )
        if num_with_error > 0:
            num_with_error_but_pka = (
                base_query.join(ORMErrorMessage)
                .join(ORMProtonDissociationConstant)
                .distinct()
                .count()
            )
            logger.info(
                f"  - {num_with_error_but_pka:n} "
                f"({num_with_error_but_pka / num_with_error:.2%}) "
                f"of those with pKa values"
            )
            num_with_error_but_major_ms = (
                base_query.join(ORMErrorMessage)
                .join(ORMMicrospecies)
                .distinct()
                .count()
            )
            logger.info(
                f"  - {num_with_error_but_major_ms:n} "
                f"({num_with_error_but_major_ms / num_with_error:.2%}) "
                f"of those with major microspecies at pH 7"
            )
