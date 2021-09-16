import pathlib

from cloudspec import CloudSpec


def run(hub, ctx, root_directory: pathlib.Path or str):
    if isinstance(root_directory, str):
        root_directory = pathlib.Path(root_directory)
    cloud_spec = CloudSpec(**ctx.cloud_spec)
    exec_dir = (
        root_directory
        / ctx.clean_name
        / "exec"
        / ctx.service_name
        / ctx.clean_api_version
    )
    for ref, plugin in cloud_spec.plugins.items():
        split = ref.split(".")
        subs = split[:-1]
        mod = split[-1]
        ref = ".".join([ctx.service_name] + subs + [mod])
        cli_ref = ".".join([ctx.service_name] + subs + [plugin.virtualname or mod])
        mod_file = exec_dir
        for sub in subs:
            mod_file = mod_file / sub
        mod_file = mod_file / f"{mod}.py"
        hub.tool.path.touch(mod_file)

        to_write = hub.cloudspec.parse.plugin.header(plugin)

        for function_name, function_data in plugin.functions.items():
            template = hub.tool.jinja.template(
                f"{hub.cloudspec.template.exec.FUNCTION}\n    {cloud_spec.request_format}\n\n\n"
            )

            if function_data.doc:
                doc = function_data.doc.replace('"""', "'''")
                doc = "\n" + hub.tool.format.wrap.indent(doc, 1) + "\n"
            else:
                doc = ""

            function_alias = plugin.func_alias.get(function_name, function_name)

            to_write += template.render(
                function=dict(
                    name=function_name,
                    hardcoded=function_data.hardcoded,
                    doc=doc
                    + hub.cloudspec.parse.param.sphinx_doc(function_data.params)
                    + hub.cloudspec.parse.function.return_sphinx_doc(function_data),
                    ref=f"{ref}.{function_alias}",
                    cli_ref=f"{cli_ref}.{function_alias}",
                    header_params=hub.cloudspec.parse.param.headers(
                        function_data.params
                    ),
                    required_call_params=hub.cloudspec.parse.param.callers(
                        function_data.params
                    ),
                    return_type=function_data.return_type,
                ),
                parameter=dict(
                    mapping=hub.cloudspec.parse.param.mappings_get_map_params(
                        function_data.params
                    )
                ),
            )

        mod_file.write_text(to_write)
