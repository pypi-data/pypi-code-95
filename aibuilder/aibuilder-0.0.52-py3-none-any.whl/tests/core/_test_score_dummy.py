#
#  -------------------------------------------------------------
#   Copyright (c) Microsoft Corporation.  All rights reserved.
#  -------------------------------------------------------------
import json
import os

import lightgbm
import pandas as pd
from azureml.contrib.services.aml_response import AMLResponse
from azureml.core.model import Model
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType
from inference_schema.schema_decorators import input_schema, output_schema

sample_input = PandasParameterType(pd.DataFrame([{
    "fixed acidity": 0.0,
    "volatile acidity": 0.0,
    "citric acid": 0.0,
    "residual sugar": 0.0,
    "chlorides": 0.0,
    "free sulfur dioxide": 0.0,
    "total sulfur dioxide": 0.0,
    "density": 0.0,
    "pH": 0.0,
    "sulphates": 0.0,
    "alcohol": 0.0
}]))

sample_prediction = {"result": 1}
sample_output_schema = PandasParameterType(pd.DataFrame([sample_prediction]))


def init():
    print(f"called init")


@input_schema("data", sample_input)
@output_schema(sample_output_schema)
def run(data):
    global model
    print("Processing request...")
    print(f"POST Request: {data}")
    df = pd.DataFrame(data)
    print(f"Dataframe: {df}")

    return [{"result": 1}] * df.shape[0]

