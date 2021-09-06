from typing import Any, Dict, List

import asyncio

from lunar.config import Config
from lunar.lunar_client import LunarClient

LUNAR_DATA_API_URL = "/v1/data"

loop = asyncio.get_event_loop()


class DataClient(LunarClient):
    """
    Client for Lunar Data API (`/v1/data/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("data")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

        self.api_url = LUNAR_DATA_API_URL if config.ENV == "LOCAL" else f"/api{LUNAR_DATA_API_URL}"

    async def get_data_async(
        self, dataset_id: str, id: str, attributes: List[str] = None, headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get a data result (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (optional) (str) Unique identifier of a target
        - attributes: (optional) (str) Attributes to get from datasets
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        data = await client.get_data_async(dataset_id="my_dataset", id="my_id", attributes=["f1", "f2"])
        ```
        """
        if attributes:
            assert type(attributes) == list, "`attributes` type must be list"

        params = {"dataset_id": dataset_id, "id": id}
        if attributes:
            params["f"] = attributes

        body = await self._request(method="GET", url=self.api_url, params=params, headers=headers)

        return body["data"]

    def get_data(
        self, dataset_id: str, id: str, attributes: List[str] = None, headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get a data result.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (optional) (str) Unique identifier of a target
        - attributes: (optional) (str) Attributes to get from datasets. If not, all attributes of result would be returned
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        data = client.get_data(dataset_id="my_dataset", id="my_id", attributes=["f1", "f2"])
        ```
        """

        return loop.run_until_complete(
            self.get_data_async(dataset_id=dataset_id, id=id, attributes=attributes, headers=headers)
        )
