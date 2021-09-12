"""
Molecular Structure
-------------------
This module provides abstracted functions to convert the molecular structures into the mathematical graphs.
The converted molecular structure is stored as a ``torch_geometric.Data`` object.
"""


import torch
from torch_geometric.data import Data
from rdkit import Chem
from maica.chem.base import *
from maica.data.util import get_one_hot_feat


def get_mol_graph(elem_feats: numpy.ndarray,
                  smiles: str,
                  numeric_feats: numpy.ndarray,
                  target: float = None,
                  gid: int = -1):
    """
    Convert the SMILES representation of a molecular structure into the mathematical graph
    :math:`G = (\mathcal{V}, \mathcal{E}, X, R)`, where :math:`\mathcal{V}` is a set of atoms,
    :math:`\mathcal{E}` is a set of bonds, :math:`X` is a atom-feature matrix,
    and :math:`R` is a bond-feature matrix.

    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :param smiles: (*str*) A SMILES representation of the input molecular structure.
    :param numeric_feats: (*numpy.ndarray*) Numerical features of the molecule (e.g., molecular weight).
    :param target: (*float, optional*) The target property that you want to predict from the molecular structure (*default* = ``None``).
    :param gid: (*int, optional*) An integer identifier of the molecular structure (*default* = -1).
    :return: A molecular graph :math:`G = (\mathcal{V}, \mathcal{E}, X, R)`.
    """

    try:
        # Get RDKit.Mol object from the given SMILES.
        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        # Global information of the molecule.
        n_rings = mol.GetRingInfo().NumRings()

        atom_feats = list()
        bonds = list()
        bond_feats = list()

        # Generate node-feature matrix.
        for atom in mol.GetAtoms():
            # Get elemental features of the atom.
            elem_attr = elem_feats[atom.GetAtomicNum() - 1, :]

            # Get hybridization type of the atom.
            hbd_type = get_one_hot_feat(cat_hbd, str(atom.GetHybridization()))

            # Get formal charge of the atom.
            fc_type = get_one_hot_feat(cat_fc, str(atom.GetFormalCharge()))

            # Check whether the atom belongs to the aromatic ring in the molecule.
            mem_aromatic = 1 if atom.GetIsAromatic() else 0

            # Get the number of bonds.
            degree = atom.GetDegree()

            # Get the number of hydrogen bonds.
            n_hs = atom.GetTotalNumHs()

            # Concatenate the given numerical features if they exist.
            if numeric_feats is None:
                atom_feats.append(numpy.hstack([elem_attr, hbd_type, fc_type, mem_aromatic,
                                                degree, n_hs, n_rings]))
            else:
                atom_feats.append(numpy.hstack([elem_attr, hbd_type, fc_type, mem_aromatic,
                                                degree, n_hs, n_rings, numeric_feats]))

        # Check bonds in the molecule.
        for bond in mol.GetBonds():
            bonds.append([bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()])
            bond_feats.append(get_one_hot_feat(cat_bond_types, str(bond.GetBondType())))

            bonds.append([bond.GetEndAtomIdx(), bond.GetBeginAtomIdx()])
            bond_feats.append(get_one_hot_feat(cat_bond_types, str(bond.GetBondType())))

        # Check isolated graph.
        if len(bonds) == 0:
            raise RuntimeError

        # Convert numpy.ndarray to torch.tensor.
        atom_feats = torch.tensor(atom_feats, dtype=torch.float)
        bonds = torch.tensor(bonds, dtype=torch.long).t().contiguous()
        bond_feats = torch.tensor(bond_feats, dtype=torch.float)
        gid = torch.tensor(gid, dtype=torch.long).view(1, 1)

        # Check target property.
        if target is not None:
            target = torch.tensor(target, dtype=torch.float).view(1, 1)

        return Data(x=atom_feats, edge_index=bonds, edge_attr=bond_feats, y=target, gid=gid)
    except RuntimeError:
        return None
