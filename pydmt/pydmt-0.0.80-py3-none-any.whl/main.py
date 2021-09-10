import sys
import os
import pathlib

import pylogconf.core
from pytconf import register_endpoint, register_main, config_arg_parse_and_launch

from pydmt.features.documentation import Documentation
from pydmt.core.pydmt import PyDMT
from pydmt.features.templating import Templating
from pydmt.static import APP_NAME, VERSION_STR, DESCRIPTION


def add_to_path():
    """
    This adds to PYTHONPATH various paths we need
    If you disable this then templates would not be able to find things like 'config/python.py'
    """
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


@register_endpoint(
    description="Build the project",
)
def build():
    add_to_path()

    pylogconf.core.setup()
    p = PyDMT()

    f = Templating()
    f.setup(p)
    f = Documentation()
    f.setup(p)

    stats = p.build_all()
    sys.exit(stats.get_os_error_code())


@register_endpoint(
    description="Clean all generated files"
)
def clean() -> None:
    pass


@register_main(
    app_name=APP_NAME,
    version=VERSION_STR,
    main_description=DESCRIPTION,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
