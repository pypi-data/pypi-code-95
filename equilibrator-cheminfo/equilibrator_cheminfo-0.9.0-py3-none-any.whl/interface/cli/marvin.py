#!/usr/bin/env python3


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


"""Provide a ChemAxon CLI for transforming structures into molecular entities."""


import argparse
import logging
import os
from pathlib import Path
from typing import List, Optional

from equilibrator_cheminfo.application.service import (
    ApplicationServiceRegistry,
    CheminformaticsBackend,
    CreateMolecularEntitiesFromTableCommand,
    StructuresTableService,
)
from equilibrator_cheminfo.infrastructure.persistence import DomainRegistry
from equilibrator_cheminfo.infrastructure.persistence.orm import ORMManagementService


logger = logging.getLogger()


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Define the command line arguments and immediately parse them."""
    num_processes = len(os.sched_getaffinity(0))
    if not num_processes:
        num_processes = 1
    if num_processes > 1:
        num_processes -= 1

    parser = argparse.ArgumentParser(
        prog="marvin",
        description="Build a molecular entity database containing proton dissociation "
        "constants and major microspecies using ChemAxon Marvin.",
    )
    parser.add_argument(
        "--db-url",
        required=True,
        metavar="URL",
        help="A string interpreted as an rfc1738 compatible database URL.",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        help="The desired log level.",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
    )
    parser.add_argument(
        "--minimum-ph",
        type=float,
        default=0.0,
        help="The minimum pH value to consider (default 0).",
    )
    parser.add_argument(
        "--maximum-ph",
        type=float,
        default=14.0,
        help="The maximum pH value to consider (default 14).",
    )
    parser.add_argument(
        "--ph",
        type=float,
        default=7.0,
        help="The pH value at which to determine the major microspecies (default 7).",
    )
    parser.add_argument(
        "--large-model",
        action="store_true",
        help="Use a model for pKa values estimation that is suitable for large "
        "molecules. Without this flag a small model is used which is faster and works "
        "fine for most metabolites.",
    )
    parser.add_argument(
        "--backend",
        choices=("ChemAxon",),
        default="ChemAxon",
        help="The cheminformatics backend (default ChemAxon).",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=num_processes,
        help=f"The number of parallel processes to start (default {num_processes}).",
    )
    parser.add_argument(
        "structures",
        type=Path,
        help="Path to a TSV file with chemical structures defined by the columns "
        "inchikey, inchi, smiles. Missing values are allowed.",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    """Coordinate argument parsing and command calling."""
    args = parse_arguments(args)
    logging.basicConfig(level=args.log_level, format="[%(levelname)s] %(message)s")
    command = CreateMolecularEntitiesFromTableCommand(
        cheminformatics_backend=CheminformaticsBackend(args.backend),
        database_url=args.db_url,
        structures_table=args.structures,
        minimum_ph=args.minimum_ph,
        maximum_ph=args.maximum_ph,
        fixed_ph=args.ph,
        use_large_model=args.large_model,
        processes=args.processes,
    )
    logger.info("Set up clean database.")
    ORMManagementService.initialize(command.database_url)
    StructuresTableService(
        molecular_entity_repository=DomainRegistry.molecular_entity_repository(
            command.database_url
        ),
        molecular_entity_service=ApplicationServiceRegistry.molecular_entity_service(
            command.cheminformatics_backend
        ),
    ).transform(command)
