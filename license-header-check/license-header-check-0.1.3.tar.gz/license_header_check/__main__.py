"""License Header checker.

Copyright 2021 Tobias Schaffner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import argparse
import importlib
import pkgutil
import sys
from importlib.util import find_spec
from pathlib import Path
from types import ModuleType


def _load_modules(package_name: str) -> list[ModuleType]:
    package = importlib.import_module(package_name)
    modules = [package]

    # Only walk the package, if it actually is a package not a module
    package_path = getattr(package, "__path__", None)
    if package_path:
        name = f"{package.__name__}."

        for _, modname, _ in pkgutil.walk_packages(package_path, name, onerror=lambda err: None):
            modules.append(importlib.import_module(modname))

    return modules


def _check_modules_for_license(modules: list[ModuleType], license: str) -> bool:
    prestine = True
    for module in modules:
        if not module.__doc__:
            print(f"Module {module.__name__} has no or empty documentation string")
            prestine = False
        elif license not in module.__doc__:
            print(f"Module {module.__name__} does not have the correct copyright notice")
            prestine = False
    return prestine


def check_licenses(license_file: Path, package_name: str) -> tuple[bool, int]:
    """Check all modules of a python package for license headers.

    Args:
        license_file (Path): A file containing the license header.
        package_name (str): The package that should be checked.

    Returns:
        tuple[bool, int]: the bool indicates, if any checks failed,
                          the int gives the number of checked modules
    """
    if not license_file.is_file():
        _print_fail("Given license_file is not a file")
    if not find_spec(package_name):
        _print_fail("Given package_name is not a valid module")
    license = license_file.read_text().strip()
    modules = _load_modules(package_name)
    return _check_modules_for_license(modules, license), len(modules)


def _print_fail(msg: str) -> None:
    sys.exit(msg)


def main() -> None:
    """License header check main that handles arg parsing."""
    parser = argparse.ArgumentParser()
    parser.add_argument("license_file")
    parser.add_argument("package_name")
    args = parser.parse_args()
    license_file = Path(args.license_file)
    prestine, count = check_licenses(license_file, args.package_name)
    if prestine:
        print(f"Checked {count} modules, all good!")
    else:
        _print_fail(f"Checked {count} modules, but some errors occured.")


if __name__ == "__main__":
    main()
