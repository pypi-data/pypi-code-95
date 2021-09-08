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

from typing import Sequence, Union

import matplotlib.pyplot as pypl
import matplotlib.text as text
import numpy as nmpy
import scipy.interpolate as ntrp
import skimage.measure as msre
from matplotlib.widgets import Slider as slider_t
from mpl_toolkits.mplot3d import Axes3D as axes_3d_t

from cell_tracking_BC.in_out.screen.generic import (
    FinalizeDisplay,
    SetTimeAxisProperties,
    SetZAxisProperties,
)
from cell_tracking_BC.in_out.storage.archiver import archiver_t
from cell_tracking_BC.type.sequence import sequence_t

array_t = nmpy.ndarray


def ShowSequenceStatistics(
    sequence: sequence_t,
    /,
    *,
    channel: Union[str, Sequence[str]] = None,
    show_and_wait: bool = True,
    figure_name: str = "sequence-statistics",
    archiver: archiver_t = None,
) -> None:
    """"""
    if channel is None:
        channels = sequence.base_channels
    elif isinstance(channel, str):
        channels = (channel,)
    else:
        channels = channel

    statistics = ("amin", "amax", "mean", "median")
    ComputedStatistics = tuple(getattr(nmpy, _stt) for _stt in statistics)
    records = {_stt: {_chl: [] for _chl in channels} for _stt in statistics}
    for frames in sequence.Frames(channel=channels):
        for channel, frame in zip(channels, frames):
            for name, Computed in zip(statistics, ComputedStatistics):
                records[name][channel].append(Computed(frame))

    figure, all_axes = pypl.subplots(nrows=statistics.__len__())

    for s_idx, (name, values_per_channel) in enumerate(records.items()):
        for channel, values in values_per_channel.items():
            all_axes[s_idx].plot(values, label=channel)

    for name, axes in zip(records.keys(), all_axes):
        SetTimeAxisProperties(sequence.length - 1, axes)
        axes.legend()
        axes.set_title(name)

    FinalizeDisplay(figure, figure_name, show_and_wait, archiver)


def ShowSequence(
    sequence: sequence_t,
    channel: str,
    /,
    *,
    mode: str = "2d+t",
    time_stretching: float = 1.0,
    n_levels: int = 100,
    iso_value: float = None,
    show_and_wait: bool = True,
    figure_name: str = "sequence",
    archiver: archiver_t = None,
) -> None:
    """
    mode: "2d+t", "mille-feuille", "tunnels"
    time_stretching: must be >= 1.0
    """
    figure = pypl.figure()

    frames = sequence.Frames(channel=channel)
    if mode == "2d+t":
        axes = figure.add_subplot(111)
        # Maintain a reference to the slider so that it remains functional
        figure.__SEQUENCE_SLIDER_REFERENCE__ = _ShowFramesAs2DpT(
            frames, False, figure, axes
        )
    elif mode in ("mille-feuille", "tunnels"):
        axes = figure.add_subplot(projection=axes_3d_t.name)
        axes.set_xlabel("row positions")
        axes.set_ylabel("column positions")
        axes.set_zlabel("time points")

        if mode == "mille-feuille":
            _ShowFramesAsMilleFeuille(
                frames, False, time_stretching, axes, n_levels=n_levels
            )
        else:
            if iso_value is None:
                iso_value = nmpy.median(frames[0])
            _ShowFramesAsTunnels(frames, time_stretching, axes, iso_value=iso_value)
    else:
        raise ValueError(
            f'{mode}: Invalid mode; Expected="2d+t", "mille-feuille", "tunnels"'
        )

    FinalizeDisplay(figure, figure_name, show_and_wait, archiver)


def ShowSegmentation(
    sequence: sequence_t,
    /,
    *,
    which_compartment: str = None,
    with_labels: bool = True,
    mode: str = "2d+t",
    time_stretching: float = 1.0,
    show_and_wait: bool = True,
    figure_name: str = "segmentation",
    archiver: archiver_t = None,
) -> None:
    """
    which_compartment: "nucleus" or "cytoplasm" or "cell" or None. If None, then the first non-None in the order "cell",
    "cytoplasm", "nucleus" is selected.
    mode: see ShowSequence
    time_stretching: see ShowSequence
    """
    if which_compartment == "nucleus":
        segmentations = sequence.nuclei_sgms
    elif which_compartment == "cytoplasm":
        segmentations = sequence.cytoplasms_sgms
    elif which_compartment == "cell":
        segmentations = sequence.cells_sgms
    elif which_compartment is None:
        if sequence.cells_sgms is not None:
            segmentations = sequence.cells_sgms
        elif sequence.cytoplasms_sgms is not None:
            segmentations = sequence.cytoplasms_sgms
        elif sequence.nuclei_sgms is not None:
            segmentations = sequence.nuclei_sgms
        else:
            raise RuntimeError("No segmentations computed yet")
    else:
        raise ValueError(f"{which_compartment}: Invalid compartment designation")

    figure = pypl.figure()

    if mode == "2d+t":
        axes = figure.add_subplot(111)
        # Maintain a reference to the slider so that it remains functional
        figure.__SEQUENCE_SLIDER_REFERENCE__ = _ShowFramesAs2DpT(
            segmentations, with_labels, figure, axes
        )
    elif mode in ("mille-feuille", "tunnels"):
        axes = figure.add_subplot(projection=axes_3d_t.name)
        axes.set_xlabel("row positions")
        axes.set_ylabel("column positions")
        axes.set_zlabel("time points")

        if mode == "mille-feuille":
            _ShowFramesAsMilleFeuille(segmentations, with_labels, time_stretching, axes)
        else:
            _ShowFramesAsTunnels(segmentations, time_stretching, axes)
    else:
        raise ValueError(
            f'{mode}: Invalid mode; Expected="2d+t", "mille-feuille", "tunnels"'
        )

    FinalizeDisplay(figure, figure_name, show_and_wait, archiver)


