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


"""Provide a concrete molecule implementation that wraps ChemAxon."""


from __future__ import annotations

import logging
from collections import defaultdict
from typing import Dict

from equilibrator_cheminfo.domain.model import AbstractMolecule

from .chemaxon_error import ChemAxonError
from .chemaxon_manager import ChemAxonManager


NativeChemAxonMolecule = ChemAxonManager.get_instance().chemaxon.struc.Molecule


logger = logging.getLogger(__name__)


class ChemAxonMolecule(AbstractMolecule):
    """Define the RDKit molecule adapter."""

    _importer = ChemAxonManager.get_instance().chemaxon.formats.MolImporter
    _FormatError = ChemAxonManager.get_instance().chemaxon.formats.MolFormatException
    _exporter = ChemAxonManager.get_instance().chemaxon.formats.MolExporter
    _ExportError = ChemAxonManager.get_instance().chemaxon.marvin.io.MolExportException
    _hydrogenizer = (
        ChemAxonManager.get_instance().chemaxon.calculations.hydrogenize.Hydrogenize
    )

    def __init__(self, *, molecule: NativeChemAxonMolecule, **kwargs):
        """Initialize the ChemAxonMolecule from a native instance."""
        super().__init__(molecule=molecule, **kwargs)

    def __len__(self) -> int:
        """Return the number of atoms in the molecule."""
        mol = self.native.clone()
        self._hydrogenizer.convertImplicitHToExplicit(mol)
        return int(mol.getAtomCount())

    @classmethod
    def from_mol_block(cls, mol: str) -> ChemAxonMolecule:
        """Return a ChemAxonMolecule instance from an MDL MOL block."""
        if not mol:
            raise ChemAxonError(errors=["No MDL MOL block was provided."])
        try:
            return ChemAxonMolecule(molecule=cls._importer.importMol(mol, "mol"))
        except cls._FormatError as error:
            raise ChemAxonError(
                errors=[
                    "Failed to generate an ChemAxon molecule from the given MDL MOL "
                    "block."
                ]
            ) from error

    @classmethod
    def from_inchi(cls, inchi: str) -> ChemAxonMolecule:
        """Return a ChemAxonMolecule instance from an InChI string."""
        if not inchi:
            raise ChemAxonError(errors=["No InChI was provided."])
        try:
            return ChemAxonMolecule(molecule=cls._importer.importMol(inchi, "inchi"))
        except cls._FormatError as error:
            raise ChemAxonError(
                errors=["Failed to generate an ChemAxon molecule from the given InChI."]
            ) from error

    @classmethod
    def from_smiles(cls, smiles: str) -> ChemAxonMolecule:
        """Return a ChemAxonMolecule instance from a SMILES string."""
        if not smiles:
            raise ChemAxonError(errors=["No SMILES was provided."])
        try:
            return ChemAxonMolecule(molecule=cls._importer.importMol(smiles, "smiles"))
        except cls._FormatError as error:
            raise ChemAxonError(
                errors=[
                    "Failed to generate an ChemAxon molecule from the given SMILES."
                ]
            ) from error

    @property
    def inchi(self) -> str:
        """Return an InChI representation of the molecule."""
        try:
            aux_inchi = str(self._exporter.exportToFormat(self.native, "inchi"))
        except self._ExportError as error:
            raise ChemAxonError() from error
        # ChemAxon adds a second line with `AuxInfo=` which we drop here.
        return aux_inchi.split("\n")[0]

    @property
    def inchikey(self) -> str:
        """Return an InChIKey representation of the molecule."""
        try:
            inchikey = str(self._exporter.exportToFormat(self.native, "inchikey"))
        except self._ExportError as error:
            raise ChemAxonError() from error
        # Remove the non-standard prefix.
        return inchikey[len("InChIKey=") :]

    @property
    def smiles(self) -> str:
        """Return a SMILES representation of the molecule."""
        try:
            return str(self._exporter.exportToFormat(self.native, "smiles"))
        except self._ExportError as error:
            raise ChemAxonError() from error

    @property
    def molecular_formula(self) -> str:
        """Return the molecular formula of the molecule including charge."""
        result = str(self.native.getFormula())
        if (charge := self.charge) != 0:
            if abs(charge) == 1:
                return f"{result}{charge:+}"[:-1]
            else:
                return f"{result}{charge:+}"
        else:
            return result

    @property
    def molecular_mass(self) -> float:
        """
        Return the molecular mass of the molecule in dalton (Da or u).

        This takes into account the average atom mass based on isotope frequency.
        """
        return float(self.native.getMass())

    @property
    def charge(self) -> int:
        """Return the molecule's formal charge."""
        return int(self.native.getFormalCharge())

    @property
    def atom_bag(self) -> Dict[str, int]:
        """Return a mapping of the molecule's chemical symbols to their counts."""
        mol = self.native.clone()
        self._hydrogenizer.convertImplicitHToExplicit(mol)
        symbols = defaultdict(int)
        formal_charge = 0
        num_protons = 0
        for atom in mol.getAtomArray():
            if atom.getAtno() == 131:
                continue
            symbols[str(atom.getSymbol())] += 1
            num_protons += atom.getAtno()
            formal_charge += atom.getCharge()
        symbols["e-"] = num_protons - formal_charge
        return dict(symbols)
