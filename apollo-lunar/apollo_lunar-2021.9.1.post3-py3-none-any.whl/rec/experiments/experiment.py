from typing import Any, Dict, List, Optional

import asyncio
from pydantic import BaseModel, Field, validator, ValidationError

from lunar.config import Config
from lunar.lunar_client import LunarClient, LunarError

LUNAR_EXPERIMENTS_API_URL = "/v1/experiments"

loop = asyncio.get_event_loop()


class Bucket(BaseModel):
    name: str = Field(..., title="Name of a bucket")
    ratio: int = Field(..., ge=0, le=100, title="Ratio for bucketing", description="The ratio must be 0 ~ 100.")
    model_name: Optional[str] = Field(None, title="Name of an ML model")
    model_version: Optional[str] = Field(None, title="Version of an ML model")


class ExperimentBase(BaseModel):
    buckets: List[Bucket]
    bucketing_seed: Optional[str] = ""

    class Config:
        fields = {
            "id": {"title": "Unique identifier of an experiment"},
            "buckets": {
                "min_items": 1,
                "title": "Bucket list",
                "description": "Experiment must have at least one bucket.",
            },
            "bucketing_seed": {"title": "Random seed for bucketing"},
        }

    @validator("buckets")
    def check_sum_ratio(cls, buckets):
        if buckets is None:
            return buckets
        sum_ratio = 0
        for bucket in buckets:
            sum_ratio += bucket.ratio
        if sum_ratio != 100:
            raise ValueError("Sum of bucket ratios must be 100")
        return buckets

    @validator("buckets")
    def check_bucket_names(cls, buckets):
        if buckets is None:
            return buckets
        bucket_names = {bucket.name for bucket in buckets}
        if len(bucket_names) != len(buckets):
            raise ValueError("Bucket names are duplicated")
        return buckets


class Experiment(ExperimentBase):
    id: str


class ExperimentPutIn(ExperimentBase):
    pass


class ExperimentPatchIn(ExperimentBase):
    buckets: Optional[List[Bucket]] = None
    bucketing_seed: Optional[str] = None


