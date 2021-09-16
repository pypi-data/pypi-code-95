import pathlib
import re
from typing import Dict
from typing import Tuple

from dict_tools.data import NamespaceDict

try:
    import botocore.exceptions
    import botocore.model
    import botocore.session
    import botocore.client
    import botocore.docs.docstring
    import tqdm

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


REQUEST_FORMAT = """
return await hub.{service_name}.client.exec(
    ctx,
    service_name="{{{{ function.hardcoded.service }}}}",
    operation="{{{{ function.hardcoded.operation }}}}",
    op_kwargs={{{{ parameter.mapping.kwargs|default({{}}) }}}}
)
""".strip()


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    session = botocore.session.Session()
    services = hub.OPT.pop_create.services or session.get_available_services()
    ctx.servers = [None]

    # Get API version
    ctx.cloud_api_version = hub.OPT.pop_create.api_version or botocore.__version__
    ctx.clean_api_version = hub.tool.case.snake(ctx.cloud_api_version).strip("_")
    # If the api version starts with a digit then make sure it can be used for python namespacing
    if ctx.clean_api_version[0].isdigit():
        ctx.clean_api_version = "v" + ctx.clean_api_version

    # We will generate our own acct plugin
    ctx.has_acct_plugin = False

    # Get the service name
    if ctx.get("simple_service_name"):
        ctx.service_name = ctx.simple_service_name
    elif not ctx.get("service_name"):
        ctx.service_name = (
            ctx.clean_name.replace("idem", "").replace("cloud", "").strip("_")
        )

    # Initialize cloud spec
    ctx.cloud_spec = NamespaceDict(
        api_version=ctx.cloud_api_version,
        project_name=ctx.project_name,
        service_name=ctx.service_name,
        request_format=REQUEST_FORMAT.format(service_name=ctx.service_name),
        plugins={},
    )

    # This takes a while because we are making http calls to aws
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
            create_plugins=["exec_modules"],
        )

    ctx.cloud_spec.plugins = {}
    hub.pop_create.init.run(directory=directory, subparsers=["cicd"], **ctx)
    return ctx


def _get_plugins(hub, session: "botocore.session.Session", service: str):
    plugins = {}

    # Create the boto client that will be parsed for capabilities
    client = session.create_client(
        service_name=service,
        region_name=hub.OPT.pop_create.region,
        api_version=hub.OPT.pop_create.api_version,
    )

    pathops = _map_ops_to_path(hub, client, service)

    for operation, pathverb in pathops.items():
        # compile the new path with all the sanitized names
        path, verb = pathverb
        path = path.replace("__", "_")

        if path not in plugins:
            plugins[path] = {"functions": {}, "doc": str(client.__doc__)}

        # If a function name ends in an underscore, create an alias
        if verb.endswith("_"):
            alias = verb[:-1]
            if "func_alias" not in plugins[path]:
                plugins[path]["func_alias"] = {}
            plugins[path]["func_alias"][verb] = alias

        if "." in path:
            subs, plugin = path.rsplit(".", 1)
            subs = subs.split(".")
        else:
            plugin = path
            subs = []

        # Handle virtualnames for plugins
        if plugin.endswith("_"):
            plugins[path]["virtualname"] = plugin[:-1]

        # Handle sub_aliases
        builder = []
        for sub in subs:
            builder.append(sub)
            if sub.endswith("_"):
                build_path = ".".join(builder + ["init"])
                if build_path not in plugins:
                    plugins[build_path] = {
                        "functions": {},
                        "doc": str(client.__doc__),
                        "sub_alias": [sub, sub[:-1]],
                    }

        plugins[path]["imports"] = ["from typing import *"]
        try:
            if verb in plugins[path]["functions"]:
                # See if we have an alternate
                verb = _redefine_verb(hub, verb)
                if verb in plugins[path]["functions"]:
                    raise NameError(
                        "Oh no! There was a name clash, probably from a function"
                        f" from a plural plugin made singular: {path}.{verb}"
                    )
            plugins[path]["functions"][verb] = _get_function(
                hub, client, service, operation
            )
        except AttributeError as err:
            hub.log.warning(
                f"Could not find functions for {service}.{operation}: {err}"
            )

    return plugins


