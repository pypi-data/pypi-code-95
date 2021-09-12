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


"""Provide a domain registry which makes available configured repositories."""


from equilibrator_cheminfo.domain.model import (
    AbstractDomainRegistry,
    AbstractMolecularEntityRepository,
)

from .orm import ORMManagementService, ORMMolecularEntityRepository


class DomainRegistry(AbstractDomainRegistry):
    """Implement a domain registry returning ORM-based repository instances."""

    @classmethod
    def molecular_entity_repository(
        cls, backend: str
    ) -> AbstractMolecularEntityRepository:
        """Return an instance of a molecular entity repository."""
        return ORMMolecularEntityRepository(
            session=ORMManagementService.create_session(backend)
        )
