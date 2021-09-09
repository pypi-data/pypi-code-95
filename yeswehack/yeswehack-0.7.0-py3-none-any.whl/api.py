# -*- encoding: utf-8 -*-


__all__ = [
    "YesWeHack",
    "Category",
    "Attachment",
    "BugType",
    "Author",
    "CVSS",
    "Log",
    "Report",
    "Program",
]
import json
import logging
import urllib.parse as urlparse
from io import BytesIO
from typing import List

import requests

from .exceptions import (
    APIError,
    AccessDenied,
    BadCredentials,
    InvalidResponse,
    JWTInvalid,
    JWTNotFound,
    OAuth2CodeError,
    ObjectNotFound,
    TOTPLoginEnabled,
)
from .models import (
    Attr,
    YwhApiObject,
)

logger = logging.getLogger(__name__)

class YesWeHack(YwhApiObject):
    # attributes item
    _attrs = [
        Attr(name="token", type_=str),
        Attr(name="api_url", type_=str, default="https://api.yeswehack.com"),
        Attr(name="username", type_=str),
        Attr(name="password", type_=str),
        Attr(name="lazy", type_=bool, default=True),
        Attr(name="verify", type_=bool, default=True),
        Attr(name="oauth_mode", type_=bool, default=False),
        Attr(name='oauth_args', type_=dict, default={}),
        Attr(name='session', type_=object),
        Attr(name='apps_headers', type_=object, default={}),
        Attr(name='managed_pgms', type_=list, default=[]),
        Attr(name='pat', type_=str, default=None),
    ]

    def __init__(self, headers={}, totp_code=None, **kwargs):
        logging.basicConfig()
        super().__init__(**kwargs)
        logger.debug("init {0} on {1}".format(__name__, self.api_url))

        self.session = requests.session()
        self.session.verify = self.verify
        self.session.headers = headers
        if self.pat:
            self.session.headers['X-AUTH-TOKEN'] = self.pat

        if not self.lazy and self.username != None and self.password != None:
            self.login(totp_code=totp_code)

    def call(self, method, path, data=None):
        logger.debug("Calling " + path)
        resp = self.session.request(
            method,
            self.api_url + path,
            data=data
        )
        try:
            json_resp = resp.json()
        except Exception as e:
            raise InvalidResponse

        if resp.status_code != 200:
            if resp.status_code == 401:
                if json_resp.get("message", '') == "JWT Token not found":
                    raise JWTNotFound
                if json_resp.get("message", '') == "Invalid JWT Token":
                    raise JWTInvalid
                if json_resp.get("message", '') == "Bad credentials":
                    raise BadCredentials
                if json_resp.get("error", '') == 'access_denied':
                    raise AccessDenied(json_resp.get("error_description", 'Authentication Failed'))
            if resp.status_code == 404:
                raise ObjectNotFound
            raise Exception("YWH error " + resp.text)

        return json_resp

    def raw_call(self, method, url, data=None, headers=None, files=None):
        logger.debug("Raw Calling " + url)
        resp = self.session.request(
            method, url, data=data, headers=headers, files=files,
        )
        return resp

    def _oauth_login(self):
        if any([ params not in self.oauth_args for params in ['client_id', 'client_secret', 'redirect_uri']]):
            raise BadCredentials
        client_id = self.oauth_args['client_id']
        client_secret = self.oauth_args['client_secret']
        redirect_uri = self.oauth_args['redirect_uri']
        resp = self.session.request('GET', f'{self.api_url}/oauth/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}')

        if resp.url == f"{self.api_url}/oauth/v2/auth/login":
            creds = {"_username": self.username, '_password': self.password}
            resp = self.session.request('POST', f'{self.api_url}/oauth/v2/auth/login_check', data=creds)

        auth_data = {'authorization[client_id]': client_id,'authorization[redirect_uri]': redirect_uri,'authorization[state]': None, 'accepted': True}
        resp = self.session.request('POST', f'{self.api_url}/oauth/v2/auth', data=auth_data, allow_redirects=False)
        if resp.status_code == 302 and resp.headers.get('Location', '') not in ['', f'{self.api_url}/oauth/v2/auth/login']:
            code = [q[1] for q in urlparse.parse_qsl(resp.headers['Location']) if q[0] == 'code']
            if len(code) <= 0:
                raise OAuth2CodeError
            resp = self.session.request('GET', f'{self.api_url}/oauth/v2/token?client_id={client_id}&client_secret={client_secret}&code={code[0]}&grant_type=authorization_code')
            if "error" in resp.json():
                raise AccessDenied(resp.json().get('error_description', 'invalid credential'))
            self.token = resp.json()['access_token']
            self.session.headers['Authorization'] = 'Bearer ' + self.token
            return True
        raise OAuth2CodeError

    def _login(self, totp_code=None):
        """
        Login against the api
        """
        logger.info("Login with {0}".format(self.username))
        data = {"email": self.username, "password": self.password}
        json_resp = self.call("POST", "/login", data=json.dumps(data))
        if "token" in json_resp:
            self.token = json_resp["token"]
            logger.info("Login successfull")
            self.session.headers["Authorization"] = "Bearer " + self.token
            return True
        elif "totp_token" in json_resp and totp_code is not None:
            data = {"token": json_resp["totp_token"], "code": totp_code}
            resp = self.raw_call(
                "POST", self.api_url + "/account/totp", data=json.dumps(data)
            )
            json_resp = resp.json()
            if "token" in json_resp:
                self.token = json_resp["token"]
                logger.info("Totp login successfull")
                self.session.headers["Authorization"] = "Bearer " + self.token
                return True
        elif "totp_token" in json_resp and totp_code is None:
            raise TOTPLoginEnabled
        return False

    def login(self, totp_code=None):
        if self.pat:
            return  # no login with PAT
        if self.oauth_mode:
            return self._oauth_login()
        else:
            return self._login(totp_code=totp_code)

    def get_business_units(self):
        resp = self.call("GET", "/business-units")
        return resp["items"]

    def get_programs(self, business_unit):
        resp = self.call(
            "GET", "/business-units/" + business_unit + "/programs"
        )
        return [Program(self, **program) for program in resp["items"]]

    def get_program(self, program):
        resp = self.call("GET", "/programs/" + program)
        return Program(self, **resp)

    def get_reports(self, program, filters=None, lazy=False):
        """
        Get reports for a program

        :param str program: Program slug
        :param dict filters: Filter to apply
        """
        path = (
            "/programs/"
            + program
            + "/reports?page={page}&filter[sortBy]=changedAt&filter[order]=DESC"
        )
        reports = []
        if filters != None:
            path += "&"
            count = 0
            for i in filters:
                count += 1
                path += i + "=" + str(filters[i])
                if count != len(filters):
                    path += "&"
        resp_json = self.call("GET", path.format(page=1), data=filters)
        reports += resp_json["items"]
        for i in range(1, resp_json["pagination"]["nb_pages"]):
            resp_json = self.call("GET", path.format(page=i + 1), data=filters)
            reports += resp_json["items"]
        return [Report(self, lazy=lazy, **report) for report in reports]

    def get_report(self, report, lazy=False):
        resp = self.call("GET", "/reports/" + str(report))
        return Report(self, lazy=False, **resp)

    def post_comment(self, report_id, comment, private=False):
        path = "/reports/{id}/comments".format(id=report_id)
        data = {"private": private, "message": comment, "attachments": []}
        resp = self.call("POST", path, data=json.dumps(data))
        try:
            resp.raise_for_status()
            json_resp = resp.json()
        except Exception as e:
            raise InvalidResponse from e
        return Log(ywh_api=self, **json_resp)

    def managed_programs(self, lazy=False):
        if not self.managed_pgms or not lazy:
            self.managed_pgms = [slug['slug'] for slug in self.call('GET', '/manager/programs')['items']]
        return self.managed_pgms




