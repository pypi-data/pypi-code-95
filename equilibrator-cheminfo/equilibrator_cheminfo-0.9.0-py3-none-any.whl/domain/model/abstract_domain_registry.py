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


"""Provide an interface for a domain registry."""


from abc import ABC, abstractmethod

from .abstract_molecular_entity_repository import AbstractMolecularEntityRepository


class AbstractDomainRegistry(ABC):
    """Define an interface for a domain registry returning repository instances."""

    @classmethod
    @abstractmethod
    def molecular_entity_repository(
        cls, backend: str
    ) -> AbstractMolecularEntityRepository:
        """Return an instance of a molecular entity repository."""
