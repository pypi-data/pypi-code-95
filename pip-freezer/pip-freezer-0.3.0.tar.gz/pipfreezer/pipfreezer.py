import glob
import json
import logging
import re
import subprocess

from colorama import Fore, Style, init

logger = logging.getLogger(__name__)

init()

# -----------------------------------------------------------------------------


class PackageData:
    """Data class so we can manipulate packages and versions easily."""

    def __init__(self, package):
        package = package.strip()
        matches = re.search(r"[==|~=|>=|<=]{2}", package, re.IGNORECASE)
        if matches:
            pack_ver = package.split(matches[0])
            self.name = pack_ver[0].lower()
            # Get version and comment if any
            ver_com = [x.strip() for x in pack_ver[1].split("#")]
            self.version = ver_com.pop(0)
            self.comment = "  # ".join(ver_com) if ver_com else None
        else:
            pack_com = [x.strip() for x in package.split("#")]
            self.name = pack_com.pop(0).lower()
            self.version = None
            self.comment = "  # ".join(pack_com) if pack_com else None

    def freeze(self):
        if self.version:
            if not self.comment:
                return f"{self.name}=={self.version}"
            else:
                return f"{self.name}=={self.version} # {self.comment}"
        return self.name

    def __str__(self):
        return f"PackageData(name='{self.name}', version='{self.version}', comment='{self.comment}')"

    def __repr__(self):
        return self.__str__()

    def as_json(self):
        return json.dumps(
            {
                "name": self.name,
                "version": self.version,
                "comment": self.comment,
            }
        )


def get_pip_list():
    """Return a list of PackageData classes."""
    # print("subprocess")
    pip_freeze = subprocess.check_output(("pip", "freeze")).decode("utf8")
    pip_freeze = pip_freeze.split("\n")
    return [PackageData(x) for x in pip_freeze]


def get_pip_dict():
    """
    Return pip list as a dictoionary with package as key name and value
    as version.
    """
    return {p.name: p.version for p in get_pip_list()}


def find_requirements_files():
    """Return a list of requirements files."""
    files = glob.glob("**/requirements*.txt", recursive=True)
    return files + glob.glob("requirements/*.txt", recursive=True)


def open_requirements(file):
    """Return a clean list of requirements."""
    with open(file) as fp:
        return fp.readlines()


def save_requirements(file, lines):
    "Save a list of requirements."
    with open(file, "w") as fp:
        fp.writelines(lines)


def update_requirements_file(file, package_dict):
    """Open and update the requirements file."""
    lines = open_requirements(file)
    replaced_content = ""
    updated = []
    not_installed = []

    # Go line by line and determine if a package needs to be updated
    for line in lines:
        # Simply re-add comments or empty lines
        if line.startswith("#") or line.startswith("\n"):
            replaced_content += line
            continue

        package = PackageData(line)
        print(package)
        if package.name in package_dict:
            if package.version != package_dict[package.name]:
                updated.append(f"{package.name} {package.version} => {package_dict[package.name]}")
                package.version = package_dict[package.name]
            replaced_content += package.freeze() + "\n"
        else:
            replaced_content += line
            not_installed.append(package.name)
        save_requirements(file, replaced_content)
    return updated, not_installed


def run():
    """Main program."""
    package_dict = get_pip_dict()
    print(package_dict)
    requirements_files = find_requirements_files()

    updated = []
    not_installed = []
    for file in requirements_files:
        list1, list2 = update_requirements_file(file, package_dict)
        updated += list1
        not_installed += list2

    if updated:
        print(
            Fore.GREEN
            + "\nThe following packages have updated pinned versions:"
            + Fore.RESET
        )
        [print(Style.DIM + x + Style.RESET_ALL) for x in updated]

    if not_installed:
        print(
            Fore.YELLOW
            + "\nThe following packages are referenced in requirements, but are not installed:"
            + Fore.RESET
        )
        [print(Style.DIM + x + Style.RESET_ALL) for x in not_installed]


if __name__ == "__main__":
    run()
