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

from pathlib import Path as path_t
from typing import Callable, Sequence, Union

import imageio as mgio
import matplotlib.pyplot as pypl
import mrc as mrci
import numpy as nmpy
import scipy.ndimage as imge
import tifffile as tiff

import cell_tracking_BC.in_out.storage.frame as frio
from cell_tracking_BC.type.sequence import sequence_t
from cell_tracking_BC.type.track import single_track_descriptions_h


array_t = nmpy.ndarray


# TODO: check the output format of the different functions. In particular, do they all output the time dimension as the
# last one?
# TODO: Probably add (generic) parameters to specify eventual required hints for reading function such as number of
# channels...


def SequenceByITK(path: path_t, /) -> array_t:
    """
    Shape: time*channel x row x col
    """
    return frio.FrameByITK(path)


def SequenceByIMAGEIO(path: path_t, /) -> array_t:
    """"""
    return mgio.volread(path)


def SequenceFromPath(
    path: path_t,
    /,
    *,
    SequenceLoading: Callable[[path_t], array_t] = SequenceByITK,
) -> array_t:
    """"""
    # TODO: make this function work in "every" cases (add a parameter about expected dimension arrangements), or
    #     remove the sequence loading functionality from cell-tracking-bc, leaving this task to the end user.
    if not (path.exists() and path.is_file()):
        raise ValueError(f"{path}: Not a path to an existing file")

    if (format := path.suffix[1:].lower()) in ("tif", "tiff"):
        output = tiff.imread(path)
    elif format in ("dv", "mrc"):
        # numpy.array: Because the returned value seems to be a read-only memory map
        output = nmpy.array(mrci.imread(str(path)))
        if output.ndim == 5:
            # Probably: time x channel x Z x Y x X while sequences are time x channel x (Z=1 x) Y x X, so one gets:
            # time x channel=1 x Z=actual channels x Y x X
            output = output[:, 0, :, :]
    else:
        output = SequenceLoading(path)

    return output


def SaveAnnotatedSequence(
    sequence: sequence_t,
    single_track_descriptions: single_track_descriptions_h,
    path: Union[str, path_t],
    /,
    *,
    channel: str = None,
    as_sequence: bool = True,
) -> None:
    """
    channel: None=segmentation channel
    """
    if isinstance(path, str):
        path = path_t(path)
    if channel is None:
        channel = sequence.cell_channel

    folder = path.parent
    basename = path.stem
    extension = path.suffix

    annotations = [{} for _ in range(sequence.length)]
    for label, description in single_track_descriptions.items():
        for time_point, cell_description in enumerate(description):
            position = tuple(cell_description.position)
            annotation = annotations[time_point]
            if position in annotation:
                annotation[position].append(str(label))
            else:
                annotation[position] = [str(label)]
            if cell_description.divides and ("Y" not in annotation[position]):
                annotation[position].append("Y")

    output = None
    frames = sequence.Frames(channel=channel)
    for time_point, (frame, frame_annotation) in enumerate(zip(frames, annotations)):
        figure, axes = pypl.subplots()
        axes.matshow(frame, cmap="gray")
        for (row, col), cell_annotation in frame_annotation.items():
            annotation = "\n".join(sorted(cell_annotation))
            axes.text(
                col,
                row,
                annotation,
                ha="center",
                va="center",
                fontsize=8,
                color="red",
            )
        figure.canvas.draw()  # draw_idle is not appropriate here
        if as_sequence:
            contents = _FigureContents(figure)
            if output is None:
                output = nmpy.empty(
                    (*contents.shape, sequence.length), dtype=nmpy.uint8
                )
            output[..., time_point] = contents
        else:
            figure.savefig(folder / f"{basename}_{time_point}{extension}", dpi=300)
        pypl.close(fig=figure)

    if as_sequence:
        row_slice, col_slice = _BoundingBoxSlices(output)
        output = output[row_slice, col_slice, :, :]
        output = nmpy.moveaxis(output, (0, 1, 2, 3), (2, 3, 1, 0))
        output = output[:, nmpy.newaxis, :, :, :]
        tiff.imwrite(
            str(path),
            output,
            photometric="rgb",
            compression="deflate",
            planarconfig="separate",
            metadata={"axes": "XYZCT"},
        )


def _FigureContents(figure: pypl.Figure, /) -> array_t:
    """
    Alternative:
        - fig.canvas.renderer._renderer?
        - Agg Buffer To Array: np.array(canvas.renderer.buffer_rgba())
    """
    height, width = figure.canvas.get_width_height()
    output = nmpy.fromstring(figure.canvas.tostring_rgb(), dtype=nmpy.uint8)
    output.shape = (width, height, 3)

    return output


def _BoundingBoxSlices(sequence: array_t, /) -> Sequence[slice]:
    """"""
    min_reduction = nmpy.amin(sequence, axis=-1)
    max_reduction = nmpy.amax(sequence, axis=-1)
    constant = nmpy.any(min_reduction != max_reduction, axis=-1)
    output = imge.find_objects(constant)[0]

    return output
