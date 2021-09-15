import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import TrajectoryDataList, TrajectoryList
from cognite.well_model.client.models.trajectory_rows import TrajectoryRows
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._identifier_list import identifier_list
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
    TrajectoryItems,
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
