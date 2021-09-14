"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import urllib3
import logging
import os
import tqdm

# Disable warnings: InsecureRequestWarning
urllib3.disable_warnings()


class BDBAApi:
    """
    Class that facilitates an authenticated connection to the hub for uploading binary files to BDBA.
    """

    def __init__(self, hub_api):
        hub_api.authenticate()
        self.hub = hub_api.hub

    def upload_binary(self, project_name, version_name, codelocation_name, binary_file):
        if not os.path.exists(binary_file):
            logging.warning("Binary file not found. There will be no BDBA results.")
            return

        logging.info("Uploading file...")

        multipart_encoder = MultipartEncoder(fields={'projectName': project_name,
                                                     'version': version_name,
                                                     'codeLocationName': codelocation_name + "-BDBA",
                                                     'fileupload': (binary_file, open(binary_file, "rb"))
                                                     }
                                             )
        headers = self.hub.get_headers()
        headers.pop('Accept')
        headers.pop('Content-Type')

        with tqdm.tqdm(desc="BDBA Upload",
                       total=multipart_encoder.len,
                       dynamic_ncols=True,
                       unit='B',
                       unit_scale=True,
                       unit_divisor=1024) as bar:
            multipart_monitor = MultipartEncoderMonitor(multipart_encoder,
                                                        lambda monitor: bar.update(monitor.bytes_read - bar.n))
            headers['Content-Type'] = multipart_monitor.content_type
            response = requests.post('{}/api/uploads'.format(self.hub.config['baseurl']),
                                     headers=headers,
                                     data=multipart_monitor,
                                     verify=not self.hub.config['insecure'])
        if not response.ok:
            if response.status_code == 402:
                logging.error("BDBA is not licensed for use with the current Hub instance -- will not be used.")
            else:
                logging.error("Problem uploading the file to BDBA -- (Response({}): {})".format(response.status_code,
                                                                                                response.text))
        else:
            logging.info("Upload completed!")

    def __call__(self, project_name, version_name, codelocation_name, binary_file):
        self.upload_binary(project_name, version_name, codelocation_name, binary_file)
