import requests
import pandas as pd
from datetime import datetime

from sgclimaapiclient.baseapi import BaseAPI


class SGClimaDataAPI(BaseAPI):

    def __init__(self, token, endpoint='https://data-api.dc.indoorclima.com', verify=True):
        super().__init__(token, endpoint, verify)

    def get_site(self, id):
        return self._call_json("/sites/{id}".format(id=id))

    def get_zone(self, id):
        return self._call_json("/zones/{id}".format(id=id))

    def get_equipment(self, id):
        return self._call_json("/equipments/{id}".format(id=id))

    def get_site_data(self, id, start, end):
        params = {"start": start, "end": end}
        df = self._call_df("/sites/{id}/data/download".format(id=id), params=params)
        return df

    def calculate_health(self, id, date):
        params = {"date": date}
        return self._call("/sites/{id}/health/calculate".format(id=id), params=params)

    def get_zone_data(self, id, start, end):
        params = {"start": start, "end": end}
        df = self._call_df("/zones/{id}/data/download".format(id=id), params=params)
        return df

    def get_equipment_data(self, id, start, end):
        params = {"start": start, "end": end}
        df = self._call_df("/equipments/{id}/data/download".format(id=id), params=params)
        return df

    # this method extracts pids from layout
    def extract_pids(self, x):
        pids = []
        if type(x) == dict:
            for k, v in x.items():
                if k.endswith('_pid'):
                    try:
                        pids.append({k: int(v)})
                    except TypeError:
                        # print(k, '=>', v, 'is not ok')
                        pids.append({k: None})
                        pass
                    except ValueError:
                        pids.append({k: None})
                else:
                    pids.extend(self.extract_pids(v))
        elif type(x) == list:
            for v in x:
                pids.extend(self.extract_pids(v))
        return pids

    def extract_filtered_pids(self, x, tags=None):
        pids = []
        if type(x) == dict:
            for k, v in x.items():
                if k.endswith('_pid'):
                    try:
                        if k in tags:
                            pids.append(str(v))
                    except TypeError:
                        pass
                    except ValueError:
                        pass
                else:
                    pids.extend(self.extract_filtered_pids(v, tags))
        elif type(x) == list:
            for v in x:
                pids.extend(self.extract_filtered_pids(v, tags))
        return pids