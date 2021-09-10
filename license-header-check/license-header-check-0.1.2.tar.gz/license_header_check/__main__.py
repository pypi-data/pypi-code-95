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
from types import ModuleType


def _load_modules(package_name: str) -> list[ModuleType]:
    package = importlib.import_module(package_name)
    modules = [package]

    path = package.__path__  # type: ignore # noqa: WPS609
    name = f"{package.__name__}."

    for _, modname, _ in pkgutil.walk_packages(path, name, onerror=lambda err: None):
        modules.append(importlib.import_module(modname))
    return modules


def _check_modules_for_license(modules: list[ModuleType], license: str) -> None:
    for module in modules:
        assert module.__doc__, f"Module {module.__name__} has no or empty documentation string"
        assert (
            license in module.__doc__
        ), f"Module {module.__name__} does not have the correct copyright notice"


def check_licenses(license_file: str, package_name: str) -> None:
    """Check all modules of a python package for license headers.

    Args:
        license_file (str): A file containing the license header.
        package_name (str): The package that should be checked.
    """
    modules = _load_modules(package_name)
    with open(license_file, "r") as license_file_handler:
        license = license_file_handler.read()
    _check_modules_for_license(modules, license)


def main() -> None:
    """License header check main that handles arg parsing."""
    parser = argparse.ArgumentParser()
    parser.add_argument("license_file")
    parser.add_argument("package_name")
    args = parser.parse_args()
    check_licenses(args.license_file, args.package_name)


if __name__ == "__main__":
    main()
