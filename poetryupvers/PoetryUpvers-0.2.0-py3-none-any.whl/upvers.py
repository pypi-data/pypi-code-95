"""PyProjectUpVers

Copyright (c) 2021 - GitLab
"""

import semver
import tomlkit as toml
from json import load as json_load
from os.path import exists
from os import getcwd
import poetryupvers.util as util
import poetryupvers.git as git


class PyProjectUpVers():
    def __init__(self, messages_file=None):
        self.check_pyproject()
        self.messages = self.get_message_config(messages_file=messages_file)
        self.pyproject = self.get_pyproject()
        self.version = self.parse_version()

    def check_pyproject(self):
        """
            Checks if directory contains pyproject.toml.

            If not, exit the command
        """
        if not exists("./pyproject.toml"):
            util.eprint(f"Unable to find pyproject in {getcwd()}")
            exit()

    def get_pyproject(self):
        """
            Opens pyproject.toml file and stores data as dictionary
        """
        with open("pyproject.toml", "r") as f:
            return toml.loads(f.read())

    def set_pyproject(self):
        """
            Writes to pyproject.toml file from modified dictionary
        """
        with open("pyproject.toml", "w") as f:
            f.write(toml.dumps(self.pyproject))
    
    def write_version_file(self):
        """
            Write VERSION file containig the version. To be used by a tool like release-cli
        """
        with open("VERSION", "w") as f:
            f.write(str(self.version))
    
    def get_message_config(self, messages_file=None):
        """
            Gets JSON file containing message 
            snippets to determine version bump
        """
        if messages_file:
            path = messages_file
        else:
            path = "./messages.json"
        if not exists(path):
            path = f"{util.get_install_dir(self.__class__)}/messages.json"
        
        print(f"Reading version message snippets from {path}")
        with open(path, "r") as f:
            return json_load(f)

    def parse_version(self):
        """
            Safe version parse using semver parsing
            and some exception handling
        """
        try:
            return semver.VersionInfo.parse(self.get_version())
        except ValueError as e:
            return self.to_valid_semver(e)

    def get_version(self):
        """
            Gets version stored in pyproject.toml
        """
        return self.pyproject["tool"]["poetry"]["version"]

    def set_version(self, version):
        """
            Sets version to be stored in pyproject.toml
        """
        print(f"Bumping version from {self.version} to {version}")
        self.version = version
        self.pyproject["tool"]["poetry"]["version"] = str(self.version)
    
    def determine_bump_type(self):
        """
            Iterates over commit messages and looks for keywords
            to denote a specific version bump type.

            This function only determines major, minor, and patch
        """
        bump_type = "patch"
        for m in git.get_all_msg_from_tag(git.get_latest_tag()):
            if self.messages["major"] in m:
                bump_type = "major"
                break
            elif any(msg in m for msg in self.messages["minor"]):
                bump_type = "minor"
                break
        return bump_type
    
    def bump_version(self):
        """
            Bumps version based on the bump type
        """
        bump_type = self.determine_bump_type()
        if bump_type == "major":
            self.set_version(self.version.bump_major())
        elif bump_type == "minor":
            self.set_version(self.version.bump_minor())
        else:
            self.set_version(self.version.bump_patch())
        self.set_pyproject()
    
    def to_valid_semver(self, error):
        """
            Error handler to get a valid version number.

            Note this should only occur once, before semver
            is implemented.
        """
        wrong_version = str(error).split(" is not")[0]
        if len(wrong_version.split(".")) == 2:
            version = wrong_version + ".0"
            return semver.VersionInfo.parse(version)
        elif len(wrong_version.split(".")) == 1:
            version = wrong_version + ".0.0"
            return semver.VersionInfo.parse(version)


    
