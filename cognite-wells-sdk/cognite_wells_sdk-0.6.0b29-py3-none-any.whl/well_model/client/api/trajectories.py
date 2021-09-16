import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import TrajectoryDataList, TrajectoryList
from cognite.well_model.client.models.trajectory_rows import TrajectoryRows
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._distance_unit import create_distance_unit
from cognite.well_model.client.utils._identifier_list import create_identifier, identifier_list
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DistanceRange,
    Trajectory,
    TrajectoryDataItems,
    TrajectoryDataRequest,
    TrajectoryDataRequestItems,
    TrajectoryFilter,
    TrajectoryFilterRequest,
    TrajectoryIngestion,
    TrajectoryIngestionItems,
    TrajectoryInterpolationRequest,
    TrajectoryInterpolationRequestItems,
    TrajectoryItems,
    TrueVerticalDepths,
)

logger = logging.getLogger(__name__)


class TrajectoriesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

        @extend_class(Trajectory)
        def data(
            this: Trajectory,
            measured_depth: Optional[DistanceRange] = None,
            true_vertical_depth: Optional[DistanceRange] = None,
        ):
            return self.list_data(
                [
                    TrajectoryDataRequest(
                        sequence_external_id=this.source.sequence_external_id,
                        measured_depth=measured_depth,
                        true_vertical_depth=true_vertical_depth,
                    )
                ]
            )[0]

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = 100,
    ) -> TrajectoryList:
        """
        Get trajectories that matches the filter

        @param wellbore_asset_external_ids: list of wellbore asset external ids
        @param wellbore_matching_ids: list of wellbore matching ids
        @param limit: optional limit. Set to None to get everything
        """

        def request(cursor):
            filter = TrajectoryFilterRequest(
                filter=TrajectoryFilter(
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                ),
                cursor=cursor,
            )

            path: str = self._get_path("/trajectories/list")
            response: Response = self.client.post(url_path=path, json=filter.json())
            trajectory_items: TrajectoryItems = TrajectoryItems.parse_raw(response.text)
            return trajectory_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return TrajectoryList(items)

    def list_data(self, trajectory_data_request_list: List[TrajectoryDataRequest]) -> TrajectoryDataList:
        """
        Get multiple trajectory data by a list of TrajectoryDataRequest

        @param trajectory_data_request_list: list of trajectory data requests
        @return: list of TrajectoryData objects
        """
        trajectory_data_request_items = TrajectoryDataRequestItems(items=trajectory_data_request_list)
        path = self._get_path("/trajectories/data")
        response: Response = self.client.post(url_path=path, json=trajectory_data_request_items.json())
        trajectory_data_items = TrajectoryDataItems.parse_raw(response.text)
        trajectory_rows = [TrajectoryRows(x) for x in trajectory_data_items.items]
        return TrajectoryDataList(trajectory_rows)

    def interpolate(
        self,
        meausured_depths: List[float],
        measured_depth_unit: str = "meter",
        true_vertical_depth_unit: str = "meter",
        *,
        wellbore_matching_id: Optional[str] = None,
        wellbore_asset_external_id: Optional[str] = None,
    ) -> List[float]:
        """
        Get the true vertical depths corresponding to a list of measured depths
        by interpolating the definitive trajectory for a wellbore.

        @param measured_depths: List of measured depths to interpolate
        @param measured_depth_unit: The unit for the measured depths. Default: meter
        @param true_vertical_depth_unit: The unit for the returned true vertical depths. Default: meter
        @wellbore_matching_id: The matching id of the wellbore to query
        @wellbore_asset_external_id: The CDF asset external id of the wellbore to query
        @return: A list of true vertical depths corresponding to the given measured depths
        """
        identifier = create_identifier(
            external_id=wellbore_asset_external_id,
            matching_id=wellbore_matching_id,
        )
        tvd_unit = create_distance_unit(true_vertical_depth_unit)
        md_unit = create_distance_unit(measured_depth_unit)

        request = TrajectoryInterpolationRequestItems(
            items=[
                TrajectoryInterpolationRequest(
                    wellbore_id=identifier,
                    measured_depths=meausured_depths,
                    measured_depth_unit=md_unit,
                    true_vertical_depth_unit=tvd_unit,
                )
            ]
        )
        path = self._get_path("/trajectories/interpolate")
        response = self.client.post(path, request.json())
        interps = response.json()["items"]
        assert len(interps) == 1
        interp = TrueVerticalDepths.parse_obj(interps[0])
        assert interp.true_vertical_depth_unit == tvd_unit
        return interp.true_vertical_depths

    def ingest(self, ingestions: List[TrajectoryIngestion]) -> TrajectoryList:
        """
        Ingests list of trajectories into WDL

        @param ingestions: list of trajectories to ingest
        @return: list of ingested trajectories
        """
        path = self._get_path("/trajectories")
        json = TrajectoryIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)

        return TrajectoryList([Trajectory.parse_obj(x) for x in response.json()["items"]])
