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

import warnings as wrng
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as nmpy
import skimage.morphology as mrph
import skimage.segmentation as sgmt

from cell_tracking_BC.in_out.console.uid import ShortID
from cell_tracking_BC.type.cell import cell_t


array_t = nmpy.ndarray
inner_outer_associations_h = Dict[int, Union[int, Tuple[int, int]]]


class frame_t(array_t):
    """
    A Frame is one plane, or channel, of a (potentially multi-channel) image
    """

    def __new__(cls, array: array_t, /) -> frame_t:
        """"""
        if (n_dims := array.ndim) != 2:
            raise ValueError(
                f"{n_dims}: Invalid number of dimensions of frame with shape {array.shape}; "
                f"Expected=2=ROWSxCOLUMNS"
            )

        instance = nmpy.asarray(array).view(cls)
        instance.path = None
        instance.cells = []
        instance.runtime = {}

        return instance

    def __array_finalize__(self, array: Optional[array_t], /) -> None:
        """"""
        if array is None:
            return
        self.path = getattr(array, "path", None)
        self.cells = getattr(array, "cells", None)

    def ApplyTransform(self, Transform: transform_h, /, **kwargs) -> None:
        """"""
        transformed = Transform(self, **kwargs)
        self[...] = transformed[...]

    def AddCellsFromSegmentations(
        self,
        /,
        *,
        nuclei_sgm: array_t = None,
        cytoplasms_sgm: array_t = None,
        cells_sgm: array_t = None,
        should_clear_border_cells: bool = True,
    ) -> None:
        """
        Segmentation are supposed to be binary (as opposed to already labeled)
        Valid options: See cell_t.AllCompartmentsFromSomeCompartments
        """
        # --- Generic inner and outer segmentation list for all call options
        segmentations = cell_t.AllCompartmentsFromSome(
            nuclei_sgm, cytoplasms_sgm, cells_sgm
        )
        nuclei_sgm, cytoplasms_sgm, cells_sgm = segmentations
        if nuclei_sgm is None:
            if cytoplasms_sgm is None:
                segmentations = [cells_sgm]
                parameters = ("cell_map",)
            else:
                segmentations = [cytoplasms_sgm, cells_sgm]
                parameters = ("cytoplasm_map", "cell_map")
        else:
            if cytoplasms_sgm is None:
                segmentations = [nuclei_sgm, cells_sgm]
                parameters = ("nucleus_map", "cell_map")
            else:
                segmentations = [nuclei_sgm, cytoplasms_sgm]
                parameters = ("nucleus_map", "cytoplasm_map")

        if should_clear_border_cells:
            self.__class__._ClearBorderObjects(segmentations, cytoplasms_sgm)

        # --- Segmentation labeling and (if needed) inner-outer label associations
        n_objects_per_sgm = []
        for s_idx in range(segmentations.__len__()):
            segmentation = segmentations[s_idx]
            segmentations[s_idx], n_objects = mrph.label(
                segmentation, return_num=True, connectivity=1
            )
            n_objects_per_sgm.append(n_objects)
        if segmentations.__len__() > 1:
            inner_label_of_outer = self.__class__._InnerOuterAssociations(
                segmentations, n_objects_per_sgm
            )
            self.__class__._CheckInnerOuterAssociations(
                inner_label_of_outer, n_objects_per_sgm
            )
        else:
            inner_label_of_outer = None

        # --- Cell creation and addition
        for outer_label in range(1, n_objects_per_sgm[-1] + 1):
            if inner_label_of_outer is None:
                labels = (outer_label,)
            else:
                labels = (inner_label_of_outer[outer_label], outer_label)
            kwargs = {}
            additional_nucleus = None
            for parameter, segmentation, label in zip(
                parameters, segmentations, labels
            ):
                label: Union[int, Tuple[int, int]]
                if isinstance(label, int):
                    kwargs[parameter] = segmentation == label
                else:
                    kwargs[parameter] = segmentation == label[0]
                    additional_nucleus = label[1]
            cell = cell_t.NewFromMaps(labels[-1], **kwargs)
            if additional_nucleus is not None:
                cell.AddNucleus(segmentations[0] == additional_nucleus)
            self.cells.append(cell)

    @staticmethod
    def _ClearBorderObjects(
        segmentations: List[array_t], cytoplasms_sgm: array_t, /
    ) -> None:
        """
        Is a static method (as opposed to module function) so that it can be overridden in class derivation
        """
        # --- Clear outer segmentation border objects
        sgmt.clear_border(segmentations[-1], in_place=True)

        if segmentations.__len__() > 1:
            # --- Clear inner segmentation border objects
            if segmentations[0] is cytoplasms_sgm:
                sgmt.clear_border(segmentations[0], in_place=True)
            else:
                dilated = mrph.dilation(segmentations[0])
                labeled, n_objects = mrph.label(
                    dilated, return_num=True, connectivity=1
                )
                for label in range(1, n_objects + 1):
                    where_label = labeled == label
                    if nmpy.any(segmentations[1][where_label] > 0):
                        pass
                    else:
                        dilated[where_label] = 0
                segmentations[0][dilated == 0] = 0

    @staticmethod
    def _InnerOuterAssociations(
        segmentations: List[array_t], n_objects_per_sgm: Sequence[int], /
    ) -> inner_outer_associations_h:
        """
        Is a static method (as opposed to module function) so that it can be overridden in class derivation
        """
        output = {}

        for inner_label in range(1, n_objects_per_sgm[0] + 1):
            dilated = mrph.dilation(segmentations[0] == inner_label)
            outer_label = nmpy.amax(segmentations[1][dilated])
            if outer_label in output:
                output[outer_label] = (
                    output[outer_label],
                    inner_label,
                )
                if output[outer_label].__len__() > 2:
                    raise RuntimeError("Cell with more than 2 nuclei")
            else:
                output[outer_label] = inner_label

        return output

    @staticmethod
    def _CheckInnerOuterAssociations(
        inner_label_of_outer: inner_outer_associations_h,
        n_objects_per_sgm: Sequence[int],
        /,
    ) -> None:
        """
        Is a static method (as opposed to module function) so that it can be overridden in class derivation
        """
        if n_objects_per_sgm[0] != n_objects_per_sgm[1]:
            wrng.warn(
                f"Mismatch in number of segmented objects: {n_objects_per_sgm}; Might be due to cell divisions though"
            )

        inner_labels = []
        for label in inner_label_of_outer.values():
            if isinstance(label, int):
                inner_labels.append(label)
            else:
                inner_labels.extend(label)
        outer_labels = tuple(inner_label_of_outer.keys())
        n_inner_labels = nmpy.unique(inner_labels).size
        n_outer_labels = nmpy.unique(outer_labels).size
        if (n_missing_associations := n_objects_per_sgm[0] - n_inner_labels) > 0:
            wrng.warn(
                f"{n_missing_associations} inner comportment(s) not associated with outer compartments"
            )
        if (n_missing_associations := n_objects_per_sgm[1] - n_outer_labels) > 0:
            wrng.warn(
                f"{n_missing_associations} outer comportment(s) without inner compartment(s)"
            )

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.path=}\n"
            f"    {self.shape=}\n"
            f"    {self.cells.__len__()=}"
        )


transform_h = Callable[[frame_t, Dict[str, Any]], array_t]