def _map_ops_to_path(hub, client, service: str) -> Dict[str, str]:
    """
    Map the operations on a client to sane organized grouped paths
    """
    pathops = {}
    for operation in sorted(client.meta.method_to_api_mapping):
        if "_" in operation:
            verb, attr = operation.split("_", maxsplit=1)
        else:
            verb = operation
            attr = "init"

        # if the path ends in an "s", remove the "s"
        made_singular = hub.tool.inflect.singular(attr)
        if made_singular:
            # For plural modules being merged into singular modules, modify function names as needed to avoid clashes
            attr = made_singular
            verb = _redefine_verb(hub, verb)

        verb = hub.tool.keyword.unclash(verb)

        # Remove plural words from the middle of attributes
        path = ".".join(
            hub.tool.keyword.unclash(hub.tool.inflect.singular(p) or p)
            for p in re.split(r"[_\-.]", f"{service}.{attr}")
        )

        pathops[operation] = (path, verb)

    return hub.pop_create.botocore.init.organize_paths(pathops)


def organize_paths(
    hub, pathops: Dict[str, Tuple[str, str]]
) -> Dict[str, Tuple[str, str]]:
    for op, pathverb in pathops.items():
        path, verb = pathverb
        full_path = []

        iterator = iter(path.split("."))
        p = next(iterator)
        while True:
            try:
                n = next(iterator)

                try_path = ".".join(full_path + [p, n])
                sure_path = ".".join(full_path + [p])
                if all(
                    i.startswith(try_path)
                    for i, _ in pathops.values()
                    if i.startswith(sure_path)
                ):
                    p = f"{p}_{n}"
                    sub_path = ".".join(full_path + [p])
                    for k, v in pathops.items():
                        new_v0 = re.sub(fr"^{try_path}", sub_path, v[0])
                        pathops[k] = new_v0, v[1]
                else:
                    full_path.append(p)
                    p = n
            except StopIteration:
                full_path.append(p)
                break

        clean_path = ".".join(hub.tool.keyword.unclash(p) for p in full_path)
        pathops[op] = (clean_path, verb)

    # Add "init" to the paths of plugins with the same name of a sub at the same level
    for op, pathverb in pathops.items():
        path, verb = pathverb
        if any(p[0].startswith(f"{path}.") for p in pathops.values()):
            pathops[op] = (f"{path}.init", verb)

    return pathops


def _redefine_verb(hub, verb: str) -> str:
    if verb == "create":
        return "create_multiple"
    elif verb == "get":
        return "get_all"
    elif verb == "describe":
        return "describe_all"
    elif verb == "list":
        return "list_all"
    elif verb == "put":
        return "put_multiple"
    elif verb == "update":
        return "update_multiple"
    elif verb == "delete":
        return "delete_multiple"
    return verb


def _get_function(
    hub, client: "botocore.client.BaseClient", service: str, operation: str
):
    function = getattr(client, operation)
    doc: botocore.docs.docstring.ClientMethodDocstring = function.__doc__
    docstring = hub.tool.html.parse(doc._gen_kwargs["method_description"])
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
        "doc": docstring,
        "params": parameters,
        "return_type": return_type,
        "hardcoded": {"service": service, "operation": operation},
    }

    return ret


def _get_parameter(hub, param: "botocore.model.Shape", required: bool):
    return {
        "required": required,
        "default": None,
        "target_type": "mapping",
        "target": "kwargs",
        "param_type": _get_type(hub, param.type_name),
        "doc": hub.tool.html.parse(param.documentation),
    }


def _get_type(hub, type_name: str):
    if type_name == "string":
        return "str"
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
        return "str"
    elif type_name == "blob":
        return "bytes"
    else:
        raise NameError(type_name)
