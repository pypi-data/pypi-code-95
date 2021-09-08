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
from typing import Optional, Sequence

import numpy as nmpy
from cell_tracking_BC.task.tracking.generic import context_t
from cell_tracking_BC.task.tracking.main import array_t
from cell_tracking_BC.type.cell import cell_t
from scipy.spatial import distance as dstc


@dcls.dataclass(repr=False, eq=False)
class cbnn_context_t(context_t):
    """
    cbnn: Centroid-Based Nearest Neighbor
    """

    max_distance: float = nmpy.inf
    centroids: array_t = dcls.field(init=False, default=None)
    next_centroids: array_t = dcls.field(init=False, default=None)
    pairwise_distances: array_t = dcls.field(init=False, default=None)

    def DiscoverNextCells(self, next_cells: Sequence[cell_t], /) -> None:
        """"""
        super().DiscoverNextCells(next_cells)

        self.next_centroids = self.__class__._CellsCentroids(next_cells)
        if self.centroids is not None:
            self.pairwise_distances = dstc.cdist(self.centroids, self.next_centroids)

    def PredecessorOfCell(
        self, next_cell: cell_t, next_cell_idx: int, /
    ) -> Optional[cell_t]:
        """"""
        output = None

        cell_idx = nmpy.argmin(self.pairwise_distances[:, next_cell_idx]).item()
        distance = self.pairwise_distances[cell_idx, next_cell_idx]
        if distance <= self.max_distance:
            output = self.cells[cell_idx]

        return output

    def Advance(self) -> None:
        """"""
        super().Advance()
        self.centroids = self.next_centroids

    @staticmethod
    def _CellsCentroids(cells: Sequence[cell_t]) -> array_t:
        """"""
        centroids = tuple(_cll.centroid for _cll in cells)
        output = nmpy.array(centroids, dtype=nmpy.float64)

        return output


@dcls.dataclass(repr=False, eq=False)
class bcbnn_context_t(cbnn_context_t):
    """
    bcbnn: Bidirectional Centroid-Based Nearest Neighbor. Use only if no cell divisions are expected.
    """

    def PredecessorOfCell(
        self, next_cell: cell_t, next_cell_idx: int, /
    ) -> Optional[cell_t]:
        """"""
        output = None

        cell_idx = nmpy.argmin(self.pairwise_distances[:, next_cell_idx]).item()
        distance = self.pairwise_distances[cell_idx, next_cell_idx]
        if distance <= self.max_distance:
            symmetric_idx = nmpy.argmin(self.pairwise_distances[cell_idx, :]).item()
            if symmetric_idx == next_cell_idx:
                output = self.cells[cell_idx]

        return output


@dcls.dataclass(repr=False, eq=False)
class pjb_context_t(context_t):
    """
    pjb: Pseudo-Jaccard-Based=area intersection t+1|t / area t+1
    """

    shape: Sequence[int] = None
    min_jaccard: float = 0.5
    labeled_map: array_t = dcls.field(init=False, default=None)
    next_labeled_map: array_t = dcls.field(init=False, default=None)
    pairwise_jaccards: array_t = dcls.field(init=False, default=None)

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
            self.pairwise_jaccards = dstc.cdist(
                cells_idc, next_cells_idc, metric=self._PseudoJaccard
            )

    def PredecessorOfCell(
        self, next_cell: cell_t, next_cell_idx: int, /
    ) -> Optional[cell_t]:
        """"""
        output = None

        cell_idx = nmpy.argmax(self.pairwise_jaccards[:, next_cell_idx]).item()
        jaccard = self.pairwise_jaccards[cell_idx, next_cell_idx]
        if jaccard >= self.min_jaccard:
            output = self.cells[cell_idx]

        return output

    def Advance(self) -> None:
        """"""
        super().Advance()
        self.labeled_map = self.next_labeled_map

    def _PseudoJaccard(self, idx_1: int, idx_2: int, /) -> float:
        """"""
        map_1 = self.labeled_map == idx_1
        map_2 = self.next_labeled_map == idx_2

        intersection = nmpy.logical_and(map_1, map_2)
        intersection_area = nmpy.count_nonzero(intersection)

        t_p_1_area = nmpy.count_nonzero(map_2)

        return intersection_area / t_p_1_area
