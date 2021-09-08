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
from pathlib import Path as path_t
from typing import Any, Callable, Dict, Iterator, Optional, Sequence, Tuple, Union

import numpy as nmpy

from cell_tracking_BC.in_out.console.uid import ShortID
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.frame import frame_t, transform_h
from cell_tracking_BC.type.track import (
    single_track_descriptions_h,
    single_track_t,
    time_point_t,
    track_h,
)
from cell_tracking_BC.type.tracks import tracks_t, unstructured_tracks_t


array_t = nmpy.ndarray
channel_computation_h = Callable[[Dict[str, array_t], Dict[str, Any]], array_t]
morphological_feature_computation_h = Callable[
    [cell_t, Dict[str, Any]], Union[Any, Sequence[Any]]
]
radiometric_feature_computation_h = Callable[
    [cell_t, Union[array_t, Sequence[array_t]], Dict[str, Any]],
    Union[Any, Sequence[Any]],
]


@dcls.dataclass(repr=False, eq=False)
class sequence_t:

    path: Optional[path_t] = None
    shape: Tuple[int, int] = None
    length: int = None
    base_channels: Sequence[str] = None
    frames_of_channel: Dict[str, Sequence[Union[array_t, frame_t]]] = None
    cell_channel: str = None  # Name of channel whose frames store the segmented cells
    nuclei_sgms: Sequence[array_t] = dcls.field(init=False, default=None)
    cytoplasms_sgms: Sequence[array_t] = dcls.field(init=False, default=None)
    cells_sgms: Sequence[array_t] = dcls.field(init=False, default=None)
    tracks: tracks_t = dcls.field(init=False, default=None)

    @classmethod
    def NewFromFrames(
        cls,
        frames: array_t,
        in_channel_names: Sequence[Optional[str]],
        path: path_t,
        /,
        *,
        first_frame: int = 0,
        last_frame: int = 999999,
    ) -> sequence_t:
        """
        in_channel_names: names equal to None or "___" or "---" indicate channels that should be discarded
        """
        n_in_channels = in_channel_names.__len__()

        frames_of_channel = {}
        for name in in_channel_names:
            if (name is not None) and (name != "___") and (name != "---"):
                frames_of_channel[name] = []
        base_channel_names = tuple(frames_of_channel.keys())

        c_idx = n_in_channels - 1
        time_point = -1
        for raw_frame in frames:
            c_idx += 1
            if c_idx == n_in_channels:
                c_idx = 0
                time_point += 1

            if time_point < first_frame:
                continue
            elif time_point > last_frame:
                break

            name = in_channel_names[c_idx]
            if name in base_channel_names:
                frame = frame_t(raw_frame)
                frames_of_channel[name].append(frame)

        frames = frames_of_channel[base_channel_names[0]]
        shape = frames[0].shape
        length = frames.__len__()
        instance = cls(
            path=path,
            shape=shape,
            length=length,
            base_channels=base_channel_names,
            frames_of_channel=frames_of_channel,
        )

        return instance

    @property
    def channels(self) -> Sequence[str]:
        """
        Names of channels read from file (base channels) and computed channels
        """
        return tuple(self.frames_of_channel.keys())

    @property
    def cell_frames(self) -> Sequence[frame_t]:
        """"""
        return self.Frames(channel=self.cell_channel)

    def Frames(
        self,
        /,
        *,
        channel: Union[str, Sequence[str]] = None,
    ) -> Union[
        Sequence[Union[array_t, frame_t], ...],
        Iterator[Sequence[Union[array_t, frame_t], ...]],
    ]:
        """
        channel: None=all (!) base channels; Otherwise, only (a) base channel name(s) can be passed
        as_iterator: Always considered True if channel is None or a sequence of channel names
        """
        if isinstance(channel, str):
            return self.frames_of_channel[channel]
        else:
            return self._FramesForMultipleChannels(channel)

    def _FramesForMultipleChannels(
        self, channels: Optional[Sequence[str]], /
    ) -> Iterator[Sequence[Union[array_t, frame_t], ...]]:
        """
        /!\ If "channels" contains both base and non-base channels, then the returned tuples will contain both array_t
        and frame_t elements (but frame_t is a subclass of array_t, so...).
        """
        if channels is None:
            channels = self.base_channels

        for f_idx in range(self.length):
            frames = (self.frames_of_channel[_chl][f_idx] for _chl in channels)

            yield tuple(frames)

    def RootCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        return self.tracks.RootCells(with_time_point=with_time_point)

    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        return self.tracks.DividingCells(with_time_point=with_time_point)

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        return self.tracks.LeafCells(with_time_point=with_time_point)

    # def SaveFramesWithLeaves(self, channel: str, path: Union[str, path_t], /) -> None:
    #     """"""
    #     if isinstance(path, str):
    #         path = path_t(path)
    #     folder = path.parent
    #     basename = path.stem
    #     extension = path.suffix
    #
    #     leaves_at_time_point = {}
    #     for leaf, time_point in self.LeafCells(with_time_point=True):
    #         if time_point in leaves_at_time_point:
    #             leaves_at_time_point[time_point].append(leaf)
    #         else:
    #             leaves_at_time_point[time_point] = [leaf]
    #
    #     frames = self.Frames(channel=channel)
    #     for time_point, leaves in leaves_at_time_point.items():
    #         figure, axes = pypl.subplots()
    #         axes.matshow(frames[time_point], cmap="gray")
    #         for leaf in leaves:
    #             row, col = leaf.centroid
    #             label = self.tracks.TrackLabelWithLeaf(leaf)
    #             axes.text(
    #                 col,
    #                 row,
    #                 str(label),
    #                 ha="center",
    #                 fontsize=10,
    #                 color="red",
    #             )
    #         figure.canvas.draw_idle()
    #         figure.savefig(folder / f"{basename}_{time_point}{extension}", dpi=300)
    #         pypl.close(fig=figure)

    def CellsIterator(self) -> Iterator[Sequence[cell_t]]:
        """"""
        for frame in self.cell_frames:
            yield frame.cells

    def TracksIterator(self, /, *, leaf_based: bool = True) -> Iterator[track_h]:
        """"""
        return self.tracks.TracksIterator(leaf_based=leaf_based)

    def TrackWithLabel(self, label: int, /) -> single_track_t:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        return self.tracks.TrackWithLabel(label)

    def ApplyTransform(
        self,
        Transform: transform_h,
        /,
        *,
        channel: Union[str, Sequence[str]] = None,
        **kwargs,
    ) -> None:
        """
        channel: None=all (!)
        """
        if channel is None:
            channels = self.base_channels
        elif isinstance(channel, str):
            channels = (channel,)
        else:
            channels = channel

        for channel in channels:
            targets = self.Frames(channel=channel)
            references_sets = self.Frames(channel=self.channels)
            for target, references in zip(targets, references_sets):
                refs_as_dict = {
                    _nme: _frm for _nme, _frm in zip(self.channels, references)
                }
                target.ApplyTransform(Transform, channels=refs_as_dict, **kwargs)

    def AddComputedChannel(
        self, name: str, ChannelComputation: channel_computation_h, /, **kwargs
    ) -> None:
        """"""
        computed = []
        for frames in self.Frames(channel=self.channels):
            frames_as_dict = {_nme: _frm for _nme, _frm in zip(self.channels, frames)}
            computed.append(ChannelComputation(frames_as_dict, **kwargs))

        self.frames_of_channel[name] = computed

    def AddCellsFromSegmentations(
        self,
        channel: str,
        /,
        *,
        nuclei_sgms: Sequence[array_t] = None,
        cytoplasms_sgms: Sequence[array_t] = None,
        cells_sgms: Sequence[array_t] = None,
        should_clear_border_cells: bool = True,
    ) -> None:
        """
        Segmentation are supposed to be binary (as opposed to already labeled)
        Valid options: See cell_t.AllCompartmentsFromSomeCompartments
        """
        self.cell_channel = channel
        self.nuclei_sgms = nuclei_sgms
        self.cytoplasms_sgms = cytoplasms_sgms
        self.cells_sgms = cells_sgms

        if nuclei_sgms is None:
            nuclei_sgms = self.length * [None]
        if cytoplasms_sgms is None:
            cytoplasms_sgms = self.length * [None]
        if cells_sgms is None:
            cells_sgms = self.length * [None]

        parameters = {
            "nuclei_sgm": None,
            "cytoplasms_sgm": None,
            "cells_sgm": None,
            "should_clear_border_cells": should_clear_border_cells,
        }
        for frame, *segmentations in zip(
            self.cell_frames,
            nuclei_sgms,
            cytoplasms_sgms,
            cells_sgms,
        ):
            parameters["nuclei_sgm"] = segmentations[0]
            parameters["cytoplasms_sgm"] = segmentations[1]
            parameters["cells_sgm"] = segmentations[2]
            frame.AddCellsFromSegmentations(**parameters)

    def AddTracks(
        self, tracks: unstructured_tracks_t, /, *, when_fails: str = "raise"
    ) -> None:
        """
        when_fails: See tracks_t.IsConform
        """
        if tracks.IsConform(when_fails=when_fails):
            self.tracks = tracks_t.NewFromUnstructuredTracks(tracks)

    def AddMorphologicalFeature(
        self,
        name: Union[str, Sequence[str]],
        Feature: morphological_feature_computation_h,
        /,
        **kwargs,
    ) -> None:
        """
        name: If an str, then the value returned by Feature will be considered as a whole, whether it is actually a
        single value or a value container. If a sequence of str's, then the object returned by Feature will be iterated
        over as many times as the length of this sequence.
        """
        if isinstance(name, str):
            for cells in self.CellsIterator():
                for cell in cells:
                    feature = Feature(cell, **kwargs)
                    cell.AddFeature(name, feature)
        else:
            names = name
            for cells in self.CellsIterator():
                for cell in cells:
                    features = Feature(cell, **kwargs)
                    for name, feature in zip(names, features):
                        cell.AddFeature(name, feature)

    def AddRadiometricFeature(
        self,
        name: Union[str, Sequence[str]],
        Feature: radiometric_feature_computation_h,
        channel: Union[str, Sequence[str]],
        /,
        **kwargs,
    ) -> None:
        """
        See AddMorphologicalFeature
        """
        for frame_w_cells, frame in zip(self.cell_frames, self.Frames(channel=channel)):
            for cell in frame_w_cells.cells:
                if isinstance(name, str):
                    feature = Feature(cell, frame, **kwargs)
                    cell.AddFeature(name, feature)
                else:
                    features = Feature(cell, frame, **kwargs)
                    for f_name, feature in zip(name, features):
                        cell.AddFeature(f_name, feature)

    def AvailableCellFeatures(self) -> Sequence[str]:
        """"""
        one_cell = self.RootCells()[0]

        return tuple(one_cell.features.keys())

    def FeatureEvolutionOfCell(
        self, cell: cell_t, feature: str, /
    ) -> Sequence[Sequence[Any]]:
        """"""
        try:
            track = self.tracks.TrackWithRoot(cell)
        except ValueError:
            track = None
        if track is None:
            try:
                track = self.tracks.TrackWithLeaf(cell)
            except ValueError:
                track = None
        if track is None:
            raise ValueError(f"{cell}: Neither a root or a leaf cell")

        if isinstance(track, single_track_t):
            tracks = (track,)
        else:
            tracks = track.SingleTracks()

        output = []

        for track in tracks:
            evolution = tuple(_cll.features[feature] for _cll in track)
            output.append(evolution)

        return output

    def FeatureEvolutionsOfAllCells(self, feature: str, /) -> Dict[int, Sequence[Any]]:
        """"""
        output = {}

        for track in self.tracks.TracksIterator():
            output[track.label] = tuple(_cll.features[feature] for _cll in track)

        return output

    def SingleTrackDescriptions(self) -> single_track_descriptions_h:
        """"""
        output = {}

        dividing_cells = self.DividingCells(with_time_point=True)
        for track in self.tracks.TracksIterator():
            description = []
            for t_idx, cell in enumerate(track):
                divides = False
                for dividing_cell in dividing_cells:
                    if (cell is dividing_cell[0]) and (t_idx == dividing_cell[1]):
                        divides = True
                        break
                time_point = time_point_t(position=cell.centroid, divides=divides)
                description.append(time_point)

            output[track.label] = description

        return output

    def ClearContents(self):
        """
        To free up some memory when all processing has been done
        """
        for frames in self.Frames():
            for frame in frames:
                frame.ClearContents()

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.path=}\n"
            f"    {self.base_channels=}\n"
            f"    {self.channels=}\n"
            f"    {self.shape=}\n"
            f"    {self.length=}\n"
            f"    {self.tracks=}"
        )