class Priority(YwhApiObject):

    _attrs = [
        Attr(name="name", type_=str, default=""),
        Attr(name="slug", type_=str, default=""),
        Attr(name="level", type_=int, default=0),
        Attr(name='color', type_=str, default="")
    ]

class Category(YwhApiObject):

    _attrs = [Attr(name="name", type_=str), Attr(name="slug", type_=str)]


class Attachment(YwhApiObject):
    _attrs = [
        Attr(name="ywh_api", type_=YesWeHack),
        Attr(name="id", type_=int),
        Attr(name="name", type_=str),
        Attr(name="original_name", type_=str),
        Attr(name="mime_type", type_=str),
        Attr(name="size", type_=int),
        Attr(name="url", type_=str),
        Attr(name="_data", type_=bytes, default=bytes()),
    ]

    def __init__(self, ywh_api, id=None, lazy=False, **data):
        super().__init__(ywh_api=ywh_api, id=id, **data)

    def load_data(self, force_no_id=False):
        if not self._data and (force_no_id or self.id is not None):
            r = self.ywh_api.raw_call("GET", self.url)
            if r.status_code == 200:
                self._data = r.content

    @property
    def data(self) -> bytes:
        self.load_data()
        return self._data


class BugType(YwhApiObject):

    _attrs = [
        Attr(name="category", type_=Category),
        Attr(name="description", type_=str),
        Attr(name="link", type_=str),
        Attr(name="name", type_=str),
        Attr(name="remediation_link", type_=str),
        Attr(name="slug", type_=str),
    ]

    def __init__(self, **kwargs):

        kwargs["category"] = Category(**kwargs.get("category", {}))
        super().__init__(**kwargs)


