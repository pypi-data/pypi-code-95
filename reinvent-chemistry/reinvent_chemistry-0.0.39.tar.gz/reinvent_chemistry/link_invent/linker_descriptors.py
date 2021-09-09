import numpy as np

from rdkit.Chem import Mol, GetDistanceMatrix

from reinvent_chemistry.link_invent.bond_breaker import BondBreaker


class LinkerDescriptors:
    """ Molecular descriptors specific for properties of the linker """
    def __init__(self):
        self._bond_breaker = BondBreaker()

    def effective_length(self, labeled_mol: Mol) -> int:
        linker_mol = self._bond_breaker.get_linker_fragment(labeled_mol)
        ap_idx = [i[0] for i in self._bond_breaker.get_labeled_atom_dict(linker_mol).values()]
        distance_matrix = GetDistanceMatrix(linker_mol)
        effective_linker_length = distance_matrix[ap_idx[0], ap_idx[1]]
        return int(effective_linker_length)

    def max_graph_length(self, labeled_mol) -> int:
        linker_mol = self._bond_breaker.get_linker_fragment(labeled_mol)
        distance_matrix = GetDistanceMatrix(linker_mol)
        max_graph_length = np.max(distance_matrix)
        return int(max_graph_length)

    def length_ratio(self, labeled_mol: Mol) -> float:
        """
        ratio of the maximum graph length of the linker to the effective linker length
        """
        max_length = self.max_graph_length(labeled_mol)
        effective_length = self.effective_length(labeled_mol)
        return effective_length/ max_length * 100



