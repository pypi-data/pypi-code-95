import os

import sys
import pathlib

import pylogconf.core
from pytconf import register_function_group, register_endpoint

import pydmt.version
from pydmt.features.documentation import Documentation
from pydmt.core.pydmt import PyDMT
from pydmt.features.templating import Templating


GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "all pydmt commands"


def register_group_default():
    """
    register the name and description of this group
    """
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
)
def version() -> None:
    """
    Print version
    """
    print(pydmt.version.VERSION_STR)


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
)
def build():
    """ build the project """
    # parameters
    debug = False
    add_import_of_cwd = True
    add_import_of_home = True
    add_import_of_shared = True
    if add_import_of_shared:
        folder = "/etc/pydmt"
        if folder not in sys.path:
            sys.path.insert(0, folder)
    if add_import_of_home:
        folder = os.path.join(str(pathlib.Path.home()), ".config/pydmt")
        if folder not in sys.path:
            sys.path.insert(0, folder)
    if add_import_of_cwd:
        if "" not in sys.path:
            sys.path.insert(0, "")

    pylogconf.core.setup()
    if debug:
        print("system path is [{}]".format(sys.path))
    p = PyDMT()

    # add templating support
    f = Templating()
    f.setup(p)

    # add sphinx support
    f = Documentation()
    f.setup(p)

    stats = p.build_all()
    sys.exit(stats.get_os_error_code())


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
)
def clean() -> None:
    """
    clean all generated files
    """
