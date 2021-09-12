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


"""Provide a service that coordinates the transformation of structures."""


import logging
import multiprocessing
from pathlib import Path
from typing import Type

import pandas as pd
from tqdm import tqdm

# Import needed for activating the pandas.DataFrame accessor definition.
from equilibrator_cheminfo.domain.model import StructuresTable  # noqa: F401
from equilibrator_cheminfo.domain.model import AbstractMolecularEntityRepository

from .abstract_molecular_entity_service import AbstractMolecularEntityService
from .create_molecular_entities_from_table_command import (
    CreateMolecularEntitiesFromTableCommand,
)


logger = logging.getLogger(__name__)


class StructuresTableService:
    """Define a service that coordinates the transformation of structures."""

    def __init__(
        self,
        *,
        molecular_entity_repository: AbstractMolecularEntityRepository,
        molecular_entity_service: Type[AbstractMolecularEntityService],
        **kwargs,
    ) -> None:
        """Initialize a structures table service with correct sub-service instances."""
        super().__init__(**kwargs)
        self._repo = molecular_entity_repository
        self._service = molecular_entity_service

    def transform(self, command: CreateMolecularEntitiesFromTableCommand) -> None:
        """Transform a structures table into a database of molecular entities."""
        assert command.structures_table.is_file(), (
            f"The TSV file '{command.structures_table}' defining the chemical "
            f"structures was not found."
        )

        structures = self._create_structures_table(command.structures_table)
        if command.processes > 1:
            self._concurrently(structures, command)
        else:
            self._sequentially(structures, command)
        self._repo.log_summary()

    def _sequentially(
        self,
        structures: pd.DataFrame,
        command: CreateMolecularEntitiesFromTableCommand,
    ) -> None:
        """Coordinate predictions on all structures sequentially and load results."""
        self._service.setup(
            command.minimum_ph,
            command.maximum_ph,
            command.fixed_ph,
            command.use_large_model,
        )
        for structure in tqdm(
            structures.cheminfo.iter_structures(),
            total=len(structures),
            desc="Molecular Entity",
            unit_scale=True,
        ):
            if (entity := self._service.run(structure)) is not None:
                self._repo.add(entity)

    def _concurrently(
        self,
        structures: pd.DataFrame,
        command: CreateMolecularEntitiesFromTableCommand,
        batch_size: int = 1000,
    ) -> None:
        """Coordinate predictions on all structures concurrently and load results."""
        args = list(structures.cheminfo.iter_structures())
        chunk_size = min(max(len(args) // command.processes, 1), batch_size)
        with multiprocessing.get_context("spawn").Pool(
            processes=command.processes,
            initializer=self._service.setup,
            initargs=(
                command.minimum_ph,
                command.maximum_ph,
                command.fixed_ph,
                command.use_large_model,
            ),
        ) as pool:
            result_iter = pool.imap_unordered(
                self._service.run,
                args,
                chunksize=chunk_size,
            )
            for molecular_entity in (
                result
                for result in tqdm(
                    result_iter,
                    total=len(args),
                    desc="Molecular Entity",
                    unit_scale=True,
                )
                if result is not None
            ):
                self._repo.add(molecular_entity)

    @classmethod
    def _create_structures_table(cls, molecules: Path) -> pd.DataFrame:
        """Extract and transform chemical structures from the given TSV file."""
        logger.info("Extract chemical structures.")
        raw = pd.read_csv(molecules, sep="\t")
        logger.info(f"Found {len(raw):n} entries.")
        logger.info("Transform chemical structures.")
        logger.debug("Ignore rows with missing InChIs.")
        result = raw.loc[raw["inchi"].notnull(), :].cheminfo.neutralize_protonation()
        logger.info(f"Maintained {len(result):n} entries.")
        assert len(result["inchikey"].unique()) == len(
            result
        ), "InChIKeys are not unique even though they *should* be."
        return result
