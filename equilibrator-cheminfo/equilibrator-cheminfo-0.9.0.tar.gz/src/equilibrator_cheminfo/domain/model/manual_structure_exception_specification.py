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


"""Provide a specification for which structures require exceptional treatment."""


from importlib.resources import open_text
from typing import FrozenSet

import pandas as pd

from . import data
from .structure import Structure


class ManualStructureExceptionSpecification:
    """
    Define a specification for which structures require exceptional treatment.

    This list is mostly comprised of metal ions for which ChemAxon will predict a major
    microspecies and pKa values but they are very likely incorrect and are not of
    interest for eQuilibrator.

    """

    with open_text(data, "manual_exceptions.tsv") as handle:
        _exceptions: FrozenSet[str] = frozenset(
            pd.read_table(handle, sep="\t")["inchikey"]
        )

    @classmethod
    def is_satisfied_by(cls, structure: Structure) -> bool:
        """Check the given structure to see if it needs special treatment."""
        return structure.identifier.neutralize_protonation().inchikey in cls._exceptions
