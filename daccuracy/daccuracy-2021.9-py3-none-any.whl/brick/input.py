# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2019)
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

import sys as sstm
from csv import reader as csv_reader_t
from pathlib import Path as path_t
from typing import Callable, Optional, Sequence, Tuple

import imageio as mgio
import numpy as nmpy
import scipy.ndimage as spim

import daccuracy.brick.csv_gt as csgt


array_t = nmpy.ndarray


def GroundTruthFromImage(
    img_path: path_t,
    _: Tuple[int, int] = None,
    __: Sequence[int] = None,
    ___: Callable[[float], float] = None,
    /,
) -> Optional[array_t]:
    #
    return _ImageFromPath(img_path)


def GroundTruthFromCSV(
    csv_path: path_t,
    shape: Tuple[int, int],
    col_idc: Sequence[int],
    row_transform: Callable[[float], float],
    /,
) -> Optional[array_t]:
    #
    ground_truth = nmpy.zeros(shape, dtype=nmpy.uint8)
    if row_transform is None:
        row_transform = lambda f_idx: csgt.SymmetrizedRow(f_idx, float(shape[0]))

    try:
        with open(csv_path) as csv_accessor:
            csv_reader = csv_reader_t(csv_accessor)
            # Do not enumerate csv_reader below since some rows might be dropped
            label = 1
            for line in csv_reader:
                coords = csgt.CSVLineToCoords(line, col_idc, row_transform)
                if coords is not None:
                    if ground_truth[coords] > 0:
                        print(
                            f"{csv_path}: Multiple GTs at same position (due to rounding or duplicates)"
                        )
                        ground_truth = None
                        break
                    else:
                        ground_truth[coords] = label
                        label += 1
    except BaseException as exc:
        print(
            f"{csv_path}: Error while reading or unreadable\n({exc})", file=sstm.stderr
        )
        ground_truth = None

    return ground_truth


def GroundTruthForDetection(
    detection_name: str,
    detection_shape: Sequence[int],
    ground_truth_path: path_t,
    ground_truth_folder: path_t,
    ground_truth: Optional[array_t],
    gt_loading_fct: Callable,
    rc_idc: Tuple[int, int],
    row_transform: Callable[[float], float],
    mode: str,
) -> Tuple[Optional[array_t], path_t]:
    """"""
    if mode == "one-to-one":
        ground_truth_path = ground_truth_folder / detection_name
        ground_truth = gt_loading_fct(
            ground_truth_path, detection_shape, rc_idc, row_transform
        )
    elif ground_truth is None:  # mode = 'one-to-many'
        ground_truth = gt_loading_fct(
            ground_truth_path, detection_shape, rc_idc, row_transform
        )

    return ground_truth, ground_truth_path


def DetectionFromImage(
    path: path_t, shift_r_x_c: Tuple[int, int], /
) -> Optional[array_t]:
    """"""
    return _ImageFromPath(path, shift_r_x_c=shift_r_x_c)


def DetectionWithTolerance(detection: array_t, tolerance: int, /) -> array_t:
    #
    output = nmpy.zeros_like(detection)
    distance_map = spim.distance_transform_edt(detection != 1)
    output[distance_map <= tolerance] = 1

    for label in range(2, nmpy.amax(detection) + 1):
        current_map = spim.distance_transform_edt(detection != label)
        closer_bmap = current_map < distance_map
        output[nmpy.logical_and(closer_bmap, current_map <= tolerance)] = label
        distance_map[closer_bmap] = current_map[closer_bmap]

    return output


def LabelImageIsValid(image: array_t, /) -> Tuple[bool, Optional[str]]:
    #
    if image is None:
        return False, None

    unique_values = nmpy.unique(image)
    expected_values = range(nmpy.amax(image) + 1)

    validity = (unique_values.__len__() > 1) and nmpy.array_equal(
        unique_values, expected_values
    )

    if validity:
        mistakes = None
    elif unique_values.__len__() == 1:
        mistakes = f"Only one value present in image: {unique_values[0]}; Expected=at least 0 and 1"
    else:
        if unique_values[0] > 0:
            mistakes = ["???"]
        else:
            mistakes = [str(unique_values[0])]
        for v_m_1_idx, label in enumerate(unique_values[1:]):
            previous = unique_values[v_m_1_idx]
            label_as_str = str(label)
            if label == previous:
                mistakes.append("=" + label_as_str)
            elif label > previous + 1:
                mistakes.extend(["???", label_as_str])
            else:
                mistakes.append(label_as_str)
        mistakes = ", ".join(mistakes)

    return validity, mistakes


def _ImageFromPath(
    img_path: path_t, /, *, shift_r_x_c: Tuple[int, int] = None
) -> Optional[array_t]:
    #
    try:
        output = mgio.imread(img_path)

        if shift_r_x_c is not None:
            shifted_img = nmpy.roll(output, shift_r_x_c[0], axis=0)
            shifted_img = nmpy.roll(shifted_img, shift_r_x_c[1], axis=1)
            if shift_r_x_c[0] > 0:
                shifted_img[: shift_r_x_c[0], :] = 0
            elif shift_r_x_c[0] < 0:
                shifted_img[shift_r_x_c[0] :, :] = 0
            if shift_r_x_c[1] > 0:
                shifted_img[:, : shift_r_x_c[1]] = 0
            elif shift_r_x_c[1] < 0:
                shifted_img[:, shift_r_x_c[1] :] = 0
            output = shifted_img

        validity, mistakes = LabelImageIsValid(output)
        if not validity:
            print(
                f"{img_path}: Incorrectly labeled image:\n    {mistakes}",
                file=sstm.stderr,
            )
            output = None
    except BaseException as exc:
        print(
            f"{img_path}: Not a valid image or unreadable by imageio\n({exc})",
            file=sstm.stderr,
        )
        output = None

    return output
