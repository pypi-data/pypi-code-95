from __future__ import absolute_import
from __future__ import unicode_literals

import json
import jwt
import datetime
import requests
import urllib3
import re

__all__ = [
    "ERROR",
    "Warning",
    "InterfaceERROR",
    "DatabaseERROR",
    "InternalERROR",
    "OperationalERROR",
    "ProgrammingERROR",
    "DataERROR",
    "NotSupportedERROR",
]


class ERROR(Exception):
    pass


class Warning(Exception):
    pass


class InterfaceERROR(ERROR):
    pass


class DatabaseERROR(ERROR):
    pass


class InternalERROR(DatabaseERROR):
    pass


class OperationalERROR(DatabaseERROR):
    pass


class ProgrammingERROR(DatabaseERROR):
    pass


class IntegrityERROR(DatabaseERROR):
    pass


class DataERROR(DatabaseERROR):
    pass


class NotSupportedERROR(DatabaseERROR):
    pass


class uptycs_rest_call(object):
    def __init__(
        self,
        url=None,
        customer_id=None,
        key=None,
        secret=None,
        verify_ssl=False,
        api=None,
        method=None,
        post_data=None,
        media_type=None,
        download_location=None,
        threat_source_name=None,
        threat_source_description=None,
        threat_data_csv=None,
        **kwargs
    ):

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.baseurl = url
        self.customer_id = customer_id
        self.final_url = "%s/public/api/customers/%s%s" % (url, customer_id, api)
        self.api = api
        self.osquery_list_url = "%s/public/api/osqueryPackages" % (url)
        self.key = key
        self.secret = secret
        self.method = method
        self.verify_ssl = verify_ssl
        self.post_data = post_data
        self.media_type = media_type
        self.download_location = download_location
        self.threat_data_csv = threat_data_csv
        self.threat_source_name = threat_source_name
        self.threat_source_description = threat_source_description

        self.header = {}
        utcnow = datetime.datetime.utcnow()
        date = utcnow.strftime("%a, %d %b %Y %H:%M:%S GMT")
        authVar = jwt.encode({"iss": self.key}, self.secret, algorithm="HS256")
        authorization = "Bearer %s" % (authVar)
        self.header["date"] = date
        self.header["Authorization"] = authorization

        self._is_response_json = False
        self._error = None
        self._response_content = None

    @property
    def is_response_json(self):
        return self._is_response_json

    @property
    def response_content(self):
        return self._response_content

    @property
    def errir(self):
        return self._error

    def filename_in_content_disposition(self, contnt_disp):
        """
            Get filename from content-disposition
            """
        if not contnt_disp:
            return None
        fname = re.findall("filename=(.+)", contnt_disp)
        if len(fname) == 0:
            return None
        filename = fname[0]
        if (filename.startswith('"') and filename.endswith('"')) or (
            filename.startswith("'") and filename.endswith("'")
        ):
            filename = filename[1:-1]
        if self.download_location:
            filename = self.download_location + "/" + filename
        return filename

    def rest_api_call(self):

        if (
            self.method.lower() == "get"
            and not self.api.startswith("/packageDownloads")
            and self.api != "/osqueryPackages"
        ):
            try:
                response = requests.get(
                    url=self.final_url, headers=self.header, verify=self.verify_ssl
                )
                if response and response.status_code in [
                    requests.codes.ok,
                    requests.codes.bad,
                ]:
                    self._is_response_json = True
                    self._response_content = response.content.decode("utf-8")
                else:
                    self._is_response_json = False
                    self._response_content = response.content

            except requests.exceptions.RequestException as e:
                self._error = "ERROR: {}".format(e)
                raise OperationalERROR(self._error)

        elif (self.method.lower() == "get") and self.api.startswith(
            "/packageDownloads"
        ):
            try:
                response = requests.get(
                    url=self.final_url,
                    headers=self.header,
                    verify=self.verify_ssl,
                    allow_redirects=True,
                )
                if response and response.status_code in [
                    requests.codes.ok,
                    requests.codes.bad,
                ]:
                    self._is_response_json = True
                    filename = self.filename_in_content_disposition(
                        response.headers.get("content-disposition")
                    )
                    open(filename, "wb").write(response.content)

                    temp_response_content = {
                        "status": response.status_code,
                        "filename": filename,
                    }
                    self._response_content = json.dumps(temp_response_content).decode(
                        "utf-8"
                    )
                else:
                    self._is_response_json = False
                    self._response_content = response.content

            except requests.exceptions.RequestException as e:
                self._error = "ERROR: {}".format(e)
                raise OperationalERROR(self._error)

        elif self.method.lower() == "get" and self.api == "/osqueryPackages":
            try:
                response = requests.get(
                    url=self.osquery_list_url,
                    headers=self.header,
                    verify=self.verify_ssl,
                )
                if response and response.status_code in [
                    requests.codes.ok,
                    requests.codes.bad,
                ]:
                    self._is_response_json = True
                    self._response_content = response.content.decode("utf-8")
                else:
                    self._is_response_json = False
                    self._response_content = response.content

            except requests.exceptions.RequestException as e:
                self._error = "ERROR: {}".format(e)
                raise OperationalERROR(self._error)

        elif self.method.lower() == "post" and self.api == "/threatSources":
            if (
                self.threat_source_name
                and self.threat_source_description
                and self.threat_data_csv
            ):
                try:
                    files = {"file": open(self.threat_data_csv, "rb")}

                    payload = {
                        "name": self.threat_source_name,
                        "description": self.threat_source_description,
                    }
                    response = requests.post(
                        headers=self.header,
                        url=self.final_url,
                        files=files,
                        data=payload,
                        verify=self.verify_ssl,
                        timeout=None,
                    )
                    if response and response.status_code in [
                        requests.codes.ok,
                        requests.codes.bad,
                    ]:
                        self._is_response_json = True
                    self._response_content = response.content.decode("utf-8")
                except requests.exceptions.RequestException as e:
                    self._error = "ERROR: {}".format(e)
                    raise OperationalERROR(self._error)

            else:
                raise OperationalERROR(
                    "ERROR: with post method. " "please pass post data json"
                )

        elif self.method.lower() == "post":
            if self.post_data:
                try:
                    response = requests.post(
                        url=self.final_url,
                        headers=self.header,
                        json=self.post_data,
                        verify=self.verify_ssl,
                        timeout=None,
                    )
                    if response and response.status_code in [
                        requests.codes.ok,
                        requests.codes.bad,
                    ]:
                        self._is_response_json = True
                    self._response_content = response.content.decode("utf-8")
                except requests.exceptions.RequestException as e:
                    self._error = "ERROR: {}".format(e)
                    raise OperationalERROR(self._error)

            else:
                raise OperationalERROR(
                    "ERROR: with post method. " "please pass post data json"
                )

        elif self.method.lower() == "put":
            if self.post_data:
                try:
                    response = requests.put(
                        url=self.final_url,
                        headers=self.header,
                        json=self.post_data,
                        verify=self.verify_ssl,
                        timeout=None,
                    )
                    if response and response.status_code in [
                        requests.codes.ok,
                        requests.codes.bad,
                    ]:
                        self._is_response_json = True
                    self._response_content = response.content.decode("utf-8")
                except requests.exceptions.RequestException as e:
                    self._error = "ERROR: {}".format(e)
                    raise OperationalERROR(self._error)

            else:
                raise OperationalERROR(
                    "ERROR: with put method. " "please pass post data json"
                )

        elif self.method.lower() == "delete":
            try:
                response = requests.delete(
                    url=self.final_url,
                    headers=self.header,
                    verify=self.verify_ssl,
                    timeout=None,
                )
                if response and response.status_code in [
                    requests.codes.ok,
                    requests.codes.bad,
                ]:
                    self._is_response_json = False
                self._response_content = response.content.decode("utf-8")
            except requests.exceptions.RequestException as e:
                self._error = "ERROR: {}".format(e)
                raise OperationalERROR(self._error)
        else:
            raise OperationalERROR("ERROR: Unknown request")
