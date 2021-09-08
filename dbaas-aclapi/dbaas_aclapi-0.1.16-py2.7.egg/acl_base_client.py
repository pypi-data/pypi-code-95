# -*- coding: utf-8 -*-
import json
import urllib3
import logging
from urllib import urlencode
from dbaas_aclapi import helpers
from dbaas_credentials.models import CredentialType

logging.basicConfig()
LOG = logging.getLogger("AclBaseClient")
LOG.setLevel(logging.DEBUG)


GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


class GetRuleError(Exception):
    pass


def get_credential(environment, credential_type=CrentialType.ACLAPI):
    from util import get_credentials_for

    return get_credentials_for(environment, credential_type)


def get_acl_client(environment, credential_type=CrentialType.ACLAPI):
    raise Exception("A")
    credential = get_credential(environment, credential_type)
    return AclClient(
        credential.endpoint, credential.user, credential.password, environment
    )


class AclClient(object):

    def __init__(self, base_url, username, password, database_environment,
                 ip_version=4):
        LOG.info("Initializing new acl base client.")
        self.kind = ""
        self.acls = []
        self.headers = {}
        self.base_url = base_url
        self.username = username
        self.password = password
        self.ip_version = ip_version
        self.database_environment = database_environment
        self._add_basic_athentication()
        self._http_pool = urllib3.PoolManager()

    def _add_basic_athentication(self):
        LOG.info("Setting up authentication.")
        basic_auth = '{}:{}'.format(self.username, self.password)
        self.headers.update(urllib3.util.make_headers(basic_auth=basic_auth))

    def _add_content_type_json(self,):
        LOG.info("Setting up \"Content-Type\".")
        self.headers.update({'Content-Type': 'application/json'})

    def _do_get(self, endpoint, timeout=None):
        if timeout:
            return self._http_pool.request(
                method=GET, url=endpoint, headers=self.headers,
                timeout=timeout
            )
        return self._http_pool.request(
            method=GET, url=endpoint, headers=self.headers
        )

    def _encode_payload(self, payload):
        if type(payload) is not str:
            payload = json.dumps(payload)

        LOG.info("JSON PAYLOAD: {}".format(payload))
        return payload

    def _do_post(self, http_verb, endpoint, payload):
        self._add_content_type_json()
        return self._http_pool.urlopen(
            method=http_verb, body=self._encode_payload(payload),
            url=endpoint, headers=self.headers
        )

    def _build_route(self, endpoint):
        return self.base_url + endpoint

    def _make_request(self, endpoint, http_verb=GET, payload=None, timeout=None):
        endpoint = self._build_route(endpoint)
        LOG.debug("Requesting {} on {}".format(http_verb, endpoint))

        if http_verb == GET:
            response = self._do_get(endpoint, timeout)
        else:
            response = self._do_post(http_verb, endpoint, payload)

        LOG.debug("Response data: {}".format(response.data))
        LOG.debug("Response headers: {}".format(response.getheaders()))
        return response

    def delete_acl(self, environment_id, vlan, acl_id):
        LOG.info("Deleting ACL.")
        response = self._make_request(
            http_verb=DELETE,
            endpoint="api/ipv{}/acl/{}/{}/{}".format(
                self.ip_version, environment_id, vlan, acl_id
            )
        )
        return json.loads(response.data)

    def grant_acl_for(self, environment, vlan, payload):
        LOG.info("GRANT ACLs for {} on {}".format(vlan, environment))
        response = self._make_request(
            http_verb=PUT, payload=payload,
            endpoint="api/ipv{}/acl/{}".format(
                self.ip_version, "{}/{}".format(environment, vlan)
            )
        )
        json_data = json.loads(response.data)
        LOG.debug("JSON request.DATA decoded: {}".format(json_data))

        return json_data, response.status

    def rules_by_network(self, network, params=None):
        url = 'api/ipv{}/acl/{}?{}'.format(
            self.ip_version,
            network,
            urlencode(params or {})
        )
        response = self._make_request(
            http_verb=GET,
            endpoint=url
        )
        json_data = json.loads(response.data)
        LOG.debug(
            "JSON request.DATA decoded for get_rules_by_network: {}".format(
                json_data
            )
        )

        if response.status != 200:
            raise GetRuleError("Cant get rule for network: {} Error: {}".format(
                network,
                response.data
            ))

        for rule in json_data['rules']:
            yield rule

    def is_rule_executed(self, rule_to_find):
        rule_to_find.pop('id')
        for rule_found in helpers.iter_on_acl_rules(self, rule_to_find):
            applied_rules = self.rules_by_network(
                rule_found['source'],
                params={'status': 'applied'}
            )
            for rule in applied_rules:
                if rule['id'] == rule_found['id']:
                    return True
        return False

    def get_job(self, job_id):
        LOG.info("Retrieving job {}".format(job_id))
        response = self._make_request(
            endpoint="api/jobs/{}".format(job_id)
        )
        return json.loads(response.data)

    def run_job(self, job_id, timeout=3.0):
        LOG.info("Run job {}".format(job_id))

        run_url = self.run_job_endpoint.format(job_id)
        response = self._make_request(endpoint=run_url, timeout=timeout)

        return json.loads(response.data), response.status

    def query_acls(self, payload):
        response = self._make_request(
            http_verb=POST, payload=payload,
            endpoint='api/ipv{}/acl/search'.format(self.ip_version)
        )
        return json.loads(response.data)

    @property
    def run_job_endpoint(self):
        url = "api/jobs/{}/run"

        credential = get_credential(self.database_environment)
        run_job_params = credential.get_parameters_by_group('run_params')
        if run_job_params:
            url += '?'
            url += '&'.join('{}={}'.format(key, value)
                            for key, value in run_job_params.items())

        return url
