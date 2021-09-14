"""Module where the metadata helpers live."""

import logging
from typing import Dict, List, Union


from pyportall.api.engine.core import APIClient, APIHelper
from pyportall.api.models.metadata import IndicatorMetadata


logger = logging.getLogger("metadata")


class MetadataHelper(APIHelper):
    """Help with indicator metadata."""

    def __init__(self, client: APIClient) -> None:
        """Class constructor to attach the corresponding API client.

        Args:
            client: API client object that the helper will use to actually send requests to the metadata API when it has to.
        """
        super().__init__(client)

        self.metadata: Dict[str, IndicatorMetadata] = {indicator["code"]: IndicatorMetadata(**indicator) for indicator in self.client.call_metadata()}

    def all(self) -> List[IndicatorMetadata]:
        """Get all the indicators available in the metadata database.

        Returns:
            A list of indicators with their metadata.
        """

        return [indicator for indicator in self.metadata.values()]

    def get(self, indicator_code: str) -> Union[IndicatorMetadata, None]:
        """Get just one of the indicators available in the metadata database.

        Args:
            indicator_code: Code of the indicator to be retrieved.

        Returns:
            Indicator with its metadata.
        """

        return self.metadata.get(indicator_code)

    def refresh(self) -> None:
        """Update the metadata with a fresh copy from the database."""

        self.metadata = {indicator["code"]: IndicatorMetadata(**indicator) for indicator in self.client.call_metadata()}
