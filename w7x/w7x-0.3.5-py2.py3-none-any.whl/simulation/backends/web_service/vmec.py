"""
Web Services VMEC tools.
"""

import logging
from time import sleep

import numpy as np
from netCDF4 import Dataset
import tfields

import w7x
from w7x.simulation.backends.web_service import (
    get_server,
    to_tfields_type,
    to_osa_type,
    run_service,
)
from w7x.simulation.vmec import VmecInput, Wout, get_run_status_from_threed1


WS_SERVER = w7x.config.get_option("vmec.web_service", "server")
LOGGER = logging.getLogger(__name__)


class VmecWebServiceBackend(w7x.simulation.vmec.VmecBackend):
    """
    A concrete VMEC implementation trought the web service.

    Examples:
        >>> import w7x
        >>> from w7x.simulation.backends.web_service.vmec import VmecWebServiceBackend as Vmec
        >>> state = w7x.State(
        ...     w7x.config.CoilSets.Ideal(), w7x.config.Plasma.Vacuum(),
        ...     w7x.config.Equilibria.InitialGuess())
        >>> vmec = Vmec()

        Do not run not to pollute the web service
        # >>> wout = vmec._compute(state, free_boundary=True)

        From: http://svvmec1.ipp-hgw.mpg.de:8080/vmecrest/v1/
        >>> vmec.exists("w7x.1000_1000_1000_1000_+0500_+0500.06.088")
        True

        >>> vmec.is_ready("w7x.1000_1000_1000_1000_+0500_+0500.06.088")
        True

        >>> vmec.is_successful("w7x.1000_1000_1000_1000_+0500_+0500.06.088")
        False

    """

    @staticmethod
    def _compute(state, **kwargs) -> Wout:
        """
        Compute a equilibrium with the VMEC web service.
        """

        dry_run = kwargs.pop("dry_run")

        if dry_run:
            raise TypeError("The VMEC webservice does not support the dry_run option")

        #  TODO-2(@amerlo): how to handle runs which have already been executed? -> remember long
        #  discussiong
        # TODO-1(@amerlo): look if VmecRun exists -> requires option to allow
        vmec_input = VmecInput.from_state(state, **kwargs)

        LOGGER.info(f"Executing {vmec_input.vmec_id} VMEC run on the web service.")
        vmec_server = get_server(WS_SERVER)
        vmec_id = run_service(
            vmec_server.service.execVmec,
            to_osa_type(vmec_input, ws_server=WS_SERVER),
            vmec_input.vmec_id,
        )
        assert vmec_id == vmec_input.vmec_id

        while not VmecWebServiceBackend.is_ready(vmec_id):
            #  TODO-2(@amerlo): best interval for this? -> wait mean-std, mean-std+1/x*std, ...
            LOGGER.info("%s is not ready yet ...", vmec_id)
            sleep(5)

        if not VmecWebServiceBackend.is_successful(vmec_id):
            LOGGER.warning(f"VMEC run {vmec_id} has failed.")
            status = VmecWebServiceBackend.get_status(vmec_id)
            return Wout(file_id=vmec_id, status=status)

        LOGGER.info(f"{vmec_id} run was successful.")
        return VmecWebServiceBackend.get_wout(vmec_id)

    ########################
    # BACKEND ONLY METHODS #
    ########################

    @staticmethod
    def exists(vmec_id: str) -> bool:
        """
        Check if VMEC run exists.
        """
        vmec_server = get_server(WS_SERVER)
        return run_service(vmec_server.service.vmecIdentifierExists, vmec_id)

    @staticmethod
    def is_ready(vmec_id: str) -> bool:
        """
        Check if VMEC run is ready.
        """
        vmec_server = get_server(WS_SERVER)
        return run_service(vmec_server.service.isReady, vmec_id)

    @staticmethod
    def is_successful(vmec_id: str) -> bool:
        """
        Check if VMEC run was successful.
        """
        vmec_server = get_server(WS_SERVER)
        return run_service(vmec_server.service.wasSuccessful, vmec_id)

    @staticmethod
    def get_wout(vmec_id: str) -> Wout:
        """
        Get the wout file for the requested run.

        TODO-1(@amerlo): add the path information here.
        """
        vmec_server = get_server(WS_SERVER)
        wout = Dataset(
            f"wout_{vmec_id}.nc",
            memory=run_service(vmec_server.service.getVmecOutputNetcdf, vmec_id),
            mode="r",
            diskless=True,
        )
        status = VmecWebServiceBackend.get_status(vmec_id)
        return Wout(file_id=vmec_id, data=wout, status=status)

    @staticmethod
    def get_threed1(vmec_id: str) -> str:
        """
        Get the threed1 file content as a string for the requested run.
        """
        vmec_server = get_server(WS_SERVER)
        threed1 = run_service(vmec_server.service.getVmecRunData, vmec_id, "threed1")
        return threed1

    @staticmethod
    def get_status(vmec_id: str) -> w7x.simulation.vmec.Status:
        """
        Get VMEC run status.
        """
        threed1 = VmecWebServiceBackend.get_threed1(vmec_id)
        return get_run_status_from_threed1(threed1)

    @staticmethod
    def get_b_axis(vmec_id: str, phi: float = 0.0) -> float:
        """
        Retrieve magnetic field strength on axis at given toroidal angle.

        Args:
            vmec_id: vmec identifier
            phi: phi in radian

        Returns:
            Bax(phi) - magnetic field magnitude on the magnetic axis at phi = <phi>
        """

        vmec_server = get_server(WS_SERVER)

        points = to_tfields_type(
            vmec_server.service.getMagneticAxis(vmec_id, phi),
            coord_sys=tfields.bases.CYLINDER,
        )
        points.transform(tfields.bases.CARTESIAN)

        res = vmec_server.service.magneticField(
            vmec_id, to_osa_type(points, ws_server=WS_SERVER)
        )
        B = to_tfields_type(res)

        return np.linalg.norm(B)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
