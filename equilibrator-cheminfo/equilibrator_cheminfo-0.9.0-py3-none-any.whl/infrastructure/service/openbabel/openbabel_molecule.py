# Copyright (c) 2020, Moritz E. Beber.
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


"""Provide a concrete molecule implementation that wraps Open Babel."""


from __future__ import annotations

from collections import defaultdict
from typing import Dict

from openbabel import openbabel as ob
from openbabel import pybel
from periodictable import elements

from equilibrator_cheminfo.domain.model import AbstractMolecule

from .openbabel_error import OpenBabelError


# Disable the Open Babel logging. Unfortunately, we cannot redirect the stream
# which would be preferable.
ob.obErrorLog.SetOutputLevel(-1)


class OpenBabelMolecule(AbstractMolecule):
    """Define the concrete Open Babel molecule adapter class."""

    _atomic_number_to_symbol = {elem.number: elem.symbol for elem in elements}

    def __init__(self, *, molecule: pybel.Molecule, **kwargs):
        """Initialize the OpenBabelMolecule from a native instance."""
        super().__init__(molecule=molecule, **kwargs)

    def __len__(self) -> int:
        """Return the number of atoms in the molecule."""
        mol = pybel.Molecule(pybel.ob.OBMol(self.native.OBMol))
        mol.addh()
        return len(mol.atoms)

    @classmethod
    def from_mol_block(cls, mol: str) -> OpenBabelMolecule:
        """Return an OpenBabelMolecule instance from an MDL MOL block."""
        if not mol:
            raise OpenBabelError(errors=["No MDL MOL block was provided."])
        try:
            return OpenBabelMolecule(molecule=pybel.readstring("mol", mol))
        except IOError as error:
            raise OpenBabelError(
                errors=[
                    "Failed to generate an Open Babel molecule from the given MDL MOL "
                    "block."
                ]
            ) from error

    @classmethod
    def from_inchi(cls, inchi: str) -> OpenBabelMolecule:
        """Return an OpenBabelMolecule instance from an InChI string."""
        if not inchi:
            raise OpenBabelError(errors=["No InChI was provided."])
        try:
            return OpenBabelMolecule(molecule=pybel.readstring("inchi", inchi))
        except IOError as error:
            raise OpenBabelError(
                errors=[
                    "Failed to generate an Open Babel molecule from the given InChI."
                ]
            ) from error

    @classmethod
    def from_smiles(cls, smiles: str) -> OpenBabelMolecule:
        """Return an OpenBabelMolecule instance from a SMILES string."""
        if not smiles:
            raise OpenBabelError(errors=["No SMILES was provided."])
        try:
            return OpenBabelMolecule(molecule=pybel.readstring("smiles", smiles))
        except IOError as error:
            raise OpenBabelError(
                errors=[
                    "Failed to generate an Open Babel molecule from the given SMILES."
                ]
            ) from error

    @property
    def inchi(self) -> str:
        """Return an InChI representation of the molecule."""
        return self._molecule.write("inchi").strip()

    @property
    def inchikey(self) -> str:
        """Return an InChIKey representation of the molecule."""
        return self._molecule.write("inchikey").strip()

    @property
    def smiles(self) -> str:
        """Return a SMILES representation of the molecule."""
        return self._molecule.write("smiles").strip()

    @property
    def molecular_formula(self) -> str:
        """Return the molecular formula of the molecule including charge."""
        # Open Babel adds multiple `+` or `-` signs to the formula.
        # We convert that to a number if necessary.
        result = self._molecule.formula
        if abs(charge := self.charge) > 1:
            return f"{result[:-abs(charge)]}{charge:+}"
        else:
            return result

    @property
    def molecular_mass(self) -> float:
        """Return the molecular mass of the molecule in dalton (Da or u)."""
        # TODO: Make sure this is in dalton and not g/mol.
        return self._molecule.molwt

    @property
    def charge(self) -> int:
        """Return the molecule's formal charge."""
        return self._molecule.charge

    @property
    def atom_bag(self) -> Dict[str, int]:
        """Return a mapping of the molecule's chemical symbols to their counts."""
        mol = pybel.Molecule(pybel.ob.OBMol(self.native.OBMol))
        mol.addh()
        symbols = defaultdict(int)
        formal_charge = 0
        num_protons = 0
        for atom in mol.atoms:
            if atom.atomicnum == 0:
                continue
            symbols[self._atomic_number_to_symbol[atom.atomicnum]] += 1
            num_protons += atom.atomicnum
            formal_charge += atom.formalcharge
        symbols["e-"] = num_protons - formal_charge
        return dict(symbols)
