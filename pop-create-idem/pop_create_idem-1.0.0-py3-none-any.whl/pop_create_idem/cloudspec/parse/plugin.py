"""
Functions for processing plugins
"""
from cloudspec import CloudSpecPlugin


def header(hub, plugin: CloudSpecPlugin) -> str:
    """
    Initialize the render of a plugin file and return the template
    """
    # noinspection JinjaAutoinspect
    template = hub.tool.jinja.template(hub.cloudspec.template.plugin.HEADER)

    return template.render(plugin=plugin)
