from contextlib import contextmanager
from distutils.core import run_setup
from itertools import chain
import json
import os
from pathlib import Path
from setuptools.config import read_configuration
import sys

def command(args):
    package_info = get_package_info(args.directory)
    print(json.dumps(package_info, sort_keys=True, indent=4))

def get_package_info(path):
    setup_cfg_options = _get_config_from_setup_cfg(path)
    setup_py_options = _get_config_from_setup_py(path)

    # Last argument wins, so setup_cfg takes precedence for all non-None values
    merged_options = merge_config_dicts(setup_py_options, setup_cfg_options)

    if merged_options["name"] is None:
        raise Exception(f"Could not determine package name from setup files in {path}")

    if (merged_options["package_dir"] and merged_options["root_package"]):
        return {
            "name": merged_options["name"],
            "package_src_dir": str(
                Path(
                    path,
                    merged_options["package_dir"],
                    merged_options["root_package"],
                ),
            ),
        }

    if merged_options["root_package"] is None:
        raise Exception(f"Could not determine root package directory from setup files in {path}")

    return {
        "name": merged_options["name"],
        "package_src_dir": str(Path(path, merged_options["root_package"])),
    }


def _get_config_from_setup_cfg(path):
    """Return config data from setup.cfg file in path if one exists."""
    setup_cfg_path = Path(path, "setup.cfg")
    res = {
        "name": None,
        "package_dir": None,
        "root_package": None,
    }

    if (not setup_cfg_path.is_file()):
        return res

    setup_cfg_data = read_configuration(setup_cfg_path)
    metadata = setup_cfg_data.get("metadata", {})
    options = setup_cfg_data.get("options", {})

    res["name"] = metadata.get("name")

    try:
        # In my simple repo where setup.cfg configures package_dir like
        # this:
        #
        # [options]
        # package_dir =
        #     = src
        #
        # package_dir is a dictionary with the value:
        # {"": "src"}
        # For now, let's assume the first value in this dictionary is
        # the package directory we want.
        res["package_dir"] = list(options.get("package_dir", {}).values())[0]
    except IndexError:
        pass

    try:
        # Since Python packages nest under the top level package, e.g.
        # 'django', 'django.db', 'django.coore.cache', etc. we sort
        # the package names *by length* so the first one is the shortest.
        res["root_package"] = sorted(options.get("packages", []), key=len)[0]
    except IndexError:
        pass

    return res


def _get_config_from_setup_py(path):
    """Return config data from setup.py file in path if one exists."""
    setup_py_path = Path(path, "setup.py")
    res = {
        "name": None,
        "package_dir": None,
        "root_package": None,
    }

    if (not setup_py_path.is_file()):
        return res

    with push_setup_py_dir(path):
        distribution = run_setup(setup_py_path, stop_after="init")

    res["name"] = distribution.metadata.name
    res["package_dir"] = distribution.package_dir

    try:
        # Since Python packages nest under the top level package, e.g.
        # 'django', 'django.db', 'django.coore.cache', etc. we sort
        # the package names *by length* so the first one is the shortest.
        res["root_package"] = sorted(distribution.packages or [], key=len)[0]
    except IndexError:
        pass

    return res


def merge_config_dicts(*dicts):
    """Returns a new dictionary merging one or more config dictionaries.

    Generates a new dictionary that merges one or more configuration
    dictionaries returned by the _get_config_from_* functions.

    Copies key-value pairs where the value is not None. If multiple
    inputs have non-None values for the same key, the last input with
    a non-None value for the given key is the one that is included.

    This guarantees that all config keys are present, so, if any
    key-value pairs are absent after the merge, it will restore the
    keys with associated value None.

    """
    res = {
        k: v for (k, v)
        in chain.from_iterable([d.items() for d in dicts])
        if v is not None
    }

    for k in dicts[0]:
        if k not in res:
            res[k] = None

    return res

@contextmanager
def push_setup_py_dir(path):
    previous_dir = os.getcwd()
    try:
        # Shim in the path to the directory where setup.py is located.
        # Typically, setup.py is invoked by running a command like:
        #
        # python setup.py
        #
        # in the same directory where setup.py is located. Since the
        # current directory is usually in sys.path, it allows package
        # maintainers to write things like:
        #
        # from package import __version__
        #
        # Where package is the name of the package. This is pretty
        # common, but it only works if the directory with setup.py
        # is in sys.path.
        sys.path.insert(0, path)
        os.chdir(path)
        yield
    finally:
        try:
            sys.path.remove(path)
        except ValueError:
            pass
        os.chdir(previous_dir)
