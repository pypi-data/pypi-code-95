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

import os.path as osph
import sys as sstm

import matplotlib.pyplot as pypl
import numpy as nmpy


array_t = nmpy.ndarray


def OutputStream(output_path: str, /) -> object:
    """"""
    if output_path == "-":
        return sstm.stdout

    if osph.exists(output_path):
        print(f"{output_path}: Overwriting not supported; Delete first to use the same name", file=sstm.stderr)
        sstm.exit(-1)

    return open(output_path, "w")


def ImageForDisplay(image: array_t) -> array_t:
    """"""
    img_for_display = nmpy.array(image, dtype=nmpy.float32)

    img_for_display[img_for_display == 0] = nmpy.nan
    img_for_display -= nmpy.nanmin(img_for_display)
    img_max = nmpy.nanmax(img_for_display)
    if img_max > 0.0:
        img_for_display *= 150.0 / img_max
    img_for_display += 105.0
    img_for_display[nmpy.isnan(img_for_display)] = 0

    return nmpy.around(img_for_display).astype(nmpy.uint8)


def PrepareMixedGTDetectionImage(ground_truth:array_t, detection:array_t)->None:
    """"""
    gt_for_display = ImageForDisplay(ground_truth)
    img = nmpy.dstack(
        (gt_for_display, gt_for_display, ImageForDisplay(detection))
    )
    pypl.imshow(img)


def ShowPreparedImages()->None:
    """"""
    pypl.show()
