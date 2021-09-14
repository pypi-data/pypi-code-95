import sys


def bdrc_util_version() -> str:
    import pkg_resources  # part of setuptools
    return str(pkg_resources.require("bdrc-util")[0])


def ver_check():
    if "-v" in sys.argv or "--version" in sys.argv:
        print(bdrc_util_version())
        sys.exit(0)
