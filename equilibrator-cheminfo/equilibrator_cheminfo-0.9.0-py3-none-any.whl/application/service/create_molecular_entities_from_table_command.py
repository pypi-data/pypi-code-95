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


"""Provide a command for creating molecular entities from structures."""

from pathlib import Path
from typing import NamedTuple

from .cheminformatics_backend import CheminformaticsBackend


class CreateMolecularEntitiesFromTableCommand(NamedTuple):
    """Define a command for creating molecular entities from structures."""

    cheminformatics_backend: CheminformaticsBackend
    database_url: str
    structures_table: Path
    minimum_ph: float
    maximum_ph: float
    fixed_ph: float
    use_large_model: bool
    processes: int
