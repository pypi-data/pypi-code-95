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


"""Provide a standard chemical structure identifier as a value object."""


from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar, Pattern


@dataclass(frozen=True)
class StructureIdentifier:
    """
    Define a standard chemical structure identifier as a value object.

    The StructureIdentifier is designed as an immutable value object[1]_.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Domain-driven_design#Building_blocks

    """

    inchikey: str = field(hash=True, compare=True)
    inchi: str = field(hash=False, compare=True)
    _inchikey_pattern: ClassVar[Pattern] = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")
    # Match the proton sublayer until the next layer or until the end of the string.
    _proton_layer_pattern: ClassVar[Pattern] = re.compile(r"/p.*?(/|$)")

    def __init__(self, *, inchikey: str, inchi: str) -> None:
        """
        Initialize a structure identifier from an InChIKey and an InChI[2]_.

        Assertions about the structure of those strings are enforced. However, currently
        it is assumed that the InChIKey is the correct hash of the InChI.

        Parameters
        ----------
        inchikey
            A hash key of the IUPAC International Chemical Identifier.
        inchi
            An IUPAC International Chemical Identifier.

        References
        ----------
        .. [2] https://www.inchi-trust.org/

        """
        assert (
            self._inchikey_pattern.match(inchikey) is not None
        ), f"The given string '{inchikey}' does not look like an InChIKey."
        assert inchi.startswith(
            "InChI=1"
        ), f"The given string '{inchi}' does not look like an InChI."
        # Since the dataclass is frozen, we cannot use normal attribute setting here.
        object.__setattr__(self, "inchikey", inchikey)
        object.__setattr__(self, "inchi", inchi)

    def __repr__(self) -> str:
        """Return a string representation of the structure identifier."""
        return (
            f"{type(self).__name__}(InChIKey={self.inchikey}, "
            f"{self.shorten_inchi(self.inchi)})"
        )

    @staticmethod
    def shorten_inchi(inchi: str) -> str:
        """Return a shortened InChI that only includes the molecular formula layer."""
        tokens = inchi.split("/", 2)
        if len(tokens) < 3:
            return inchi
        else:
            return f"{tokens[0]}/{tokens[1]}/..."

    def neutralize_protonation(self) -> StructureIdentifier:
        """Neutralize protonation on both the InChIKey and InChI."""
        return StructureIdentifier(
            inchikey=self.inchikey[:-1] + "N",
            inchi=self._proton_layer_pattern.sub(
                repl=r"\g<1>", string=self.inchi, count=1
            ),
        )
