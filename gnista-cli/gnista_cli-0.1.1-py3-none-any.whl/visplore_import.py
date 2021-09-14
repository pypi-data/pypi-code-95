from structlog import get_logger

import visplorepy

from gnista_library import GnistaDataPoint, KeyringGnistaConnection

log = get_logger()


class VisploreImport:
    @staticmethod
    def start_import(gnista_id: str):

        connection = KeyringGnistaConnection()

        data_point_id = gnista_id
        data_point = GnistaDataPoint(connection=connection, data_point_id=data_point_id)

        data_point_data = None
        try:
            data_point_data = data_point.get_data_point_data()
        # pylint:disable=W0703
        except Exception as ex:
            log.critical("Exception retrieving datapoint, does it exist?", ex=ex, data_point_id=data_point_id)
            return

        if data_point_data is None:
            log.critical("could not retrive data for", data_point_id=data_point_id)
            return

        log.info("Data has been received. Plotting")

        # pylint:disable=E1101
        visplore = visplorepy.start_visplore()

        # pylint:disable=E1101
        visplore = visplorepy.connect("127.0.0.1", 50200)
        visplore.send_data(data_point_data)
