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


"""Provide a service registry for accessing configured service instances."""


from typing import Type

from .abstract_molecular_entity_service import AbstractMolecularEntityService
from .cheminformatics_backend import CheminformaticsBackend


class ApplicationServiceRegistry:
    """Define a registry which returns configured application service instances."""

    @classmethod
    def molecular_entity_service(
        cls, backend: CheminformaticsBackend
    ) -> Type[AbstractMolecularEntityService]:
        """Return a molecular entity service for the specified backend."""
        if backend == CheminformaticsBackend.ChemAxon:
            from .chemaxon import ChemAxonMolecularEntityService

            return ChemAxonMolecularEntityService
        else:
            raise ValueError(
                "Currently, pKa and major microspecies estimation is only provided by "
                "ChemAxon Marvin."
            )
