import platform
import types
from git import Repo, InvalidGitRepositoryError
from multiprocessing import cpu_count
import subprocess
import importlib
import inspect
import socket

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata

"""
Source: https://github.com/rasbt/watermark

New BSD License

Copyright (c) 2014-2018, Sebastian Raschka.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of watermark nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

class Watermark():

    def get_packages(self, pkgs):
        packages = pkgs.split(",")
        return {package: self.get_package_version(package)
                for package in packages}

    def get_package_version(self, pkg_name):
        """Return the version of a given package"""
        if pkg_name == "scikit-learn":
            pkg_name = "sklearn"
        try:
            imported = importlib.import_module(pkg_name)
        except ImportError:
            version = "not installed"
        else:
            try:
                version = importlib_metadata.version(pkg_name)
            except importlib_metadata.PackageNotFoundError:
                try:
                    version = imported.__version__
                except AttributeError:
                    try:
                        version = imported.version
                    except AttributeError:
                        try:
                            version = imported.version_info
                        except AttributeError:
                            version = "unknown"
        return version

    def get_pyversions(self):
        return {
            "Python implementation": platform.python_implementation(),
            "Python version": platform.python_version()
        }

    def get_sysinfo(self):
        return {
            "Compiler": platform.python_compiler(),
            "OS": platform.system(),
            "Release": platform.release(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "CPU cores": cpu_count(),
            "Architecture": platform.architecture()[0],
            "Hostname": socket.gethostname(),
        }

    def get_git_info(self):
        data = {"hash": self.get_commit_hash(), 
        "origin": self.get_git_remote_origin(), 
        "branch": self.get_git_branch()}
        if data["hash"] != "":
            return data
        return None

    def get_commit_hash(self):
        process = subprocess.Popen(
            ["git", "rev-parse", "HEAD"], shell=False, stdout=subprocess.PIPE
        )
        git_head_hash = process.communicate()[0].strip()
        return git_head_hash.decode("utf-8")

    def get_git_remote_origin(self):
        process = subprocess.Popen(
            ["git", "config", "--get", "remote.origin.url"],
            shell=False,
            stdout=subprocess.PIPE,
        )
        git_remote_origin = process.communicate()[0].strip()
        return git_remote_origin.decode("utf-8")

    def get_git_branch(self):
        process = subprocess.Popen(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            shell=False,
            stdout=subprocess.PIPE,
        )
        git_branch = process.communicate()[0].strip()
        return git_branch.decode("utf-8")

    def get_repo(self, package_name):
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            return
            
        path = spec.origin
        try:
            repo = Repo(path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            return
        
        return repo
    
    def get_repo_info(self, package_name):
        repo = self.get_repo(package_name)
        assert repo is not None, 'Unable to find the repo.'
        
        return {
            'branch': repo.active_branch.name,
            'commit': repo.active_branch.commit.hexsha,
            'remote': repo.remotes.origin.url
        }
        
    def get_all_import_versions(self, global_namespaces):

        to_print = {}
        imported_pkgs = {
            val.__name__.split(".")[0]
            for _, val in global_namespaces.items()
            if isinstance(val, types.ModuleType)
        }
        submodules = {
            inspect.getmodule(val).__name__.split(".")[0]
            for _, val in global_namespaces.items()
            if (inspect.getmodule(val) is not None)
        }
        imported_pkgs = set.union(submodules, imported_pkgs)

        imported_pkgs.discard("builtins")
        imported_pkgs.discard("IPython")
        imported_pkgs.discard("__main__")
        
        for pkg_name in imported_pkgs:
            pkg_version = self.get_package_version(pkg_name)
            if pkg_version not in ("not installed", "unknown"):
                to_print[pkg_name] = pkg_version
        return to_print