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

from pathlib import Path as path_t
from typing import Callable, Optional, Sequence, Tuple, Union

from daccuracy.brick.measures import ext_measures_t, std_measures_t


COL_SEPARATOR = "; "


# --- INPUT


def SymmetrizedRow(idx: float, img_height: float) -> float:
    """"""
    return img_height - idx - 1.0


def ColLabelToIdx(label: str) -> int:
    #
    reference = ord("A")
    if (length := label.__len__()) > 1:
        ords = map(lambda _ltt: ord(_ltt) - reference + 1, reversed(label))
        powers = (26 ** _idx for _idx in range(length))
        output = sum(_ord * _pwr for _ord, _pwr in zip(ords, powers)) - 1
    else:
        output = ord(label) - reference

    return output


def CSVLineToCoords(
    # line instead of row to avoid confusion with row index of center
    line: Sequence[str],
    col_idc: Sequence[int],
    row_transform: Callable[[float], float],
) -> Optional[Tuple[int, ...]]:
    #
    try:
        row = float(line[col_idc[0]])
    except ValueError:
        # CSV header line
        return None

    coords = (row_transform(row), float(line[col_idc[1]]))

    return tuple(round(elm) for elm in coords)


# --- OUTPUT


def HeaderRow(measure_header: Sequence[str]) -> Sequence[str]:
    #
    measure_header = tuple(elm.capitalize() for elm in measure_header)

    return (
        "Ground truth",
        "Detection",
        *measure_header,
    )


def MeasureRow(
    ground_truth_path: path_t,
    detection_path: path_t,
    measures: Union[
        Tuple[int, int, std_measures_t], Tuple[int, int, std_measures_t, ext_measures_t]
    ],
) -> Sequence[str]:
    #
    measure_row = [
        ground_truth_path.name,
        detection_path.name,
        *tuple(elm.__str__() for elm in measures[:2]),
    ]

    for group in measures[2:]:
        measure_row.extend(elm.__str__() for elm in group._asdict().values())

    return measure_row
