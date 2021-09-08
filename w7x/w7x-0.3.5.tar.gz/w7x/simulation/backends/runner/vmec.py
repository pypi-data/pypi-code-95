"""
Runner Vmec tools.
"""

import logging
import os

from netCDF4 import Dataset

import w7x
from w7x.simulation.vmec import (
    VmecInput,
    VmecBackend,
    Wout,
    Status,
    get_indata_file_name,
    get_run_status_from_threed1,
    is_status_successful,
    is_status_ready,
)
from w7x.simulation.backends.runner.base import (
    Job,
    RunnerBackendMixin,
    submit,
    isfile,
    isdir,
    read_file,
)


LOGGER = logging.getLogger(__name__)


class VmecRunnerBackend(VmecBackend, RunnerBackendMixin):
    """
    A concrete VMEC implementation.

    Examples:
        >>> import w7x
        >>> import tempfile
        >>> dtemp = tempfile.mkdtemp()
        >>> w7x.config.set_option("vmec.slurm", "folder", dtemp)
        >>> from w7x.simulation.vmec import Vmec
        >>> state = w7x.State(
        ...     w7x.config.CoilSets.Ideal(), w7x.config.Plasma.Vacuum(),
        ...     w7x.config.Equilibria.InitialGuess())
        >>> vmec = Vmec()
        >>> vmec.backend = "slurm"

        >>> wout = vmec.backend._compute(state, free_boundary=True, dry_run=True)
        >>> wout.status == w7x.simulation.vmec.Status.NOT_STARTED
        True

        >>> os.path.isfile(
        ...     os.path.join(
        ...         dtemp, wout.file_id, "slurm"
        ...     )
        ... )
        True

        >>> import shutil
        >>> shutil.rmtree(dtemp)

    """

    def _compute(self, state, **kwargs):
        """
        Compute an equilibrium with VMEC on the HPC.
        """

        dry_run = kwargs.pop("dry_run")

        vmec_input = VmecInput.from_state(state, **kwargs)
        vmec_id = vmec_input.vmec_id

        LOGGER.info(f"Executing {vmec_id} run on the {self.runner} runner.")
        job = Job(
            name=vmec_id,
            cwd=self.folder,
            files=[(vmec_input.to_string(), get_indata_file_name(vmec_id))],
            modules=["cmake", "gcc", "impi", "mkl", "hdf5-mpi", "netcdf-mpi"],
            cmd=f"{self.exe} {get_indata_file_name(vmec_id)}",
        )
        submit(self.runner, job, dry_run=dry_run)

        if dry_run:
            return Wout(file_id=vmec_id, status=Status.NOT_STARTED)

        status = self.get_status(vmec_id)
        LOGGER.info(f"{vmec_id} has finished with {status}.")
        return self.get_wout(vmec_id)

    ########################
    # BACKEND ONLY METHODS #
    ########################

    def get_run_path(self, vmec_id: str) -> str:
        """
        Return path for vmec_id run.
        """
        return os.path.join(self.folder, vmec_id)

    def exists(self, vmec_id: str) -> bool:
        """
        Chekc if VMEC run exists.
        """
        return isdir(self.runner, self.get_run_path(vmec_id)) and isfile(
            self.runner,
            os.path.join(self.get_run_path(vmec_id), get_indata_file_name(vmec_id)),
        )

    def is_ready(self, vmec_id: str) -> bool:
        """
        Check if VMEC run is ready.
        """
        status = self.get_status(vmec_id)
        return is_status_ready(status)

    def is_successful(self, vmec_id: str) -> bool:
        """
        Check if VMEC run was successful.
        """
        status = self.get_status(vmec_id)
        return is_status_successful(status)

    def get_status(self, vmec_id: str) -> w7x.simulation.vmec.Status:
        """
        Get VMEC run status.
        """

        threed1_file_path = os.path.join(
            self.get_run_path(vmec_id), f"threed1.{vmec_id}"
        )

        if not isfile(self.runner, threed1_file_path):
            return w7x.simulation.vmec.Status.NOT_STARTED

        threed1 = str(read_file(self.runner, threed1_file_path))
        return get_run_status_from_threed1(threed1)

    def get_wout(self, vmec_id: str) -> Wout:
        """
        Get the wout file for the requested run.
        """
        wout_file_path = os.path.join(self.get_run_path(vmec_id), f"wout_{vmec_id}.nc")
        wout = None
        if os.path.isfile(wout_file_path):
            wout = Dataset(
                f"wout_{vmec_id}.nc",
                memory=read_file(self.runner, wout_file_path),
                mode="r",
                diskless=True,
            )
        status = self.get_status(vmec_id)
        return Wout(file_id=vmec_id, path=wout_file_path, data=wout, status=status)
