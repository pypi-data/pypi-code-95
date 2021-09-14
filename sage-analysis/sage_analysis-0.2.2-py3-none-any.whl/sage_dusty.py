#!/usr/bin/env python
"""
This module defines the ``SageBinaryData`` class. This class interfaces with the
:py:class:`~sage_analysis.model.Model` class to read in binary data written by **SAGE**.
The value of :py:attr:`~sage_analysis.model.Model.sage_output_format` is generally
``sage_binary`` if it is to be read with this class.

We refer to :doc:`../user/custom_data_classes` for more information about adding your
own Data Class to ingest data.

Author: Jacob Seiler.
"""
import logging
import os
from typing import Any, Dict, Optional

import numpy as np
from tqdm import tqdm

from sage_analysis.data_class import DataClass
from sage_analysis.model import Model
from sage_analysis.utils import read_generic_sage_params
from sage_analysis.sage_binary import SageBinaryData

logger = logging.getLogger(__name__)


class SageDustyData(SageBinaryData):

    def __init__(self, model: Model, sage_file_to_read: str) -> None:
        """
        Instantiates the Data Class for reading in **SAGE** binary data. In particular,
        generates the ``numpy`` structured array to read the output galaxies.

        model: :py:class:`~sage_analysis.model.Model` instance
            The model that this data class is associated with; this class will read the
            data for this model.
        """
        super().__init__(model, sage_file_to_read)

    def determine_volume_analyzed(self, model: Model) -> float:
        """
        Determines the volume analyzed. This can be smaller than the total simulation box.

        Parameters
        ----------
        model : :py:class:`~sage_analysis.model.Model` instance
            The model that this data class is associated with.

        Returns
        -------
        volume : float
            The numeric volume being processed during this run of the code in (Mpc/h)^3.
        """
        return super().determine_volume_analyzed(model)

    def read_sage_params(self, sage_file_path: str) -> Dict[str, Any]:
        """
        Read the **SAGE** parameter file.

        Parameters
        ----------
        sage_file_path: string
            Path to the **SAGE** parameter file.

        Returns
        -------
        model_dict: dict [str, var]
            Dictionary containing the parameter names and their values.
        """
        return super().read_sage_params(sage_file_path)


    def _get_galaxy_struct(self):
        """
        Sets the ``numpy`` structured array for holding the galaxy data.
        """
        galdesc_full = [
            ("SnapNum", np.int32),
            ("Type", np.int32),

            ("GalaxyIndex", np.int64),
            ("CentralGalaxyIndex", np.int64),
            ("SAGEHaloIndex", np.int32),
            ("SAGETreeIndex", np.int32),
            ("SimulationHaloIndex", np.int64),

            ("mergeType", np.int32),
            ("mergeIntoID", np.int32),
            ("mergeIntoSnapNum", np.int32),
            ("dT", np.float32),

            ("Pos", (np.float32, 3)),
            ("Vel", (np.float32, 3)),
            ("Spin", (np.float32, 3)),
            ("Len", np.int32),
            ("Mvir", np.float32),
            ("CentralMvir", np.float32),
            ("Rvir", np.float32),
            ("Vvir", np.float32),
            ("Vmax", np.float32),
            ("VelDisp", np.float32),

            ("ColdGas", np.float32),
            ("f_H2", np.float32),
            ("f_HI", np.float32),
            ("cf", np.float32),
            ("Zp", np.float32),
            ("Pressure", np.float32),
            ("StellarMass", np.float32),
            ("BulgeMass", np.float32),
            ("BulgeInstability", np.float32),
            ("HotGas", np.float32),
            ("EjectedMass", np.float32),
            ("BlackHoleMass", np.float32),
            ("IntraClusterStars", np.float32),

            ("MetalsColdGas", np.float32),
            ("MetalsStellarMass", np.float32),
            ("MetalsBulgeMass", np.float32),
            ("MetalsHotGas", np.float32),
            ("MetalsEjectedMass", np.float32),
            ("MetalsIntraClusterStars", np.float32),

            ("ColdDust", np.float32),
            ("HotDust", np.float32),
            ("EjectedDust", np.float32),

            ("SfrDisk", np.float32),
            ("SfrBulge", np.float32),
            ("SfrDiskZ", np.float32),
            ("SfrBulgeZ", np.float32),

            ("dustdotform", np.float32),
            ("dustdotgrowth", np.float32),
            ("dustdotdestruct", np.float32),

            ("DiskRadius", np.float32),
            ("Cooling", np.float32),
            ("Heating", np.float32),
            ("QuasarModeBHaccretionMass", np.float32),
            ("TimeOfLastMajorMerger", np.float32),
            ("TimeOfLastMinorMerger", np.float32),
            ("OutflowRate", np.float32),

            ("infallMvir", np.float32),
            ("infallVvir", np.float32),
            ("infallVmax", np.float32)
        ]
        names = [galdesc_full[i][0] for i in range(len(galdesc_full))]
        formats = [galdesc_full[i][1] for i in range(len(galdesc_full))]
        galdesc = np.dtype({"names": names, "formats": formats}, align=True)

        self.galaxy_struct = galdesc

    def determine_num_gals(self, model: Model, *args) -> None:
        """
        Determines the number of galaxies in all files for this
        :py:class:`~sage_analysis.model.Model`.

        Parameters
        ----------

        model: :py:class:`~sage_analysis.model.Model` class
            The :py:class:`~sage_analysis.model.Model` we're reading data for.

        *args : Any
            Extra arguments to allow other data class to pass extra arguments to their version of
            ``determine_num_gals``.
        """
        super().determine_num_gals(model, *args)

    def read_gals(
        self,
        model: Model,
        file_num: int,
        snapshot: int,
        pbar: Optional[tqdm] = None,
        plot_galaxies: bool = False,
        debug: bool = False
    ):
        """
        Reads the galaxies of a model file at snapshot specified by
        :py:attr:`~sage_analysis.model.Model.snapshot`.

        Parameters
        ----------

        model: :py:class:`~sage_analysis.model.Model` class
            The :py:class:`~sage_analysis.model.Model` we're reading data for.

        file_num: int
            Suffix number of the file we're reading.

        pbar: ``tqdm`` class instance, optional
            Bar showing the progress of galaxy reading.  If ``None``, progress bar will
            not show.

        plot_galaxies: bool, optional
            If set, plots and saves the 3D distribution of galaxies for this file.

        debug: bool, optional
            If set, prints out extra useful debug information.

        Returns
        -------
        gals : ``numpy`` structured array with format given by :py:method:`~_get_galaxy_struct`
            The galaxies for this file.

        Notes
        -----
        ``tqdm`` does not play nicely with printing to stdout. Hence we disable
        the ``tqdm`` progress bar if ``debug=True``.
        """
        return super().read_gals(model, file_num, snapshot, pbar=pbar, plot_galaxies=plot_galaxies, debug=debug)

    def update_snapshot_and_data_path(self, model: Model, snapshot: int, use_absolute_path: bool = False) -> None:
        """
        Updates the :py:attr:`~sage_analysis.model.Model._sage_data_path` to point to a new redshift file. Uses the
        redshift array :py:attr:`~sage_analysis.model.Model.redshifts`.

        Parameters
        ----------
        snapshot : int
            Snapshot we're updating :py:attr:`~sage_analysis.model.Model._sage_data_path` to
            point to.

        use_absolute_path : bool
            If specified, will use the absolute path to the **SAGE** output data. Otherwise, will use the path that is
            relative to the **SAGE** parameter file.  This is hand because the **SAGE** parameter file can contain
            either relative or absolute paths.
        """
        super().update_snapshot_and_data_path(model, snapshot, use_absolute_path)

    def _check_for_file(self, model: Model, file_num: int) -> Optional[str]:
        """
        Checks to see if a file for the given file number exists.  Importantly, we check assuming that the path given
        in the **SAGE** parameter file is **relative** and **absolute**.

        Parameters
        ----------
        file_num : int
            The file number that we're checking for files.

        Returns
        -------
        fname or ``None``
            If a file exists, the name of that file.  Otherwise, if the file does not exist (using either relative or
            absolute paths), then ``None``.
        """

        return super()._check_for_file(model, file_num)

    def close_file(self, model: Model):
        """
        An empty method to ensure consistency with the HDF5 data class. This is empty because snapshots are saved over
        different files by default in the binary format.
        """
        pass
