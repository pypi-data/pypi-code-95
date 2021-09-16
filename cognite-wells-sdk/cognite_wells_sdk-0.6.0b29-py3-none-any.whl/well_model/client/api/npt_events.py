import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import NptList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DistanceRange,
    DurationRange,
    Npt,
    NptFilter,
    NptFilterRequest,
    NptIngestion,
    NptIngestionItems,
    NptItems,
)

logger = logging.getLogger(__name__)


class NptEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, npt_events: List[NptIngestion]):
        """
        Ingests a list of Npt events into WDL

        @param npt_events: list of Npt events to ingest
        @return: list of ingested Npt events
        """
        path = self._get_path("/npt")
        json = NptIngestionItems(items=npt_events).json()
        response: Response = self.client.post(path, json)
        return NptList(NptItems.parse_raw(response.text).items)

    def list(
        self,
        md: Optional[DistanceRange] = None,
        duration: Optional[DurationRange] = None,
        npt_codes: Optional[List[str]] = None,
        npt_code_details: Optional[List[str]] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = 100,
    ) -> NptList:
        """
        Get Npt events that matches the filter

        @param md - range of measured depth in desired Npt events
        @param duration - duration of desired Nds events
        @param npt_codes - npt_codes of desired Nds events
        @param npt_code_details - npt_code_details of desired Nds events
        @param wellbore_external_ids - list of interested wellbore external ids
        @return: NptList object
        """

        def request(cursor):
            npt_filter = NptFilterRequest(
                filter=NptFilter(
                    measured_depth=md,
                    duration=duration,
                    npt_codes=npt_codes,
                    npt_code_details=npt_code_details,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                ),
                cursor=cursor,
            )

            path: str = self._get_path("/npt/list")
            response: Response = self.client.post(url_path=path, json=npt_filter.json())
            npt_items: NptItems = NptItems.parse_raw(response.text)
            return npt_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NptList(items)

    def codes(self) -> List[str]:
        """
        Get all Npt codes

        @return: list of Npt codes
        """
        # For some reason I need to be explicit about types here.
        output: List[str] = self._string_items_from_route("npt/codes")
        return output

    def detail_codes(self) -> List[str]:
        """
        Get all Npt detail codes

        @return: list of Npt detail codes
        """
        output: List[str] = self._string_items_from_route("npt/detailcodes")
        return output

    @staticmethod
    def _get_items(npt_items: NptItems) -> List[Npt]:
        items: List[Npt] = npt_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(npt_items: NptItems) -> Optional[str]:
        next_cursor: Optional[str] = npt_items.next_cursor  # For mypy
        return next_cursor
