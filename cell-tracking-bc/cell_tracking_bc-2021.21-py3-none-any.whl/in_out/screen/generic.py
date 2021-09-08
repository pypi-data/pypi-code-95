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
import numpy as nmpy
from mpl_toolkits.mplot3d import Axes3D as axes_3d_t

from cell_tracking_BC.in_out.storage.archiver import archiver_t


def FinalizeDisplay(
    figure: pypl.Figure, figure_name: str, show_and_wait: bool, archiver: archiver_t, /
) -> None:
    """"""
    if archiver is not None:
        figure.canvas.draw_idle()
        archiver.Store(figure, figure_name)

    if show_and_wait:
        pypl.show()


def SetTimeAxisProperties(highest_value: int, axes: pypl.Axes, /) -> None:
    """"""
    axes.set_xlim(0, highest_value)
    axes.set_xticks(range(highest_value + 1))
    axes.set_xticklabels(str(_idx) for _idx in range(highest_value + 1))


def SetZAxisProperties(
    n_segmentations: int, time_stretching: float, axes: axes_3d_t, /
) -> None:
    """"""
    z_max = time_stretching * (n_segmentations - 1)
    axes.set_zlim(0, z_max)
    axes.set_zticks(nmpy.linspace(0.0, z_max, num=n_segmentations))
    axes.set_zticklabels(str(_idx) for _idx in range(n_segmentations))
