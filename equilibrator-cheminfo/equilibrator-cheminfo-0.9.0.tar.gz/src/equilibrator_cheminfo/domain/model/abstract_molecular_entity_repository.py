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


"""Provide an abstract molecular entity repository class interface."""


from abc import ABC, abstractmethod

from .molecular_entity import MolecularEntity


class AbstractMolecularEntityRepository(ABC):
    """Define the abstract interface for a molecular entity repository."""

    def __init__(self, **kwargs) -> None:
        """Initialize the base."""
        super().__init__(**kwargs)

    @abstractmethod
    def find_by_inchikey(self, inchikey: str) -> MolecularEntity:
        """Find a molecular entity in the repository by its InChIKey."""

    @abstractmethod
    def add(self, molecular_entity: MolecularEntity) -> None:
        """Add a molecular entity to the repository."""

    @abstractmethod
    def remove(self, molecular_entity: MolecularEntity) -> None:
        """Remove a molecular entity from the repository."""

    @abstractmethod
    def log_summary(self) -> None:
        """Log a comprehensive summary of the repository in implementing classes."""
