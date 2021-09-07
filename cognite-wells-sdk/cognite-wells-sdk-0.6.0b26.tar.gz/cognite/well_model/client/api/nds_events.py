import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import NdsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DistanceRange,
    Nds,
    NdsFilter,
    NdsFilterRequest,
    NdsIngestion,
    NdsIngestionItems,
    NdsItems,
)

logger = logging.getLogger(__name__)


class NdsEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, nds_events: List[NdsIngestion]):
        """
        Ingests a list of Nds events into WDL

        @param nds_events: list of Nds events to ingest
        @return: list of ingested Nds events
        """
        path = self._get_path("/nds")
        json = NdsIngestionItems(items=nds_events).json()
        response: Response = self.client.post(path, json)
        return NdsList(NdsItems.parse_raw(response.text).items)

    def list(
        self,
        hole_start: Optional[DistanceRange] = None,
        hole_end: Optional[DistanceRange] = None,
        probabilities: Optional[List[int]] = None,
        severities: Optional[List[int]] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = 100,
    ) -> NdsList:
        """
        Get Nds events that matches the filter

        @param hole_start: range of hole start in desired Nds events
        @param hole_end: range of hole end in desired Nds events
        @param probabilities: list of interested probabilities
        @param severities: list of interested severities
        @param wellbore_asset_external_ids: list of wellbore asset external ids
        @param wellbore_matching_ids: list of wellbore matching ids
        @param limit: optional limit. Set to None to get everything
        @return: NdsList object
        """

        def request(cursor):
            nds_filter = NdsFilterRequest(
                filter=NdsFilter(
                    hole_start=hole_start,
                    hole_end=hole_end,
                    probabilities=probabilities,
                    severities=severities,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                ),
                cursor=cursor,
            )

            path: str = self._get_path("/nds/list")
            response: Response = self.client.post(url_path=path, json=nds_filter.json())
            nds_items: NdsItems = NdsItems.parse_raw(response.text)
            return nds_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NdsList(items)

    def risk_types(self) -> List[str]:
        """
        Get all Nds risk types

        @return: list of Nds risk types
        """
        output: List[str] = self._string_items_from_route("nds/risktypes")
        return output

    @staticmethod
    def _get_items(nds_items: NdsItems) -> List[Nds]:
        items: List[Nds] = nds_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(nds_items: NdsItems) -> Optional[str]:
        next_cursor: Optional[str] = nds_items.next_cursor  # For mypy
        return next_cursor
