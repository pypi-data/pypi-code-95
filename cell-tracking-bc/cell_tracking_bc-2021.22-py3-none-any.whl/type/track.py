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

from __future__ import annotations

from typing import ClassVar, Dict, Final, Iterator
from typing import NamedTuple as named_tuple_t
from typing import Optional, Sequence, Tuple, Union

import networkx as grph

from cell_tracking_BC.in_out.console.uid import ShortID
from cell_tracking_BC.type.cell import cell_t


unstructured_track_t = grph.DiGraph


TIME_POINT = "time_point"


class time_point_t(named_tuple_t):
    position: Sequence[int]
    divides: bool = False
    dies: bool = False


class single_track_t(list):
    n_leaves: Final[ClassVar[int]] = 1

    label: Optional[int]
    root_time_point: Optional[int]

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.label = None
        self.root_time_point = None

    @classmethod
    def NewFromOrderedCells(
        cls, cells: Sequence[cell_t], root_time_point: int, label: int, /
    ) -> single_track_t:
        """"""
        # This must be the only place where direct instantiation is allowed. Anywhere else, instantiation must be
        # performed with this class method.
        instance = cls(cells)
        instance.label = label
        instance.root_time_point = root_time_point

        return instance

    def RootCell(
        self, /, *, with_time_point: bool = False
    ) -> Union[cell_t, Tuple[cell_t, int]]:
        """"""
        if with_time_point:
            output = (self[0], self.root_time_point)
        else:
            output = self[0]

        return output

    def DividingCells(
        self, /, *, _: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        return ()

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = (self[-1], self.leaf_time_point)
        else:
            output = self[-1]

        return (output,)

    @property
    def leaf_time_point(self) -> int:
        """"""
        return self.root_time_point + self.__len__() - 1

    def SegmentsIterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        for c_idx in range(1, self.__len__()):
            time_point = c_idx - 1
            is_last = c_idx == self.__len__() - 1
            yield time_point, *self[(c_idx - 1) : (c_idx + 1)], is_last

    def __str__(self) -> str:
        """"""
        cell_labels = tuple(_cll.label for _cll in self)

        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.leaf_time_point=}\n"
            f"    single_tracks_labels={self.label}\n"
            f"    {cell_labels}"
        )


class forking_track_t(unstructured_track_t):

    single_track_label: ClassVar[str] = "single_track_label"

    root: cell_t
    leaves: Sequence[cell_t]
    root_time_point: int
    leaves_time_points: Sequence[int]

    @classmethod
    def NewFromUnstructuredTrack(
        cls, track: unstructured_track_t, single_track_starting_label: int, /
    ) -> forking_track_t:
        """"""
        instance = cls(track)

        root, time_point = RootCellOfUnstructuredTrack(track)
        instance.root = root
        instance.root_time_point = time_point

        leaves, time_points = LeafCellsOfUnstructuredTrack(track)
        for c_idx, cell in enumerate(leaves):
            grph.set_node_attributes(
                instance,
                {cell: single_track_starting_label + c_idx},
                name=forking_track_t.single_track_label,
            )
        instance.leaves = leaves
        instance.leaves_time_points = time_points

        return instance

    @property
    def n_leaves(self) -> int:
        """"""
        return self.leaves.__len__()

    def RootCell(
        self, /, *, with_time_point: bool = False
    ) -> Union[cell_t, Tuple[cell_t, int]]:
        """"""
        if with_time_point:
            output = (self.root, self.root_time_point)
        else:
            output = self.root

        return output

    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = (
                _rcd
                for _rcd in self.nodes.data(TIME_POINT)
                if self.out_degree(_rcd[0]) == 2
            )
        else:
            output = (_cll for _cll in self.nodes if self.out_degree(_cll) == 2)

        return tuple(output)

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = tuple(zip(self.leaves, self.leaves_time_points))
        else:
            output = self.leaves

        return output

    def SegmentsIterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        time_points = grph.get_node_attributes(self, TIME_POINT)

        for edge in self.edges:
            time_point = time_points[edge[0]]
            is_last = edge[1] in self.leaves
            yield time_point, *edge, is_last

    def TrackWithLeaf(self, leaf: cell_t, /) -> single_track_t:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        if leaf not in self.leaves:
            raise ValueError(f"{leaf}: Not a leaf cell")

        cells = grph.shortest_path(self, source=self.root, target=leaf)
        label = self.nodes[leaf][forking_track_t.single_track_label]
        output = single_track_t.NewFromOrderedCells(cells, self.root_time_point, label)

        return output

    def SingleTracks(self) -> Sequence[single_track_t]:
        """"""
        output = []

        for cell in self.leaves:
            output.append(self.TrackWithLeaf(cell))

        return output

    def AsSingleTrack(self) -> Optional[single_track_t]:
        """"""
        output = []

        cell = self.root
        label = None
        while cell is not None:
            output.append(cell)

            neighbors = tuple(self.neighbors(cell))
            if neighbors.__len__() == 0:
                label = self.nodes[cell][forking_track_t.single_track_label]
                cell = None
            elif neighbors.__len__() == 1:
                cell = neighbors[0]
            else:
                cell = None
                output = None

        if output is not None:
            output = single_track_t.NewFromOrderedCells(
                output, self.root_time_point, label
            )

        return output

    def __str__(self) -> str:
        """"""
        cell_labels = tuple(_cll.label for _cll in self.nodes)
        single_tracks_labels = tuple(
            self.nodes[_nde][forking_track_t.single_track_label] for _nde in self.leaves
        )

        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.number_of_nodes()=}\n"
            f"    {self.number_of_edges()=}\n"
            f"    {self.n_leaves=}\n"
            f"    {self.leaves_time_points=}\n"
            f"    {single_tracks_labels=}\n"
            f"    {cell_labels}"
        )


def RootCellOfUnstructuredTrack(
    track: unstructured_track_t, /, *, should_be_unique: bool = True
) -> Union[Tuple[cell_t, int], Sequence[Tuple[cell_t, int]]]:
    """
    This function is typically called on single or forking tracks. It can also be called on general directed graphs, in
    which case, multiple root cells must be allowed, and a sequence is returned.
    """
    output = tuple(
        _rcd for _rcd in track.nodes.data(TIME_POINT) if track.in_degree(_rcd[0]) == 0
    )

    if should_be_unique:
        if (n_roots := output.__len__()) != 1:
            raise ValueError(f"{n_roots}: Invalid number of root cells; Expected=1")

        output = output[0]

    return output


def LeafCellsOfUnstructuredTrack(
    track: unstructured_track_t, /
) -> Tuple[Sequence[cell_t], Sequence[int]]:
    """"""
    # TODO: Contact the Networkx team about the following comment
    # /!\ It seems that networkx.DiGraph.nodes.data does not guarantee the node enumeration order. This could be
    # inconvenient for reproducibility checks.
    records = (
        _rcd for _rcd in track.nodes.data(TIME_POINT) if track.out_degree(_rcd[0]) == 0
    )
    leaves, time_points = zip(*records)

    leaves = tuple(leaves)
    time_points = tuple(time_points)

    return leaves, time_points


track_h = Union[single_track_t, forking_track_t]
single_track_descriptions_h = Dict[int, Sequence[time_point_t]]
