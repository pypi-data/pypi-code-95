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

import matplotlib.pyplot as pypl

from cell_tracking_BC.in_out.screen.generic import (
    FinalizeDisplay,
    SetTimeAxisProperties,
)
from cell_tracking_BC.in_out.storage.archiver import archiver_t
from cell_tracking_BC.type.sequence import sequence_t


def ShowCellFeatureEvolution(
    sequence: sequence_t,
    feature: str,
    /,
    *,
    show_and_wait: bool = True,
    figure_name: str = "segmentation",
    archiver: archiver_t = None,
) -> None:
    """"""
    figure = pypl.figure()
    axes = figure.add_subplot(111)
    axes.set_title(feature)

    longest_evolution = 0
    for c_idx, cell in enumerate(sequence.RootCells()):
        evolutions = sequence.FeatureEvolutionOfCell(cell, feature)
        for e_idx, evolution in enumerate(evolutions):
            if e_idx > 0:
                label = f"{c_idx}.{e_idx}"
            else:
                label = str(c_idx)
            axes.plot(evolution, label=label)

            if (length := evolution.__len__()) > longest_evolution:
                longest_evolution = length
    SetTimeAxisProperties(longest_evolution - 1, axes)
    axes.legend()

    FinalizeDisplay(figure, figure_name, show_and_wait, archiver)
