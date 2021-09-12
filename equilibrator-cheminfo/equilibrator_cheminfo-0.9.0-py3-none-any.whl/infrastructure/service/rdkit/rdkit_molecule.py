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


"""Provide a concrete molecule implementation that wraps RDKit."""


from __future__ import annotations

from collections import defaultdict
from typing import Dict

import rdkit.Chem as chem
from rdkit.Chem import Descriptors, rdMolDescriptors, rdmolops

from equilibrator_cheminfo.domain.model import AbstractMolecule

from .rdkit_error import RDKitError


# from rdkit.Chem.inchi import InchiReadWriteError


class RDKitMolecule(AbstractMolecule):
    """Define the RDKit molecule adapter."""

    def __init__(self, *, molecule: chem.Mol, **kwargs):
        """Initialize the RDKitMolecule from a native instance."""
        super().__init__(molecule=molecule, **kwargs)

    def __len__(self) -> int:
        """Return the number of atoms in the molecule."""
        mol = chem.AddHs(self.native)
        return mol.GetNumAtoms()

    @classmethod
    def from_mol_block(cls, mol: str) -> RDKitMolecule:
        """Return an RDKitMolecule instance from an MDL MOL block."""
        if not mol:
            raise RDKitError(errors=["No MDL MOL block was provided."])
        molecule = chem.MolFromMolBlock(mol)
        if molecule:
            return RDKitMolecule(molecule=molecule)
        else:
            raise RDKitError(
                errors=[
                    "Failed to generate an RDKit molecule from the given MDL MOL block."
                ]
            )

    @classmethod
    def from_inchi(cls, inchi: str) -> RDKitMolecule:
        """Return an RDKitMolecule instance from an InChI string."""
        if not inchi:
            raise RDKitError(errors=["No InChI was provided."])
        molecule = chem.MolFromInchi(inchi)
        if molecule:
            return RDKitMolecule(molecule=molecule)
        else:
            raise RDKitError(
                errors=["Failed to generate an RDKit molecule from the given InChI."]
            )

    @classmethod
    def from_smiles(cls, smiles: str) -> RDKitMolecule:
        """Return an RDKitMolecule instance from a SMILES string."""
        if not smiles:
            raise RDKitError(errors=["No SMILES was provided."])
        molecule = chem.MolFromSmiles(smiles)
        if molecule:
            return RDKitMolecule(molecule=molecule)
        else:
            raise RDKitError(
                errors=["Failed to generate an RDKit molecule from the given SMILES."]
            )

    @property
    def inchi(self) -> str:
        """Return an InChI representation of the molecule."""
        return chem.MolToInchi(self._molecule)

    @property
    def inchikey(self) -> str:
        """Return an InChIKey representation of the molecule."""
        return chem.MolToInchiKey(self._molecule)

    @property
    def smiles(self) -> str:
        """Return a SMILES representation of the molecule."""
        return chem.MolToSmiles(self._molecule)

    @property
    def molecular_formula(self) -> str:
        """Return the molecular formula of the molecule including charge."""
        return rdMolDescriptors.CalcMolFormula(self._molecule)

    @property
    def molecular_mass(self) -> float:
        """
        Return the molecular mass of the molecule in dalton (Da or u).

        This takes into account the average atom mass based on isotope frequency.
        """
        return Descriptors.MolWt(self._molecule)

    @property
    def charge(self) -> int:
        """Return the molecule's formal charge."""
        return rdmolops.GetFormalCharge(self._molecule)

    @property
    def atom_bag(self) -> Dict[str, int]:
        """Return a mapping of the molecule's chemical symbols to their counts."""
        mol = chem.AddHs(self.native)
        symbols = defaultdict(int)
        formal_charge = 0
        num_protons = 0
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() == 0:
                continue
            symbols[atom.GetSymbol()] += 1
            num_protons += atom.GetAtomicNum()
            formal_charge += atom.GetFormalCharge()
        symbols["e-"] = num_protons - formal_charge
        return dict(symbols)
