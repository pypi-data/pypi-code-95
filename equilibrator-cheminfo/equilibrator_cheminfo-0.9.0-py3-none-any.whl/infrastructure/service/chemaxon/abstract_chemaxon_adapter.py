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


"""Provide an abstract base adapter class for ChemAxon plugins."""


import logging
from abc import ABC
from typing import Optional, Type

from jpype.types import JClass

from .chemaxon_error import ChemAxonError
from .chemaxon_molecule import ChemAxonMolecule


logger = logging.getLogger(__name__)


class AbstractChemAxonAdapter(ABC):
    """Define an abstract adapter for ChemAxon plugins."""

    _plugin_cls: Type[JClass]
    _JavaException: JClass = JClass("java.lang.Exception")

    def __init__(self, **kwargs) -> None:
        """Initialize the base adapter attributes."""
        super().__init__(**kwargs)
        self._plugin: JClass = self._plugin_cls()
        self._molecule: Optional[ChemAxonMolecule] = None

    @property
    def molecule(self) -> Optional[ChemAxonMolecule]:
        """Get the current molecule if any."""
        return self._molecule

    @molecule.setter
    def molecule(self, molecule: ChemAxonMolecule) -> None:
        """Set a new molecule to do computations on."""
        if molecule is self._molecule:
            return
        self._plugin.setMolecule(molecule.native)
        try:
            success = self._plugin.run()
        except self._JavaException as error:
            raise ChemAxonError(
                errors=[f"Structure is incompatible with the {type(self).__name__}."]
            ) from error
        if not success:
            raise ChemAxonError(
                errors=[str(self._plugin.getErrorMessage())],
                warnings=[str(self._plugin.getWarningMessage())],
            )
        self._molecule = molecule