class Author(YwhApiObject):
    _attrs = [
        Attr(name="ywh_api", type_=YesWeHack),
        Attr(name="username", type_=str),
        Attr(name="slug", type_=str),
        Attr(name="hunter_profile", type_=dict),
        Attr(name="avatar", type_=Attachment),
    ]

    def __init__(self, ywh_api, lazy=False, **kwargs):
        kwargs["avatar"] = Attachment(
            ywh_api, lazy=lazy, **kwargs.get("avatar", {})
        )
        super().__init__(ywh_api=ywh_api, **kwargs)

    def __str__(self):
        return self.username


class CVSS(YwhApiObject):

    _attrs = [
        Attr(name="criticity", type_=str),
        Attr(name="score", type_=float),
        Attr(name="vector", type_=str),
    ]


class Log(YwhApiObject):

    _attrs = [
        Attr(name="ywh_api", type_=YesWeHack),
        Attr(name="created_at", type_=str),
        Attr(name="duplicate_of", type_=dict),
        Attr(name="id", type_=int),
        Attr(name="type", type_=str),
        Attr(name="points", type_=int),
        Attr(name="private", type_=bool),
        Attr(name="author", type_=Author),
        Attr(name="canceled", type_=bool),
        Attr(name="cvss_bonus", type_=int),
        Attr(name="old_status", type_=dict),
        Attr(name="status", type_=dict),
        Attr(name="message_html", type_=str),
        Attr(name="attachments", type_=list, default=[]),
        Attr(name="old_cvss", type_=CVSS),
        Attr(name="new_cvss", type_=CVSS),
        Attr(name="priority", type_=Priority, default=None),
        Attr(name="old_bug_type", type_=BugType),
        Attr(name="new_bug_type", type_=BugType),
        Attr(name="old_tags", type_=list, default=[]),
        Attr(name="new_tags", type_=list, default=[]),
        Attr(name="reward_type", type_=str),
        Attr(name="bounty_reward_amount", type_=int),
        Attr(name="marked_as", type_=str),
        Attr(name="fix_verified"),
        Attr(name="old_details"),
        Attr(name="new_details"),
        Attr(name="rights", type_=list, default=[]),
        Attr(name="tracker_name", type_=str, default=None),
        Attr(name="tracker_url", type_=str, default=None),
        Attr(name="tracker_id", type_=str, default=None),
        Attr(name="tracker_token", type_=str, default=None),
    ]

    def __init__(self, ywh_api, lazy=False, **kwargs):
        if "author" in kwargs:
            kwargs["author"] = Author(
                ywh_api=ywh_api, lazy=lazy, **kwargs["author"]
            )
        kwargs["priority"] = Priority(**kwargs["priority"]) if "priority" in kwargs and kwargs['priority'] else None
        kwargs["old_cvss"] = CVSS(**kwargs["old_cvss"]) if "old_cvss" in kwargs and kwargs["old_cvss"] else CVSS()
        kwargs["new_cvss"] = CVSS(**kwargs["new_cvss"]) if "new_cvss" in kwargs and kwargs["new_cvss"] else CVSS()
        kwargs["old_bug_type"] = BugType(
            **(kwargs.get("old_bug_type", {}) or {})
        )
        kwargs["new_bug_type"] = BugType(
            **(kwargs.get("new_bug_type", {}) or {})
        )
        kwargs["attachments"] = [
            Attachment(
                ywh_api,
                attachment["id"],
                lazy=lazy,
                **attachment["attachment"]
            )
            for attachment in kwargs.get("attachments", [])
        ]
        super().__init__(ywh_api=ywh_api, **kwargs)

    def __str__(self):
        return_str = self.type
        if self.type == "comment":
            return_str += " from " + str(self.author)
        return return_str