def _ShowFramesAs2DpT(
    segmentations: Sequence[array_t],
    with_labels: bool,
    figure: pypl.Figure,
    axes: pypl.Axes,
    /,
) -> slider_t:
    """
    Returns the slider so that a reference can be kept in calling function to maintain it responsive
    """
    _ShowFrame(segmentations[0], with_labels, axes)

    figure.subplots_adjust(bottom=0.25)
    slider_axes = figure.add_axes([0.25, 0.15, 0.65, 0.03])
    slider = slider_t(
        slider_axes,
        "Time Point",
        0,
        segmentations.__len__() - 1,
        valinit=0,
        valstep=1,
    )

    def OnNewSliderValue(value: float, /) -> None:
        time_point = int(round(value))
        _ShowFrame(segmentations[time_point], with_labels, axes)
        figure.canvas.draw_idle()

    slider.on_changed(OnNewSliderValue)

    return slider


def _ShowFrame(segmentation: array_t, with_labels: bool, axes: pypl.Axes, /) -> None:
    """"""
    axes.matshow(segmentation, cmap="gray")
    if with_labels:
        _AnnotateCells(segmentation, axes)


def _ShowFramesAsMilleFeuille(
    segmentations: Sequence[array_t],
    with_labels: bool,
    time_stretching: float,
    axes: axes_3d_t,
    /,
    *,
    n_levels: int = 1,
) -> None:
    """"""
    n_segmentations = segmentations.__len__()
    shape = segmentations[0].shape

    all_rows, all_cols = nmpy.meshgrid(range(shape[0]), range(shape[1]), indexing="ij")
    for t_idx, segmentation in enumerate(segmentations):
        axes.contourf(
            all_rows,
            all_cols,
            segmentation,
            levels=n_levels,
            offset=time_stretching * t_idx,
            alpha=0.8,
            cmap="gray",
        )
        if with_labels:
            _AnnotateCells(
                segmentation, axes, elevation=time_stretching * (t_idx + 0.2)
            )
    SetZAxisProperties(n_segmentations, time_stretching, axes)


def _ShowFramesAsTunnels(
    segmentations: Sequence[array_t],
    time_stretching: float,
    axes: axes_3d_t,
    /,
    *,
    iso_value: float = 0.5,
) -> None:
    """"""
    n_segmentations = segmentations.__len__()
    volume = nmpy.array(segmentations, dtype=nmpy.uint8)
    original_extents = (
        range(n_segmentations),
        range(volume.shape[1]),
        range(volume.shape[2]),
    )
    interpolated_extents = (
        nmpy.linspace(
            0, n_segmentations - 1, num=int(round(time_stretching * n_segmentations))
        ),
        *original_extents[1:],
    )
    all_times, all_rows, all_cols = nmpy.meshgrid(*interpolated_extents, indexing="ij")
    interpolated_sites = nmpy.vstack((all_times.flat, all_rows.flat, all_cols.flat)).T
    interpolated = ntrp.interpn(original_extents, volume, interpolated_sites)
    reshaped = nmpy.reshape(
        interpolated, (interpolated_extents[0].size, *volume.shape[1:])
    )
    reorganized = nmpy.moveaxis(reshaped, (0, 1, 2), (2, 0, 1))
    flipped = nmpy.flip(reorganized, axis=2)
    vertices, faces, *_ = msre.marching_cubes(flipped, iso_value, step_size=5)
    axes.plot_trisurf(
        vertices[:, 0],
        vertices[:, 1],
        faces,
        nmpy.amax(vertices[:, 2]) - vertices[:, 2],
        cmap="rainbow",
        lw=1,
    )
    SetZAxisProperties(n_segmentations, time_stretching, axes)


def _AnnotateCells(
    segmentation: array_t, axes: pypl.Axes, /, *, elevation: float = None
) -> None:
    """"""
    if elevation is None:
        AnnotateCell = lambda _pos, _txt: axes.annotate(
            _txt,
            _pos,
            ha="center",
            fontsize="x-small",
            color="red",
        )

        annotations = (
            _chd for _chd in axes.get_children() if isinstance(_chd, text.Annotation)
        )
        for annotation in annotations:
            annotation.remove()
    else:
        AnnotateCell = lambda _pos, _txt: axes.text(
            *_pos, _txt, fontsize="x-small", color="red"
        )

    labeled = msre.label(segmentation, connectivity=1)
    cells_properties = msre.regionprops(labeled)
    for properties in cells_properties:
        if elevation is None:
            position = nmpy.flipud(properties.centroid)
        else:
            position = (*properties.centroid, elevation)
        AnnotateCell(position, str(properties.label))
