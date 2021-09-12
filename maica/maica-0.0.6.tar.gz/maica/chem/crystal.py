"""
Crystal Structure
-----------------
This module provides abstracted functions to convert the crystal structures into the mathematical graphs.
Like the molecular structure, the converted crystal structure are stored as a ``torch_geometric.Data`` object.
"""


import numpy
import torch
import pymatgen
from torch_geometric.data import Data
from pymatgen.core.structure import Structure
from sklearn.metrics import pairwise_distances
from maica.chem.base import atom_nums


def rbf(x: numpy.ndarray,
        mu: numpy.ndarray,
        beta: float):
    """
    Apply radial basis function to the given data ``x`` with the mean vector ``mu`` and a constant ``beta``.
    The Gaussian kernel was used to implement this radial basis function.

    :param x: (*numpy.ndarray*) An input data of radial basis function.
    :param mu: (*numpy.ndarray*) Feature-wise mean vector of the Gaussian kernel.
    :param beta: (*float*) A shape parameter of radial basis function.
    :return: Converted data of the input ``x``.
    """

    return numpy.exp(-(x - mu)**2 / beta**2)


def even_samples(min_val: float,
                 max_val: float,
                 n_samples: int):
    """
    Sample ``n_samples`` values evenly within ``[min_val, max_val]``.

    :param min_val: (*float*) The minimum value of the sample range.
    :param max_val: (*float*) The maximum value of the sample range.
    :param n_samples: (*int*) The number of samples.
    :return: An array of the samples.
    """

    samples = numpy.empty(n_samples)
    len_range = (max_val - min_val) / n_samples

    # Sample data evenly.
    for i in range(0, n_samples):
        samples[i] = min_val + len_range * (i + 1)

    return samples


def get_crystal_graph(elem_feats: numpy.ndarray,
                      path_cif: str,
                      numeric_feats: numpy.ndarray,
                      rbf_means: numpy.ndarray,
                      target: float = None,
                      gid: int = -1,
                      radius: float = 3.0):
    """
    Convert the crystallographic information framework (CIF) file into the mathematical graph
    :math:`G = (\mathcal{V}, \mathcal{E}, X, R)`, where :math:`\mathcal{V}` is a set of atoms,
    :math:`\mathcal{E}` is a set of bonds, :math:`X` is a atom-feature matrix,
    and :math:`R` is a bond-feature matrix.

    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :param path_cif: (*str*) The path of the CIF file of the crystal structure.
    :param numeric_feats: (*numpy.ndarray*) Numerical features of the crystal (e.g., density).
    :param rbf_means: (*numpy.ndarray*) A feature-wise mean vector of the Gaussian kernel for radial basis function to generate bond features.
    :param target: (*float, optional*) The target property that you want to predict from the crystal structure (*default* = ``None``).
    :param gid: (*int, optional*) An integer identifier of the crystal structure (*default* = -1).
    :param radius: (*float, optional*) The maximum value of the radius to define neighbor atoms (*default* = 3.0).
    :return: A crystal graph :math:`G = (\mathcal{V}, \mathcal{E}, X, R)`.
    """

    try:
        # Get Crystal object from the given CIF.
        crystal = Structure.from_file(path_cif)

        # Get the atomic information of the crystal structure.
        atom_coord, atom_feats = get_atom_info(crystal, elem_feats, numeric_feats, radius)

        # Get the bond information of the crystal structure.
        bonds, bond_feats = get_bond_info(atom_coord, rbf_means, radius)

        # Check isolated graph.
        if bonds is None:
            return None

        # Convert numpy.ndarray to torch.tensor.
        atom_feats = torch.tensor(atom_feats, dtype=torch.float)
        bonds = torch.tensor(bonds, dtype=torch.long).t().contiguous()
        bond_feats = torch.tensor(bond_feats, dtype=torch.float)
        gid = torch.tensor(gid, dtype=torch.long).view(1, 1)

        # Check target property.
        if target is not None:
            target = torch.tensor(target, dtype=torch.float).view(1, 1)

        # Return a generated crystal graph as torch_geometric.Data object.
        return Data(x=atom_feats, edge_index=bonds, edge_attr=bond_feats, y=target, gid=gid)
    except RuntimeError:
        return None


def get_atom_info(crystal: pymatgen.core.Structure,
                  elem_feats: numpy.ndarray,
                  numeric_feats: numpy.ndarray,
                  radius: float):
    """
    Calculate an atom-feature matrix and an atom-coordination matrix from the given ``pymatgen.core.Structure`` object.

    :param crystal: (*pymatgen.core.Structure*) The Pymatgen object of the crystal structure.
    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :param numeric_feats: (*numpy.ndarray*) Numerical features of the crystal (e.g., density).
    :param radius: (*float*) The maximum value of the radius to define neighbor atoms.
    :return: The atom-feature and atom-coordination matrices.
    """

    atoms = list(crystal.atomic_numbers)
    atom_coord = list()
    atom_feats = list()
    list_nbrs = crystal.get_all_neighbors(radius)

    # Get overall charge of the crystal structure.
    charge = crystal.charge

    # Get density in units of g/cc.
    density = float(crystal.density)

    # Get volume of the crystal structure.
    volume = crystal.volume

    coords = dict()
    for coord in list(crystal.cart_coords):
        coord_key = ','.join(list(coord.astype(str)))
        coords[coord_key] = True

    for i in range(0, len(list_nbrs)):
        nbrs = list_nbrs[i]

        for j in range(0, len(nbrs)):
            coord_key = ','.join(list(nbrs[j][0].coords.astype(str)))
            if coord_key not in coords.keys():
                coords[coord_key] = True
                atoms.append(atom_nums[nbrs[j][0].species_string])

    for coord in coords.keys():
        atom_coord.append(numpy.array([float(x) for x in coord.split(',')]))
    atom_coord = numpy.vstack(atom_coord)

    for i in range(0, len(atoms)):
        # Get elemental attributes of the atom.
        elem_attr = elem_feats[atoms[i] - 1, :]

        # Concatenate the given numerical features if they exist.
        if numeric_feats is None:
            atom_feats.append(numpy.hstack([elem_attr, charge, density, volume]))
        else:
            atom_feats.append(numpy.hstack([elem_attr, charge, density, volume, numeric_feats]))
    atom_feats = numpy.vstack(atom_feats).astype(float)

    return atom_coord, atom_feats


def get_bond_info(atom_coord: numpy.ndarray,
                  rbf_means: numpy.ndarray,
                  radius: float):
    """
    Calculate bond information of the crystal structure.
    If the crystal structure was converted into an isolated graph, it returns (None, None).

    :param atom_coord: (*numpy.ndarray*) The XYZ coordinates of the atoms in the crystal structure.
    :param rbf_means: (*numpy.ndarray*) A feature-wise mean vector of the Gaussian kernel for radial basis function to generate bond features.
    :param radius: (*float*) The maximum value of the radius to define neighbor atoms.
    :return: Indices of the bonds in the crystal structure and the bond-feature matrix.
    """

    bonds = list()
    bond_feats = list()
    pdist = pairwise_distances(atom_coord)

    # Calculate bond information.
    for i in range(0, atom_coord.shape[0]):
        for j in range(0, atom_coord.shape[0]):
            if i != j and pdist[i, j] <= radius:
                bonds.append([i, j])
                bond_feats.append(rbf(numpy.full(rbf_means.shape[0], pdist[i, j]), rbf_means, beta=0.5))

    if len(bonds) == 0:
        return None, None
    else:
        bonds = numpy.vstack(bonds)
        bond_feats = numpy.vstack(bond_feats)

        return bonds, bond_feats
