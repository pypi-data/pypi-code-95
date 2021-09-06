from typing import Any, Dict, List, Optional

import asyncio
from pydantic import BaseModel, Field, validator

from lunar.config import Config
from lunar.lunar_client import LunarClient

LUNAR_RECOMMENDATIONS_API_URL = "/v1/recommend"

loop = asyncio.get_event_loop()


class RecommendationIn(BaseModel):
    id: str = Field(..., title="Unique identifier of a recommendation target")
    channel_id: str = Field(..., title="Unique identifier of a channel")
    params: Optional[Dict[str, Any]] = Field(dict(), title="Additional parameters for recommendation")


class RecommendationOut(BaseModel):
    items: List[Dict[str, Any]] = Field(
        ..., title="Recommended items for the target", description="Each item map(dict) in this must have `id` field."
    )

    @validator("items")
    def check_ids(cls, items):
        for item in items:
            if "id" not in item:
                raise ValueError("'id' is a required field in an item")
        return items


class RecommendationClient(LunarClient):
    """
    Client for Lunar Recommendation API (`/v1/recommend/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("recommend")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

        self.api_url = (
            LUNAR_RECOMMENDATIONS_API_URL if config.ENV == "LOCAL" else f"/api{LUNAR_RECOMMENDATIONS_API_URL}"
        )

    async def recommend_async(
        self, id: str, channel_id: str, params: Dict[str, Any] = dict(), headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get recommended items for the target (async).

        ## Args

        - id: (str) Unique identifier of a recommendation target
        - channel_id: (str) Unique identifier of a channel
        - params: (optional) (dict) Additional parameters for recommendation
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        result = await client.recommend_async(id="a", channel_id="my_channel", params={"first_param": 100, "second_param": "value"}
        ```
        """

        data = RecommendationIn(id=id, channel_id=channel_id, params=params)

        body = await self._request(method="POST", url=self.api_url, data=data.dict(), params=params, headers=headers)
        result = RecommendationOut(**body["data"])

        return result.dict()

    def recommend(
        self, id: str, channel_id: str, params: Dict[str, Any] = dict(), headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get recommended items for the target.

        ## Args

        - id: (str) Unique identifier of a recommendation target
        - channel_id: (str) Unique identifier of a channel
        - params: (optional) (dict) Additional parameters for recommendation
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        result = client.recommend(id="a", channel_id="my_channel", params={"first_param": 100, "second_param": "value"}
        ```
        """

        return loop.run_until_complete(
            self.recommend_async(id=id, channel_id=channel_id, params=params, headers=headers)
        )
