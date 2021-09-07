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

import re as rgex
import sys as sstm
from argparse import ArgumentParser as argument_parser_t
from argparse import RawDescriptionHelpFormatter
from pathlib import Path as path_t
from typing import Sequence

import __main__ as main_package

import daccuracy.brick.csv_gt as csgt
import daccuracy.brick.input as inpt
import daccuracy.brick.measures as msrs
import daccuracy.brick.output as otpt


DACCURACY_DESCRIPTION = """3 modes:
    - one-to-one: one ground-truth (image or csv) vs. one detection (image)
    - one-to-many: one ground-truth (image or csv) vs. several detections (folder of images)
    - many-to-many: several ground-truths (folder of images and/or csv's) vs. corresponding detections (folder of images)

Note that, WITH MOST IMAGE FORMATS, ground-truth and detection CANNOT CONTAIN MORE THAN 255 OBJECTS.
If they do, DAccuracy will complain about the image being incorrectly labeled. This constraint will be relaxed in a
future version (it cannot be simply removed when using fixed-length representations of integers) by allowing to pass
files of Numpy arrays and unlabeled images.
"""


def ProcessedArguments(arguments: Sequence[str], /) -> tuple:
    #
    parser = _ArgumentParser()
    std_args, other_args = parser.parse_known_args(arguments)

    ground_truth_path = path_t(std_args.ground_truth_path)
    detection_path = path_t(std_args.detection_path)

    if not (ground_truth_path.is_file() or ground_truth_path.is_dir()):
        print(f"{ground_truth_path}: Not a file or folder", file=sstm.stderr)
        sstm.exit(-1)
    if not (detection_path.is_file() or detection_path.is_dir()):
        print(f"{detection_path}: Not a file or folder", file=sstm.stderr)
        sstm.exit(-1)
    if detection_path.is_file() and not ground_truth_path.is_file():
        print(
            f"{ground_truth_path}: Not a file while detection is a file",
            file=sstm.stderr,
        )
        sstm.exit(-1)

    if (other_args.__len__() > 0) and (
        (other_args[0] == __file__)
        or (path_t(other_args[0]).resolve() == path_t(main_package.__file__).resolve())
    ):
        other_args = other_args[1:]

    in_mode = row_idx = col_idx = row_transform = None

    if other_args.__len__() > 1:
        print("Too many arguments", file=sstm.stderr)
        parser.print_help()
        sstm.exit(-1)
    #
    elif other_args.__len__() > 0:
        in_mode = other_args[0]
        match = rgex.fullmatch("--([rx])([A-Z]+)([cy])([A-Z]+)", in_mode)

        if match is None:
            print(f"{in_mode}: Invalid option", file=sstm.stderr)
            parser.print_help()
            sstm.exit(-1)

        if match.group(1) == "r":
            if match.group(3) != "c":
                print(f'{in_mode}: "r"/"y" mixing', file=sstm.stderr)
                sstm.exit(-1)

            row_idx = csgt.ColLabelToIdx(match.group(2))
            col_idx = csgt.ColLabelToIdx(match.group(4))
            row_transform = lambda f_idx: f_idx
        #
        else:
            if match.group(3) != "y":
                print(f'{in_mode}: "x"/"c" mixing', file=sstm.stderr)
                sstm.exit(-1)

            row_idx = csgt.ColLabelToIdx(match.group(4))
            col_idx = csgt.ColLabelToIdx(match.group(2))

        in_mode = "csv"
    #
    elif ground_truth_path.suffix.lower() == ".csv":
        row_idx = 0
        col_idx = 1
        row_transform = lambda f_idx: f_idx
        in_mode = "csv"
    #
    else:
        in_mode = "map"

    if in_mode == "csv":
        gt_loading_fct = inpt.GroundTruthFromCSV
        measure_fct = msrs.StandardMeasures
    else:
        gt_loading_fct = inpt.GroundTruthFromImage
        measure_fct = msrs.ExtendedMeasures

    return (
        ground_truth_path,
        detection_path,
        gt_loading_fct,
        measure_fct,
        (row_idx, col_idx),
        row_transform,
        std_args,
    )


def _ArgumentParser() -> argument_parser_t:
    """"""
    output = argument_parser_t(
        prog=path_t(main_package.__file__).stem,
        description=DACCURACY_DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    output.add_argument(
        "--gt",
        type=str,
        required=True,
        dest="ground_truth_path",
        metavar="ground_truth",
        help="Ground-truth labeled image or CSV file of centers, or ground-truth folder; "
        "If CSV, --rAcB (or --xAyB) can be passed additionally "
        "to indicate that columns A and B contain the centers' "
        "rows and cols, respectively (or x's and y's in x/y mode)."
        "Columns must be specified as (possibly sequences of) uppercase letters, "
        "as is usual in spreadsheet applications.",
    )
    output.add_argument(
        "--dn",
        type=str,
        required=True,
        dest="detection_path",
        metavar="detection",
        help="Detection labeled image, or detection folder.",
    )
    output.add_argument(
        "--shifts",
        type=int,
        nargs=2,
        default=None,
        dest="shift_r_x_c",
        metavar="Dn_shift",
        help="Vertical (row) and horizontal (col) shifts to apply to detection.",
    )
    output.add_argument(
        "-e",
        "--exclude-border",
        action="store_true",
        dest="should_exclude_border",
        help="If present, this option instructs to discard objects touching image border, "
        "both in ground-truth and detection.",
    )
    output.add_argument(
        "-t",
        "--tol",
        "--tolerance",
        type=int,
        default=0,
        dest="tolerance",
        help="Max ground-truth-to-detection distance to count as a hit "
        "(meant to be used when ground-truth is a CSV file of centers).",
    )
    output.add_argument(
        "-f",
        "--format",
        type=str,
        choices=("csv", "nev"),
        default="nev",
        dest="output_format",
        help='nev: one "Name = Value"-row per measure; '
        "csv: one CSV-row per ground-truth/detection pairs.",
    )
    output.add_argument(
        "-o",
        type=otpt.OutputStream,  # Do not use the same approach with gt and dn since they can be folders
        default=sstm.stdout,
        dest="output_accessor",
        metavar="Output file",
        help="Name-Value or CSV file to store the computed measures, "
        'or "-" for console output.',
    )
    output.add_argument(
        "-s",
        "--show-image",
        action="store_true",
        dest="should_show_image",
        help="If present, this option instructs to show an image "
        "superimposing ground-truth onto detection.",
    )
    output.add_argument(
        "--no-usage-notice",
        action="store_false",
        dest="should_show_usage_notice",
        help="Silences usage notice about maximum number of objects.",
    )

    return output
