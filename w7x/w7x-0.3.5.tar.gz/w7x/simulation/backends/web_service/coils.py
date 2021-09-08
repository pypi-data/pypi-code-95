"""
Web service backend of the components code
"""
import typing
import numpy as np

import tfields
import w7x
from w7x.simulation.coils import CoilsBackend
from w7x.simulation.backends.web_service.base import get_server


WS_DB = w7x.config.get_option("coils.web_service", "database")


class CoilsWebServiceBackend(CoilsBackend):
    """
    Backend implementation
    """

    @staticmethod
    @w7x.node
    # pylint:disable=too-many-locals
    def _get_filaments(
        *coil_ids: typing.Union[int, w7x.model.Coil]
    ) -> typing.List[tfields.Points3D]:
        """
        Get the filaments belonging to the coils of the given coil_ids
        """
        coils_db_client = get_server(WS_DB)

        # One request is nothing in time as compared to the communication time with the ws!
        coil_data = coils_db_client.service.getCoilData(list(coil_ids))

        filaments = []
        for coil_info in coil_data:
            filament = tfields.Points3D(
                np.transpose(
                    [
                        coil_info.vertices.x1,
                        coil_info.vertices.x2,
                        coil_info.vertices.x3,
                    ]
                )
            )
            filaments.append(filament)
        return filaments


if __name__ == "__main__":
    import logging
    from netCDF4 import Dataset

    logging.basicConfig(level=0)
    cwb = CoilsWebServiceBackend()
    filaments = cwb._get_filaments(*range(69))

    path = "test.txt"
    joined_filaments = tfields.Points3D.merged(
        *filaments,
        name="Joined Filaments of 70 coils. Coil indices and lenghts :"
        + str({i: len(fil) for i, fil in enumerate(filaments)}),
    )
    joined_filaments.save(path)

    path = "test.nc"

    with Dataset(path, "w") as ds:
        coordinates = ds.createDimension("coordinates", 3)  # x, y, z
        vertices = ds.createDimension(
            "vertices", None
        )  # unlimited axis (can be appended to).

        for i, filament in enumerate(filaments):
            value = ds.createVariable(
                f"coil_{i}_filaments", filament.dtype, (vertices.name, coordinates.name)
            )
            value.units = "m"
            value[:, :] = filament

    ds = Dataset(path)
    print(ds["coil_0_filaments"][:])
    print(ds["coil_1_filaments"][:])
    print(ds)
    # import pdb; pdb.set_trace()
