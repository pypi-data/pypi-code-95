import json
from io import BytesIO

import requests
import pandas as pd

from sgclimaapiclient.baseapi import BaseAPI


class SGClimaModelsAPI(BaseAPI):

    def __init__(self, token, endpoint='https://models-api.dc.indoorclima.com', verify=True):
        super().__init__(token, endpoint, verify)

    def list_models(self):
        """
        List models
        :return: List with a JSON of registered models
        """
        return self._call_json("/ml/list")

    def get_model(self, id):
        """
        Get model by id
        :return: List with a JSON of registered models
        """
        return self._call_json("/ml/{id}/".format(id=id))

    def predict(self, id, df, version="production"):
        params = {"version": version}
        data = df.to_json(orient="split")
        headers = {'Content-Type': 'application/json; format=pandas-split'}
        df = self._call_df(url="/ml/predict/{id}".format(id=id), params=params, json_payload=data, headers=headers)
        df = df.stack().to_frame().reset_index()[[0]]
        df.columns = ["prediction"]
        return df



