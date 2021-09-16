import pathlib

from cloudspec import CloudSpec


def run(hub, ctx, root_directory: pathlib.Path or str):
    if isinstance(root_directory, str):
        root_directory = pathlib.Path(root_directory)
    cloud_spec = CloudSpec(**ctx.cloud_spec)
    states_dir = root_directory / ctx.clean_name / "states" / ctx.service_name
    for ref, plugin in cloud_spec.plugins.items():
        split = ref.split(".")
        subs = split[:-1]
        mod = split[-1]
        ref = ".".join([ctx.service_name] + subs + [mod])
        state_ref = ".".join([ctx.service_name] + subs + [plugin.virtualname or mod])
        mod_file = states_dir
        for sub in subs:
            mod_file = mod_file / sub
        mod_file = mod_file / f"{mod}.py"
        hub.tool.path.touch(mod_file)

        to_write = hub.cloudspec.parse.plugin.header(plugin)

        # Create the present, absent, and describe functions; these are required for every state module
        for function_name, TEMPLATE in zip(
            ("present", "absent", "describe"),
            (
                hub.cloudspec.template.state.PRESENT_FUNCTION,
                hub.cloudspec.template.state.ABSENT_FUNCTION,
                hub.cloudspec.template.state.DESCRIBE_FUNCTION,
            ),
        ):
            template = hub.tool.jinja.template(
                f"{TEMPLATE}\n    {cloud_spec.request_format[function_name]}\n\n\n"
            )

            try:
                function_data = plugin.functions[function_name]
            except KeyError as e:
                hub.log.error(f"No '{function_name}' function defined for module {ref}")
                continue

            # noinspection JinjaAutoinspect
            if function_data.doc:
                doc = function_data.doc.replace('"""', "'''")
                doc = "\n" + hub.tool.format.wrap.indent(doc, 1) + "\n"
            else:
                doc = ""

            if function_name != "describe":
                doc += hub.cloudspec.parse.param.sphinx_docs(function_data.params)

            doc += "\n\n    Returns:\n        Dict[str, Any]\n"
            to_write += template.render(
                function=dict(
                    name=function_name,
                    hardcoded=function_data.hardcoded,
                    doc=doc,
                    ref=ref,
                    state_ref=f"states.{state_ref}",
                    header_params=hub.cloudspec.parse.param.headers(
                        function_data.params
                    ),
                    required_call_params=hub.cloudspec.parse.param.callers(
                        function_data.params
                    ),
                ),
                parameter=dict(
                    mapping=hub.cloudspec.parse.param.mappings(function_data.params)
                ),
            )

            mod_file.write_text(to_write)
