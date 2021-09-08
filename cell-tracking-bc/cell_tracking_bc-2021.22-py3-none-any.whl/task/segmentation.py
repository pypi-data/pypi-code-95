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

import numpy as nmpy
import skimage.morphology as mrph
import skimage.segmentation as sgmt
import tensorflow.keras.models as modl
from scipy import ndimage as image_t
from scipy.spatial import distance as dstc


array_t = nmpy.ndarray
processing_h = Callable[[array_t], array_t]


def SegmentationsWithTFNetwork(
    frames: Sequence[array_t],
    network_path: Union[str, path_t],
    /,
    *,
    threshold: float = 0.9,
    PreProcessed: processing_h = None,
    PostProcessed: processing_h = None,
) -> Sequence[array_t]:
    """
    PostProcessed: Could be used to clear border objects. However, since one might want to segment cytoplasms and
    nuclei, clearing border objects here could lead to clearing a cytoplasm while keeping its nucleus. Consequently,
    clearing border objects here, i.e. independently for each segmentation task, is not appropriate. Instead, it has
    been deferred to frame_t.AddCellsFromSegmentations.
    """
    output = []

    if PreProcessed is not None:
        frames = tuple(PreProcessed(_frm) for _frm in frames)
    if PostProcessed is None:
        PostProcessed = lambda _prm: _prm

    frames = nmpy.array(frames, dtype=nmpy.float32)
    if frames.ndim == 3:
        frames = nmpy.expand_dims(frames, axis=3)

    network = modl.load_model(network_path)
    predictions = network.predict(frames)
    shape = network.layers[0].input_shape[0][1:-1]

    for t_idx, prediction in enumerate(predictions):
        reshaped = nmpy.reshape(prediction, shape)
        segmentation = reshaped > threshold
        post_processed = PostProcessed(segmentation)
        if nmpy.amax(post_processed.astype(nmpy.uint8)) == 0:
            raise ValueError(f"{t_idx}: Empty segmentation")

        output.append(post_processed)

    return output


def CorrectSegmentationBasedOnTemporalCoherence(
    segmentation: array_t, previous: array_t, /, *, min_jaccard: float = 0.75
) -> bool:
    """
    Actually, Pseudo-Jaccard
    """
    has_been_corrected = False

    labeled, n_cells = mrph.label(segmentation, return_num=True, connectivity=1)
    labeled_previous, n_cells_previous = mrph.label(
        previous, return_num=True, connectivity=1
    )

    def PseudoJaccard(idx_1: int, idx_2: int, /) -> float:
        """"""
        map_1 = labeled_previous == idx_1
        map_2 = labeled == idx_2

        intersection = nmpy.logical_and(map_1, map_2)
        intersection_area = nmpy.count_nonzero(intersection)

        t_p_1_area = nmpy.count_nonzero(map_2)

        return intersection_area / t_p_1_area

    cells_idc = nmpy.fromiter(range(1, n_cells + 1), dtype=nmpy.uint64)
    cells_idc_previous = nmpy.fromiter(
        range(1, n_cells_previous + 1), dtype=nmpy.uint64
    )
    pairwise_jaccards = dstc.cdist(
        cells_idc_previous[:, None], cells_idc[:, None], metric=PseudoJaccard
    )

    for label in range(1, n_cells + 1):
        previous_label = nmpy.argmax(pairwise_jaccards[:, label - 1]).item() + 1
        jaccard = pairwise_jaccards[previous_label - 1, label - 1]

        # TODO: do a post-check: cell at t and divided cells at t+1 ~ same areas
        if 0.0 < jaccard < min_jaccard:
            where_fused = labeled == label
            distance_map = image_t.distance_transform_edt(where_fused)

            first_seed = labeled_previous == previous_label
            nmpy.logical_and(first_seed, where_fused, out=first_seed)

            threshold_too_large = nmpy.amax(distance_map[where_fused])
            threshold = nmpy.amin(distance_map[first_seed])
            labeled_seeds = None
            n_seeds = 1
            while (n_seeds < 2) and (threshold < threshold_too_large):
                seeds = distance_map > threshold
                labeled_seeds, n_seeds = mrph.label(
                    seeds, return_num=True, connectivity=2
                )
                threshold += 1.0

            if n_seeds > 1:
                separated = sgmt.watershed(
                    -distance_map, labeled_seeds, mask=where_fused, watershed_line=True
                )
                segmentation[where_fused] = 0
                segmentation[separated > 0] = 1
                has_been_corrected = True

    return has_been_corrected


def CorrectSegmentationsBasedOnTemporalCoherence(
    segmentations: Sequence[array_t], /, *, min_jaccard: float = 0.75
) -> None:
    """"""
    for f_idx in range(1, segmentations.__len__()):
        has_been_corrected = True
        while has_been_corrected:
            has_been_corrected = CorrectSegmentationBasedOnTemporalCoherence(
                segmentations[f_idx], segmentations[f_idx - 1], min_jaccard=min_jaccard
            )
