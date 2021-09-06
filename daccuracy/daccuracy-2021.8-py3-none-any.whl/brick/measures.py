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

from collections import namedtuple as namedtuple_t
from typing import Dict, Optional, Tuple, Union

import numpy as nmpy
import scipy.optimize as spop

import daccuracy.brick.input as inpt


MEASURE_COUNTS_HEADER = ("n ground truths", "n detections")


array_t = nmpy.ndarray

std_measures_t = namedtuple_t(
    "std_measures_t",
    "correct missed invented "
    "true_positive false_positive false_negative "
    "precision recall f1_score "
    "froc_sample "
    "check_c_m_gt check_c_i_dn",
)

ext_measures_t = namedtuple_t(
    "ext_measures_t",
    "overlap_mean overlap_stddev overlap_min overlap_max "
    "jaccard_mean jaccard_stddev jaccard_min jaccard_max "
    "precision_p_mean precision_p_stddev precision_p_min precision_p_max "
    "recall_p_mean recall_p_stddev recall_p_min recall_p_max "
    "f1_score_p_mean f1_score_p_stddev f1_score_p_min f1_score_p_max",
)


def StandardMeasures(
    ground_truth: Optional[array_t],
    detection: Optional[array_t],
    tolerance: int = 0,
    return_associations: bool = False,
) -> Union[
    Tuple[str, ...],
    Tuple[int, int, std_measures_t],
    Tuple[int, int, std_measures_t, Dict[int, int]],
]:
    #
    if (ground_truth is None) and (detection is None):
        return *MEASURE_COUNTS_HEADER, *std_measures_t._fields

    # ground_truth = inpt.PointwiseGroundTruth(ground_truth)
    if tolerance > 0:
        detection = inpt.DetectionWithTolerance(detection, tolerance)

    n_gt_objects = nmpy.amax(ground_truth)
    n_dn_objects = nmpy.amax(detection)

    dn_2_gt_associations = _ObjectAssociations(
        n_dn_objects, detection, n_gt_objects, ground_truth
    )
    # gt_2_dn_associations = _ObjectAssociations(n_gt_objects, ground_truth, n_dn_objects, detection)
    # for key, value in dn_2_gt_associations.items():
    #     assert key == gt_2_dn_associations[value]
    correct = dn_2_gt_associations.__len__()
    missed = n_gt_objects - correct
    invented = n_dn_objects - correct

    result = [
        n_gt_objects,
        n_dn_objects,
        _StandardMeasuresFromCounts(correct, missed, invented),
    ]

    if return_associations:
        result.append(dn_2_gt_associations)

    return tuple(result)


def ExtendedMeasures(
    ground_truth: Optional[array_t], detection: Optional[array_t], tolerance: int = 0
) -> Union[Tuple[str, ...], Tuple[int, int, std_measures_t, ext_measures_t]]:
    #
    if (ground_truth is None) and (detection is None):
        return (
            *MEASURE_COUNTS_HEADER,
            *std_measures_t._fields,
            *ext_measures_t._fields,
        )

    n_gt_objects, n_dn_objects, std_measures, dn_2_gt_associations = StandardMeasures(
        ground_truth, detection, tolerance=tolerance, return_associations=True
    )

    overlap, jaccard, precision_p, recall_p, f1_score_p = [], [], [], [], []
    for dn_label, gt_label in dn_2_gt_associations.items():
        ground_truth_obj = ground_truth == gt_label
        detected_obj = detection == dn_label

        gt_area = nmpy.count_nonzero(ground_truth_obj)
        dn_area = nmpy.count_nonzero(detected_obj)
        union_area = nmpy.count_nonzero(nmpy.logical_or(ground_truth_obj, detected_obj))
        intersection_area = nmpy.count_nonzero(
            nmpy.logical_and(ground_truth_obj, detected_obj)
        )
        assert intersection_area > 0, "This should never happen; Contact Developer"
        one_precision = intersection_area / dn_area
        one_recall = intersection_area / gt_area

        overlap.append(100.0 * intersection_area / min(gt_area, dn_area))
        jaccard.append(intersection_area / union_area)
        precision_p.append(one_precision)
        recall_p.append(one_recall)
        f1_score_p.append(
            2.0 * one_precision * one_recall / (one_precision + one_recall)
        )

    ext_measures = ext_measures_t(
        overlap_mean=nmpy.mean(overlap),
        overlap_stddev=nmpy.std(overlap),
        overlap_min=nmpy.amin(overlap),
        overlap_max=nmpy.amax(overlap),
        jaccard_mean=nmpy.mean(jaccard),
        jaccard_stddev=nmpy.std(jaccard),
        jaccard_min=nmpy.amin(jaccard),
        jaccard_max=nmpy.amax(jaccard),
        precision_p_mean=nmpy.mean(precision_p),
        precision_p_stddev=nmpy.std(precision_p),
        precision_p_min=nmpy.amin(precision_p),
        precision_p_max=nmpy.amax(precision_p),
        recall_p_mean=nmpy.mean(recall_p),
        recall_p_stddev=nmpy.std(recall_p),
        recall_p_min=nmpy.amin(recall_p),
        recall_p_max=nmpy.amax(recall_p),
        f1_score_p_mean=nmpy.mean(f1_score_p),
        f1_score_p_stddev=nmpy.std(f1_score_p),
        f1_score_p_min=nmpy.amin(f1_score_p),
        f1_score_p_max=nmpy.amax(f1_score_p),
    )

    return n_gt_objects, n_dn_objects, std_measures, ext_measures


def _ObjectAssociations(
    n_ref_objects: int, ref_img: array_t, n_objects: int, image: array_t
) -> Dict[int, int]:
    #
    assignement_costs = nmpy.ones((n_ref_objects, n_objects), dtype=nmpy.float64)

    for ref_label in range(1, n_ref_objects + 1):
        ref_obj = ref_img == ref_label

        corresponding_labels = nmpy.unique(image[ref_obj])
        if corresponding_labels[0] == 0:
            corresponding_labels = corresponding_labels[1:]

        for crr_label in corresponding_labels:
            corresponding_obj = image == crr_label

            union_area = nmpy.count_nonzero(nmpy.logical_or(corresponding_obj, ref_obj))
            intersection_area = nmpy.count_nonzero(
                nmpy.logical_and(corresponding_obj, ref_obj)
            )

            assignement_costs[ref_label - 1, crr_label - 1] = (
                1.0 - intersection_area / union_area
            )

    row_ind, col_ind = spop.linear_sum_assignment(assignement_costs)
    valid_idc = assignement_costs[row_ind, col_ind] < 1.0
    obj_associations = dict(zip(row_ind[valid_idc] + 1, col_ind[valid_idc] + 1))

    return obj_associations


def _StandardMeasuresFromCounts(
    correct: int, missed: int, invented: int
) -> std_measures_t:
    #
    true_positive = correct
    false_positive = invented
    false_negative = missed

    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1_score = 2.0 * precision * recall / (precision + recall)
    # accuracy = (TP + TN) / (TP + TN + FP + FN)

    true_positive_rate = recall
    froc_sample = (false_positive, true_positive_rate)

    measures = std_measures_t(
        correct=correct,
        missed=missed,
        invented=invented,
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        froc_sample=froc_sample,
        check_c_m_gt=correct + missed,
        check_c_i_dn=correct + invented,
    )

    return measures
