"""
web_service backend for Extender

TODO-2(@dboe): check that magnetic config is indeed the same as the field used for VMEC!!!
"""
import os
import logging
import requests

import tfields
import w7x
import w7x.simulation.flt
from w7x.simulation.backends.web_service import (
    get_server,
    run_service,
    to_osa_type,
    to_tfields_type,
)


LOGGER = logging.getLogger(__name__)
WS_SERVER = w7x.config.get_option("extender.web_service", "server")


def wout_from_state(state):
    """
    Retrieve the Wout reference from the state
    """
    wout = state.equilibrium.get_ref("flux_surfaces", "phi")
    if isinstance(wout, w7x.simulation.vmec.Wout):
        return wout
    LOGGER.warning(
        "No explicit reference to wout file found in equilibrium. "
        "Will take the last Wout file from resources."
    )

    wout_files = list(
        filter(
            lambda item: isinstance(item, w7x.simulation.vmec.Wout),
            state.resources.items,
        )
    )
    if not wout_files:
        return None
    return wout_files[-1]


def equilibrium_from_wout(wout):
    """
    Returns:
        the url to the web service run database or the local file
    """
    equilibrium_file = None
    equilibrium_url = None

    if wout.file_id:
        equilibrium_url = os.path.join(
            w7x.config.get_option("vmec.web_service", "database"),
            wout.file_id,
            "wout.nc",
        )
        request = requests.get(equilibrium_url)
        if request.status_code != 200:
            # wout file does not exist online
            equilibrium_url = None

    if equilibrium_url is not None:
        # has been set above (and not been unset)
        pass
    elif wout.path and os.path.exists(wout.path):
        with open(wout.path, "rb") as buff:
            equilibrium_file = bytearray(buff.read())
        raise NotImplementedError("Web service bug known (osa throws error).")
        # TODO: Als work-around könntest du die Dateien bei dir via SimpleHTTPServer verfügbar
        #       machen und beim Service-Aufruf die URL übergeben: der Webserver würde sich dann die
        #       Dateien via http von dir runterladen.
    else:
        raise NotImplementedError("Retrieving equilibrium from wout")

    return equilibrium_file, equilibrium_url


# pylint:disable=too-many-locals
def magnetic_config_from_state(state):
    """
    Build the osa magnetic config including coil set data, current carrier etc.
    """
    # pylint:disable=import-outside-toplevel
    from w7x.simulation.coils import Coils

    extender_client = get_server(WS_SERVER)
    my_config = extender_client.types.MagneticConfiguration()
    my_config.name = "w7x"

    active_coils = []
    active_coil_indices = []
    circuits = []
    for group in state.coil_set.get_coils(flat=True, groups=True):
        shared_supply = group.shared_supply or [(i,) for i in range(len(group.coils))]
        for supply_index, shared_coil_indices in enumerate(shared_supply):
            coils = [group.coils[i] for i in shared_coil_indices]
            current = coils[0].current  # shared supply -> all the same current

            if current == 0:
                # remove coil if curent is 0
                continue
            assert len(set(coil.n_windings for coil in coils)) == 1

            serial_circuit = extender_client.types.SerialCircuit()
            serial_circuit.name = "coil set " + group.name + f" - group {supply_index}"
            # The current direction goes to the winding direction.
            serial_circuit.current = abs(current)
            serial_circuit.currentCarrier = []
            for coil_index, coil in enumerate(coils):
                # the serial_circuit will be initialized witout the filaments for speed reasons
                active_coils.append(coil)

                current_carrier = extender_client.types.Coil()
                current_carrier.name = coil.name
                current_carrier.numWindings = coil.n_windings

                # The current direction goes to the winding direction.
                if current > 0:
                    current_carrier.windingDirection = 1.0
                else:
                    current_carrier.windingDirection = -1.0
                serial_circuit.currentCarrier.append(current_carrier)
                active_coil_indices.append((supply_index, coil_index))
            circuits.append(serial_circuit)

    coils_code = Coils("web_service")
    # this is much faster for the whole coil ids than for single ids
    # pylint:disable=protected-access
    filaments = coils_code.backend._get_filaments(*[coil.id for coil in active_coils])
    for active_coil_index, filament in zip(active_coil_indices, filaments):
        polygon_filament = extender_client.types.PolygonFilament()
        polygon_filament.vertices = to_osa_type(filament, ws_server=WS_SERVER)
        supply_index, coil_index = active_coil_index
        circuits[supply_index].currentCarrier[coil_index].currentCarrierPrimitive = [
            polygon_filament
        ]

    my_config.circuit = circuits
    return my_config


class ExtenderWebServiceBackend(w7x.simulation.extender.ExtenderBackend):
    """
    Web service backend for the extender code.
    """

    @staticmethod
    @w7x.node
    def _plasma_field(state, **kwargs) -> tfields.TensorFields:
        points = kwargs.pop("points")
        extender_server = get_server(WS_SERVER)
        wout = wout_from_state(state)
        equilibrium_file, equilibrium_url = equilibrium_from_wout(wout)

        points.transform(tfields.bases.CYLINDER)
        field = run_service(
            extender_server.service.getPlasmaField,
            equilibrium_file,
            equilibrium_url,
            to_osa_type(points, ws_server=WS_SERVER),
            None,
        )
        field = to_tfields_type(field, coord_sys=tfields.bases.PHYSICAL_CYLINDER)
        return field

    @staticmethod
    @w7x.node
    def _field(state, **kwargs) -> tfields.TensorFields:
        """
        The returned field can directly be used as a magnetic config grid with the
        field line tracer
        """
        points = kwargs.pop("points")
        extender_server = get_server(WS_SERVER)
        wout = wout_from_state(state)
        equilibrium_file, equilibrium_url = equilibrium_from_wout(wout)
        coils = magnetic_config_from_state(state)

        points.transform(tfields.bases.CYLINDER)
        field = run_service(
            extender_server.service.getExtendedField,
            equilibrium_file,
            equilibrium_url,
            coils,
            None,
            to_osa_type(points, ws_server=WS_SERVER),
            None,
        )
        field = to_tfields_type(field, coord_sys=tfields.bases.PHYSICAL_CYLINDER)
        return field


if __name__ == "__main__":
    pass
