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

import dataclasses as dcls
import warnings as wrng
from typing import Iterator, Optional, Sequence, Tuple, Union

import networkx as grph

from cell_tracking_BC.in_out.console.uid import ShortID
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.track import (
    TIME_POINT,
    RootCellOfUnstructuredTrack,
    forking_track_t,
    single_track_t,
    track_h,
    unstructured_track_t,
)


@dcls.dataclass(repr=False, eq=False)
class tracks_t(list):
    @classmethod
    def NewFromUnstructuredTracks(cls, tracks: unstructured_tracks_t, /) -> tracks_t:
        """"""
        instance = cls()

        single_track_starting_label = 1
        for track in grph.weakly_connected_components(tracks):
            forking_track = forking_track_t.NewFromUnstructuredTrack(
                tracks.subgraph(track), single_track_starting_label
            )
            single_track_starting_label += forking_track.n_leaves

            single_track = forking_track.AsSingleTrack()
            if single_track is None:
                instance.append(forking_track)
            else:
                instance.append(single_track)

        return instance

    def RootCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        output = []

        for track in self:
            output.append(track.RootCell(with_time_point=with_time_point))

        return output

    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        output = []

        for track in self:
            if isinstance(track, forking_track_t):
                output.extend(track.DividingCells(with_time_point=with_time_point))

        return output

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        output = []

        for track in self:
            output.extend(track.LeafCells(with_time_point=with_time_point))

        return output

    def TrackWithRoot(self, root: cell_t, /) -> track_h:
        """"""
        for track in self:
            if root is track.RootCell():
                return track

        raise ValueError(f"{root}: Not a root cell")

    def TrackWithLeaf(self, leaf: cell_t, /) -> single_track_t:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        for track in self:
            for cell in track.LeafCells():
                if leaf is cell:
                    if isinstance(track, single_track_t):
                        output = track
                    else:
                        output = track.TrackWithLeaf(cell)

                    return output

        raise ValueError(f"{leaf}: Not a leaf cell")

    def TrackWithLabel(self, label: int, /) -> single_track_t:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        for track in self.TracksIterator():
            if label == track.label:
                return track

        raise ValueError(f"{label}: Not an existing single track label")

    def TracksIterator(self, /, *, leaf_based: bool = True) -> Iterator[track_h]:
        """"""
        if leaf_based:
            return self._SingleTracksIterator()
        else:
            return iter(self)

    def _SingleTracksIterator(self) -> Iterator[single_track_t]:
        """"""
        for track in self:
            if isinstance(track, single_track_t):
                single_tracks = (track,)
            else:
                single_tracks = track.SingleTracks()

            for single_track in single_tracks:
                yield single_track

    def TrackLabelWithLeaf(self, leaf: cell_t, /) -> int:
        """"""
        track = self.TrackWithLeaf(leaf)

        return track.label

    def Print(self) -> None:
        """"""
        for track in self:
            print(track)

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}: {self.__len__()=}"
        )


class unstructured_tracks_t(grph.DiGraph):
    def AddTrackSegment(
        self, src_cell: cell_t, tgt_cell: cell_t, src_time_point: int, /
    ) -> None:
        """"""
        time_point = {TIME_POINT: src_time_point}
        time_point_p_1 = {TIME_POINT: src_time_point + 1}
        self.add_node(src_cell, **time_point)
        self.add_node(tgt_cell, **time_point_p_1)
        self.add_edge(src_cell, tgt_cell)

    def Clean(self) -> None:
        """"""
        for cell, time_point in RootCellOfUnstructuredTrack(
            self, should_be_unique=False
        ):
            if time_point > 0:
                unstructured_track = self._UnstructuredTrackContainingCell(cell)
                self.remove_nodes_from(unstructured_track)
            elif self.out_degree(cell) == 0:
                self.remove_node(cell)

    def IsConform(self, /, *, when_fails: str = "warn silently") -> bool:
        """
        when_fails:
            - "warn silently": Return a boolean
            - "warn aloud": Print a message and return a boolean
            - "raise": Raises a ValueError exception
        """
        issues = []

        for cell in self.nodes:
            if (n_predecessors := self.in_degree(cell)) > 1:
                issues.append(f"{cell}: {n_predecessors} predecessors; Expected=0 or 1")
            elif (n_successors := self.out_degree(cell)) > 2:
                issues.append(
                    f"{cell}: {n_successors} successors; Expected=0 or 1 or 2"
                )

        for cell, time_point in RootCellOfUnstructuredTrack(
            self, should_be_unique=False
        ):
            if time_point > 0:
                issues.append(
                    f"{cell}: Root cell with non-zero time point ({time_point})"
                )
            if self.out_degree(cell) == 0:
                issues.append(f"{cell}: Empty track")

        if issues.__len__() > 0:
            if when_fails == "warn silently":
                return False
            elif when_fails == "warn aloud":
                issues.append(f"{self}: Conformity Check:")
                wrng.warn("\n".join(issues))
                return False
            elif when_fails == "raise":
                issues.append(f"{self}")
                raise ValueError("\n".join(issues))
            else:
                raise ValueError(f'{when_fails}: Invalid "when_fails" argument value')
        else:
            return True

    def _UnstructuredTrackContainingCell(
        self, cell: cell_t, /
    ) -> Optional[unstructured_track_t]:
        """"""
        for track in grph.weakly_connected_components(self):
            if cell in track:
                return self.subgraph(track)

        return None
