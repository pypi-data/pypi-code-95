from .common.api_request import make_request, make_paginated_request
import json
import time
from collections import namedtuple
import pandas as pd


class Query:
    def __init__(self, query, *, default_project=None, default_dataset=None):
        self.properties = make_request(
            method="post",
            path="/queries",
            parse_response=False,
            payload={
                "query": query,
                "defaultProject": default_project.uri.split("projects/")[1]
                if default_project
                else None,
                "defaultDataset": default_dataset.uri.split("datasets/")[1]
                if default_dataset
                else None,
            },
        )
        self.uri = f"/queries/{self.properties.id}"

    def __getitem__(self, key):
        return self.properties[key]

    def __str__(self):
        return json.dumps(self.properties, indent=2)

    def get(self):
        self.properties = make_request(method="GET", path=self.uri)
        return self

    def list_rows(self, limit, *, offset_start=0):
        while True:
            if self.properties["status"] == "success":
                break
            elif self.properties["status"] == "failed":
                raise Exception(
                    f"Query job failed with message: {self.properties['message']}"
                )
            else:
                time.sleep(2)
                self.get()

        variables = make_paginated_request(path=f"{self.uri}/variables")
        Row = namedtuple(
            "Row",
            [variable["name"] for variable in variables],
        )

        page = 0
        page_size = 10000

        max_results = (
            min(limit, int(self.properties["numRows"]))
            if limit is not None
            else self.properties.numRows
        )

        rows = ""
        while page * page_size < max_results:
            results = make_request(
                method="get",
                path=f"{self.uri}/rows",
                parse_response=False,
                query={
                    "selectedVariables": ",".join(
                        map(lambda variable: variable["name"], variables)
                    ),
                    "startIndex": page * page_size + offset_start,
                    "max_results": page_size
                    if (page + 1) * page_size < max_results
                    else max_results - page * page_size,
                },
            )
            rows += results
            page += 1

        return [Row(*json.loads(row)) for row in rows.split("\n")]

    def to_data_frame(self, limit, *, offset_start=0):
        rows = self.list_rows(limit=limit, offset_start=offset_start)
        return pd.DataFrame(rows, columns=rows[0]._fields)
