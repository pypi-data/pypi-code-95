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
from types import ModuleType
import pkgutil
import importlib
import argparse


def load_modules(package_name: str) -> list[ModuleType]:
    package = importlib.import_module(package_name)
    modules = [package]
    for _, modname, __ in pkgutil.walk_packages(path=package.__path__,
                                                        prefix=package.__name__+'.',
                                                        onerror=lambda x: None):
        modules.append(importlib.import_module(modname))
    return modules


def check_modules_for_license(modules: list[ModuleType], license: str) -> None:
    for module in modules:
        assert module.__doc__, f"Module {module.__name__} has no or empty documentation string"
        assert license in module.__doc__, f"Module {module.__name__} does not have the correct copyright notice"


def check_licenses(license_file, package_name) -> None:
    """This tool checks all modules of a python package for license headers."""
    modules = load_modules(package_name)
    license = open(license_file, 'r').read()
    check_modules_for_license(modules, license)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("license_file")
    parser.add_argument("package_name")
    args = parser.parse_args()
    check_licenses(args.license_file, args.package_name)


if __name__ == "__main__":
    main()