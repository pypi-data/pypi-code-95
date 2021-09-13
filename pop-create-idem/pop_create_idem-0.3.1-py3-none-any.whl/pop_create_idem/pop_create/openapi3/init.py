import pathlib
from typing import Any
from typing import Dict
from typing import Tuple

import openapi3.object_base
import requests
import yaml
from dict_tools.data import NamespaceDict

from pop_create_idem.tool.string import to_snake

REQUEST_FORMAT = """
return await hub.tool.http.session.request(
    ctx,
    method="{{{{ function.hardcoded.method }}}}",
    path=ctx.acct.endpoint_url + "{{{{ function.hardcoded.path }}}}".format(
        **{{{{ parameter.mapping.path|default({{}}) }}}}
    ),
    query_params={{{{ parameter.mapping.query|default({{}}) }}}},
    data={{{{ parameter.mapping.header|default({{}}) }}}}
)
""".strip()


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    spec = hub.pop_create.openapi3.init.read(source=ctx.specification)

    api = openapi3.OpenAPI(spec, validate=True)
    errors = api.errors()
    if errors:
        for e in errors:
            hub.log.warning(e)

    # list these as defaults in the acct plugin
    if api.servers:
        ctx.servers = [x.url for x in api.servers]
    else:
        ctx.servers = ["https://"]

    hub.log.debug(f"Working with openapi spec version: {api.openapi}")
    ctx.cloud_api_version = api.info.version or "latest"
    ctx.clean_api_version = hub.tool.string.to_snake(ctx.cloud_api_version).strip("_")
    # If the api version starts with a digit then make sure it can be used for python namespacing
    if ctx.clean_api_version[0].isdigit():
        ctx.clean_api_version = "v" + ctx.clean_api_version

    cloud_spec = NamespaceDict(
        api_version=ctx.cloud_api_version,
        project_name=ctx.project_name,
        service_name=ctx.service_name,
        request_format=REQUEST_FORMAT.format(acct_plugin=ctx.acct_plugin),
        plugins=_get_plugins(ctx, api.paths),
    )
    ctx.cloud_spec = cloud_spec

    hub.pop_create.init.run(directory=directory, subparsers=["idem_cloud"], **ctx)
    return ctx


def _get_plugins(ctx, paths: openapi3.object_base.Map) -> Dict[str, Any]:
    ret = {}
    for name, path in paths.items():
        assert isinstance(path, openapi3.paths.Path)
        # Get the request type that works for this request
        for request_type in path.raw_element.keys():
            func: openapi3.paths.Operation = getattr(path, request_type)
            if not func:
                continue
            subs = [to_snake("", sub) for sub in func.tags]
            if not subs:
                plugin = "init"
            else:
                plugin = subs.pop()

            refs = [ctx.service_name] + subs + [plugin]
            ref = ".".join(refs)
            if ref not in ret:
                # This is the first time we have looked at this plugin
                ret[ref] = {"functions": {}, "doc": ""}
            func_name, func_data = _get_function(name, func)
            func_data["hardcoded"] = {
                "method": request_type,
                "path": name.split(" ")[0],
            }
            ret[ref]["functions"][func_name] = func_data
    return ret


def _get_function(
    name: str,
    func: openapi3.paths.Operation,
) -> Tuple[str, Dict[str, Any]]:
    # This is the preferred way to get a function name
    func_name = func.operationId
    # Fallback function name based on the pets example
    if not func_name and " " in name:
        func_name = "_".join(name.split(" ")[1:]).lower()
    if not func_name and func.extensions:
        func_name = func.extensions[sorted(func.extensions.keys())[0]]
    else:
        func_name = func.summary

    # Maybe we need more fallbacks, you tell me
    if not func_name:
        # Maybe a fallback based on the path and method?
        raise AttributeError(f"Not sure how to find func name for {name}, help me out")

    func_name = to_snake("hub", func_name)

    func_spec = {
        "doc": (func.description or "").strip(),
        "params": {p.name: _get_parameter(p) for p in func.parameters},
    }
    return func_name, func_spec


def _get_parameter(parameter: openapi3.paths.Parameter):
    if parameter.in_ == "query":
        target_type = "mapping"
    elif parameter.in_ == "path":
        target_type = "mapping"
    elif parameter.in_ == "header":
        target_type = "mapping"
    elif parameter.in_ == "cookie":
        target_type = "mapping"
    else:
        raise ValueError(f"Unknown parameter type: {parameter.in_}")

    return {
        "required": parameter.required,
        "target_type": target_type,
        "target": parameter.in_,
        "param_type": _get_type(parameter.schema.type),
        "doc": parameter.description or parameter.name,
    }


def _get_type(param_type: str) -> str:
    if "integer" == param_type:
        return "int"
    elif "boolean" == param_type:
        return "bool"
    elif "number" == param_type:
        return "float"
    elif "string" == param_type:
        return "str"
    else:
        return ""


def read(hub, source: str or Dict):
    """
    If the path is a file, then parse the json contents of the file,
    If the path is a url, then return a json response from the url.
    """
    if isinstance(source, Dict):
        return source

    path = pathlib.Path(source)

    if path.exists():
        with path.open("r") as fh:
            ret = yaml.safe_load(fh)
    else:
        request = requests.get(source, headers={"Content-Type": "application/json"})
        ret = request.json()

    return ret
