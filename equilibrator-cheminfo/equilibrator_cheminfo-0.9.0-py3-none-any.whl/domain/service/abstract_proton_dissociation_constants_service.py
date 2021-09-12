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


"""Provide an abstract proton dissociation constants service class interface."""


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..model import AbstractMolecule


class AbstractProtonDissociationConstantsService(ABC):
    """Define the abstract interface for a service to estimate pKa values."""

    def __init__(self, **kwargs):
        """Initialize the base."""
        super().__init__(**kwargs)

    @abstractmethod
    def estimate_pka_values(self, molecule: AbstractMolecule) -> List[float]:
        """Return sorted acidic and basic proton dissociation constants (pKa values)."""
        raise NotImplementedError()
