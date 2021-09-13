import pathlib
import re

import boto3.docs.docstring
import boto3.exceptions
import boto3.session
import botocore.client
import botocore.docs.docstring
import botocore.exceptions
import botocore.model
from dict_tools.data import NamespaceDict

try:
    import inflect
    import textwrap
    import tqdm

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


DESCRIBE_FUNCTIONS = ("describe", "get", "search", "list")

DELETE_FUNCTIONS = (
    "delete",
    "disassociate",
    "reject",
    "deallocate",
    "unassign",
    "deregister",
    "deprovision",
    "revoke",
    "release",
    "terminate",
    "cancel",
    "disable",
)
CREATE_FUNCTIONS = (
    "create",
    "associate",
    "accept",
    "allocate",
    "assign",
    "register",
    "provision",
    "authorize",
    "run",
    "enable",
    "upload",
    "put",
    "publish",
)

NAME_PARAMETER = {
    "default": None,
    "doc": "A name, ID, or JMES search path to identify the resource",
    "param_type": "Text",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

PRESENT_REQUEST_FORMAT = r"""
    result = dict(comment="", changes= None, name=name, result=True)

    {%- if (not function.hardcoded.is_idempotent) %}
    ret = await hub.exec.boto3.client.{{ function.hardcoded.service_name }}.{{ function.hardcoded.resource }}.id(
        ctx,
        jmes_path=name
    )
    if ret["status"]:
        # name is now the first id that matched the JMES search path
        name = ret["ret"]
    {% endif %}

    {{ function.hardcoded.resource_function_call }}
    before = {{ function.hardcoded.describe_function_call }}

    if before:
        result["comment"] = f"'{name}' already exists"
    else:
        try:
            ret = await {{ function.hardcoded.create_function }}(
                ctx,
                {{ "DryRun=ctx.test," if function.hardcoded.has_dry_run }}
                {{ "ClientToken=name," if function.hardcoded.has_client_token }}
                **{{ parameter.mapping.kwargs|default({}) }}
            )
            result["result"] = ret["status"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            ret["comment"] = f"Created '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = f"{e.__class__.__name__}: {e}"

    {{ function.hardcoded.waiter_call }}
    # TODO perform other modifications as needed here
    ...

    after = {{ function.hardcoded.describe_function_call }}
    result["changes"] = differ.deep_diff(before, after)
    return result
"""
ABSENT_REQUEST_FORMAT = """
    result = dict(comment="", changes= None, name=name, result=True)
    {%- if (not function.hardcoded.is_idempotent) %}
    ret = await hub.exec.boto3.client.{{ function.hardcoded.service_name }}.{{ function.hardcoded.resource }}.id(
        ctx,
        jmes_path=name
    )
    if ret["status"]:
        # name is now the first id that matched the JMES search path
        name = ret["ret"]
    {% endif %}

    {{ function.hardcoded.resource_function_call }}

    before = {{ function.hardcoded.describe_function_call }}

    if not before:
        result["comment"] = f"'{name}' already absent"
    else:
        try:
            ret = await {{ function.hardcoded.delete_function }}(
                ctx,
                {{ "DryRun=ctx.test," if function.hardcoded.has_dry_run }}
                {{ "ClientToken=name," if function.hardcoded.has_client_token }}
                **{{ parameter.mapping.kwargs|default({}) }}
            )
            result["result"] = ret["status"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            result["comment"] = f"Deleted '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = f"{e.__class__.__name__}: {e}"

    {{ function.hardcoded.waiter_call }}

    after = {{ function.hardcoded.describe_function_call }}
    result["changes"] = differ.deep_diff(before, after)
    return result
"""
DESCRIBE_REQUEST_FORMAT = """
    result = {}

    ret = await {{ function.hardcoded.list_function}}(ctx)
    if not ret["status"]:
        hub.log.debug(f"Could not describe {{ function.hardcoded.resource }} {ret['comment']}")
        return result

    for {{ function.hardcoded.resource }} in ret["ret"]["{{ function.hardcoded.list_item }}"]:
        new_{{ function.hardcoded.resource }} = [
                {{ parameter.mapping.kwargs|default({}) }}
        ]
        result[{{ function.hardcoded.resource }}["{{ function.hardcoded.resource }}Id"]] = {"{{ function.ref }}.present": new_{{ function.hardcoded.resource }}}

        for i, data in enumerate({{ function.hardcoded.resource }}.get("", ())):
            sub_{{ function.hardcoded.resource }} = copy.deepcopy(new_{{ function.hardcoded.resource }})

            # TODO check for subresouruces
            sub_{{ function.hardcoded.resource }}.append({})
            sub_{{ function.hardcoded.resource }}.append({"name": "{{ function.hardcoded.resource_id }}"})
            result[f"{{ function.hardcoded.resource_id }}-{i}"] = {"{{ function.ref }}.present": sub_{{ function.hardcoded.resource }}}

    return result
"""


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    session = boto3.session.Session()
    services = hub.OPT.pop_create.services or session.get_available_services()
    ctx.servers = [None]

    # We already have an acct plugin
    ctx.has_acct_plugin = False
    ctx.service_name = "aws_auto"

    # Initialize cloud spec
    ctx.cloud_spec = NamespaceDict(
        api_version="",
        project_name=ctx.project_name,
        service_name=ctx.service_name,
        request_format={
            "present": PRESENT_REQUEST_FORMAT,
            "absent": ABSENT_REQUEST_FORMAT,
            "describe": DESCRIBE_REQUEST_FORMAT,
        },
        plugins={},
    )

    # This takes a while bcause we are making http calls to aws
    for service in tqdm.tqdm(services):
        try:
            plugins = _get_plugins(hub, session, service)
        except botocore.exceptions.UnknownServiceError as err:
            plugins = {}
            hub.log.error(f"{err.__class__.__name__}: {err}")

        ctx.cloud_spec.plugins = plugins

        # Generate the exec modules for this specific service
        hub.cloudspec.init.run(
            ctx,
            directory,
            create_plugins=["state_modules"],
        )

    ctx.cloud_spec.plugins = {}
    return ctx


def _get_plugins(hub, session: "boto3.session.Session", service: str):
    grammar = inflect.engine()
    plugins = {}

    # Create the boto client that will be parsed for capabilities
    client = session.client(
        service_name=service,
        region_name=hub.OPT.pop_create.region,
        api_version=hub.OPT.pop_create.api_version,
    )
    operations = {}
    for op in client.meta.method_to_api_mapping:
        try:
            verb, resource = op.split("_", maxsplit=1)
            if re.match(fr"\w+[^aoius]s$", resource):
                resource = grammar.singular_noun(resource)
            if resource not in operations:
                operations[resource] = {}
            operations[resource][verb] = op
        except ValueError:
            ...

    # Get resources if we can for this object
    resources = {}
    try:
        service_resource = session.resource(
            service_name=service,
            region_name=hub.OPT.pop_create.region,
            api_version=hub.OPT.pop_create.api_version,
        )
        for sub_resource in service_resource.meta.resource_model.subresources:
            resources[hub.tool.string.to_snake(sub_resource.name)] = (
                sub_resource.name,
                [],
            )
            resources[hub.tool.string.to_snake(sub_resource.name)][1].extend(
                [
                    f"hub.tool.boto3.resource.exec(resource, {action.name}, *args, **kwargs)"
                    for action in sub_resource.resource.model.actions
                ]
            )
    except boto3.exceptions.ResourceNotExistsError:
        ...

    clean_service = hub.tool.string.unclash(service).replace("-", "_")
    if clean_service != service.replace("-", "_"):
        plugin_docstring = hub.tool.string.from_html(
            client._service_model.documentation
        )
        plugins[f"{clean_service}.init"] = {
            "imports": [],
            "functions": {},
            "doc": "\n".join(textwrap.wrap(plugin_docstring, width=120)),
            "sub_alias": [service.replace("-", "_"), clean_service],
        }

    # Create a state for everything that has a create/delete/describe function
    for resource, functions in operations.items():
        other_calls = [
            f"hub.exec.boto3.client.{clean_service}.{op}" for op in functions.values()
        ]
        get_resource_call = ""

        # Get resource and describe func
        if resource in resources:
            r = resources[resource]
            get_resource_call = f'resource = hub.tool.boto3.resource.create(ctx, "{clean_service}", "{r[0]}", name)'
            other_calls.append(get_resource_call)
            describe_function_call = "await hub.tool.boto3.resource.describe(resource)"
            other_calls.extend(r[1])
        else:
            for func_name in DESCRIBE_FUNCTIONS:
                if func_name in functions:
                    describe_function_call = f"await hub.exec.boto3.client.{clean_service}.{functions[func_name]}(name)"
                    break
            else:
                hub.log.info(
                    f"Cannot determine how to describe {clean_service}.{resource}: {list(functions.keys())}"
                )
                continue

        # Get create function
        for func_name in CREATE_FUNCTIONS:
            if func_name in functions:
                create_function = functions[func_name]
                break
        else:
            hub.log.info(
                f"Cannot determine how to create {clean_service}.{resource}: {list(functions.keys())}"
            )
            continue

        # Get delete function
        for func_name in DELETE_FUNCTIONS:
            if func_name in functions:
                delete_function = functions[func_name]
                break
        else:
            hub.log.info(
                f"Cannot determine how to delete {clean_service}.{resource}: {list(functions.keys())}"
            )
            continue

        # Get list function
        for func_name in functions:
            if client.can_paginate(functions[func_name]):
                list_function = functions[func_name]
                break
        else:
            hub.log.info(
                f"Cannot determine how to describe {clean_service}.{resource}: {list(functions.keys())}"
            )
            continue

        clean_resource = hub.tool.string.unclash(resource)
        plugin_key = f"{clean_service}.{clean_resource}".replace("-", "_")
        plugins[plugin_key] = {
            "imports": [
                "import copy",
                "from typing import *",
                "import dict_tools.differ as differ",
            ],
            "functions": {},
            "doc": str(client.__doc__),
        }
        if clean_resource != resource:
            plugins[plugin_key]["virtualname"] = resource

        plugins[plugin_key]["doc"] = "\n".join(other_calls)
        shared_function_data = {
            "delete_function": f"hub.exec.boto3.client.{clean_service}.{delete_function}",
            "create_function": f"hub.exec.boto3.client.{clean_service}.{create_function}",
            "list_function": f"hub.exec.boto3.client.{clean_service}.{list_function}",
            "waiter_call": "",
            "resource_function_call": get_resource_call,
            "describe_function_call": describe_function_call,
            "list_item": "TODO",
            "resource_id": "TODOs",
            "service_name": clean_service,
            "resource": resource,
            "has_dry_run": False,
            "has_client_token": False,
            "is_idempotent": False,
            "tag_method": "TODO, unify the way resources are tagged",
        }
        for state_function, op_name in zip(
            ("present", "absent", "describe"),
            (create_function, delete_function, list_function),
        ):
            func_definition = _get_client_function(hub, client, service, op_name)
            func_definition["hardcoded"].update(shared_function_data)
            func_definition["hardcoded"].update(
                {
                    "has_dry_run": func_definition["params"].pop("DryRun", None),
                    "has_client_token": func_definition["params"].pop(
                        "ClientToken", None
                    ),
                    "is_idempotent": func_definition["params"].pop(
                        "ClientToken", "idempotent" in func_definition["doc"].lower()
                    ),
                }
            )

            # Normalize the name parameter
            if "Name" in func_definition["params"]:
                name = func_definition["params"].pop("Name")
            elif "name" in func_definition["params"]:
                name = func_definition["params"].pop("name")
            else:
                name = NAME_PARAMETER.copy()
                if func_definition["hardcoded"]["is_idempotent"]:
                    name["doc"] = "The name of the state"

            # Create a new param list the puts "name" first in the orderered dict
            func_definition["params"] = dict(
                Name=name,
                **func_definition["params"],
            )
            plugins[plugin_key]["functions"][state_function] = func_definition

        # plugins[plugin_key]["functions"]["describe"]["params"] = {}

    return plugins


def _get_client_function(
    hub, client: "botocore.client.BaseClient", service: str, operation: str
):
    function = getattr(client, operation)
    doc: botocore.docs.docstring.ClientMethodDocstring = function.__doc__
    docstring = hub.tool.string.from_html(doc._gen_kwargs["method_description"])
    try:
        # TODO what does botocore expect?
        params = doc._gen_kwargs["operation_model"].input_shape.members
        required_params = doc._gen_kwargs[
            "operation_model"
        ].input_shape.required_members
        parameters = {
            p: _get_parameter(hub, param=data, required=p in required_params)
            for p, data in params.items()
        }
    except AttributeError:
        parameters = {}
    try:
        return_type = _get_type(
            hub, doc._gen_kwargs["operation_model"].output_shape.type_name
        )
    except AttributeError:
        return_type = None

    ret = {
        "doc": "\n".join(textwrap.wrap(docstring, width=112)),
        "params": parameters,
        "return_type": return_type,
        "hardcoded": {"service": service, "operation": operation},
    }

    return ret


def _get_parameter(hub, param: "botocore.model.Shape", required: bool):
    docstring = hub.tool.string.from_html(param.documentation)
    return {
        "required": required,
        "default": None,
        "target_type": "mapping",
        "target": "kwargs",
        "param_type": _get_type(hub, param.type_name),
        "doc": "\n            ".join(textwrap.wrap(docstring, width=96)),
    }


def _get_type(hub, type_name: str):
    if type_name == "string":
        return "Text"
    elif type_name == "map":
        return "Dict"
    elif type_name == "structure":
        return "Dict"
    elif type_name == "list":
        return "List"
    elif type_name == "boolean":
        return "bool"
    elif type_name in ("integer", "long"):
        return "int"
    elif type_name in ("float", "double"):
        return "float"
    elif type_name == "timestamp":
        return "Text"
    elif type_name == "blob":
        return "ByteString"
    else:
        raise NameError(type_name)
