import os
import json
import requests
import collections.abc

from alfa_sdk.common.auth import Authentication
from alfa_sdk.common.helpers import EndpointHelper
from alfa_sdk.common.stores import ConfigStore
from alfa_sdk.common.exceptions import (
    RequestError,
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
)


DEFAULT_ALFA_ENV = "prod"


class Session:
    def __init__(self, credentials=None, *, context=None, **kwargs):
        self.context = fetch_context(context)

        self.alfa_env = fetch_alfa_env(kwargs, context=self.context)
        self.alfa_id = fetch_setting("alfa_id", kwargs, context=self.context)
        self.region = fetch_setting("platform_region", kwargs, context=self.context)
        credentials = fetch_credentials(credentials, self.context)

        alfa_config = {"alfa_env": self.alfa_env, "alfa_id": self.alfa_id, "region": self.region}
        self.endpoint = EndpointHelper(**alfa_config)
        self.auth = Authentication(credentials, **alfa_config)

        options = self.auth.authenticate_request({})
        self.http_session = requests.Session()
        self.http_session.headers.update(options["headers"])

    def request(self, method, service, path, *, parse=True, **kwargs):
        url = self.endpoint.resolve(service, path)
        kwargs = filter_none_arguments(kwargs)
        res = self.http_session.request(method, url, **kwargs)

        if parse:
            return parse_response(res)
        else:
            return res

    def invoke(self, function_id, environment, problem, **kwargs):
        if type(problem) is not dict:
            try:
                problem = json.loads(problem)
            except ValueError:
                raise ValueError("Problem must be a valid JSON string or a dict.")

        #

        function_type = kwargs.get("function_type", "algorithm")

        if function_type == "algorithm":
            return self.invoke_algorithm(function_id, environment, problem, **kwargs)
        elif function_type == "integration":
            return self.invoke_integration(function_id, environment, problem, **kwargs)

        raise ValidationError(error="Unknown type of release provided.")

    def invoke_algorithm(self, algorithm_id, environment, problem, **kwargs):
        return_holding_response = kwargs.get("return_holding_response")
        include_details = kwargs.get("include_details")
        can_buffer = kwargs.get("can_buffer")

        #

        body = {
            "algorithmId": algorithm_id,
            "environment": environment,
            "problem": problem,
            "returnHoldingResponse": return_holding_response,
            "includeDetails": include_details,
            "canBuffer": can_buffer,
        }
        return self.request("post", "baas", "/api/Algorithms/submitRequest", json=body)

    def invoke_integration(self, integration_id, environment, problem, **kwargs):
        function_name = kwargs.get("function_name")
        return self.request(
            "post",
            "ais",
            "/api/Integrations/{}/environments/{}/functions/{}/invoke".format(
                integration_id, environment, function_name
            ),
            json=problem,
        )


#


def parse_response(res):
    url = res.request.url
    try:
        data = res.json()
    except:
        data = res.text

    #

    if isinstance(data, collections.abc.Mapping) and "error" in data:
        if isinstance(data["error"], collections.abc.Mapping):
            error = data.get("error")

            if "code" in error:
                if error["code"] == "RESOURCE_NOT_FOUND":
                    raise ResourceNotFoundError(url=url, error=str(error))
                if error["code"] == "MISSING_TOKEN" or error["code"] == "INVALID_TOKEN":
                    raise AuthenticationError(error=str(error))
                if error["code"] == "UNAUTHORIZED" or error["code"] == "ACCESS_DENIED":
                    raise AuthorizationError(url=url, error=str(error))
                if error["code"] == "VALIDATION_FAILED":
                    raise ValidationError(error=str(error))

            # backward compatibility
            if "message" in error and isinstance(error["message"], str):
                if error["message"].startswith("No token provided"):
                    raise AuthenticationError(error=str(error))
                if error["message"].startswith("Error checking token"):
                    raise AuthenticationError(error=str(error))

            # backward compatibility
            if "name" in error:
                if error["name"] == "ModelNotFoundError":
                    raise ResourceNotFoundError(url=url, error=error.get("message"))
                if error["name"] == "AuthorizationError":
                    raise AuthorizationError(url=url, error=error.get("message"))

            raise RequestError(url=url, status=res.status_code, error=str(data.get("error")))

    #

    if res.status_code == 403:
        raise AuthorizationError(url=url, error=res.text)

    if not res.ok:
        raise RequestError(url=url, status=res.status_code, error=res.text)

    return data


def fetch_alfa_env(configuration={}, *, context={}):
    alfa_env = fetch_setting("alfa_env", configuration, context=context)

    if alfa_env in ["dev", "develop", "development"]:
        alfa_env = "dev"
    if alfa_env in ["test", "test-u", "test_u"]:
        alfa_env = "test"
    if alfa_env in ["prod", "production", "prod-u", "prod_u"]:
        alfa_env = "prod"

    return alfa_env


def fetch_context(context):
    if isinstance(context, collections.abc.Mapping):
        return context

    env_context = os.environ.get("ALFA_CONTEXT")

    try:
        env_context = json.loads(env_context)
    except:
        pass

    if isinstance(env_context, collections.abc.Mapping):
        return env_context

    return {}


def fetch_setting(name, configuration={}, *, context={}):
    context_names = {
        "alfa_env": "alfaEnvironment",
        "alfa_id": "alfaID",
        "platform_region": "platformRegion",
    }
    envvar_names = {
        "alfa_env": "ALFA_ENV",
        "alfa_id": "ALFA_ID",
        "platform_region": "PLATFORM_REGION",
    }
    defaults = {"alfa_env": "prod", "alfa_id": "public", "platform_region": "eu-central-1"}

    if name in configuration:
        return configuration.get(name)
    if envvar_names[name] in os.environ:
        return os.environ.get(envvar_names[name])
    if context_names[name] in context:
        return context.get(context_names[name])
    store = ConfigStore.get_group("alfa")
    if store and name in store:
        return store[name]
    return defaults[name]


def fetch_credentials(credentials, context):
    if not isinstance(credentials, collections.abc.Mapping):
        credentials = {}

    if not isinstance(context, collections.abc.Mapping):
        return credentials

    if "token" not in credentials:
        if "accessToken" in context:
            credentials["token"] = context.get("accessToken")

        if "auth0Token" in context:
            credentials["token"] = context.get("auth0Token")

        if "token" in context:
            credentials["token"] = context.get("token")

    if "cookie" not in credentials:
        if "cookie" in context:
            credentials["cookie"] = context.get("cookie")

    return credentials


#


def filter_none_arguments(kwargs):
    params = kwargs.get("params")
    if isinstance(params, collections.abc.Mapping):
        params = {k: v for k, v in params.items() if v is not None}
        kwargs["params"] = params

    body = kwargs.get("json")
    if isinstance(body, collections.abc.Mapping):
        body = {k: v for k, v in body.items() if v is not None}
        kwargs["json"] = body

    return kwargs
