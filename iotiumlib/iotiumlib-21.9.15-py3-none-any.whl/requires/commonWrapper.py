"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

import json

import requests
import urllib3

from iotiumlib.requires.commonVariables import *
from iotiumlib.requires.utils import formattedOutput

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Response:
    def __init__(self):
        self.code = int()
        self.output = list()
        self.formattedOutput = list()
        self.message = str()

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self[item]

    def __str__(self):
        return str(self.output)


class Session(object):
    def __init__(self):
        self.host = commonVariables().__orchip__
        self.token = commonVariables().__token__
        self.apikey = commonVariables().__apikey__
        self.header = headers(token=self.token, apikey=self.apikey)


def headers(token, apikey):
    return {'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'X_AUTH_TOKEN {}'.format(token),
            'X-API-KEY':apikey
            }


def applyFilters(filters):

    import re

    # default_filters = {'org_id':orch.id, 'own':"true"}

    if not filters:
        filters = {'org_id': orch.id, 'own': "true"}
    else:
        default_filters = dict()
        for k, v in filters.items():
            default_filters.update({k: v})
        filters = default_filters

    filter_string = ''
    if filters is not None:
        for key, value in filters.items():
            if re.search('\?', filter_string) is None:
                filter_string = filter_string + '?' + key + '=' + value
            else:
                filter_string = filter_string + '&' + key + '=' + value

    return filter_string


def formUri(uri):
    return "https://{}/{}".format(Session().host, uri)

def postApi(uri, payload):
    return requests.post(uri, data=json.dumps(payload), verify=False, headers=Session().header)

def putApi(uri, payload):
    return requests.put(uri, data=json.dumps(payload), verify=False, headers=Session().header)

def getApiv2(uri, filters=None):

    import inspect

    v2resp = Response()

    try:
        resp = requests.get("{}{}".format(format(uri), applyFilters(filters)), verify=False, headers=Session().header)

        resp.raise_for_status()

        final_result = []
        results = []

        if resp.status_code == 200:
            v2resp.code = resp.status_code
            if int(resp.json()['total_count']) > 25 and applyFilters(filters).find('page') == -1:
                a, b = divmod(resp.json()['total_count'], 100)
                page_list = [100] * a
                page_list.append(b)
                for page in range(len(page_list)):
                    url1 = ''
                    url1 = '{}{}&page={}&size={}'.format(uri, applyFilters(filters), page, 100)
                    resp = requests.get(url1, verify=False, headers=Session().header)
                    if resp.status_code == 200:
                        results.append(resp.json()['results'])
                for result in results:
                    for r in result:
                        final_result.append(r)

                v2resp.output = final_result
                v2resp.formattedOutput = formattedOutput(v2resp.output, inspect.stack()[1][3])
                return v2resp
            else:
                for result in resp.json()['results']:
                    final_result.append(result)
                v2resp.output = final_result
                v2resp.formattedOutput = formattedOutput(v2resp.output, inspect.stack()[1][3])
                return v2resp
        else:
            v2resp.code = resp.status_code
            v2resp.output = []
            v2resp.formattedOutput = []
            v2resp.message = resp.json()["message"]
            return v2resp
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
            requests.exceptions.Timeout, requests.exceptions.RequestException) as errh:
        print("HTTPRequestException: {}".format(errh))
        v2resp.code = 0
        v2resp.output = []
        v2resp.formattedOutput = []
        v2resp.message = str(errh)
        return v2resp
    except Exception as err:
        print("Exception: {}".format(err))
        v2resp.code = 0
        v2resp.output = []
        v2resp.formattedOutput = []
        v2resp.message = str(err)
        return v2resp


def getApi(uri):
    return requests.get(uri, verify=False, headers=Session().header)


def deleteApi(uri):
    return requests.delete(uri, verify=False, headers=Session().header)