class ExperimentClient(LunarClient):
    """
    Client for Lunar Recommendation API (`/v1/experiments/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("experiment")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

        self.api_url = LUNAR_EXPERIMENTS_API_URL if config.ENV == "LOCAL" else f"/api{LUNAR_EXPERIMENTS_API_URL}"

    async def create_experiment_async(
        self, id: str, buckets: List[Dict[str, Any]], bucketing_seed: str = ""
    ) -> Experiment:
        """
        Create a new experiment (async).

        ## Args

        - id: (str) Unique identifier of an experiment
        - buckets: (list(dict)) Bucket list in an experiment
        - bucketing_seed: (optional) (str) Random seed for bucketing (default: "")

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = await client.create_experiment_async(
            id="my_experiment", buckets=[{"name": "a", "ratio": 20}, {"name": "b", "ratio": 80}], bucketing_seed="100"
        )
        ```
        """

        assert isinstance(buckets, list), "`buckets` should be `list` type"
        for bucket in buckets:
            assert isinstance(bucket, dict), "`bucket` should be `dict` type"

        try:
            experiment = Experiment(
                id=id,
                buckets=buckets,
                bucketing_seed=bucketing_seed,
            )
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="POST", url=self.api_url, data=experiment.dict())
        return Experiment(**body["data"])

    def create_experiment(self, id: str, buckets: List[Dict[str, any]], bucketing_seed: str = "") -> Experiment:
        """
        Create a new experiment.

        ## Args

        - id: (str) Unique identifier of an experiment
        - buckets: (list(dict)) Bucket list in an experiment
        - bucketing_seed: (optional) (str) Random seed for bucketing (default: "")

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = client.create_experiment(
            id="my_experiment", buckets=[{"name": "a", "ratio": 20}, {"name": "b", "ratio": 80}], bucketing_seed="100"
        )
        ```
        """

        return loop.run_until_complete(
            self.create_experiment_async(id=id, buckets=buckets, bucketing_seed=bucketing_seed)
        )

    async def list_experiments_async(self) -> List[Experiment]:
        """
        List experiments (async).

        ## Returns
        list(`lunar.rec.Experiment`)

        ## Example

        ```python
        experiments = await client.list_experiments_async()
        ```
        """

        body = await self._request(method="GET", url=self.api_url)
        return [Experiment(**experiment) for experiment in body["data"]]

    def list_experiments(self) -> List[Experiment]:
        """
        List experiments.

        ## Returns
        list(`lunar.rec.Experiment`)

        ## Example

        ```python
        experiments = client.list_experiments()
        ```
        """

        return loop.run_until_complete(self.list_experiments_async())

    async def get_experiment_async(self, id: str) -> Experiment:
        """
        Get an experiment (async).

        ## Args

        - id: (str) Unique identifier of an experiment

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = await client.get_experiment_async(id="my_experiment")
        ```
        """

        body = await self._request(method="GET", url=f"{self.api_url}/{id}")
        return Experiment(**body["data"])

    def get_experiment(self, id: str) -> Experiment:
        """
        Get an experiment.

        ## Args

        - id: (str) Unique identifier of an experiment

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = client.get_experiment(id="my_experiment")
        ```
        """

        return loop.run_until_complete(self.get_experiment_async(id=id))

    async def update_experiment_async(
        self, id: str, buckets: List[Dict[str, any]], bucketing_seed: str = ""
    ) -> Experiment:
        """
        Update an experiment (async).

        ## Args

        - id: (str) Unique identifier of an experiment
        - buckets: (list(dict)) Bucket list in an experiment
        - bucketing_seed: (optional) (str) Random seed for bucketing (default: "")

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = await client.update_experiment_async(
            id="my_experiment", buckets=[{"name": "a", "ratio": 90}, {"name": "c", "ratio": 10}], bucketing_seed="200"
        )
        ```
        """

        assert isinstance(buckets, list), "`buckets` should be `list` type"
        for bucket in buckets:
            assert isinstance(bucket, dict), "`bucket` should be `dict` type"

        try:
            updated_experiment = ExperimentPutIn(
                buckets=buckets,
                bucketing_seed=bucketing_seed,
            )
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="PUT", url=f"{self.api_url}/{id}", data=updated_experiment.dict())
        return Experiment(**body["data"])

    def update_experiment(self, id: str, buckets: List[Dict[str, any]], bucketing_seed: str = "") -> Experiment:
        """
        Update an experiment.

        ## Args

        - id: (str) Unique identifier of an experiment
        - buckets: (list(dict)) Bucket list in an experiment
        - bucketing_seed: (optional) (str) Random seed for bucketing (default: "")

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = client.update_experiment(
            id="my_experiment", buckets=[{"name": "a", "ratio": 90}, {"name": "c", "ratio": 10}], bucketing_seed="200"
        )
        ```
        """

        return loop.run_until_complete(
            self.update_experiment_async(id=id, buckets=buckets, bucketing_seed=bucketing_seed)
        )

    async def update_experiment_partial_async(
        self, id: str, buckets: List[Dict[str, any]] = None, bucketing_seed: str = None
    ) -> Experiment:
        """
        Partially update an experiment (async).

        ## Args

        - id: (str) Unique identifier of an experiment
        - buckets: (optional) (list(dict)) Bucket list in an experiment
        - bucketing_seed: (optional) (str) Random seed for bucketing

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = await client.update_experiment_partial_async(
            id="my_experiment", buckets=[{"name": "a", "ratio": 50}, {"name": "b", "ratio": 50}]
        )
        ```
        """

        if buckets:
            assert isinstance(buckets, list), "`buckets` should be `list` type"
            for bucket in buckets:
                assert isinstance(bucket, dict), "`bucket` should be `dict` type"

        patched_experiment = ExperimentPatchIn(**{"buckets": buckets, "bucketing_seed": bucketing_seed})

        body = await self._request(
            method="PATCH", url=f"{self.api_url}/{id}", data=patched_experiment.dict(exclude_none=True)
        )
        return Experiment(**body["data"])

    def update_experiment_partial(
        self, id: str, buckets: List[Dict[str, any]] = None, bucketing_seed: str = None
    ) -> Experiment:
        """
        Partially update an experiment.

        ## Args

        - id: (str) Unique identifier of an experiment
        - buckets: (optional) (list(dict)) Bucket list in an experiment
        - bucketing_seed: (optional) (str) Random seed for bucketing

        ## Returns
        `lunar.rec.Experiment`

        ## Example

        ```python
        experiment = client.update_experiment_partial(
            id="my_experiment", buckets=[{"name": "a", "ratio": 50}, {"name": "b", "ratio": 50}]
        )
        ```
        """
        buckets = buckets or None
        bucketing_seed = bucketing_seed or None

        return loop.run_until_complete(
            self.update_experiment_partial_async(id=id, buckets=buckets, bucketing_seed=bucketing_seed)
        )

    async def delete_experiment_async(self, id: str) -> None:
        """
        Delete an experiment (async)

        ## Args

        - id: (str) Unique identifier of an experiment

        ## Example

        ```python
        await client.delete_experiment_async(id="my_experiment")
        ```
        """

        return await self._request(method="DELETE", url=f"{self.api_url}/{id}")

    def delete_experiment(self, id: str) -> None:
        """
        Delete an experiment.

        ## Args

        - id: (str) Unique identifier of an experiment

        ## Example

        ```python
        client.delete_experiment_async(id="my_experiment")
        ```
        """

        return loop.run_until_complete(self.delete_experiment_async(id=id))
