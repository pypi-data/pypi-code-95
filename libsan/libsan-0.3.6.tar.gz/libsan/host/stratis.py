from __future__ import absolute_import, division, print_function, unicode_literals

# Copyright (C) 2018 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

"""stratis.py: Module to manipulate stratis userspace package."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2018 Red Hat, Inc. All rights reserved."

import re  # regex
import libsan.host.linux
from libsan.host.cmdline import run
from libsan.host.cli_tools import Wrapper


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def get_stratis_service():
    return "stratisd"


class Stratis(Wrapper):
    def __init__(self, disable_check=True):
        self.disable_check = disable_check
        if libsan.host.linux.dist_ver() < 8:
            _print("FATAL: Stratis is not supported on RHEL < 8.")

        for pkg in ["stratisd", "stratis-cli"]:
            if not libsan.host.linux.is_installed(pkg):
                if not libsan.host.linux.install_package(pkg, check=False):
                    _print("FATAL: Could not install %s package" % pkg)

        self.commands = {}
        self.commands["all"] = list(self.commands.keys())
        self.arguments = {
            "force": [self.commands["all"], " --force"],
            "redundancy": [self.commands["all"], " --redundancy"],
            "propagate": [self.commands["all"], "--propagate "],
        }

        if libsan.host.linux.service_status(get_stratis_service(), verbose=False) != 0:
            if not libsan.host.linux.service_restart(get_stratis_service()):
                _print("FAIL: Could not start %s service" % get_stratis_service())
            else:
                _print("INFO: Service %s restarted." % get_stratis_service())

        Wrapper.__init__(self, self.commands, self.arguments, self.disable_check)

    @staticmethod
    def _remove_nones(kwargs):
        return {k: v for k, v in kwargs.items() if v is not None}

    def _run(self, cmd, verbosity=True, return_output=False, **kwargs):
        # Constructs the command to run and runs it

        # add '--propagate' flag by default to show whole trace when getting errors
        # This is a suggestion from devs
        if not ("propagate" in kwargs and not kwargs["propagate"]):
            cmd = self.arguments["propagate"][1] + cmd

        cmd = "stratis " + cmd
        cmd = self._add_arguments(cmd, **kwargs)

        ret = run(cmd, verbose=verbosity, return_output=return_output)
        if isinstance(ret, tuple) and ret[0] != 0:
            _print("WARN: Running command: '%s' failed. Return with output." % cmd)
        elif isinstance(ret, int) and ret != 0:
            _print("WARN: Running command: '%s' failed." % cmd)
        return ret

    def pool_create(self, pool_name=None, blockdevs=None, force=False, redundancy=None, key_desc=None, **kwargs):
        cmd = "pool create "
        if pool_name:
            cmd += "%s " % pool_name
        if key_desc:
            cmd += "--key-desc %s " % key_desc
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        kwargs.update({
            'force': force,
            'redundancy': redundancy,
        })
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_list(self, **kwargs):
        return self._run("pool list", **kwargs)

    def pool_destroy(self, pool_name=None, **kwargs):
        cmd = "pool destroy "
        if pool_name:
            cmd += "%s " % pool_name
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_rename(self, current=None, new=None, **kwargs):
        cmd = "pool rename "
        if current:
            cmd += "%s " % current
        if new:
            cmd += "%s " % new
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_add_data(self, pool_name=None, blockdevs=None, **kwargs):
        cmd = "pool add-data "
        if pool_name:
            cmd += "%s " % pool_name
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_add_cache(self, pool_name=None, blockdevs=None, **kwargs):
        cmd = "pool add-cache "
        if pool_name:
            cmd += "%s " % pool_name
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_init_cache(self, pool_name=None, blockdevs=None, **kwargs):
        cmd = "pool init-cache "
        if pool_name:
            cmd += "%s " % pool_name
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        return self._run(cmd, **self._remove_nones(kwargs))

    def blockdev_list(self, pool_name=None, **kwargs):
        cmd = "blockdev list "
        if pool_name:
            cmd += "%s " % pool_name
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_create(self, pool_name=None, fs_name=None, **kwargs):
        cmd = "fs create "
        if pool_name:
            cmd += "%s " % pool_name
        if fs_name:
            cmd += "%s " % fs_name
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_snapshot(self, pool_name=None, origin_name=None, snapshot_name=None, **kwargs):
        cmd = "fs snapshot "
        if pool_name:
            cmd += "%s " % pool_name
        if origin_name:
            cmd += "%s " % origin_name
        if snapshot_name:
            cmd += "%s " % snapshot_name
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_list(self, pool_name=None, **kwargs):
        cmd = "fs list "
        if pool_name:
            cmd += "%s " % pool_name
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_destroy(self, pool_name=None, fs_name=None, **kwargs):
        cmd = "fs destroy "
        if pool_name:
            cmd += "%s " % pool_name
        if fs_name:
            cmd += "%s " % fs_name
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_rename(self, pool_name=None, fs_name=None, new_name=None, **kwargs):
        cmd = "fs rename "
        if pool_name:
            cmd += "%s " % pool_name
        if fs_name:
            cmd += "%s " % fs_name
        if new_name:
            cmd += "%s " % new_name
        return self._run(cmd, **kwargs)

    def key_set(self, keyfile_path=None, key_desc=None, **kwargs):
        cmd = "key set "
        if keyfile_path:
            cmd += "--keyfile-path %s " % keyfile_path
        if key_desc:
            cmd += "%s " % key_desc
        return self._run(cmd, **kwargs)

    def key_reset(self, keyfile_path=None, key_desc=None, **kwargs):
        cmd = "key reset "
        if keyfile_path:
            cmd += "--keyfile-path %s " % keyfile_path
        if key_desc:
            cmd += "%s " % key_desc
        return self._run(cmd, **kwargs)

    def key_list(self, **kwargs):
        return self._run("key list", **kwargs)

    def key_unset(self, key_desc=None, **kwargs):
        cmd = "key unset "
        if key_desc:
            cmd += "%s " % key_desc
        return self._run(cmd, **kwargs)

    def pool_unlock(self, **kwargs):
        return self._run("pool unlock", **kwargs)

    def daemon_redundancy(self, **kwargs):
        return self._run("daemon redundancy", **kwargs)

    def daemon_version(self, **kwargs):
        return self._run("daemon version", **kwargs)

    def version(self, **kwargs):
        return self._run("--version", **kwargs)