class Report(YwhApiObject):

    _attrs = [
        Attr(name="ywh_api", type_=YesWeHack),
        Attr(name="id", type_=int),
        Attr(name="application_finger_print", type_=str),
        Attr(name="attachments", type_=list, default=[]),
        Attr(name="bonus", type_=int),
        Attr(name="bug_type", type_=BugType),
        Attr(name="chainable", type_=bool),
        Attr(name="chainable_exploit_description_html", type_=str),
        Attr(name="chainable_report", type_=dict, default={}),
        Attr(name="created_at", type_=str),
        Attr(name="cvss", type_=CVSS),
        Attr(name="cvss_bonus", type_=int),
        Attr(name="description_html", type_=str, default=""),
        Attr(name="duplicate_of", type_=dict, default={}),
        Attr(name="end_point", type_=str),
        Attr(name="hunter", type_=dict, default={}),
        Attr(name="local_id", type_=str),
        Attr(name="logs", type_=list),
        Attr(name="marked_as", type_=str),
        Attr(name="part_name", type_=str),
        Attr(name="payload_sample", type_=str),
        Attr(name="priority", type_=Priority, default=None),
        Attr(name="program", type_=dict, default={}),
        Attr(name="reward", type_=int),
        Attr(name="rights", type_=list, default=[]),
        Attr(name="scope", type_=str),
        Attr(name="source_ips", type_=list, default=[]),
        Attr(name="status", type_=dict, default={}),
        Attr(name="tags", type_=list, default=[]),
        Attr(name="technical_environment", type_=str),
        Attr(name="technical_information", type_=str),
        Attr(name="technical_information_html", type_=str),
        Attr(name="title", type_=str),
        Attr(name="tracking_status", type_=str),
        Attr(name="user_roles"),
        Attr(name="vulnerable_part", type_=str),
    ]

    def __init__(self, ywh_api, lazy=False, **kwargs):
        kwargs["attachments"] = [
            Attachment(
                ywh_api=ywh_api,
                id=attachment["id"],
                lazy=lazy,
                **attachment["attachment"]
            )
            for attachment in kwargs.get("attachments", [])
        ]
        kwargs["priority"] = Priority(**kwargs["priority"]) if "priority" in kwargs and kwargs['priority'] else None
        kwargs["bug_type"] = BugType(**kwargs.get("bug_type", {}))
        kwargs["cvss"] = CVSS(**kwargs.get("cvss", {}))
        super().__init__(ywh_api=ywh_api, **kwargs)
        if not lazy:
            self.get_report_logs(lazy=lazy)

    def __str__(self):
        return self.local_id + " : " + self.title

    def post_comment(self, comment, private=False):
        return self.ywh_api.post_comment(self.id, comment, private)

    def get_comments(self, lazy=False):

        if self.logs is None:
            self.get_report_logs(lazy=lazy)
        comments = []
        for log in self.logs:
            if log.type == "comment":
                comments.append(log)
        return comments

    def get_attachments_data(self):
        for attachment in self.attachments:
            attachment.load_data(force_no_id=True)

    def get_log_attachments_data(self):
        for log in self.logs:
            for attachment in log.attachments:
                attachment.load_data(force_no_id=True)

    def get_report_logs(self, lazy=False):
        path = "/reports/{id}/logs".format(id=self.id)
        resp = self.ywh_api.call("GET", path)
        self.logs = []
        for i in resp["items"]:
            self.logs.append(Log(ywh_api=self.ywh_api, lazy=lazy, **i))

    def export(self, export_format):
        path = "/reports/{id}/export/{export_format}".format(
            id=self.id, export_format=export_format
        )
        resp = self.ywh_api.raw_call(
            "GET", self.ywh_api.api_url + path
        )
        if resp.status_code != 200:
            print(
                "Error on pgm " + str(self.id) + " for format " + export_format
            )
        return resp.content

    def put_tracking_status(self, tracking_status, tracker_name, tracker_url, tracker_id=None, message=None):
        datas = {
            "tracking_status": tracking_status,
            "tracker_name": tracker_name,
            "tracker_url": tracker_url,
            "tracker_id" : tracker_id
        }

        if message is not None:
            datas['message'] = message
        resp = self.ywh_api.raw_call('PUT', f'{self.ywh_api.api_url}/reports/{self.id}/tracking-status', data=json.dumps(datas), headers=self.ywh_api.apps_headers)
        return resp

    def post_tracker_update(self, tracker_name, tracker_url, tracker_id=None, token=None, message=None):
        data = {
            "tracker_name": tracker_name,
            "tracker_id": tracker_id,
            "tracker_url": tracker_url,
            "tracker_token": token or '',
        }
        if message is not None:
            data['message'] = message
        resp = self.ywh_api.raw_call('POST', f'{self.ywh_api.api_url}/reports/{self.id}/tracker-update', data=json.dumps(data), headers=self.ywh_api.apps_headers)
        return resp

    def post_tracker_message(self, tracker_name, tracker_url, tracker_id=None, message=None, attachments=None) -> Log:
        data = {
            "tracker_name": tracker_name,
            "tracker_id": tracker_id,
            "tracker_url": tracker_url,
            "attachments": attachments or [],
        }
        if message is not None:
            data['message'] = message
        http_response = self.ywh_api.raw_call(
            method='POST',
            url=f'{self.ywh_api.api_url}/reports/{self.id}/tracker-message',
            data=json.dumps(data),
            headers=self.ywh_api.apps_headers,
        )
        if not http_response.ok:
            raise APIError(f'Unable to send tracker message. Response: {http_response.text}')

        try:
            content = http_response.json()
        except ValueError as e:
            raise APIError(
                f'Unable to parse response when sending tracker message. Response: {http_response.text}'
            ) from e
        return Log(ywh_api=self.ywh_api, **content)

    def post_attachment(self, filename: str, file_content: bytes, file_type: str = None, lazy: bool = False) -> Attachment:
        http_response = self.ywh_api.raw_call(
            method='POST',
            url=f'{self.ywh_api.api_url}/reports/{self.id}/attachments',
            files={
                'file': (filename, BytesIO(file_content), file_type)
            },
            headers=self.ywh_api.apps_headers,
        )
        if not http_response.ok:
            raise APIError(f'Unable to create attachment. Response: {http_response.text}')

        try:
            content = http_response.json()
        except ValueError as e:
            raise APIError(
                f'Unable to parse response when creating attachment. Response: {http_response.text}'
            ) from e
        return Attachment(
            ywh_api=self.ywh_api,
            id=content['id'],
            lazy=lazy,
            **content['attachment'],
        )

    def put_status(self, status, message=None, attachments=None) -> List[Log]:
        data = {
            "status": status,
            "attachments": attachments or [],
        }
        if message is not None:
            data['message'] = message
        http_response = self.ywh_api.raw_call(
            method='PUT',
            url=f'{self.ywh_api.api_url}/reports/{self.id}/status',
            data=json.dumps(data),
            headers=self.ywh_api.apps_headers,
        )
        if not http_response.ok:
            raise APIError(f'Unable to send report status. Response: {http_response.text}')

        try:
            content = http_response.json()
        except ValueError as e:
            raise APIError(
                f'Unable to parse response when sending report status. Response: {http_response.text}'
            ) from e

        if not isinstance(content, dict) or 'items' not in content or not isinstance(content.get('items'), list):
            raise APIError(
                f'Unexpected response format when sending report status. Response: {http_response.text}'
            )

        logs = []
        for raw_log in content.get('items'):
            logs.append(Log(ywh_api=self.ywh_api, **raw_log))

        return logs



