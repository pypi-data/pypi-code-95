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

import numbers as nmbr
import tempfile as temp
from pathlib import Path as path_t
from typing import Dict, Optional, Sequence, Union

import xlsxwriter as xlsx

from cell_tracking_BC.type.sequence import sequence_t


def SaveCellFeatureToXLSX(
    path: Union[str, path_t],
    sequence: sequence_t,
    /,
    *,
    feature: Union[str, Sequence[str]] = None,
) -> None:
    """"""
    if isinstance(path, str):
        path = path_t(path)
    if feature is None:
        features = sequence.AvailableCellFeatures()
    elif isinstance(feature, str):
        features = (feature,)
    else:
        features = feature

    if path.exists():
        print(f"{path}: File (or folder) already exists...")
        path = path_t(temp.mkdtemp()) / path.name
        print(f"Using {path} instead")

    workbook = xlsx.Workbook(str(path))

    for feature in features:
        evolutions = sequence.FeatureEvolutionsOfAllCells(feature)
        if not isinstance(evolutions[1][0], nmbr.Number):
            continue

        worksheet = workbook.add_worksheet(feature)
        for label, data in evolutions.items():
            worksheet.write_row(label - 1, 0, data)

    workbook.close()


def SaveCellEventsToXLSX(
    path: Union[str, path_t],
    cell_division_frame_idc: Dict[int, Sequence[int]],
    cell_death_frame_idc: Union[Dict[int, int], Dict[str, Dict[int, int]]],
    /,
    *,
    death_response: Union[
        Dict[int, Optional[Sequence[float]]],
        Dict[str, Dict[int, Optional[Sequence[float]]]],
    ] = None,
) -> None:
    """"""
    if isinstance(path, str):
        path = path_t(path)
    if path.exists():
        print(f"{path}: File (or folder) already exists...")
        path = path_t(temp.mkdtemp()) / path.name
        print(f"Using {path} instead")

    workbook = xlsx.Workbook(str(path))

    worksheet = workbook.add_worksheet("divisions")
    for label, divisions_idc in cell_division_frame_idc.items():
        worksheet.write_row(label - 1, 0, divisions_idc)

    if death_response is not None:
        if isinstance(tuple(death_response.keys())[0], int):
            _SaveDeathResponse(workbook, "", death_response)
        else:
            for suffix, contents in death_response.items():
                _SaveDeathResponse(workbook, " " + suffix, contents)

    if isinstance(tuple(cell_death_frame_idc.keys())[0], int):
        _SaveDeathEvents(workbook, "", cell_death_frame_idc)
    else:
        for suffix, contents in cell_death_frame_idc.items():
            _SaveDeathEvents(workbook, " " + suffix, contents)

    workbook.close()


def _SaveDeathResponse(
    workbook: xlsx.Workbook,
    sheet_suffix: str,
    death_response: Dict[int, Optional[Sequence[float]]],
    /,
) -> None:
    """"""
    worksheet = workbook.add_worksheet(f"death response{sheet_suffix}")
    for label, response in death_response.items():
        if response is not None:
            worksheet.write_row(label - 1, 0, response)


def _SaveDeathEvents(
    workbook: xlsx.Workbook, sheet_suffix: str, cell_death_frame_idc: Dict[int, int], /
) -> None:
    """"""
    worksheet = workbook.add_worksheet(f"death time{sheet_suffix}")
    for label, death_idx in cell_death_frame_idc.items():
        worksheet.write_number(label - 1, 0, death_idx)
