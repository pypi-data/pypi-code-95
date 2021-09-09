from .request import Http400, RequestErrors, request
import json
import time
import requests

from Bio import Entrez


class EnsemblRestClient(object):
    def __init__(self, server="http://rest.ensembl.org", reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0

    def perform_rest_action(self, url, hdrs=None, params=None, timeout=1):
        if hdrs is None:
            hdrs = {}

        if "Content-Type" not in hdrs:
            hdrs["Content-Type"] = "application/json"

        data = None

        # check if we need to rate limit ourselves
        if self.req_count >= self.reqs_per_sec:
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0

        try:
            response = requests.get(url, params=params, headers=hdrs, timeout=timeout)
            if response:
                data = json.loads(response)
            self.req_count += 1

        except requests.exceptions.HTTPError as e:
            # check if we are being rate limited by the server
            if e.code == 429:
                if "Retry-After" in e.headers:
                    retry = e.headers["Retry-After"]
                    time.sleep(float(retry))
                    self.perform_rest_action(url, hdrs, params)
            else:
                print(
                    "Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n".format(
                        url, e
                    )
                )

        return data
