# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import dataclasses as dcls
from typing import Dict, Optional, Sequence

import numpy as nmpy
import scipy.optimize as spop
from scipy.spatial import distance as dstc

from cell_tracking_BC.task.jaccard import PseudoJaccard
from cell_tracking_BC.task.tracking.generic import context_t
from cell_tracking_BC.task.tracking.main import array_t
from cell_tracking_BC.type.cell import cell_t


@dcls.dataclass(repr=False, eq=False)
class gmb_context_t(context_t):
    """
    gmb: Global-Matching-Based tracking
    """

    shape: Sequence[int] = None
    min_jaccard: float = 0.75
    labeled_map: array_t = dcls.field(init=False, default=None)
    next_labeled_map: array_t = dcls.field(init=False, default=None)
    tp1_to_t_associations: Dict[int, int] = dcls.field(init=False, default=None)

    def DiscoverNextCells(self, next_cells: Sequence[cell_t], /) -> None:
        """"""
        super().DiscoverNextCells(next_cells)

        cells_map = nmpy.zeros(self.shape, dtype=nmpy.uint64)
        for c_idx, cell in enumerate(next_cells, start=1):
            cell_map = cell.Map(self.shape, as_boolean=True)
            cells_map[cell_map] = c_idx
        self.next_labeled_map = cells_map

        if self.labeled_map is not None:
            cells_idc = nmpy.fromiter(
                range(1, self.cells.__len__() + 1), dtype=nmpy.uint64
            )
            next_cells_idc = nmpy.fromiter(
                range(1, self.next_cells.__len__() + 1), dtype=nmpy.uint64
            )
            cells_idc.shape = (-1, 1)
            next_cells_idc.shape = (-1, 1)
            _PseudoJaccard = lambda idx_1, idx_2: PseudoJaccard(
                self.labeled_map, self.next_labeled_map, idx_1, idx_2
            )
            pairwise_jaccards = dstc.cdist(
                cells_idc, next_cells_idc, metric=_PseudoJaccard
            )

            associations = {}
            for _ in range(2):
                row_ind, col_ind = spop.linear_sum_assignment(1.0 - pairwise_jaccards)
                valid_idc = pairwise_jaccards[row_ind, col_ind] > self.min_jaccard
                new_associations = dict(zip(col_ind[valid_idc], row_ind[valid_idc]))
                assert (
                    set(associations.keys())
                    .intersection(new_associations.keys())
                    .__len__()
                    == 0
                )
                associations.update(new_associations)
                pairwise_jaccards[:, col_ind] = 0.0

            self.tp1_to_t_associations = associations

    def PredecessorOfCell(
        self, next_cell: cell_t, next_cell_idx: int, /
    ) -> Optional[cell_t]:
        """"""
        cell_idx = self.tp1_to_t_associations.get(next_cell_idx)
        if cell_idx is None:
            return None

        return self.cells[cell_idx]

    def Advance(self) -> None:
        """"""
        super().Advance()
        self.labeled_map = self.next_labeled_map