class Program(YwhApiObject):

    _attrs = [
        Attr(name="ywh_api", type_=YesWeHack),
        Attr(name="reports", type_=list, default=[]),
        Attr(name="disabled", type_=bool),
        Attr(name="managed", type_=bool),
        Attr(name="bounty_reward_max", type_=int),
        Attr(name="reports_count", type_=int),
        Attr(name="status", type_=str),
        Attr(name="title", type_=str),
        Attr(name="slug", type_=str),
        Attr(name="banner", type_=dict),
        Attr(name="rules", type_=str),
        Attr(name="rules_html", type_=str),
        Attr(name="public", type_=bool),
        Attr(name="hall_of_fame", type_=bool),
        Attr(name="scopes", type_=list, default=[]),
        Attr(name="out_of_scope", type_=list, default=[]),
        Attr(name="qualifying_vulnerability", type_=list, default=[]),
        Attr(name="non_qualifying_vulnerability", type_=list, default=[]),
        Attr(name="bounty", type_=bool),
        Attr(name="gift", type_=bool),
        Attr(name="bounty_reward_min", type_=int),
        Attr(name="disclose_bounty_min_reward", type_=bool),
        Attr(name="disclose_bounty_average_reward", type_=bool),
        Attr(name="disclose_bounty_max_reward", type_=bool),
        Attr(name="reward_grid_default", type_=dict),
        Attr(name="reward_grid_low", type_=dict),
        Attr(name="reward_grid_medium", type_=dict),
        Attr(name="reward_grid_high", type_=dict),
        Attr(name="tags", type_=list, default=[]),
        Attr(name="business_unit", type_=dict, default={}),
        Attr(name="restricted_ips", type_=list, default=[]),
        Attr(name="vpn_active", type_=bool),
        Attr(name="vpn_ips", type_=list, default=[]),
        Attr(name="account_access", type_=str),
        Attr(name="disable_message", type_=str),
        Attr(name="user_agent", type_=str),
        Attr(name="stats", type_=dict, default={}),
        Attr(name="event", type_=dict),
        Attr(name="token", type_=str),
        Attr(name="rights", type_=list, default=[]),
    ]

    def __init__(self, ywh_api, lazy=False, **data):
        super().__init__(ywh_api=ywh_api, **data)

        if not lazy:
            reports = ywh_api.get_reports(self.slug, lazy=lazy)
            [self.reports.append(report) for report in reports]
