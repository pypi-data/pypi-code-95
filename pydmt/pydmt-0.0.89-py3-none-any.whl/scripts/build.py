import os
import pylogconf.core
import sys
import pathlib

from pydmt.builders.sphinx import Sphinx
from pydmt.core.pydmt import PyDMT
from pydmt.features.templating import Templating


def main():
    # parameters
    debug = False
    sphinx = True
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
    t = Templating()
    t.setup(p)

    # add sphinx builder support
    if sphinx and os.path.isdir("sphinx"):
        import config.project
        p.add_builder(Sphinx(package_name=config.project.project_name))
    p.build_all()


if __name__ == '__main__':
    main()
