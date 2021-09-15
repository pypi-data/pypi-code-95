#! /usr/bin/env python3

import numpy as np
import numpy.linalg as la
from ase import neighborlist, Atoms
from ase.geometry.analysis import Analysis
import copy
import re
import scipy.optimize as spo
import itertools


atom_lab_num = {"H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7,
                "O": 8, "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13,
                "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19,
                "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25,
                "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Ga": 31,
                "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37,
                "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43,
                "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49,
                "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55,
                "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61,
                "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67,
                "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71, "Hf": 72, "Ta": 73,
                "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79,
                "Hg": 80, "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85,
                "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91,
                "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97,
                "Cf": 98, "Es": 99, "Fm": 100, "Md": 101, "No": 102, "Lr": 103,
                "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108,
                "Mt": 109, "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113,
                "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118}

metals = ["Li", "Be", "Na", "Mg", "Al", "K", "Ca", "Sc", "Ti", "V",
          "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Rb", "Sr",
          "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
          "In", "Sn", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm",
          "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf",
          "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb",
          "Bi", "Po", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu",
          "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf",
          "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl",
          "Mc", "Lv"]

atom_num_lab = dict(zip(atom_lab_num.values(), atom_lab_num.keys()))


def load_xyz(f_name: str, atomic_numbers: bool = False):
    """
    Load labels and coordinates from a .xyz file

    Parameters
    ----------
        f_name : str
            File name
        atomic_numbers : bool, optional
            If true, will read xyz file with atomic numbers and convert
            to labels

    Returns
    -------
        _labels : list
            atomic labels
        _coords : list
            list of 3 element lists containing xyz coordinates of each atom
    """

    if atomic_numbers:
        _numbers = list(np.loadtxt(f_name, skiprows=2, usecols=0, dtype=int))
        _labels = num_to_lab(_numbers)
    else:
        _labels = list(np.loadtxt(f_name, skiprows=2, usecols=0, dtype=str))

    # Set labels as capitals
    _labels = [lab.capitalize() for lab in _labels]

    _coords = list(np.loadtxt(f_name, skiprows=2, usecols=(1, 2, 3)))

    return _labels, _coords


def save_xyz(f_name: str, labels: list, coords: list,
             with_numbers: bool = False, verbose: bool = True,
             mask: list = [], atomic_numbers: bool = False):
    """
    Save an xyz file containing labels and coordinates

    Parameters
    ----------
        f_name : str
            File name
        labels : list
            atomic labels
        coords : list
            list of 3 element lists containing xyz coordinates of each atom
        with_numbers : bool, optional
            If True, add/overwrite numbers to labels before printing
        verbose : bool, optional
            Print information on filename to screen
        mask : list, optional
            n_atom list of 0 (exclude) and 1 (include) indicating which
            atoms to print
        atomic_numbers : bool, optional
            If true, will save xyz file with atomic numbers

    Returns
    -------
        None
    """

    # Option to have numbers added
    if with_numbers:
        # Remove and re-add numbers to be safe
        _labels = remove_numbers(labels)
        _labels = add_numbers(_labels)
    else:
        _labels = labels

    if len(mask) != 0:
        n_atoms = int(sum(mask))
        _mask = mask
    else:
        n_atoms = len(_labels)
        _mask = [1]*n_atoms

    # Apply mask
    _labels = _mask_list(_labels, _mask)
    _coords = _mask_list(coords, _mask)

    if atomic_numbers:
        _labels = remove_numbers(_labels)
        _numbers = lab_to_num(_labels)
        _identifier = _numbers
    else:
        _identifier = _labels

    with open(f_name, 'w') as f:
        f.write("{:d}\n\n".format(n_atoms))
        for it, (ident, trio) in enumerate(zip(_identifier, _coords)):
            f.write("{:5} {:15.7f} {:15.7f} {:15.7f} \n".format(ident, *trio))

    if verbose:
        print("New xyz file written to {}".format(f_name))

    return


def remove_numbers(labels: list):
    """
    Remove numbers from a list of atomic labels

    Parameters
    ----------
        labels : list
            atomic labels

    Returns
    -------
        labels_nn : list
            atomic labels without numbers
    """

    labels_nn = []
    for label in labels:
        no_digits = []
        for i in label:
            if not i.isdigit():
                no_digits.append(i)
        result = ''.join(no_digits)
        labels_nn.append(result)

    return labels_nn


def add_numbers(labels: list, style: str = 'per_element'):
    """
    Add numbers to a list of atomic labels

    Parameters
    ----------
        labels : list
            atomic labels
        style : str, optional
            {'per_element', 'sequential'}
                'per_element' : Number by element e.g. Dy1, Dy2, N1, N2, etc.
                'sequential' : Number the atoms 1->N regardless of element

    Returns
    -------
        labels_wn : list
            atomic labels with numbers
    """

    # remove numbers just in case
    labels_nn = remove_numbers(labels)

    # Just number the atoms 1->N regardless of element
    if style == 'sequential':
        labels_wn = ['{}{:d}'.format(lab, it+1)
                     for (it, lab) in enumerate(labels)]

    # Number by element Dy1, Dy2, N1, N2, etc.
    if style == 'per_element':
        # Get list of elements
        atoms = set(labels_nn)
        # Create dict to keep track of index of current atom of each element
        atom_count = {atom: 1 for atom in atoms}
        # Create labelled list of elements
        labels_wn = []
        for lab in labels_nn:
            # Number according to dictionary
            labels_wn.append("{}{:d}".format(lab, atom_count[lab]))
            # Then add one to dictionary
            atom_count[lab] += 1

    return labels_wn


def count_n_atoms(form_str: str):
    """
    Count number of atoms in a chemical formula

    Parameters
    ----------
        form_str : str
            chemical formula string

    Returns
    -------
        n_atoms : int
            number of atoms in chemical formula
    """

    form_dict = formstr_to_formdict(form_str)

    n_atoms = sum(form_dict.values())

    return n_atoms


def index_elements(labels: list, shift: int = 0):
    """
    Return dictionary of element (keys) and indices (values) from list
    of labels

    Parameters
    ----------
        labels : list
            atomic labels
        shift : int, optional
            additive shift to apply to all indices

    Returns
    -------
        ele_index : dict
            dictionary of element (keys) and indices (values)
    """

    labels_nn = remove_numbers(labels)

    ele_index = {}

    for it, lab in enumerate(labels_nn):
        try:
            ele_index[lab].append(it+shift)
        except KeyError:
            ele_index[lab] = [it+shift]

    return ele_index


def count_elements(labels: list):
    """
    Count number of each element in a list of elements

    Parameters
    ----------
        labels : list
            atomic labels
    Returns
    -------
        ele_count : dict
            dictionary of elements (keys) and counts (vals)
    """

    labels_nn = remove_numbers(labels)

    ele_count = {}

    for lab in labels_nn:
        try:
            ele_count[lab] += 1
        except KeyError:
            ele_count[lab] = 1

    return ele_count


def get_formula(labels: list):
    """
    Returns empirical formula in alphabetical order given a list of labels

    Parameters
    ----------
        labels : list
            atomic labels
    Returns
    -------
        formula : str
            Empirical formula in alphabetical order
    """

    formdict = count_elements(labels)

    formula = formdict_to_formstr(formdict)

    return formula


def formstr_to_formdict(form_str: str):
    """
    Converts formula string into dictionary of {atomic label:quantity} pairs

    Parameters
    ----------
        form_string : str
            Chemical formula as string

    Returns
    -------
        form_dict : dict
            dictionary of {atomic label:quantity} pairs
    """

    form_dict = {}
    # Thanks stack exchange!
    s = re.sub
    f = s("[()',]", '', str(eval(s(',?(\d+)', r'*\1,', s('([A-Z][a-z]*)', # noqa
          r'("\1",),', form_str))))).split()
    for c in set(f):
        form_dict[c] = f.count(c)

    return form_dict


def formdict_to_formstr(form_dict: dict, include_one: bool = False):
    """
    Converts dictionary of {atomic label:quantity} pairs into
    a single formula string in alphabetical order

    Parameters
    ----------
        form_dict : dict
            dictionary of {atomic label:quantity} pairs
        include_one : bool, optional
            Include 1 in final chemical formula e.g. C1H4

    Returns
    -------
        form_string : str
            Chemical formula as string in alphabetical order
    """

    # Formula labels and quantities as separate lists with same order
    form_labels = ["{:s}".format(key) for key in form_dict.keys()]
    form_quants = [val for val in form_dict.values()]

    # Quantities of each element as a string
    if include_one:
        form_quants_str = ["{:d}".format(quant)
                           for quant in form_quants]
    else:
        form_quants_str = ["{:d}".format(quant)
                           if quant > 1 else ""
                           for quant in form_quants]

    # Sort labels in alphabetical order
    order = np.argsort(form_labels).tolist()
    form_labels_o = [form_labels[o] for o in order]
    # Use same ordering for quantities
    form_quants_str_o = [form_quants_str[o] for o in order]

    # Make list of elementquantity strings
    form_list = [el + quant
                 for el, quant in zip(form_labels_o, form_quants_str_o)]

    # Join strings together into empirical formula
    form_string = ''.join(form_list)

    return form_string


def contains_metal(form_string: str):
    """
    Indicates if a metal is found in a chemical formula string

    Parameters
    ----------
        form_string : str
            Chemical formula as string

    Returns
    -------
        metal_found : int
            Combined atomic labels
    """
    metal_found = 0

    for metal in metals:
        if metal in form_string:
            metal_found = 1
            break

    return metal_found


def combine_xyz(labels_1: list, labels_2: list,
                coords_1: list, coords_2: list):
    """
    Combine two sets of labels and coordinates

    Parameters
    ----------
        labels_1 : list
            Atomic labels
        coords_1 : list
            list of lists of xyz coordinates of each atom
        labels_2 : list
            Atomic labels
        coords_2 : list
            list of lists of xyz coordinates of each atom

    Returns
    -------
        labels : list
            Combined atomic labels
        coords : list
            Combined list of lists of xyz coordinates of each atom
    """

    # Concatenate labels lists
    labels = labels_1+labels_2

    # Concatenate coordinate lists
    coords = coords_1+coords_2

    return labels, coords


def get_neighborlist(labels: list, coords: list, adjust_cutoff: dict = {}):
    """
    Calculate ASE neighbourlist with cutoffs

    Parameters
    ----------
        labels : list
            Atomic labels
        coords : list
            list of lists of xyz coordinates of each atom
        adjust_cutoff : dict, optional
            dictionary of atoms (keys) and new cutoffs (values)

    Returns
    -------
        neigh_list : ASE neighbourlist object
            Neighbourlist for system
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Load molecule
    mol = Atoms(''.join(labels_nn), positions=coords)

    # Define cutoffs for each atom using atomic radii
    cutoffs = neighborlist.natural_cutoffs(mol)

    # Modify cutoff if requested
    if adjust_cutoff:
        for it, label in enumerate(labels_nn):
            if label in adjust_cutoff.keys():
                cutoffs[it] = adjust_cutoff[label]

    # Create neighbourlist using cutoffs
    neigh_list = neighborlist.NeighborList(cutoffs=cutoffs,
                                           self_interaction=False,
                                           bothways=True)

    # Update this list by specifying the atomic positions
    neigh_list.update(mol)

    return neigh_list


def get_adjacency(labels: list, coords: list, adjust_cutoff: dict = {},
                  save: bool = False, f_name: str = "adjacency.dat"):
    """
    Calculate adjacency matrix using ASE built in cutoffs with option to
    modify them

    Parameters
    ----------
        labels : list
            Atomic labels
        coords : list
            list of lists of xyz coordinates of each atom
        adjust_cutoff : dict, optional
            dictionary of atoms (keys) and new cutoffs (values)

    Returns
    -------
        adjacency : np.array
            Adjacency matrix with same order as labels/coords
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Get ASE neighbourlist object
    neigh_list = get_neighborlist(labels_nn, coords,
                                  adjust_cutoff=adjust_cutoff)

    # Create adjacency matrix
    adjacency = neigh_list.get_connectivity_matrix(sparse=False)

    # Save adjacency matrix to file
    if save:
        np.savetxt(f_name, adjacency, fmt="%i")
        print('Adjacency matrix saved to {}'.format(f_name))

    return adjacency


def get_bonds(labels: list, coords: list, neigh_list=None,
              f_name: str = 'bonds.dat', save: bool = False,
              verbose: bool = True, style: bool = 'indices'):
    """
    Calculate and save list of atoms between which there is a bond.
    Using ASE. Only unique angles are saved.
    e.g. 0-1 and not 1-0

    Parameters
    ----------
        labels : list
            Atomic labels
        coords : list
            list of lists of xyz coordinates of each atom

    Keyword arguments:
        neigh_list : ASE neighbourlist object, optional
            neighbourlist of system
        f_name : str, optional
            filename to save bond list to
        save : bool, optional
            Save bond list to file
        verbose : bool, optional
            Print number of bonds to screen
        style : str, optional
            {'index','label'}
                indices : Bond list contains atom number
                labels  : Bond list contains atom label

    Returns
    -------
        bonds : list
            list of unique bonds (atom pairs)
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Create molecule object
    mol = Atoms(''.join(labels_nn), positions=coords)

    # Get neighbourlist if not provided to function
    if not neigh_list:
        neigh_list = get_neighborlist(labels, coords)

    # Get object containing analysis of molecular structure
    ana = Analysis(mol, nl=neigh_list)

    # Get bonds from ASE
    # Returns: list of lists of lists containing UNIQUE bonds
    # Defined as
    # Atom 1 : [bonded atom, bonded atom], ...
    # Atom 2 : [bonded atom, bonded atom], ...
    # Atom n : [bonded atom, bonded atom], ...
    # Where only the right hand side is in the list
    is_bonded_to = ana.unique_bonds

    # Remove weird outer list wrapping the entire thing twice...
    is_bonded_to = is_bonded_to[0]
    # Create list of bonds (atom pairs) by appending lhs of above
    # definition to each element of the rhs
    bonds = []
    for it, ibt in enumerate(is_bonded_to):
        for atom in ibt:
            bonds.append([it, atom])

    # Count bonds
    n_bonds = len(bonds)

    # Set save format and convert to atomic labels if requested
    if style == 'indices':
        save_fmt = "%i"
    elif style == 'labels':
        bonds = [[labels[atom1], labels[atom2]] for atom1, atom2 in bonds]
        save_fmt = "%s"

    # Save bond list to file
    if save:
        np.savetxt(f_name, bonds, fmt=save_fmt)
        print('Bond list saved to {}'.format(f_name))

    # Print number of bonds to screen
    if verbose:
        print('{:d}'.format(n_bonds)+' bonds')

    return bonds


def get_angles(labels: list, coords: list, neigh_list=None,
               f_name: str = 'angles.dat', save: bool = False,
               verbose: bool = True, style: bool = 'indices'):
    """
    Calculate and save list of atoms between which there is a bond angle.
    Using ASE. Only unique angles are saved.
    e.g. 0-1-2 but not 2-1-0

    Parameters
    ----------
        labels : list
            Atomic labels
        coords : list
            list of lists of xyz coordinates of each atom
        neigh_list : ASE neighbourlist object, optional
            neighbourlist of system
        f_name : str, optional
            filename to save angle list to
        save : bool, optional
            Save angle list to file
        verbose : bool, optional
            Print number of angles to screen
        style : str, optional
            {'index','label'}
                indices : Angle list contains atom number
                labels  : Angle list contains atom label

    Returns
    -------
        angles : list
            list of unique angles (atom trios)
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Create molecule object
    mol = Atoms(''.join(labels_nn), positions=coords)

    # Get neighbourlist if not provided to function
    if not neigh_list:
        neigh_list = get_neighborlist(labels, coords)

    # Get object containing analysis of molecular structure
    ana = Analysis(mol, nl=neigh_list)

    # Get angles from ASE
    # Returns: list of lists of lists containing UNIQUE angles
    # Defined as
    # Atom 1 : [[atom,atom], [atom,atom]], ...
    # Atom 2 : [[atom,atom], [atom,atom]], ...
    # Atom n : [[atom,atom], [atom,atom]], ...
    # Where only the right hand side is in the list
    is_angled_to = ana.unique_angles

    # Remove weird outer list wrapping the entire thing twice...
    is_angled_to = is_angled_to[0]
    # Create list of angles (atom trios) by appending lhs of above
    # definition to each element of the rhs
    angles = []
    for it, ibt in enumerate(is_angled_to):
        for atoms in ibt:
            angles.append([it, *atoms])

    # Count angles
    n_angles = len(angles)

    # Set save format and convert to atomic labels if requested
    if style == 'indices':
        save_fmt = "%i"
    elif style == 'labels':
        angles = [[labels[atom1], labels[atom2], labels[atom3]]
                  for atom1, atom2, atom3 in angles]
        save_fmt = "%s"

    # Save angle list to file
    if save:
        np.savetxt(f_name, angles, fmt=save_fmt)
        print('Angle list saved to {}'.format(f_name))

    # Print number of angles to screen
    if verbose:
        print('{:d}'.format(n_angles)+' angles')

    return angles


def get_dihedrals(labels: list, coords: list, neigh_list=None,
                  f_name: str = 'dihedrals.dat', save: bool = False,
                  verbose: bool = True, style: bool = 'indices'):
    """
    Calculate and save list of atoms between which there is a dihedral.
    Using ASE. Only unique angles are saved.
    e.g. 0-1-2-3 but not 3-2-1-0

    Parameters
    ----------
        labels : list
            Atomic labels
        coords : list
            list of lists of xyz coordinates of each atom
        neigh_list : ASE neighbourlist object, optional
            neighbourlist of system
        f_name : str, optional
            filename to save angle list to
        save : bool, optional
            Save angle list to file
        verbose : bool, optional
            Print number of dihedrals to screen
        style : str, optional
            {'index','label'}
                indices : Dihedral list contains atom number
                labels  : Dihedral list contains atom label

    Returns
    -------
        dihedrals : list
            list of unique dihedrals (atom quads)
    """

    # Remove labels if present
    labels_nn = remove_numbers(labels)

    # Create molecule object
    mol = Atoms(''.join(labels_nn), positions=coords)

    # Get neighbourlist if not provided to function
    if not neigh_list:
        neigh_list = get_neighborlist(labels, coords)

    # Get object containing analysis of molecular structure
    ana = Analysis(mol, nl=neigh_list)

    # Get dihedrals from ASE
    # Returns: list of lists of lists containing UNIQUE dihedrals
    # Defined as
    # Atom 1 : [[atom,atom,atom], [atom,atom,atom]], ...
    # Atom 2 : [[atom,atom,atom], [atom,atom,atom]], ...
    # Atom n : [[atom,atom,atom], [atom,atom,atom]], ...
    # Where only the right hand side is in the list
    is_dihedraled_to = ana.unique_dihedrals

    # Remove weird outer list wrapping the entire thing twice...
    is_dihedraled_to = is_dihedraled_to[0]
    # Create list of dihedrals (atom quads) by appending lhs of above
    # definition to each element of the rhs
    dihedrals = []
    for it, ibt in enumerate(is_dihedraled_to):
        for atoms in ibt:
            dihedrals.append([it, *atoms])

    # Count dihedrals
    n_dihedrals = len(dihedrals)

    # Set save format and convert to atomic labels if requested
    if style == 'indices':
        save_fmt = "%i"
    elif style == 'labels':
        dihedrals = [
                     [
                      labels[atom1],
                      labels[atom2],
                      labels[atom3],
                      labels[atom4]
                     ]
                     for atom1, atom2, atom3, atom4 in dihedrals
                    ]
        save_fmt = "%s"

    # Save dihedral list to file
    if save:
        np.savetxt(f_name, dihedrals, fmt=save_fmt)
        print('Dihedral list saved to {}'.format(f_name))

    # Print number of dihedrals to screen
    if verbose:
        print('{:d}'.format(n_dihedrals)+' dihedrals')

    return dihedrals


def lab_to_num(labels: list):
    '''
    Convert atomic label to atomic number

    Parameters
    ----------
        labels : list
            Atomic labels

    Returns
    -------
        numbers : list
            Atomic numbers
    '''

    labels_nn = remove_numbers(labels)

    numbers = [atom_lab_num[lab] for lab in labels_nn]

    return numbers


def num_to_lab(numbers: list, numbered: bool = True):
    '''
    Convert atomic number to atomic labels

    Parameters
    ----------
        numbers : list
            Atomic numbers
        numbered : bool, optional
            Add indexing number to end of atomic labels

    Returns
    -------
        labels : list
            Atomic labels
    '''

    labels = [atom_num_lab[num] for num in numbers]

    if numbered:
        labels_wn = add_numbers(labels)
    else:
        labels_wn = labels

    return labels_wn


def reflect_coords(coords: list):
    """
    Reflect coordinates through xy plane

    Parameters
    ----------
        coords : list
            list of lists of xyz coordinates of each atom

    Returns
    -------
        coords : list
            list of lists of xyz coordinates of each atom

    """

    # Calculate normal to plane
    x = [1, 0, 0]
    y = [0, 1, 0]
    normal = np.cross(x, y)

    # Set up transformation matrix
    # https://en.wikipedia.org/wiki/Transformation_matrix#Reflection_2
    # Can reflect in any plane but xy has been used
    trans_mat = np.zeros([3, 3])

    trans_mat[0, 0] = 1. - 2.*normal[0]**2.
    trans_mat[1, 0] = -2.*normal[0]*normal[1]
    trans_mat[2, 0] = -2.*normal[0]*normal[2]
    trans_mat[0, 1] = -2.*normal[0]*normal[1]
    trans_mat[1, 1] = 1. - 2.*normal[1]**2.
    trans_mat[2, 1] = -2.*normal[1]*normal[2]
    trans_mat[0, 2] = -2.*normal[0]*normal[2]
    trans_mat[1, 2] = -2.*normal[1]*normal[2]
    trans_mat[2, 2] = 1. - 2.*normal[2]**2.

    # Apply operations
    coords = coords @ trans_mat

    return coords


def remove_broken(labels: list, coords: list, formulae: list,
                  adjust_cutoff: dict = {}, verbose: bool = False,
                  save: bool = False, frag_f_name: str = "fragments.xyz",
                  clean_f_name: str = "clean.xyz",
                  mask: list = [], skip: list = []):
    """
    Removes structures from coords which do not match formula in formulae
    Uses ASE to generate adjacency matrix and draw out bonding in coords
    allowing formulae of fragments to be found.


    Parameters
    ----------
        labels : list
            list of atomic labels
        coords : list
            list of lists of xyz coordinates of each atom
        formulae : list
            list of chemical formulae stored as dictionaries with atomic
            symbol (key) count (val) pairs
        adjust_cutoff : dict, optional
            dictionary of atoms (keys) and new cutoffs (values)
        verbose : bool, optional
            print molecule count to screen
        save : bool, optional
            Save molecules and incomplete fragments to separate xyz files
        frag_f_name : str, optional
            Name for xyz file containing fragmented structures
        clean_f_name : str, optional
            Name for xyz file containing full molecules
        mask : list, optional
            list of 0 (exclude) and 1 (include) for each element
                - if used, final lists will exclude masked elements
        skip : list, optional
            List of atomic indices which shall not be visited when tracing
            bonding network
    Returns
    -------
        labels_clean : list
            list of atomic labels for full molecules
        coords_clean (list)  :
            list of lists of xyz coordinates of each atom for full molecules
        labels_fragments : list
            list of atomic labels for fragments
        coords_fragments : list
            list of lists of xyz coordinates of each atom for fragments
        mol_indices     : dict
            dictionary containing indices of complete molecules -
                keys = molecular formula,
                vals = list of lists of atomic indices
                        for each atom
    """

    # Remove label numbers if present
    _labels = remove_numbers(labels)

    n_atoms = len(labels)

    # Set up array of atoms to ignore
    # This becomes the array of atomic indices which have been
    # visited
    if skip:
        visited = set(skip)
    else:
        visited = set()

    # Set up mask
    if mask:
        _mask = mask
    else:
        _mask = [1]*n_atoms

    # Apply mask
    _labels = _mask_list(_labels, _mask)
    _coords = _mask_list(coords, _mask)

    # Generate adjacency matrix using ASE
    adjacency = get_adjacency(_labels, _coords, adjust_cutoff=adjust_cutoff)

    # Count number of atoms
    n_atoms = len(labels)

    # Mask for fragment atom indices
    # 1 = Fragment atom
    # 0 = Not a fragment atom
    frag_mask = np.zeros(n_atoms)

    # Set starting position as first unvisited/unskipped atom
    unvisited = [ind for ind, vis
                 in zip(np.arange(n_atoms), sorted(visited)) if ind != vis]
    if unvisited:
        start = min(unvisited)
    else:
        start = 0
    # Set current fragment as start atom
    curr_frag = {start}

    # Dictionary of molecular_formula:count pairs
    num_molecules = {formdict_to_formstr(form): 0 for form in formulae}
    # Dictionary of molecular_formula:[[indices_mol1], [indices_mol2]] pairs
    mol_indices = {formdict_to_formstr(form): [] for form in formulae}

    # Loop over adjacency matrix and trace out bonding network
    # Make a first pass, recording in a list the atoms which are bonded to the
    # first atom.
    # Then make another pass, and record in another list all the atoms bonded
    # to those in the previous list
    # and again, and again etc.
    while len(visited) != n_atoms:
        # Keep copy of current fragment indices to check against for changes
        prev_frag = copy.copy(curr_frag)
        for index in prev_frag:
            # Find bonded atoms and add to current fragment
            indices = list(np.nonzero(adjacency[:, index])[0])
            curr_frag.update(indices)

        # If no changes in fragment last pass, then a complete structure must
        # have been found
        if prev_frag == curr_frag:

            # Keep list of all atom indices which have been visited
            visited.update(curr_frag)

            # Generate molecular formula of current fragment
            curr_labels = [_labels[it] for it in curr_frag]
            curr_formula = count_elements(curr_labels)

            # Check if formula matches any of user provided formulae
            if any(form == curr_formula for form in formulae):
                num_molecules[formdict_to_formstr(curr_formula)] += 1
                # Reorder indices to have same label order as formula
                # e.g. H2O --> H, H, O
                curr_frag = list(curr_frag)
                ord_frag = [
                            curr_frag[o]
                            for o in np.argsort(lab_to_num(curr_labels))
                           ]
                mol_indices[formdict_to_formstr(curr_formula)].append(ord_frag)
            # If there are no matches, then mark the fragment as a fragment
            else:
                for it in curr_frag:
                    frag_mask[it] = 1

            # Move starting point to next lowest index which has
            # not been visited
            unvisited = [
                         ind
                         for ind in np.arange(n_atoms) if ind not in visited
                        ]
            if not unvisited:
                break

            # Reset lists of labels and indices ready for next cycle
            curr_frag = {min(unvisited)}

    # Print information on how many of each formula have been found
    if verbose:
        for mol in num_molecules.keys():
            print("There is/are {:10d} molecule(s)/ion(s) of {}".format(
                num_molecules[mol], mol)
            )

    # Get indices of all molecules
    # Exclude molecules that were not found in xyz file
    # i.e. inds_clean is a list of lists
    # [
    #  [indices_of_all_instances_of_molecule1],
    #  [indices_of_all_instances_of_molecule2]
    # ]
    inds_clean = [
                  [item for sublist in molecule for item in sublist]
                  for molecule in mol_indices.values() if len(molecule) > 0
                 ]
    # Get all molecular formulae in a list
    form_clean = [
                  formula
                  for formula in mol_indices.keys()
                  if len(mol_indices[formula]) > 0
                 ]

    # Reorder inds_clean so that metal containing molecules are at the start
    metals_top_order = np.argsort(
        [not contains_metal(formula) for formula in form_clean]
        )
    inds_clean = _reorder_list(inds_clean, metals_top_order)

    # Concatenate inds_clean into a single big list
    # [
    #  indices_of_all_instances_of_molecule1,
    #  indices_of_all_instances_of_molecule2
    # ]
    inds_clean = list(itertools.chain(*inds_clean))

    # Create output array of labels and coordinates where molecules
    # are grouped together, and
    # metal containing molecules are at the top using inds_clean to
    # set that order
    labels_clean = _reorder_list(_labels, inds_clean)
    coords_clean = _reorder_list(_coords, inds_clean)

    # Mask off molecules to get output array of fragments
    # order does not matter here
    labels_fragments = _mask_list(_labels, frag_mask)
    coords_fragments = _mask_list(_coords, frag_mask)

    # Save clean and fragmented coordinates to file
    if save:
        # Write new xyz file without broken molecules
        # Save xyz for complete molecules
        save_xyz(clean_f_name, labels_clean, coords_clean)
        # Save xyz for fragments
        save_xyz(frag_f_name, labels_fragments, coords_fragments)

    return [
        labels_clean, coords_clean,
        labels_fragments, coords_fragments, mol_indices
        ]


def _mask_list(_list: list, mask: list, opp_mask: bool = False):
    """
    Truncates list to only include elements specified by 1 in mask

    Parameters
    ----------
        _list : list
            list to mask
        mask : list
            list of 0 (exclude) and 1 (include) for each element

        opp_mask : bool, optional
            Apply mask in opposite fashion:
                0 (include) and 1 (exclude)

    Returns
    -------
        _list_masked : float Masked list
    """

    # Flip mask other way around if requested
    if opp_mask:
        _mask = [not ma for ma in mask]
    else:
        _mask = mask

    # Apply mask to list
    _list_masked = [_l for it, _l in enumerate(_list) if _mask[it]]

    return _list_masked


def _reorder_list(_list: list, order: list):
    """
    Reorders list using indices in order

    Parameters
    ----------
        _list : list
            list to reorder
        order : list
            New order for list

    Returns
    -------
        _list_reordered : float
            Reordered list
    """

    # Apply mask to list
    _list_reordered = [_list[it] for it in order]

    return _list_reordered


def _calculate_rmsd(coords_1: list, coords_2: list):
    """
    Calculates RMSD between two structures
    RMSD = sqrt(mean(deviations**2))
    Where deviations are defined as norm([x1,y1,z1]-[x2,y2,z2])

    Parameters
    ----------
        coords_1 : list
            list of lists of xyz coordinates of each atom
        coords_2 : list
            list of lists of xyz coordinates of each atom

    Returns
    -------
        rmsd : float
            Root mean square of norms of deviation between two structures
    """

    # Check there are the same number of coordinates
    assert(len(coords_1) == len(coords_2))

    # Calculate difference between [x,y,z] of atom pairs
    diff = [trio_1 - trio_2 for trio_1, trio_2 in zip(coords_1, coords_2)]

    # Calculate square norm of difference
    norms_sq = [la.norm(trio)**2 for trio in diff]

    # Calculate mean of squared norms
    mean = np.mean(norms_sq)

    # Take square root of mean
    rmsd = np.sqrt(mean)

    return rmsd


def calculate_rmsd(coords_1: list, coords_2: list, mask_1: list = [],
                   mask_2: list = [], order_1: list = [], order_2: list = []):
    """
    Calculates RMSD between two structures
    RMSD = sqrt(mean(deviations**2))
    Where deviations are defined as norm([x1,y1,z1]-[x2,y2,z2])
    If coords_1 and coords_2 are not the same length, then a mask array can be
    provided for either/both and is applied prior to the calculation
    coords_1 and coords_2 can also be reordered if new orders are specified
        - note this occurs BEFORE masking

    Parameters
    ----------
        coords_1 : list
            list of lists of xyz coordinates of each atom
        coords_2 : list
            list of lists of xyz coordinates of each atom

        mask_1 : list
            list of 0 (exclude) and 1 (include) for each element in coords_1
        mask_2 : list
            list of 0 (exclude) and 1 (include) for each element in coords_2
        order_1 : list
            list of new indices for coords_1 - applied BEFORE masking
        order_2 : list
            list of new indices for coords_2 - applied BEFORE masking

    Returns
    -------
        rmsd : float
            Root mean square of norms of deviation between two structures
    """

    # Set up new ordering
    if order_1:
        _order_1 = order_1
    else:
        _order_1 = range(len(coords_1))

    if order_2:
        _order_2 = order_2
    else:
        _order_2 = range(len(coords_2))

    # Apply new order
    _coords_1 = _reorder_list(coords_1, _order_1)
    _coords_2 = _reorder_list(coords_2, _order_2)

    # Set up masks
    if mask_1:
        _mask_1 = mask_1
    else:
        _mask_1 = [1]*len(coords_1)

    # Set up masks
    if mask_2:
        _mask_2 = mask_2
    else:
        _mask_2 = [1]*len(coords_2)

    # Apply masks
    _coords_1 = _mask_list(_coords_1, _mask_1)
    _coords_2 = _mask_list(_coords_2, _mask_2)

    # Calculate rmsd
    rmsd = _calculate_rmsd(_coords_1, _coords_2)

    return rmsd


def rotate_coords(coords: list, alpha: float, beta: float, gamma: float):
    """
    Rotates coordinates by alpha, beta, gamma using the zyz convention
    https://easyspin.org/easyspin/documentation/eulerangles.html

    Parameters
    ----------
        coords_1 : list
            list of lists of xyz coordinates of each atom
        alpha : float
            alpha angle in radians
        beta : float
            beta  angle in radians
        gamma : float
            gamma angle in radians

    Returns
    -------
        rot_coords : list
            list of lists of xyz coordinates of each atom after rotation
    """

    R = np.zeros([3, 3])

    # Build rotation matrix
    R[0, 0] = np.cos(gamma)*np.cos(beta)*np.cos(alpha) - np.sin(gamma) * np.sin(alpha) # noqa
    R[0, 1] = np.cos(gamma)*np.cos(beta)*np.sin(alpha) + np.sin(gamma) * np.cos(alpha) # noqa
    R[0, 2] = -np.cos(gamma)*np.sin(beta)
    R[1, 0] = -np.sin(gamma)*np.cos(beta)*np.cos(alpha) - np.cos(gamma) * np.sin(alpha) # noqa
    R[1, 1] = -np.sin(gamma)*np.cos(beta)*np.sin(alpha) + np.cos(gamma) * np.cos(alpha) # noqa
    R[1, 2] = np.sin(gamma)*np.sin(beta)
    R[2, 0] = np.sin(beta)*np.cos(alpha)
    R[2, 1] = np.sin(beta)*np.sin(alpha)
    R[2, 2] = np.cos(beta)

    # Create (n,3) matrix from coords list
    _coords = np.asarray(coords).T

    # Apply rotation matrix
    rot_coords = R @ _coords

    # Convert back to (3,n) matrix
    rot_coords = rot_coords.T

    # Convert back to list
    rot_coords = list(rot_coords)

    return rot_coords


def minimise_rmsd(coords_1: list, coords_2: list, mask_1: list = [],
                  mask_2: list = [], order_1: list = [], order_2: list = []):
    """
    Minimising the RMSD between two structures
    If coords_1 and coords_2 are not the same length, then a mask array can be
    provided for either/both and is applied prior to the calculation
    coords_1 and coords_2 can also be reordered if new orders are specified
        - note this occurs BEFORE masking

    Parameters
    ----------
        coords_1 : list
            list of lists of xyz coordinates of each atom
        coords_2 : list
            list of lists of xyz coordinates of each atom

        mask_1 (list)  :
            list of 0 (exclude) and 1 (include) for each element in coords_1
        mask_2 (list)  :
            list of 0 (exclude) and 1 (include) for each element in coords_2
        order_1 : list
            list of new indices for coords_1 - applied BEFORE masking
        order_2 : list
            list of new indices for coords_2 - applied BEFORE masking

    Returns
    -------
        rmsd : float
            Root mean square of norms of deviation between two structures
    """

    # Set up new ordering
    if order_1:
        _order_1 = order_1
    else:
        _order_1 = range(len(coords_1))

    if order_2:
        _order_2 = order_2
    else:
        _order_2 = range(len(coords_2))

    # Apply new order
    _coords_1 = _reorder_list(coords_1, _order_1)
    _coords_2 = _reorder_list(coords_2, _order_2)

    # Set up masks
    if mask_1:
        _mask_1 = mask_1
    else:
        _mask_1 = [1]*len(coords_1)

    # Set up masks
    if mask_2:
        _mask_2 = mask_2
    else:
        _mask_2 = [1]*len(coords_2)

    # Apply masks
    _coords_1 = _mask_list(_coords_1, _mask_1)
    _coords_2 = _mask_list(_coords_2, _mask_2)

    # Fit alpha, beta, and gamma to minimise rmsd
    result = spo.least_squares(lambda angs: _rotate_and_rmsd(
            angs, _coords_1, _coords_2), x0=(1., 1., 1.))

    # Get optimum angles
    [alpha, beta, gamma] = result.x
    rmsd = result.cost

    return rmsd, alpha, beta, gamma


def _rotate_and_rmsd(angs: list, coords_1: list, coords_2: list):
    """
    Rotates coords_1 by alpha, beta, gamma using the zyz convention
    https://easyspin.org/easyspin/documentation/eulerangles.html
    then calcualtes the rmsd between coords_1 and coords_2

    Parameters
    ----------
        coords_1 : list
            list of lists of xyz coordinates of each atom of first system
        coords_2 : list
            list of lists of xyz coordinates of each atom of second system
        angs : list
            alpha, beta, gamma in radians

    Returns
    -------
        rot_coords : list
            list of lists of xyz coordinates of each atom after rotation
    """

    # Rotate coordinates of first system
    _coords_1 = rotate_coords(coords_1, angs[0], angs[1], angs[2])

    # Calculate rmsd between rotated first system and original second system
    rmsd = _calculate_rmsd(_coords_1, coords_2)

    return rmsd
