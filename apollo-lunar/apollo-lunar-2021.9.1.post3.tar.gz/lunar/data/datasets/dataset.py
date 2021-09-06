from typing import Any, Dict, List, Optional, Union

import asyncio
from pydantic import BaseModel, Field, validator, ValidationError

from lunar.config import Config
from lunar.lunar_client import LunarClient, LunarError

LUNAR_DATASETS_API_URL = "/v1/datasets"

DATA_TYPES_MAPPING_PARAMS = {"dynamodb": ["DynamoDBParams", "DynamoDBParamsPatchIn"], "docdb": ["DocDBParams"]}

loop = asyncio.get_event_loop()


class DatasetParams(BaseModel):
    pass


class DynamoDBParams(DatasetParams):
    main_table: str = Field(..., title="Name of a main table")
    tables: List[str] = Field(
        ...,
        min_items=1,
        title="Table list",
        description="'tables' must have at least one DynamoDB table name.",
    )

    @validator("tables")
    def check_main_table_in_tables(cls, tables, values):
        if "main_table" not in values:
            return tables

        if values["main_table"] is None:
            return tables

        main_table = values["main_table"]
        if main_table not in tables:
            raise ValueError("'main_table' not in 'tables'")
        return tables


class DocDBParams(DatasetParams):
    collection: str = Field(..., title="Name of a collection")


class DynamoDBParamsPatchIn(DynamoDBParams):
    main_table: Optional[str] = Field(None, title="Name of a main table")
    tables: Optional[List[str]] = Field(
        None,
        min_items=1,
        title="Table list",
        description="'tables' must have at least one DynamoDB table name.",
    )


class DatasetBase(BaseModel):
    data_type: str = Field(..., title="Dataset type")
    params: Union[DynamoDBParams, DocDBParams] = Field(..., title="Dataset parameters")

    @validator("data_type")
    def check_data_types(cls, data_type):
        if data_type not in DATA_TYPES_MAPPING_PARAMS:
            raise ValueError(f"'data_type' {data_type} is not supported.")

        return data_type

    @validator("params")
    def check_params_match_data_types(cls, params, values):
        if not values or values["data_type"] is None:
            return params

        params_type = params.__class__.__name__
        data_type = DATA_TYPES_MAPPING_PARAMS[values["data_type"]]
        if params_type not in data_type:
            raise ValueError("'params' type and 'data_type' do not match.")

        return params


class Dataset(DatasetBase):
    id: str = Field(..., title="Unique identifier of a dataset")


class DatasetPutIn(DatasetBase):
    pass


class DatasetPatchIn(DatasetBase):
    data_type: Optional[str] = Field(None, title="Dataset type")
    params: Optional[Union[DynamoDBParamsPatchIn]] = Field(None, title="Dataset parameters")


class DatasetClient(LunarClient):
    """
    Client for Lunar Data API (`/v1/datasets/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("dataset")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

        self.api_url = LUNAR_DATASETS_API_URL if config.ENV == "LOCAL" else f"/api{LUNAR_DATASETS_API_URL}"

    async def create_dataset_async(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Create a new dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        dataset = await client.create_dataset_async(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table"], "main_table": "first_table"},
        )
        ```
        """
        assert isinstance(params, dict), "`params` should be `dict` type"

        try:
            dataset = Dataset(
                id=id,
                data_type=data_type,
                params=params,
            )
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="POST", url=self.api_url, data=dataset.dict())
        return Dataset(**body["data"])

    def create_dataset(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Create a new dataset.

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        dataset = client.create_dataset(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table"], "main_table": "first_table"},
        )
        ```
        """

        return loop.run_until_complete(self.create_dataset_async(id=id, data_type=data_type, params=params))

    async def list_datasets_async(self) -> List[Dataset]:
        """
        List datasets (async).

        ## Returns
        list(`lunar.data.Dataset`)

        ## Example

        ```python
        datasets = await client.list_datasets_async()
        ```
        """

        body = await self._request(method="GET", url=self.api_url)

        return [Dataset(**dataset) for dataset in body["data"]]

    def list_datasets(self) -> List[Dataset]:
        """
        List datasets.

        ## Returns
        list(`lunar.data.Dataset`)

        ## Example

        ```python
        datasets = client.list_datasets()
        ```
        """

        return loop.run_until_complete(self.list_datasets_async())

    async def get_dataset_async(self, id: str) -> Dataset:
        """
        Get a dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        dataset = await client.get_dataset_async(id="my_dataset")
        ```
        """

        body = await self._request(method="GET", url=f"{self.api_url}/{id}")
        return Dataset(**body["data"])

    def get_dataset(self, id: str) -> Dataset:
        """
        Get a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        dataset = client.get_dataset(id="my_dataset")
        ```
        """

        return loop.run_until_complete(self.get_dataset_async(id=id))

    async def update_dataset_async(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Update a dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        experiment = await client.update_dataset_async(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table", "third_table"], "main_table": "second_table"}
        )
        ```
        """
        assert isinstance(params, dict), "`params` should be `dict` type"

        try:
            updated_dataset = DatasetPutIn(
                data_type=data_type,
                params=params,
            )
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="PUT", url=f"{self.api_url}/{id}", data=updated_dataset.dict())
        return Dataset(**body["data"])

    def update_dataset(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Update a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        experiment = client.update_dataset(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table", "third_table"], "main_table": "second_table"}
        )
        ```
        """

        return loop.run_until_complete(self.update_dataset_async(id=id, data_type=data_type, params=params))

    async def update_dataset_partial_async(
        self, id: str, data_type: str = None, params: Dict[str, Any] = None
    ) -> Dataset:
        """
        Partially update a dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (optional) (str) Dataset type
        - params: (optional) (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        dataset = await client.update_dataset_partial_async(
            id="my_dataset", params={"tables": ["first_table"], "main_table": "first_table"}
        )
        ```
        """

        request_body = {}
        if params:
            assert isinstance(params, dict), "`params` should be `dict` type"
            request_body["params"] = params

        if data_type:
            request_body["data_type"] = data_type

        patched_dataset = DatasetPatchIn(**request_body)

        body = await self._request(
            method="PATCH", url=f"{self.api_url}/{id}", data=patched_dataset.dict(exclude_none=True)
        )
        return Dataset(**body["data"])

    def update_dataset_partial(self, id: str, data_type: str = None, params: Dict[str, Any] = None) -> Dataset:
        """
        Partially update a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (optional) (str) Dataset type
        - params: (optional) (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.Dataset`

        ## Example

        ```python
        dataset = client.update_dataset_partial(
            id="my_dataset", params={"tables": ["first_table"], "main_table": "first_table"}
        )
        ```
        """
        data_type = data_type or None
        params = params or None

        return loop.run_until_complete(self.update_dataset_partial_async(id=id, data_type=data_type, params=params))

    async def delete_dataset_async(self, id: str) -> None:
        """
        Delete a dataset (async)

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Example

        ```python
        await client.delete_dataset_async(id="my_dataset")
        ```
        """

        return await self._request(method="DELETE", url=f"{self.api_url}/{id}")

    def delete_dataset(self, id: str) -> None:
        """
        Delete a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Example

        ```python
        client.delete_dataset(id="my_dataset")
        ```
        """

        return loop.run_until_complete(self.delete_dataset_async(id=id))
