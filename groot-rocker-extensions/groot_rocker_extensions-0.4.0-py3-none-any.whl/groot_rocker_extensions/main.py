#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Console scripts that provide user conveniences.
"""

##############################################################################
# Imports
##############################################################################

import argparse
import sys

import groot_rocker
import groot_rocker.console as console

##############################################################################
# Sandbox
##############################################################################


def main_workspace():
    defaults = {
        "command": "/bin/bash --login -i",
        "development_environment": True,
        "extension_blacklist": [],
        "git": True,
        "mode": "interactive",
        "named_prompt": True,
        "network": "host",
        "persistent": True,
        "user": True,
        "ssh": True,
    }
    parser = argparse.ArgumentParser(
        description=(
            "Build and enter a sandboxed docker environment for development with the\n"
            "following extensions enabled:\n"
            " - development_environment\n"
            " - git\n"
            " - named_prompt\n"
            " - network (=host)\n"
            " - persistent\n"
            " - user\n"
            " - ssh\n"
            "It also sets the command for an interactive bash login."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    build_options = parser.add_argument_group(title="Build Options", description="Options for image/container creation.")
    build_options.add_argument(
        '--name', type=str,
        default="development",
        help="human readable name for both image (sandbox:<name>) & container"
    )

    extensions_group = parser.add_argument_group(title="Extensions")
    extensions = ["bind", "colcon", "nvidia", "pulse_audio", "work_directory"]
    available_extensions = groot_rocker.core.list_plugins()  # typing.Dict[str, Extension]
    print(f"Exts: {available_extensions}")
    for extension in extensions:
        available_extensions[extension].register_arguments(extensions_group, defaults)

    parser.add_argument(
        'image', nargs='?',
        default=groot_rocker.cli.set_default("image", defaults),
        help="base image to build from (required)"
    )
    options = vars(parser.parse_args())  # work with a dict object from here, not argparse.Namespace
    options['container_name'] = options['name']
    options['image_name'] = f"devel:{options['name']}"
    del options['name']
    options.update(defaults)
    if options['image'] is None:
        console.error("No image was specified (hint: did you use --bind and not provide a '--' to close it's arguments?)")
        sys.exit(1)
    # convenience setting of work dir if there is only one mount point
    if options['work_directory'] is None and (len(options['bind']) == 1):
        bind_argument = options['bind'][0]
        if ":" in bind_argument:
            unused_source, options['work_directory'] = bind_argument.split(":")
        else:
            options['work_directory'] = bind_argument
    groot_rocker.cli.build_and_run(options)
