from infomaxy.version import __version__
from infomaxy.config import apiconfig
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import infomaxy.api.imutil
import pandas as pd
import numpy as np

def set_apikey(apikey):
    apiconfig.apikey = apikey

def IMDH(market, code, **kwargs):
    print("IMDH")
    print(apiconfig.apikey)

    #kwargs.pop('market', 'STK')

    imdata = Imdh.get(market, code, params=kwargs)
    return imdata

class ImdBase(object):
    def __init__(self):
        print("ImdBase")

    def make_req_param(params):
        headers = {}
        headers['x-api-token'] = 'application/json'
        headers['accept'] = 'application/json'
        headers['request-source'] = 'python'
        headers['request-source-version'] = __version__

        options = {}
        options['headers'] = headers
        options['params'] = params

        return options

    def make_req_url(market, code):
        url = "%s/IMDH/%s/%s" % (apiconfig.baseurl, market, code)
        return url

    @classmethod
    def req_data(cls, url, **options):
        session = cls.get_session()
        try:
            response = session.request(method='get',
                                       url=url,
                                       verify=apiconfig.verify_ssl,
                                       **options)
            if response.status_code < 200 or response.status_code >= 300:
                print("req_data error : ", response.status_code)
            else:
                return response
        except requests.exceptions.RequestException as e:
            if e.response:
                print("req_data error : ", e.response)
            raise e

    @classmethod
    def get_session(cls):
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=cls.get_retries())
        session.mount(apiconfig.apiprotocol, adapter)
        return session

    @classmethod
    def get_retries(cls):
        if not apiconfig.use_retries:
            return Retry(total=0)
        Retry.BACKOFF_MAX = apiconfig.retry_backoff_max
        retries = Retry(total=apiconfig.retry_total,
                        connect=apiconfig.retry_connect,
                        read=apiconfig.retry_read,
                        status_forcelist=apiconfig.retry_forcelist,
                        backoff_factor=apiconfig.retry_backoff_factor,
                        raise_on_status=False)
        return retries

class ImData(object):
    def __init__(self, rawdata=None):
        self._rawdata = rawdata
        self._headdata = None
        self._listdata = None
        if rawdata is not None:
            self.set_responsedata(rawdata)
        print("ImData")

    def get_rawdata(self):
        return self._rawdata

    def set_responsedata(self, rawdata):
        if isinstance(rawdata, dict):
            if 'imdata' in rawdata.keys():
                self._listdata = rawdata['imdata'].pop('data')
                self._headdata = rawdata.pop('imdata')

    def get_attr(self, name):
        #_headdata.keys = market, code, start_date, end_date, count, per
        if name in self._headdata:
            return self._headdata[name]
        return None

    def get_values(self):
        if isinstance(self._listdata, list):
            return self._listdata
        return None

    def get_value(self, field):
        fi = self.get_field_index(field)
        if fi is not None:
            return list([x[fi] for x in self._listdata])
        return None

    def get_fields(self):
        return self.get_attr('field_list')

    def get_field_index(self, field):
        fieldindexs = self.get_attr('field_index')
        if fieldindexs is not None and field in fieldindexs.keys():
            return fieldindexs[field]

    def get_pandas(self):
        values = self.get_values()
        fields = self.get_fields()
        df = pd.DataFrame(data=values, columns=fields)
        return df


class Imdh(ImdBase):
    def __init__(self):
        print("Imdh")

    @classmethod
    def get(cls, market, code, params):
        print("get")
        url = cls.make_req_url(market, code)
        options = cls.make_req_param(params)
        r = cls.req_data(url, **options)
        response_data = r.json()
        return ImData(response_data)
