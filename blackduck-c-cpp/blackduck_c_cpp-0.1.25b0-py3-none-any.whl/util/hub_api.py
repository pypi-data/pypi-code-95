"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

from blackduck.HubRestApi import HubInstance
import logging
import sys
from requests.exceptions import ConnectionError


class HubAPI:

    def __init__(self, bd_url, api_token, insecure):
        self.bd_url = bd_url
        self.api_token = api_token
        self.insecure = insecure
        self.hub = None
        # self.authenticate()

    def authenticate(self):
        try:
            self.hub = HubInstance(self.bd_url, api_token=self.api_token, insecure=self.insecure,
                                   write_config_flag=False)
        except KeyError:
            logging.error("make sure you have right api key and --insecure flag is set correctly")
            sys.exit(1)
        except ConnectionError:
            logging.error("ConnectionError occured..make sure you have correct url and insecure flag is set properly")
            sys.exit(1)
